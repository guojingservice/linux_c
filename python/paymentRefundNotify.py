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


class WebRefundNotify(object):
    def __init__(self, msgSeq, platId, transid, refundamount, channelrefundid, reason, optime, orderid):
        self.msgSeq = msgSeq
        self.platId = platId
        self.transid = transid
        self.refundamount = refundamount
        self.channelrefundid = channelrefundid
        self.reason = reason
        self.optime = optime
        self.orderid = orderid
    
    def send(self):
        logging.info("send web refund notify...")
        try:
            merchantPrx = Service.MerchantPrx.uncheckedCast(g_ice.stringToProxy("merchant"))
            req = Service.WebRefundNotifyReq(platId=self.platId, msgSeq=self.msgSeq, transid=self.transid, 
                    refundamount=self.refundamount, channelrefundid=self.channelrefundid, reason=self.reason,
                    optime=self.optime, orderid=self.orderid)
            resp = merchantPrx.webRefundNotify(req)
        except Exception, e:
            logging.error(("exception during webRefundNotify OrderId : [%s]") % (self.orderid))
            logging.error(e)
            return None
        return resp

class NotifyRefundResultReq(object):
    def __init__(self, msgSeq, platId, refundRs, refundOrderId, amount):
        self.msgSeq = msgSeq
        self.platId = platId
        self.refundRs = refundRs
        self.refundOrderId  = refundOrderId
        self.amount = amount
        
    # _M_Service.RefundResult.REFUNDSUCCESS    

    def send(self):
        logging.info("send notify refund result...")
        try:
            paymentInternalPrx = Service.PaymentInternalPrx.uncheckedCast(g_ice.stringToProxy("paymentinternal"))
            req = Service.NotifyRefundResultReq(platId=self.platId, msgSeq=self.msgSeq, refundRs=self.refundRs, 
                    refundOrderId=self.refundOrderId, amount=self.amount)
            resp = paymentInternalPrx.notifyRefundResult(req)
        except Exception, e:
            logging.error(("exception during notifyRefundResult refundOrderId: [%s]") %(self.refundOrderId))
            logging.error(e)
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
    

def loadSrcData(fileName):
    refundData = collections.OrderedDict()
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

def loadIdListFromFile(fileName):
    idList = []
    with open(fileName) as file_:
        line = file_.readline()
        while(line):
            line = line.strip()
            idList.append(line)
            line = file_.readline()
    return idList

def loadValueListFromFile(fileName):
    valueList = []
    with open(fileName) as file_:
        line = file_.readline()
        while(line):
            line = line.strip()
            sData = line.split()
            valueList.append(sData) 
            line = file_.readline()
    return valueList


def raisePaymentRefundNotify(inputFile):
    with open(inputFile) as file_:
        line = file_.readline()
        count = 0
        while(line):
            line = line.strip()
            sData = line.split()
            
            msgSeq = getMsgSeq(1)
            platId = 10000
            
            refundOrderId = sData[0]
            refundAmount = int(sData[1])
            now = datetime.datetime.now() 
            channelRefundId = ("%s%04d%02d%02d%02d%02d%02d%03d" %("py_notify", now.year, now.month, now.day, now.hour,now.minute, now.second, count))
        
            optime = str(now)
            optime = optime[0:19] 

            #self, msgSeq, platId, refundRs, refundOrderId, amount): _M_Service.RefundResult.REFUNDSUCCESS
            reqIns = NotifyRefundResultReq(msgSeq, platId, Service.RefundResult.REFUNDSUCCESS,
                        refundOrderId, refundAmount)
            resp = reqIns.send()
            print resp
            if resp and resp.retCode == 0:
                logging.info("refundorderid : [%s] notify success!" %(refundOrderId))
            else:
                logging.info("refundorderid : [%s] notify failed!" %(refundOrderId))
                print ("refundOrderId : [%s] notify failed!" % (refundOrderId))
            time.sleep(0.700)
            count = count + 1
            line = file_.readline()

if "__main__" == __name__:
    raisePaymentRefundNotify("./toPaymentRefund.txt") 
    

