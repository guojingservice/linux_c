#!/bin/env python
#-*- coding: utf-8 -*-

import re
import os
import sys
import signal
import time
import logging
import MySQLdb
import subprocess 
from collections import defaultdict
from threading import Event
from threading import Thread
#from enum import Enum

sys.path.append(os.path.join(os.environ["ICE_HOME"], "python"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "python"))

import Ice
import Service
import const 
from crypto import CryptoHelper
from tail import Tail
from timeout import timeout 
from http import HTTPHandler
import datetime

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

class RefundNotifyReq(object):
    def __init__(self, msgSeq, platId, refundOrderId, result, amount):
        self.msgSeq = msgSeq
        self.platId = platId
        self.refundOrderId = refundOrderId
        self.result = result
        self.amount = amount
    
    def send(self):
        logging.info("send merchant refund notify")
        try:
            merchantPrx = Service.MerchantPrx.uncheckedCast(g_ice.stringToProxy("merchant"))
            req = Service.RefundNotifyReq(platId=self.platId, msgSeq=self.msgSeq, refundOrderId=self.refundOrderId,
                  result=self.result, amount=self.amount)
            resp = merchantPrx.refundNotify(req)
        except Exception, e:
            logging.error(("exception during refundNotify refundOrderId:[%s]" % (self.refundOrderId)))
            logging.error(e)
            return None
        return resp

class QueryPayOrderReq(object):
    def __init__(self, msgSeq, platId, orderId):
        self.msgSeq = msgSeq
        self.platId = platId
        self.orderId = orderId

    def send(self):
        logging.info("send pay order req")
        try:
            paymentPrx = Service.PaymentPrx.uncheckedCast(g_ice.stringToProxy("payment"))
            req = Service.QueryPayOrderReq(platId=self.platId, msgSeq=self.msgSeq, orderId=self.orderId)
            resp = paymentPrx.queryPayOrder(req)
        except Exception, e:
            logging.error(("exception during query pay order ,orderId:[%s]" % (self.orderId)))
            logging.error(e)
        return resp

def loadCompleteData(fileName):
    completeData = {}
    with open(fileName) as file_:
        line = file_.readline()
        while(line):
            line = line.strip()
            completeData[line] = 1
            line = file_.readline()
    return completeData
    

def loadSrcData(fileName):
    refundData = {}
    count = 0
    with open(fileName) as file_:
        line = file_.readline()
        while(line):
            line = line.strip()
            srcData = line.split()
            
            #print ("id:[%s],amount:[%s]"%(srcData[0], srcData[1]))
            refundData[srcData[0]] = int(srcData[1])            
            line = file_.readline() 
    return refundData

def test_refundNotify():
    index =1
    now = datetime.datetime.now()
    platId = 10025
    msgSeq = getMsgSeq(index)
    
    refundOrderId = "123456"
    result = Service.RefundResult.REFUNDSUCCESS
    amount = 100    
    reqIns = RefundNotifyReq(msgSeq, platId, refundOrderId, result, amount)
    resp = reqIns.send()     
    print resp

def batchRefundNotify(refundData, completeData):
    if len(refundData) == 0:
        return
    count = 0
    for key, value in refundData.items():
        index = 1
        now = datetime.datetime.now()
        platId = 10025
        msgSeq = getMsgSeq(index)
        
        # check if this order already processed
        if completeData.has_key(key):
            logging.info(("refundorder already processed refundorderid:[%s]"%key))
            continue
    
        refundOrderId = key
        result = Service.RefundResult.REFUNDSUCCESS
        amount = value
        reqIns = RefundNotifyReq(msgSeq, platId, refundOrderId, result, amount)
        resp = reqIns.send()
        
        if getattr(resp, 'retCode', "finded") and resp.retCode == 0:
            # sucess ,record to success txt
            cmd = "echo %s >> ./completeData.txt"
            cmd = (cmd % key)
            os.system(cmd)
        else:
            #record refundorderid
            cmd = "echo %s >> ./failedRefund.txt"
            cmd = (cmd % key)
            os.system(cmd)
        
        count = count+1
        if count % 3 == 0:
            time.sleep(4)


def main():
    #test_refundNotify()
    refundData = loadSrcData("./outputData.txt")
    completeData = loadCompleteData("./completeData.txt")
    
    batchRefundNotify(refundData, completeData)
     


if "__main__" == __name__:
    main()
