#!/usr/bin/env python2
# -*- encoding=utf8 -*-
"""snsrobot - CLI interface simulates the robot client.
This should be run on each robot as a SNS client.

Usage:
  snsrobot.py (-h | --help)
  snsrobot.py --version
  snsrobot.py -u <username> -p <password> info
  snsrobot.py -u <username> -p <password> friends
  snsrobot.py -u <username> -p <password> draw-graph
  snsrobot.py -s <secret> admin-init
  snsrobot.py server-info [--users-top100 | --games-top100]
  snsrobot.py gen-users <prefix> <count> <group> <password>
  snsrobot.py -u <username> -p <password> gen-games <prefix1> <count1> <prefix2> <count2> <gamecount>

Options:
  -h --help        Show this screen.
  --version        Show version.
  -u <username>    Sign In username.
  -p <password>    Sign In password.
  -s <secret>      Super secret token for administrator

Example:
    snsrobot.py -s '5fa09e02-8525-11e5-bad8-60672041b848' admin-init
"""
from docopt import docopt
from networkx.algorithms import approximation as approx
import matplotlib.pyplot as plt
import networkx as nx
import random
import requests

URL = 'http://127.0.0.1:8080'
args = docopt(__doc__, version='snsrobot.py 0.1')
# print args

def access(slot, obj):
    """
    Request server and get answer with JSON object
    This function returns JSON object as well.

    :param obj: JSON object
    :param slot: access endpoint format like "/api/sign_up"
    """
    resp = requests.post(URL + slot, json=obj)
    if resp.status_code != 200:
        print "[ERROR] connect err"
    return resp.json()


def sign_up(username, password, group):
    """
    New robot sign-up itself to SNS
    """
    req = {
        "username": username,
        "password": password,
        "group": group
    }
    resp = access("/api/signup", req)
    return resp["code"] == 0


def sign_in(username, password):
    """
    Robot sign-in itself and get access token
    """
    req = {"username": username, "password": password}
    resp = access("/api/signin", req)
    return resp["access_token"]


def robot_rating(token, username_source, username_target):
    """
    Robot rating fight between two robot.
    Fight and upload experience result to SNS.
    The caller of the function might be a third-party robot.
    """

    # fight between username_source and username_target ...

    # report result
    req = {
        "access_token": token,
        "username_source": username_source,
        "username_target": username_target,
        "result_source": random.random(),
        "result_target": random.random(),
    }
    resp = access("/api/upload_result", req)
    print resp


def draw_graph():
    """
    Get all edges information and draw the graph of connection of robots.
    """
    token = sign_in(args["-u"], args["-p"])

    req = {"access_token": token}
    resp = access("/api/datagraph", req)
    if resp["code"] != 0:
        print "[ERROR] get robot edges info error"

    # create graph
    G = nx.Graph()

    # add nodes
    # nodes = resp["robot_nodes"]
    # for node in nodes:
    #     graph.add_node(node["username"], group=node["group"])

    # add edges
    edges = resp["robot_edges"]
    weighted_edges = [(e["source"], e["target"], e["weight"]) for e in edges]
    G.add_weighted_edges_from(weighted_edges)

    # export data with GraphML format
    # for example, Cytoscape can read the GraphML format
    nx.write_graphml(G, "static/tmp/test.graphml")

    # draw graph
    nx.draw(G)
    # nx.draw_random(G)
    # nx.draw_circular(G)
    # nx.draw_spectral(G)
    plt.show()  # need optional dependence matplotlab

    # demos the usage of algorithms in networkx
    print approx.node_connectivity(G)


def admin_init():
    """
    Initialize the MongoDB database

    WARN: ALL DATA WILL BE LOST!!!
    This interface will be removed in release.
    """
    req = {
        "secret": args["-s"],
    }
    resp = access("/api/admin_init", req)
    if resp["code"] == 0:
        print "[INFO] Initialize the MongoDB database OK."
    else:
        print "[ERROR] Initialize the MongoDB database failed!"


def gen_users():
    """
    Step 1: Generate some sample users.
    """
    for i in xrange(1, int(args["<count>"])+1):
        username = args["<prefix>"] + str(i)
        password = args["<password>"]
        group = args["<group>"]
        sign_up(username, password, group)


def gen_games():
    """
    Step 2: Generate some pair games.
    """
    token = sign_in(args["-u"], args["-p"])
    for i in xrange(1, int(args["<gamecount>"])+1):
        print "Round", i,
        id_source = random.randint(1, int(args["<count1>"]))
        id_target = random.randint(1, int(args["<count2>"]))
        username_source = args["<prefix1>"] + str(id_source)
        username_target = args["<prefix2>"] + str(id_target)
        robot_rating(token, username_source, username_target)

def info():
    print "TODO: Not NotImplementedError"

def friends():
    print "TODO: Not NotImplementedError"

def server_info():
    print "TODO: Not NotImplementedError"

def main():
    """
    Parse arguments and call.
    """

    if args["info"]:
        info()
    elif args["friends"]:
        friends()
    elif args["draw-graph"]:
        draw_graph()
    elif args["admin-init"]:
        admin_init()
    elif args["server-info"]:
        server_info()
    elif args["gen-users"]:
        gen_users()
    elif args["gen-games"]:
        gen_games()
    else:
        print "TODO: Not NotImplementedError"
        print "Arguments:"
        print args


if __name__ == '__main__':
    main()
