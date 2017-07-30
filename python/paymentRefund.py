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

class RefundReq(object):
    def __init__(self, msgSeq, platId, orderId, refundOrderId,
            reason, amount, type, manualFlag):
        self.msgSeq = msgSeq
        self.platId = platId
        self.orderId = orderId
        self.refundOrderId = refundOrderId
        self.reason = reason
        self.amount = amount
        self.type = type
        self.manualFlag = manualFlag
    
    def send(self):
        logging.info("send refund req...")
        try:
            paymentPrx = Service.PaymentPrx.uncheckedCast(g_ice.stringToProxy("payment"))
            req = Service.RefundReq(platId=self.platId, msgSeq = self.msgSeq,
                    orderId = self.orderId, refundOrderId=self.refundOrderId,
                    reason=self.reason,amount=self.amount,type=self.type,
                    manualFlag=self.manualFlag)
            resp = paymentPrx.refund(req)
             
        except Exception, e:
            logging.error(("exception during notifyRefund orderId :[%s]") %(self.orderId))
            logging.error(e)
            return None
        return resp



def paymentRefundFunc():
        msgSeq = getMsgSeq(1)
        platId = 10000
            
        orderId = "testOrderId"
        refundOrderId = "refundOrderId"
        reason = "test"
        amount = 100
        type = Service.RefundType.CPREFUND 
        manualFlag = 1
        reqIns = RefundReq(msgSeq, platId, orderId, refundOrderId,
                        reason, amount, type, manualFlag)
        resp = reqIns.send()
        print resp
        if resp and resp.retCode == 0:
            logging.info("refundorderid : [%s] notify success!" %(refundOrderId))
        else:
            logging.info("refundorderid : [%s] notify failed!" %(refundOrderId))
            print ("refundOrderId : [%s] notify failed!" % (refundOrderId))
        time.sleep(0.700)


if "__main__" == __name__:
    paymentRefundFunc() 

