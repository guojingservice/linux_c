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

commInfo = {
    "mch_id" : "1312311301",
    "nonce_str" : "123456",
    "out_refund_no" : "",
}

# 49739b7050362e4799d5910103c99f85


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
        
def genXml(commInfo):
    nodes = ""
    for(k, v) in commInfo.items():
        nodes += "<%s>%s</%s>" % (k, v, k)
    nodes = "<xml>%s</xml>" % (nodes)
    return nodes 

class QQWalletQueryRefund(object):
    def __init__(self, refundid):
        self.url = "https://qpay.qq.com/cgi-bin/pay/qpay_refund_query.cgi"
        self.refundid = refundid
        commInfo["out_refund_no"] = self.refundid
            
    def send(self): 
        od = collections.OrderedDict()
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
    refundid = "%s%04d%02d%02d%02d%02d%02d" %("qqwaletrefund",now.year, now.month, now.day, now.hour,
now.minute, now.second)

    now = datetime.datetime.now()
    refundid = sys.argv[1]
    reqIns = QQWalletQueryRefund(refundid)
    reqIns.send()
