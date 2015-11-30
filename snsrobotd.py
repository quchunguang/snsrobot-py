#!/usr/bin/env python2
# -*- encoding=utf8 -*-
"""
snsrebotd.py cli server daemon

This should be run on server as a SNS service daemon.
"""

from bson import json_util
import datetime
import elo_rating
import json
import os
import pymongo
import time
import uuid
import web

urls = (
    '/', 'Index',
    '/signup', 'SignUp',
    '/signin', 'SignIn',
    '/signout', 'SignOut',
    '/reports', 'Reports',
    '/forcedirected', 'ForceDirected',
    '/api/(.*)', 'Api',
)

web.config.debug = False

SECRET = '5fa09e02-8525-11e5-bad8-60672041b848'
app = web.application(urls, globals())
render = web.template.render('templates/')
mongo = pymongo.MongoClient('127.0.0.1', 27017)
session = web.session.Session(app,
                              web.session.DiskStore('sessions'),
                              initializer={'login': 0}, )


def logged():
    """
    判断用户是否登陆
    """
    if session.login > 0:
        return True
    else:
        return False


def getNextSequence(name):
    """
    Generate next seq id
    https://docs.mongodb.org/manual/tutorial/create-an-auto-incrementing-field/
    """
    counters = mongo.snsrobot.counters
    ret = counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        return_document=pymongo.ReturnDocument.AFTER
    )
    return ret["seq"]


class Index:
    """
    Homepage
    """

    def GET(self):
        """
        Generate HTML reports using template
        """

        if not logged():
            raise web.seeother('/signin')

        # count users & edges
        users = mongo.snsrobot.users
        edges = mongo.snsrobot.edges

        status_info = {
            "user_count": users.count(),
            "edge_count": edges.count(),
        }


        # Apply template
        return render.overview(session["username"], status_info)


class SignUp:
    """
    Sign-up a human
    """
    # vusername = form.regexp(r".{3,20}$", u'用户名长度为3-20位')
    # vpass = form.regexp(r".{6,20}$", u'密码长度为6-20位')
    # vemail = form.regexp(r".*@.*", u"must be a valid email address")
    # vgroup = form.regexp(r".{3,20}$", u'组名长度为3-20位数字')
    # signupform = web.form.Form(
    #     form.Textbox('username', description=u'邮箱名'),
    #     form.Password("password", description=u"密码"),
    #     form.Password("password2", description=u"确认密码"),
    #     form.Textbox('group', description=u'组'),
    #     form.Button(u"马上注册", type="submit", description="submit"),
    #     # validators=[form.Validator("password?", lambda i: i.password == i.password2)],
    # )

    def GET(self):
        return render.signup()

    def POST(self):
        """
        get post json and echo.
        """
        formdata = web.input()
        username = web.net.websafe(formdata.username)
        password = web.net.websafe(formdata.password)
        password2 = web.net.websafe(formdata.password2)
        group = web.net.websafe(formdata.group)
        regip = web.ctx.ip
        regdate = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        # if not self.signupform.validates():
        if password != password2:
            return render.signup(u'两次输入的密码不同,请重新输入')

        # 判断用户名是否存在
        users = mongo.snsrobot.users
        obj = users.find_one({"username": username})
        if obj is None:
            user = {
                "_id": getNextSequence("userid"),
                "username": username,
                "password": password,
                "group": group,
                "ip": regip,
                "date": regdate,
                "rank": 0,
            }
            users.insert_one(user)

            print "[INFO] users: add user", username, password
            raise web.seeother('/')
        else:
            print "[WARN] users: add user exist", username, password
            return render.signup(u'邮箱名已存在')


class SignIn:
    """
    Sign-in a human
    """

    def GET(self):
        if logged():
            return 'you are logged'
        else:
            return render.signin()

    def POST(self):
        """
        get post json and echo.
        """
        postdata = web.input()
        username = web.net.websafe(postdata.username)
        password = web.net.websafe(postdata.password)

        users = mongo.snsrobot.users
        tokens = mongo.snsrobot.tokens
        obj = users.find_one({"username": username, "password": password})

        if obj is None:
            print "[WARN] sign-in error: no such user or bad password", username, password
            return render.signin(u'邮箱名或密码错误')
            # return '{"code": 1, "access_token": ""}'
        else:
            session.login = obj["_id"]
            session["username"] = obj["username"]
            raise web.seeother('/')


# 注销登陆页面
class SignOut:
    """
    Sign Out for human
    """
    def GET(self):
        session.login = 0
        session.kill()
        raise web.seeother('/signin')


class Reports:
    """
    Human UI Reports
    """

    def GET(self):
        """
        Generate HTML reports using template
        """

        # Robot rank
        users = mongo.snsrobot.users
        robot_rank = users.find().sort("rank", pymongo.DESCENDING).limit(100)

        # Edge rank

        edges = mongo.snsrobot.edges
        edge_rank = edges.find().sort("weight", pymongo.DESCENDING).limit(100)

        # Apply template
        return render.reports(session["username"], robot_rank, edge_rank)


class ForceDirected:
    """
    Human UI Reports
    """

    def GET(self):
        """
        Generate HTML reports using template
        """

        users = mongo.snsrobot.users
        edges = mongo.snsrobot.edges

        obj = {
            "nodes": [{"name": user["username"],
                       "group": user["group"]} for user in users.find().sort("_id", pymongo.ASCENDING)],
            "links": [{"source": edge["source"] - 1,
                       "target": edge["target"] - 1,
                       "weight": edge["weight"]} for edge in edges.find()],
        }

        local = os.getenv('PWD')
        json_file = "/static/tmp/forcedirected.json"
        json.dump(obj, open(local + json_file, 'w'))

        # Apply template
        return render.forcedirected(session["username"], json_file)


# APIs
def api_signup(user):
    """
    Sign Up a robot
    """
    user["_id"] = getNextSequence("userid")
    user["rank"] = 0
    print user

    users = mongo.snsrobot.users
    obj = users.find_one({"username": user["username"]})

    if obj is None:
        users.insert_one(user)
        print "[INFO] users: add user", user
        return '{"code": 0}'
    else:
        print "[WARN] users: add user exist", user
        return '{"code": 1}'


def api_signin(user):
    """
    Sign In a robot
    """
    users = mongo.snsrobot.users
    tokens = mongo.snsrobot.tokens
    obj = users.find_one(
        {"username": user["username"], "password": user["password"]})

    if obj is None:
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


def update_edge(user1, user2):
    """
    Add edge between users, or adjust the weight.
    """
    # Smaller _id is source, so that edge {source, target} is unique.
    if user1["_id"] > user2["_id"]:
        source, target = user2, user1
    else:
        source, target = user1, user2

    edges = mongo.snsrobot.edges
    cond = {"source": source["_id"], "target": target["_id"]}
    edge = {
        "$set": {"source": source["_id"], "target": target["_id"]},
        "$inc": {"weight": 1}
    }
    edges.update_one(cond, edge, upsert=True)


def api_upload_result(req):
    """
    Upload Result
    """
    # check access right
    tokens = mongo.snsrobot.tokens
    obj = tokens.find_one({"access_token": req["access_token"]})
    if obj is None:
        print "[ERROR] upload result error, access denied."
        return '{"code": 1}'

    # score only 0 or 1
    score = 0
    if req["result_source"] > req["result_target"]:
        score = 1

    users = mongo.snsrobot.users
    user1 = users.find_one({"username": req["username_source"]})
    user2 = users.find_one({"username": req["username_target"]})

    if user1 is None or user2 is None:
        print "[ERROR] upload result error, user not exist"
        return '{"code": 2}'

    # Elo Rating
    rank1, rank2 = elo_rating.elo_rating(
        user1["rank"], user2["rank"], score, 16)

    users.update_one({"_id": user1["_id"]}, {"$set": {"rank": rank1}})
    users.update_one({"_id": user2["_id"]}, {"$set": {"rank": rank2}})

    update_edge(user1, user2)

    # create result
    res = {
        "code": 0,  # OK
        "score": score,
        "rank1": rank1,
        "rank2": rank2,
    }
    return json.dumps(res)


def api_datagraph(req):
    """
    Return data to client for create graph view
    """
    # check access right
    tokens = mongo.snsrobot.tokens
    obj = tokens.find_one({"access_token": req["access_token"]})
    if obj is None:
        return '{"code": 1}'

    users = mongo.snsrobot.users
    edges = mongo.snsrobot.edges

    res = {
        "code": 0,
        "robot_nodes": users.find(),
        "robot_edges": edges.find(),
    }
    # res includes bson objects.
    # Using bson.json_util.dumps() instead of json.dumps()
    return json_util.dumps(res)


def init_database():
    users = mongo.snsrobot.users
    tokens = mongo.snsrobot.tokens
    edges = mongo.snsrobot.edges
    counters = mongo.snsrobot.counters

    users.remove()
    tokens.remove()
    edges.remove()
    counters.remove()

    counters.insert({"_id": "userid", "seq": 0})


def api_admin_init(req):
    """
    Initialize the MongoDB database

    WARN: ALL DATA WILL BE LOST!!!
    This interface will be removed in release.
    """
    if req["secret"] == SECRET:
        init_database()
        return '{"code": 0}'
    else:
        return '{"code": 1}'


apis = {
    "signup": api_signup,
    "signin": api_signin,
    "upload_result": api_upload_result,
    "datagraph": api_datagraph,
    "admin_init": api_admin_init,
}


class Api:
    """
    Entry of all APIs access.

    APIs called by HTTP/POST method.
    The request and response data are both JSON formated.
    Authorize by slot '/api/signin' and will return a access_token if success.
    All other operations must given the access_token for authorize.
    """
    def POST(self, name):
        req = json.loads(web.data())
        resp = apis[name](req)
        return resp


if __name__ == "__main__":
    app.run()
