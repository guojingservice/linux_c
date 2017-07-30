#!/bin/env python
#-*- coding: utf-8 -*-

import hashlib
import urllib
import urllib2
import datetime

class HuiRequest():
    def __init__(self):
        self.initUrl = "http://www.97epay.com/qqpay/servicev1.0/init.jsp"
        self.queryUrl = "http://www.97epay.com/qqpay/servicev1.0/query.jsp"
        self.payUrl = "http://www.97epay.com/qqpay/servicev1.0/codepay.jsp"
        self.notifyUrl = "http://58.250.160.238:25001"
        self.username = "szlabao"
        self.key = "aaea6503-1e65-40b9-9930-b1d3b525b24c"
        self.fee = "1"
        self.desc = "test中文"
        self.index = 1
    
    def packData(self, reqMap):
        src = ""
        for (k, v) in reqMap.items():
            src += ("%s=%s&"%(k, urllib.quote_plus(v)))
        src = src[:-1]
        return src
        
    
    def getOrderId(self):
        now = datetime.datetime.now()
        return ("%s%04d%02d%02d%02d%02d%02d%03d" %("hui", now.year, now.month, now.day, now.hour, now.minute, now.second, self.index)) 
    
    def sign(self, data):
        src = ("%s|%s" % (data, self.key) )
        print ("sign src:[%s]" % src)
        m = hashlib.md5()
        m.update(src)
        return m.hexdigest() 

    def httpPost(self, url, data):
        httpReq = urllib2.Request(url=url, data=data)
        resData = urllib2.urlopen(httpReq)
        res = resData.read()
        print("res:[%s]" % (res.decode("gbk")))
        

    def orderInit(self):
        reqMap = {}
        reqMap["username"] = self.username
        reqMap["codesn"] = self.getOrderId()
        #reqMap["codesn"] = "hui20170410112759001"
        reqMap["fee"] = self.fee
        reqMap["desc"] = self.desc
        reqMap["notifyurl"] = self.notifyUrl
        data = ("%s|%s|%s|%s|%s" % (reqMap["username"], reqMap["codesn"],
                        reqMap["fee"], reqMap["desc"].decode("utf-8").encode("gbk"), reqMap["notifyurl"])) 
        sign = self.sign(data)
        reqMap["sign"] = sign
        reqMap["desc"] = reqMap["desc"].decode("utf-8").encode("gbk")
        reqData = self.packData(reqMap)
        print ("reqData:[%s]" % reqData)
 
        httpReq = urllib2.Request(url=self.initUrl, data=reqData)
        resData = urllib2.urlopen(httpReq)
        res = resData.read()
        print ("res:[%s]" % (res.decode("gbk")))
    
    def orderQuery(self):
        reqMap = {}
        reqMap["username"] = self.username
        reqMap["codesn"] = "hui20170406114605001"
        data = ("%s|%s" % (reqMap["username"], reqMap["codesn"]))
        sign = self.sign(data)
        reqMap["sign"] = sign
        reqData = self.packData(reqMap)
        print "reqData:[%s]" % reqData
        self.httpPost(self.queryUrl, reqData) 
        

if __name__ == "__main__":
    req = HuiRequest()
    req.orderInit()
    #req.orderQuery()
