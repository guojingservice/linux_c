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

CommonInfo = {"Merchant":"1312311301", "Key":"d1f7cbf1ae5ddd225a76be3d27e3a0da"}

WalletQueryCommonInfo = {
    "ver":"1.0",
    "partner":"1312311301",
    "out_trade_no":"",
    "charset":"UTF-8",
}




def getMsgSeq(index):
    now = datetime.datetime.now()
    index = (index +1) % 1000
    return "%s%04d%02d%02d%02d%02d%02d%03d" %("fx", now.year, now.month, now.day, now.hour,
now.minute, now.second, index)

def calcSign(commonInfo):
    body = ""
    for(k, v) in commonInfo.items():
        body += k + "=" + str(v) + "&"
    signbody = body + "key=" + CommonInfo["Key"]
    print "sign src : %s" %(signbody)
    md5helper = hashlib.md5()
    md5helper.update(signbody)
    result = md5helper.hexdigest()
    return result.upper()
        
class QQWalletQuery(object):
    def __init__(self, orderid):
        self.orderid = orderid
        #self.url = "https://qpay.qq.com/cgi-bin/pay/qpay_order_query.cgi"
        self.url = "https://myun.tenpay.com/cgi-bin/clientv1.0/qpay_order_query.cgi"

    def send(self):
        WalletQueryCommonInfo["out_trade_no"] = self.orderid
        
        od = collections.OrderedDict();
        items = WalletQueryCommonInfo.items()
        items.sort()
        for(k, v) in items:
            od[k] = v
        sign = calcSign(od)
        sendData = ""
        for(k,v) in od.items():
            sendData += "%s=%s&" %(k, str(v))
        sendData += "sign=%s" %(sign)

        requrl = self.url
        requrl += ("?%s" % (sendData))    
        print requrl
        req = urllib2.Request(requrl)
        response = urllib2.urlopen(req)
        theresult = response.read()
        print theresult
        
        

if "__main__" == __name__:
    orderid = sys.argv[1]
    reqIns = QQWalletQuery(orderid)
    reqIns.send()

