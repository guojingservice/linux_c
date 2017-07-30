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

if __name__=='__main__':
    svcApi = QuerySvc()
    oper=sys.argv[1]
    if oper == "file":
        orderFile = open(sys.argv[2])
        for line in orderFile:
            resp = svcApi.query(line.strip(), 1)
            time.sleep(0.005)
        orderFile.close()
    else:
        print svcApi.query(sys.argv[2], 1)
