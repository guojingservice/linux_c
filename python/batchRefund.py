#!/bin/env python
#-*- coding: utf-8 -*-

import sys, os
binpath = os.path.abspath(sys.argv[0])
bindir = os.path.dirname(binpath)
os.chdir(bindir)

sys.path.append(os.path.join(os.environ["ICE_HOME"], "python"))
sys.path.append(os.path.join(bindir, "python"))
#sys.path.append(os.path.join(bindir, "common"))

import datetime,time

import Ice
import Service
import traceback
import unittest
import logging
import logging.config

class SvcApiBase():
    def __init__(self):
        self.ic = Ice.initialize(["--Ice.Config=" + os.environ["BILLING_HOME"] + "/conf/config.client"])
        #self.ic = Ice.initialize(["--Ice.Config=" + "./conf/config.client"])
        self.index = 0
        self.name = ""
        self.CommonInfo = {"PlatId":10000, "BusPlatId":101}
        self.props = self.ic.getProperties()

    def getMsgSeq(self):
        now = datetime.datetime.now()
        self.index = (self.index + 1) % 1000
        return "%s%04d%02d%02d%02d%02d%02d%03d" %(self.name, now.year, now.month, now.day, now.hour, now.minute, now.second, self.index)


class QuerySvc(SvcApiBase):
    def __init__(self):
        SvcApiBase.__init__(self)
        self.name = "QuerySvc"
        self.payment_prx = Service.PaymentPrx.uncheckedCast(self.ic.stringToProxy("payment"))

    def query(self, orderId, retryTimes=3, retryInterval=0.2):
        for i in range(0, retryTimes):
            req = Service.QueryPayOrderReq(self.CommonInfo["PlatId"], self.CommonInfo["BusPlatId"], 0, self.getMsgSeq(), orderId = orderId)
            resp = self.payment_prx.queryPayOrder(req)
            if resp.retCode == 0 and resp.status == 0:
                time.sleep(retryInterval)
            else:
                break;
        return resp

class BatchRefundSvc(SvcApiBase):
    def __init__(self):
        SvcApiBase.__init__(self)
        self.name = "BatchRefundSvc"
        self.merchant_prx = Service.MerchantPrx.uncheckedCast(self.ic.stringToProxy("merchant"))
    
    def batchRefund(self,appid, refundno, refundtime, refunddata, notifyurl):
        req = Service.BatchRefundReq(self.CommonInfo["PlatId"], self.CommonInfo["BusPlatId"], 0, self.getMsgSeq(), appId=appid, refundNo=refundno,refundTime=refundtime, refundData=refunddata, notifyUrl=notifyurl, manualFlag=1, rtype=Service.RefundType.MANUALREFUND)
        resp = self.merchant_prx.batchRefund(req)
        print resp
        if resp.retCode == 0:
            print ("Process Success, refundData:%s" %(refundData))
        else:
            print ("Process Failed, refundData:%s" %(refundData))
            
        return resp

if __name__=='__main__':
    svcApi = BatchRefundSvc()
    
     
    orderFile = open("./batch.txt")
    for line in orderFile:
        #resp = svcApi.query(line.strip(), 1)
        #logger.info("Query order:%s, status:%d" %(line, resp.status))
        #time.sleep(0.005)
        line = line.strip()
        srcData = line.split()
        print srcData
        amountStr = srcData[0]
        appId = srcData[1]
        cpOrderId = srcData[2]
        
        now = datetime.datetime.now() 
        refundNo = "%s%04d%02d%02d%02d%02d%02d%03d" % ("112211",now.year, now.month, now.day, now.hour, now.minute, now.second, 1)
        refundTime = str(now)
        tailStr = refundTime[19:]
        refundNo = ("%s%s" %(refundNo, tailStr))
        refundTime = refundTime[0:19]
        refundData = ("%s^%s^%s" % (cpOrderId, "batchRefund", amountStr))
        
        resp = svcApi.batchRefund(appId, refundNo, refundTime, refundData, "")
        
        if(resp.retCode != 0):
            print("batchRefund failed. cporderid:%s, appid:%s, amount:%d, refunddata:%s" % (cpOrderId, appId, amount, refundData));  
        time.sleep(0.855)  
    orderFile.close()
