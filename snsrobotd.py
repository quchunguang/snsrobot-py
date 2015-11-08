#!/usr/bin/env python2
# -*- encoding=utf8 -*-
'''
snsrebotd.py cli server daemon

This should be run on server as a SNS service daemon.
'''

import os
import web
import json
import pymongo
import uuid
import time
import elo_rating
from bson import json_util

URLS = (
    '/', 'Index',
    '/sign_up', 'SignUp',
    '/sign_in', 'SignIn',
    '/upload_result', 'UploadResult',
    '/reports', 'Reports',
    '/datagraph', 'DataGraph',
    '/forcedirected', 'ForceDirected',
    '/admin/init_database', 'InitDatabase',
)

SECRET = '5fa09e02-8525-11e5-bad8-60672041b848'
RENDER = web.template.render('templates/')
MONGO = pymongo.MongoClient('127.0.0.1', 27017)


def getNextSequence(name):
    '''
    Generate next seq id
    https://docs.mongodb.org/manual/tutorial/create-an-auto-incrementing-field/
    '''
    counters = MONGO.snsrobot.counters
    ret = counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        return_document=pymongo.ReturnDocument.AFTER
    )
    return ret["seq"]


class Index:

    '''
    Homepage
    '''

    def GET(self):
        '''
        Generate HTML reports using template
        '''

        # count users
        users = MONGO.snsrobot.users
        user_count = users.count()

        # count edges
        edges = MONGO.snsrobot.edges
        edge_count = edges.count()

        # Apply template
        return RENDER.overview(user_count, edge_count)


class SignUp:

    '''
    Sign-up a robot
    '''

    def POST(self):
        '''
        get post json and echo.
        '''
        i = web.input()
        data = web.data()
        user = json.loads(data)
        user["_id"] = getNextSequence("userid")
        user["rank"] = 0
        print user

        users = MONGO.snsrobot.users
        obj = users.find_one({"username": user["username"]})

        if obj == None:
            users.insert_one(user)
            print "[INFO] users: add user", user
            return '{"code": 0}'
        else:
            print "[WARN] users: add user exist", user
            return '{"code": 1}'


class SignIn:

    '''
    Sign-in a robot
    '''

    def POST(self):
        '''
        get post json and echo.
        '''
        i = web.input()
        data = web.data()
        user = json.loads(data)

        users = MONGO.snsrobot.users
        tokens = MONGO.snsrobot.tokens
        obj = users.find_one(
            {"username": user["username"], "password": user["password"]})

        if obj == None:
            print "[WARN] sign-in error: no such user or bad password", user
            return '{"code": 1, "access_token": ""}'
        else:
            tokens.remove({"username": user["username"]})
            access_token = str(uuid.uuid3(
                uuid.NAMESPACE_DNS, user["username"].encode("ascii")))
            token = {
                "access_token": access_token,
                "time": time.ctime(),
                "username": user["username"],
            }
            tokens.insert(token)
            print "[INFO] sign-in ok, send token", access_token
            return '{"code": 0, "access_token": "' + access_token + '"}'


class UploadResult:

    '''
    Upload Result
    '''

    def POST(self):
        '''
        get post json and echo.
        '''
        i = web.input()
        res = json.loads(web.data())

        # check access right
        tokens = MONGO.snsrobot.tokens
        obj = tokens.find_one({"access_token": res["access_token"]})
        if obj == None:
            print "[ERROR] upload result error, access denied."
            return '{"code": 1}'

        # score only 0 or 1
        score = 0
        if res["result_source"] > res["result_target"]:
            score = 1

        users = MONGO.snsrobot.users
        user1 = users.find_one({"username": res["username_source"]})
        user2 = users.find_one({"username": res["username_target"]})

        if user1 == None or user2 == None:
            print "[ERROR] upload result error, user not exist"
            return '{"code": 2}'

        # Elo Rating
        rank1, rank2 = elo_rating.elo_rating(
            user1["rank"], user2["rank"], score, 16)

        users.update_one({"_id": user1["_id"]}, {"$set": {"rank": rank1}})
        users.update_one({"_id": user2["_id"]}, {"$set": {"rank": rank2}})

        update_edge(user1, user2)

        # create result
        res3 = {
            "code": 0,  # OK
            "score": score,
            "rank1": rank1,
            "rank2": rank2,
        }
        return json.dumps(res3)


def update_edge(user1, user2):
    '''
    Add edge between users, or adjust the weight.
    '''
    # Smaller _id is source, so that edge {source, target} is unique.
    if user1["_id"] > user2["_id"]:
        source, target = user2, user1
    else:
        source, target = user1, user2

    edges = MONGO.snsrobot.edges
    cond = {"source": source["_id"], "target": target["_id"]}
    edge = {
        "$set": {"source": source["_id"]},
        "$set": {"target": target["_id"]},
        "$inc": {"weight": 1}
    }
    edges.update_one(cond, edge, upsert=True)


class Reports:

    '''
    Human UI Reports
    '''

    def GET(self):
        '''
        Generate HTML reports using template
        '''

        # Robot rank
        users = MONGO.snsrobot.users
        robot_rank = users.find().sort("rank", pymongo.DESCENDING).limit(100)

        # Edge rank

        edges = MONGO.snsrobot.edges
        edge_rank = edges.find().sort("weight", pymongo.DESCENDING).limit(100)

        # Apply template
        return RENDER.reports(robot_rank, edge_rank)


class ForceDirected:

    '''
    Human UI Reports
    '''

    def GET(self):
        '''
        Generate HTML reports using template
        '''

        users = MONGO.snsrobot.users
        edges = MONGO.snsrobot.edges

        obj = {
            "nodes": [
                {"name": user["username"], "group": user["group"]}
                for user in users.find().sort("_id", pymongo.ASCENDING)
            ],
            "links": [
                {"source": edge["source"]-1, "target": edge[
                    "target"]-1, "weight":edge["weight"]}
                for edge in edges.find()
            ],
        }

        local = os.getenv('PWD')
        jsonfile = "/static/tmp/forcedirected.json"
        json.dump(obj, open(local + jsonfile, 'w'))

        # Apply template
        return RENDER.forcedirected(jsonfile)


class DataGraph:

    '''
    Return data to client for create graph view
    '''

    def POST(self):
        '''
        get post json and echo.
        '''
        i = web.input()
        data = web.data()
        res = json.loads(data)

        # check access right
        tokens = MONGO.snsrobot.tokens
        obj = tokens.find_one({"access_token": res["access_token"]})
        if obj == None:
            return '{"code": 1}'

        users = MONGO.snsrobot.users
        edges = MONGO.snsrobot.edges

        res = {
            "code": 0,
            "robot_nodes": users.find(),
            "robot_edges": edges.find(),
        }
        # res includes bson objects.
        # Using bson.json_util.dumps() instead of json.dumps()
        return json_util.dumps(res)


class InitDatabase:

    '''
    Initialize the MongoDB database

    WARN: ALL DATA WILL BE LOST!!!
    This interface will be removed in release.
    '''

    def POST(self):
        '''
        get post json and echo.
        '''
        i = web.input()
        req = json.loads(web.data())
        if req["secret"] == SECRET:
            init_database()
            return '{"code": 0}'
        else:
            return '{"code": 1}'


def init_database():
    users = MONGO.snsrobot.users
    tokens = MONGO.snsrobot.tokens
    edges = MONGO.snsrobot.edges
    counters = MONGO.snsrobot.counters

    users.remove()
    tokens.remove()
    edges.remove()
    counters.remove()

    counters.insert({"_id": "userid", "seq": 0})


def main():
    '''
    Start Webservice
    '''
    app = web.application(URLS, globals())
    app.run()

if __name__ == "__main__":
    main()
