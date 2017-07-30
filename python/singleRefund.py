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


class SingleRefundSvc(SvcApiBase):
    def __init__(self):
        SvcApiBase.__init__(self)
        self.name = "SingleRefundSvc"
        self.merchant_prx = Service.MerchantPrx.uncheckedCast(self.ic.stringToProxy("merchant"))
    
    def singleRefund(self,appid, refundno, cporderid, refundtime, notifyurl,
                        refundamount, remark):
        req = Service.SingleRefundReq(self.CommonInfo["PlatId"], self.CommonInfo["BusPlatId"], 0, self.getMsgSeq(), appId=appid, refundNo=refundno,cporderid=cporderid, refundTime=refundtime, notifyUrl=notifyurl, 
            refundamount=refundamount, remark=remark, rtype=Service.RefundType.APIREFUND)
        resp = self.merchant_prx.singleRefund(req)
        print resp
        if resp.retCode == 0:
            print ("Process Success")
        else:
            print ("Process Failed")
        return resp

if __name__=='__main__':
    svcApi = SingleRefundSvc()
        
    refundAmount = 1
    appId = ""
    cpOrderId = ""
        
    now = datetime.datetime.now() 
    refundNo = "%s%04d%02d%02d%02d%02d%02d%03d" % ("112211",now.year, now.month, now.day, now.hour, now.minute, now.second, 1)
    refundTime = str(now)
    refundNo = ("%s%s" %(refundNo, tailStr))
    refundTime = refundTime[0:19]
    remark = "testSingleRefund"
    notifyUrl = ""
     
    resp = svcApi.singleRefund(appId, refundNo, cpOrderId, refundTime, notifyUrl,
                refundAmount, remark)
        
    if(resp.retCode != 0):
        print("singleRefund failed. cporderid:%s, appid:%s, amount:%d" % (cpOrderId, appId, amount));  
