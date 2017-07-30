#!/bin/env python
#-*- coding: utf-8 -*-

import re
import os
import sys
import signal
import time
import logging
import subprocess 
from collections import defaultdict
from threading import Event
from threading import Thread
#from enum import Enum
import collections
import hashlib
import urllib
import urllib2

sys.path.append(os.path.join(os.environ["ICE_HOME"], "python"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "python"))

import Ice
import Service
import datetime, time
import collections

g_isQuit = False
g_quitEvent = Event()
g_ice = Ice.initialize(["--Ice.Config=" + os.environ["BILLING_HOME"] + "/conf/config.client"])

#CommonInfo = {"Merchant":"1312311301", "Key":"d1f7cbf1ae5ddd225a76be3d27e3a0da"}
#CommonInfo = {"Merchant":"1421911201", "Key":"nCD1yagtH0yCBp11ntOTEMOkLTvZy6u7"}
CommonInfo = {"Merchant":"1419346201", "Key":"zN0PY0nyWmTHEau4w6x16SK9sahrNRie"}

"""
commInfo = {
    "mch_id" : "1312311301",
    "nonce_str" : "123456",
    "body" : "GJTEST-t1",
    "out_trade_no" : "",
    "fee_type" : "CNY",
    "total_fee" : 0,
    "spbill_create_ip" : "119.139.199.58",
    "trade_type" : "JSAPI",
    "notify_url" : "http://www.baidu.com/"
}
"""

commInfo = {
    "mch_id" : "1419346201",
    "nonce_str" : "123456",
    "body" : "GJTEST-t1",
    "out_trade_no" : "",
    "fee_type" : "CNY",
    "total_fee" : 0,
    "spbill_create_ip" : "119.139.199.58",
    "trade_type" : "NATIVE",
    "notify_url" : "http://www.baidu.com/"
}

def getMsgSeq(index):
    now = datetime.datetime.now()
    index = (index +1) % 1000
    return "%s%04d%02d%02d%02d%02d%02d%03d" %("fx", now.year, now.month, now.day, now.hour,
now.minute, now.second, index)

def calcSign(commonInfo):
    body = ""
    for(k, v) in commonInfo.items():
        body += k + "=" + urllib.quote_plus(str(v)) + "&"
    signbody = body + "key=" + CommonInfo["Key"]
    print "sign src : %s" %(signbody)
    md5helper = hashlib.md5()
    md5helper.update(signbody)
    result = md5helper.hexdigest()
    return result.upper()
        
def genXml(commInfo):
    nodes = ""
    for(k, v) in commInfo.items():
        nodes += "<%s>%s</%s>" % (k, urllib.quote_plus(str(v)), k)
    nodes = "<xml>%s</xml>" % (nodes)
    return nodes 

class QQWalletInit(object):
    def __init__(self, orderid, amount):
        self.url = "https://qpay.qq.com/cgi-bin/pay/qpay_unified_order.cgi"
        self.orderid = orderid
        self.amount = amount
        commInfo["total_fee"] = self.amount
        commInfo["out_trade_no"] = self.orderid
            
    def send(self): 
        od = collections.OrderedDict()
        
        commInfo["spbill_create_ip"] = "219.143.16.178"
        
        items = commInfo.items()
        items.sort()
        for (k, v) in items:
            od[k] = v
        sign = calcSign(od)
        commInfo["sign"] = sign
        
        sendData = genXml(commInfo) 
        print "sendData: %s " % (sendData)
        
        f = urllib.urlopen(self.url, sendData)
        print f.read() 
    

if "__main__" == __name__:
    msgSeq = getMsgSeq(1)
    platId = 10025
    amount = 1
    now = datetime.datetime.now()
    orderid = "%s%04d%02d%02d%02d%02d%02d" %("qqwalet",now.year, now.month, now.day, now.hour,
now.minute, now.second)
    reqIns = QQWalletInit(orderid, amount)
    reqIns.send()
