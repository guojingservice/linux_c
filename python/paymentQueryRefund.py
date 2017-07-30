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

sys.path.append(os.path.join(os.environ["ICE_HOME"], "python"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "python"))

import Ice
import Service
import datetime, time
import collections

g_isQuit = False
g_quitEvent = Event()
g_ice = Ice.initialize(["--Ice.Config=" + os.environ["BILLING_HOME"] + "/conf/config.client"])

CommonInfo = {"PlatId":10000, "BusPlatId":102}
SvcCommonInfo = {"device":100, "os":1, "version": "IAPPPAY_3.4.0_Android", "acid":"999",
"country":"CHN", "lang":"CHS", "currency":"RMB"}





def getMsgSeq(index):
    now = datetime.datetime.now()
    index = (index +1) % 1000
    return "%s%04d%02d%02d%02d%02d%02d%03d" %("fx", now.year, now.month, now.day, now.hour,
now.minute, now.second, index)



class QueryRefundReq(object):
    def __init__(self, msgSeq, platId, refundOrderId):
        self.msgSeq = msgSeq
        self.platId = platId
        self.refundOrderId = refundOrderId
    
    def send(self):
        logging.info(("send refund query... refundorderid : %s") % self.refundOrderId)
        try:
            paymentPrx = Service.PaymentPrx.uncheckedCast(g_ice.stringToProxy("payment"))
            req = Service.QueryRefundReq(platId=self.platId, msgSeq=self.msgSeq, refundOrderId=self.refundOrderId)
            resp = paymentPrx.queryRefund(req)
        except Exception, e:
            logging.error(("exception during query refund. refundOrderId:[%s]") %(self.refundOrderId))
            loggine.error(e)
            return None
        return resp

def loadCompleteData(fileName):
    completeData = collections.OrderedDict()
    with open(fileName) as file_:
        line = file_.readline()
        while(line):
            line = line.strip()
            completeData[line] = 1
            line = file_.readline()
    return completeData
    


if "__main__" == __name__:
    if len(sys.argv) != 2:
        print "args not set properly!"
        print "example: python paymentQueryRefund.py 123456"
        sys.exit(1)
    refundOrderId = sys.argv[1]
    
    msgSeq = getMsgSeq(1)
    platId = 10025

    reqIns = QueryRefundReq(msgSeq, platId, refundOrderId)
    resp = reqIns.send()
    print resp
    if resp and resp.retCode == 0:
        logging.info("refundOrderId:[%s] query success!"%(refundOrderId))
    else:
        logging.info("refundOrderId:[%s] query failed!" %(refundOrderId))

