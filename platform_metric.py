#!/usr/bin/env python
#!-*- coding:utf8 -*-

import requests
import time
import json
import sys
import os.path
import yaml
import arrow

counters = [
    "vfcc.service.http.up.alive/master_alive=101.69.115.17"
]

URL = {
    "login" : "http://owl.fastweb.com.cn/api/v1/auth/login",
    "hostgroup" : 'http://owl.fastweb.com.cn/api/v1/hostgroup/hosts',
    "aggregate" : 'http://query.owl.fastweb.com.cn/graph/history',
}

def login(name, password):
    url = URL["login"]
    payload = {
        'name': name,
        'password': password
    }
    r = requests.post(url, payload)
    out = json.loads(r.text)
    return out["data"]["sig"]

def hostgroup2hostnames(user, sig, hostgroup):
    url = URL["hostgroup"]
    payload = {
        'cName': user,
        'cSig': sig,
        'hostgroups': hostgroup
    }

    r = requests.post(url, payload)
    out = json.loads(r.text)
    res = []
    for i in out["data"]["hosts"]:
        res.append(i["hostname"])
    return res

def aggregate(user, sig, startTs, endTs, endpoints):
    url = URL["aggregate"]
    endpointCounters = [{"endpoint":x, "counter":y} for x in endpoints for y in counters]
    payload = {
        "start": startTs,
        "end": endTs,
        "cf": "AVERAGE",
        "endpoint_counters": endpointCounters
    }
    r = requests.post(url, data = json.dumps(payload))
    out = json.loads(r.text)
    return out

def readConf():
    if os.path.isfile("secret.yaml"):
        pass
    else:
        return {}

    with open("secret.yaml", 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "usage:    ./platform_metric.py [time Start in ISO8601] [time End in ISO8601] [platformName]"
        print "example:  ./platform_metric.py 2017-02-28T06:01:00+0800 2017-03-28T06:01:00+0800 c01.i07"
        sys.exit(1) 
    #ts = int(time.time()) # input
    #platform = "c06.i06"  # input
    sTime = arrow.get(sys.argv[1])
    eTime = arrow.get(sys.argv[2])
    startTs = sTime.timestamp
    endTs = eTime.timestamp

    platform = sys.argv[3]     # input
    user = ""      # data
    password = ""    # data
    conf = readConf()
    if len(conf) == 2:
        user = conf["user"]
        password = conf["pass"]
    sig = login(user, password) 
    endpoints = hostgroup2hostnames(user, sig, platform)
    if len(endpoints) == 0:
        #print json.dumps({"message":"Platform is null. No endpoints inside."})
        print json.dumps(False)
        sys.exit(0)
    raw = aggregate(user, sig, startTs , endTs, endpoints) # 5mins ago  - now
    print json.dumps(raw)
