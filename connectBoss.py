#!/usr/bin/env python
#!-*- coding:utf8 -*-

import requests
import time
import json
import sys
import os.path
import yaml
import arrow

def login(name, password):
    url = "http://owl.fastweb.com.cn/api/v1/auth/login"
    payload = {
        'name': name,
        'password': password
    }
    r = requests.post(url, payload)
    out = json.loads(r.text)
    return out["data"]["sig"]

def hostgroup2hostnames(user, sig, hostgroup):
    url = 'http://owl.fastweb.com.cn/api/v1/hostgroup/hosts'
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

def history(user, sig, startTs, endTs):
    url = "http://owl.fastweb.com.cn/api/v2/portal/eventcases/get"
    if startTs >= endTs:
        print " start timestamp bigger than end timestamp"
        exit(1)
    
    payload = {
        "status": "PROBLEM,OK",
        "process": "ALL",
        "includeEvents": True,
        "limit": 20000,
        "startTime": startTs,
        "endTime":   endTs,
        "cName": user,
        "cSig": sig
    } 

    r = requests.post(url, payload)
    out = json.loads(r.text)

    #print json.dumps(out["data"]["eventCases"])
    result = []
    for i in out["data"]["eventCases"]:
        item = {
            "hostname": i["hostname"],
            "ip": i["ip"],
            "content": i["content"],
            "metric": i["metric"],
            "severity": i["severity"],
            "status": i["status"],
            "process": i["process"],
            "timeStart": i["timeStart"],
            "contact": i["contact"][0],
            "notes": i["notes"],
            "platform": i["platform"]
        }
        result.append(item)

    final = {
        "count": len(result),
        "timestamp": [startTs, endTs],
        "result": result
    }
    print json.dumps(final)

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
    if len(sys.argv) != 3:
        print "usage:    ./connectBoss.py [time Start in ISO8601] [time End in ISO8601]"
        print "example:  ./connectBoss.py 2017-05-11T06:01:00+0800 2017-05-12T06:01:00+0800"
        sys.exit(1) 
    #ts = int(time.time()) # input
    #platform = "c06.i06"  # input
    sTime = arrow.get(sys.argv[1])
    eTime = arrow.get(sys.argv[2])
    startTs = sTime.timestamp
    endTs = eTime.timestamp

    user = ""      # data
    password = ""    # data
    conf = readConf()
    if len(conf) == 2:
        user = conf["user"]
        password = conf["pass"]
    sig = login(user, password) 
    history(user, sig, startTs, endTs)
