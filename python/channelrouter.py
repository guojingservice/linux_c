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


class ChannelPaySvc(SvcApiBase):
    def __init__(self):
        SvcApiBase.__init__(self)
        self.name = "ChannelPaySvc"
        self.paychannel_prx = Service.PayChannelPrx.uncheckedCast(self.ic.stringToProxy("tonglian"))
    
    def pay(self,commandId,channelType,orderId,payTime,amount,orderDesc,currency,country,lang,payInfo,exPayInfo):
        req = Service.PayReq(self.CommonInfo["PlatId"], self.CommonInfo["BusPlatId"], commandId, self.getMsgSeq(),
                channelType=channelType,orderId=orderId,payTime=payTime,amount=amount,
                orderDesc=orderDesc, currency=currency, country=country, lang=lang,payInfo=payInfo,
                extPayInfo=exPayInfo)
        resp = self.paychannel_prx.pay(req)
        print resp
        if resp.retCode == 0:
            print ("Process Success")
        else:
            print ("Process Failed")
            
        return resp
    
    def queryResult(self, commandId, channelType, orderId):
        req = Service.QueryResultReq(self.CommonInfo["PlatId"], self.CommonInfo["BusPlatId"], commandId, self.getMsgSeq(),
              channelType=channelType, orderId=orderId, subMchId="309584072786760")
        resp = self.paychannel_prx.queryResult(req)
        print resp
        if resp.retCode == 0:
            print("Process Success")
        else:
            print("Process Failed")
        return resp
    
    def refund(self, commandId, channelType, orderId, refundId, refundOrderId, amount, desc, orderAmount):
        req = Service.ChannelRefundReq(self.CommonInfo["PlatId"], self.CommonInfo["BusPlatId"], commandId, self.getMsgSeq(),
                channelType=channelType, orderId=orderId, refundId=refundId,refundOrderId=refundOrderId,
                amount=amount,desc=desc, orderAmount=orderAmount)
        resp = self.paychannel_prx.refund(req)
        print resp
        if resp.retCode == 0:
            print("Process Success")
        else:
            print("Process Failed")
        return resp

    def queryRefund(self, commandId, channelType, orderId, refundOrderId):
        req = Service.QueryChannelRefundReq(self.CommonInfo["PlatId"], self.CommonInfo["BusPlatId"], commandId, self.getMsgSeq(),
            channelType=channelType, orderId=orderId, refundOrderId=refundOrderId)
        resp = self.paychannel_prx.queryRefund(req)
        print resp
        if resp.retCode == 0:
            print("Process Success")
        else:
            print("Process Failed")
        return resp
 

def routerRefund():
    svcApi = ChannelPaySvc()
    commandId = 813
    channelType = 001102
    refundId = "33031707060207200002100000"
    now = datetime.datetime.now()
    refundOrderId = ""
    amount = 0
    desc = "pyrefund"
    orderAmount = 0
    resp = svcApi.refund(commandId, channelType, refundId, refundId, refundOrderId, amount, desc, orderAmount)

def routerQueryRefund():
    svcApi = ChannelPaySvc()
    commandId = 685
    channelType = 159045
    orderId = "33421703300122458708100000"
    refundOrderId = "39221703301415490098"
    resp = svcApi.queryRefund(commandId, channelType, orderId, refundOrderId) 
    

def routerPay():
    svcApi = ChannelPaySvc() 
    now = datetime.datetime.now()

    dateTimeNow = str(now)
    dateTimeNow = dateTimeNow[:19]
       
    commandId=7
    channelType=120068
    orderId = "%s%04d%02d%02d%02d%02d%02d%03d" % ("88888",now.year, now.month, now.day, now.hour, now.minute, now.second, 1)
    payTime = dateTimeNow
    amount = 1
    orderDesc = "routercommit"
    currency="RMB"
    lang=""
    #payInfo='{"openid":"ovkdlwqEBXJAvJPdj3vu3-Cg41-U","appid":"wx849785f511617130"}'
    payInfo = ""
    country = ""
    exPayInfo='{"SubMchId":"309584072786760"}'
    resp = svcApi.pay(commandId,channelType,orderId,payTime,amount,orderDesc,currency,country,lang,payInfo,exPayInfo)

def routerQueryResult():
    svcApi = ChannelPaySvc()
    now = datetime.datetime.now()
    commandId = 931
    channelType = 174108
    orderId = "33011707121606230003100001"
    resp = svcApi.queryResult(commandId, channelType, orderId)


if __name__=='__main__':
    routerQueryResult()
    #routerRefund()
    #routerQueryRefund()
