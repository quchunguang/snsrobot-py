#!/usr/bin/env python2
# -*- encoding=utf8 -*-
'''
snsrebot.py cli client

This should be run on each robot as a SNS client.
'''
import requests
import random
# import json
# from bson import json_util

import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import approximation as approx

URL = 'http://127.0.0.1:8080'


def sign_up(username, password, group):
    '''
    New robot sign-up itself to SNS
    '''
    req = {
        "username": username,
        "password": password,
        "group": group
    }
    resp = access("/sign_up", req)
    return resp["code"] == 0


def sign_in(username, password):
    '''
    Robot sign-in itself and get access token
    '''
    req = {"username": username, "password": password}
    resp = access("/sign_in", req)
    return resp["access_token"]


def access(slot, obj):
    '''
    Request server and get answer with JSON object
        slot: access endpoint format like "/sign_up"
        obj:  JSON object
    This function returns JSON object as well.
    '''
    resp = requests.post(URL+slot, json=obj)
    if resp.status_code != 200:
        print "[ERROR] connect err"
    return resp.json()


def robot_rating(token, username_source, username_target):
    '''
    Robot rating fight between two robot.
    Fight and upload experience result to SNS.
    The caller of the function might be a third-party robot.
    '''

    # fight between username_source and username_target ...

    # report result
    req = {
        "access_token": token,
        "username_source": username_source,
        "username_target": username_target,
        "result_source": random.random(),
        "result_target": random.random(),
    }
    resp = access("/upload_result", req)
    print resp


def draw_robot_graph(token):
    '''
    Get all edges information and draw the graph of connection of robots.
    '''
    req = {"access_token": token}
    resp = access("/datagraph", req)
    if resp["code"] != 0:
        print "[ERROR] get robot edges info error"


    # create graph
    graph = nx.Graph()

    # add nodes
    # nodes = resp["robot_nodes"]
    # for node in nodes:
    #     graph.add_node(node["username"], group=node["group"])

    # add edges
    edges = resp["robot_edges"]
    weighted_edges = [(e["source"], e["target"], e["weight"]) for e in edges]
    graph.add_weighted_edges_from(weighted_edges)

    # export data with GraphML format
    # for example, Cytoscape can read the GraphML format
    nx.write_graphml(graph, "output/test.graphml")

    # draw graph
    nx.draw(graph)
    plt.show()

    # demos the usage of algorithms in networkx
    print approx.node_connectivity(graph)


def init_database():
    '''
    Initialize the MongoDB database

    WARN: ALL DATA WILL BE LOST!!!
    This interface will be removed in release.
    '''
    req = {
        "secret": "5fa09e02-8525-11e5-bad8-60672041b848",
    }
    resp = access("/admin/init_database", req)
    if resp["code"] == 0:
        print "[INFO] Initialize the MongoDB database OK."
    else:
        print "[ERROR] Initialize the MongoDB database failed!"

def gen_users():
    '''
    Step 1: Generate some sample users.
    '''
    for i in xrange(1, 11):
        username = "u"+str(i)
        password = str(i)
        group = i % 4
        sign_up(username, password, group)
        sign_in(username, password)


def gen_games(token):
    '''
    Step 2: Generate some pair games.
    '''
    for i in xrange(1, 101):
        print "Round", i,
        username_source = "u"+str(random.randint(1, 10))
        username_target = "u"+str(random.randint(1, 10))
        robot_rating(token, username_source, username_target)


def main():
    '''
    Test Only.
    '''
    # init_server()
    # gen_users()

    # All RPC functions, except for sign_in(), needs token to access.
    # here using u10 as demo operator account.
    token = sign_in("u10", "10")

    # gen_games(token)

    # Draw the graph with matplotlab
    draw_robot_graph(token)

if __name__ == '__main__':
    main()
