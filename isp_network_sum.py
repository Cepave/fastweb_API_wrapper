#!/usr/bin/env python
#!-*- coding:utf8 -*-

import requests
import time
import json
import sys
import os.path
import yaml
import arrow
import itertools

counters = [
    "net.if.out.bits/iface=eth_all",
    "net.if.in.bits/iface=eth_all"
]

endpoints = [
    "tvn-nm-043-254-169-220",
    "tvn-nm-043-254-169-221",
    "tvn-nm-043-254-169-222",
    "tvn-nm-043-254-169-223",
    "tvn-nm-043-254-169-224",
    "tvn-nm-043-254-169-225",
    "tvn-nm-043-254-169-226",
    "tvn-nm-043-254-169-227",
    "tvn-nm-043-254-169-228"
]

URL = {
    "login": "http://owl.fastweb.com.cn/api/v1/auth/login",
    "hostgroup": 'http://owl.fastweb.com.cn/api/v1/hostgroup/hosts',
    "aggregate": 'http://query.owl.fastweb.com.cn/graph/history',
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
    endpointCounters = [{"endpoint": x, "counter": y}
                        for x in endpoints for y in counters]
    payload = {
        "start": startTs,
        "end": endTs,
        "cf": "AVERAGE",
        "endpoint_counters": endpointCounters
    }
    r = requests.post(url, data=json.dumps(payload))
    out = json.loads(r.text)
    return out


def formatting(raw, endpoints, startTs, endTs):
    product = [(ec["endpoint"], ec["counter"], point["timestamp"],
                point["value"]) for ec in raw for point in ec["Values"]]
    result = []
    for c in counters:
        data = filter(lambda x: x[1] == c, product)     # select counter
        data = filter(lambda x: x[3] is not None, data)  # remove None
        # use timestamp as groupby argument
        data = sorted(data, key=lambda x: x[2])
        # list(grp) ->  [ ... (u'tvn-nm-043-254-169-228', u'net.if.out.bits/iface=eth_all', 1500501660, 8965.6)]
        # key       ->  1500501660
        peaks = []
        c_result = []
        for key, grp in itertools.groupby(data, key=lambda x: x[2]):
            v_data = map(lambda x: x[3], grp)
            peak = sum(v_data)
            peaks.append(peak)
            r = {
                "timestamp": key,
                "sum": peak
            }
            c_result.append(r)

        c_r = {
            "counter": c,
            "values": c_result,
            "max_value": max(peaks)
        }
        result.append(c_r)

    final = {
        "timespan": (startTs, endTs),
        "result": result
    }
    return json.dumps(final)


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
        print "usage:    ./isp_network_sum.py [time Start in ISO8601] [time End in ISO8601]"
        print "example:  ./isp_network_sum.py 2017-02-28T06:01:00+0800 2017-03-28T06:01:00+0800"
        sys.exit(1)
    # ts = int(time.time()) # input
    # platform = "c06.i06"  # input
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
    # endpoints use the global
    # endpoints = hostgroup2hostnames(user, sig, platform)
    if len(endpoints) == 0:
        print json.dumps(False)
        sys.exit(0)
    raw = aggregate(user, sig, startTs, endTs, endpoints)
    print formatting(raw, endpoints, sys.argv[1], sys.argv[2])
