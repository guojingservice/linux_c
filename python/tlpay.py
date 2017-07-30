#!/bin/env python
#-*- coding: utf-8 -*-

import sys,os
binpath = os.path.abspath(sys.argv[0])
bindir = os.path.dirname(binpath)
os.chdir(bindir)

import string,httplib,urllib,time,datetime
import json
import collections
import base64
import Crypto
import hashlib
from Crypto.Hash import SHA
sys.path.append("../common")
from common import *
from crypto import *
from urllib import quote
import logging
import logging.config
#########################参数设置区###############################
COMMON_CONFIG ={
    "merchantno":"309584072786760",
    "appid":"00011149",
    "key":"aG8DksUC3BJ6wGTdWNY2n44AwNlKvBaG",
    "url":"https://vsp.allinpay.com/apiweb/unitorder",
    "notifyurl":"http://58.250.160.238:25001"
}



class TLPayApi:
    def __init__(self):
        self.key = COMMON_CONFIG["key"]
        self.appid = COMMON_CONFIG["appid"]
        self.merchantno = COMMON_CONFIG["merchantno"]
        self.url = COMMON_CONFIG["url"]
        self.notifyurl = COMMON_CONFIG["notifyurl"]
        self.httpHeader = {"Content-Type" : "application/octet-stream",
            "User-Agent": "Dalvik/1.6.0 (Linux; U; Android 4.2.2; NX40X Build/JDQ39)",
            "Accept-Encoding": "gzip"}
        self.crypto = CryptoHelper()
        self.http = HttpApi(logger)
         
    def srcSign(self, src):
        signSrc = ""
        src["key"] = self.key
        items = src.items()
        items.sort()
        for key,value in items:
            signSrc += ("&%s=%s" % (key, value)) 
        signSrc = signSrc[1:]
        mdigest = hashlib.md5()
        mdigest.update(signSrc)
        sign = mdigest.hexdigest().upper()
        print ("md5 src:[%s],sign:[%s]" % (signSrc, sign)) 
        return sign 

    def processRequest(self, body, fixUrl=""):
        postbody = ""
        items = body.items()
        items.sort()
        for key,value in items:
            value = urllib.quote_plus(value)
            postbody += ("&%s=%s" %(key, value))
        postbody = postbody[1:] 
        print ("post:[%s]" % postbody)
        realUrl = ""
        print "fixurl:[%s]" % fixUrl
        if fixUrl:
            realUrl = fixUrl
        else:
            realUrl = self.url
        print "fixUrl:[%s], realUrl:[%s]"%(fixUrl, realUrl)
        info, response = self.http.httpPostCall(realUrl, body, True)
        if not response:
            return None
        return response

class TLPayIns(TLPayApi):
    def __init__(self):
        TLPayApi.__init__(self)
        self.name = "TLIns"
    
    def getMsgSeq(self):
        now = datetime.datetime.now()
        return "%04d%02d%02d%02d%02d%02d" %(now.year, now.month, now.day, now.hour, now.minute, now.second)    

    def getOrderTime(self):
        now = datetime.datetime.now()
        return ("%04d%02d%02d%02d%02d%02d" %
                (now.year, now.month, now.day, now.hour, now.minute, now.second))
    
    def getNowStr(self):
        now = datetime.datetime.now()
        nowStr = str(now)
        return nowStr[:nowStr.find(".")]
    
    def saveInitData(self, body):
        with open("./init.data", "w") as _file:
            cpOrderId = body["OrderNum"]
            orderTime = body["OrderTime"]
            smsOrderId = body["SmsOrderId"]
            amount = body["Amount"]
            _file.write(cpOrderId)
            _file.write("\n")
            _file.write(orderTime)
            _file.write("\n")
            _file.write(smsOrderId)    
            _file.write("\n")
            _file.write(amount)
            _file.write("\n")
    
    def loadInitData(self, outList=[]):
        with open("./init.data", "r") as _file:
            for line in _file:
                line = line.strip()
                outList.append(line) 

    def pay(self):
        #body = collections.OrderedDict()
        body = {}
        seq = self.getMsgSeq()
        payUrl = self.url + "/pay"
        orderId = ("fast_%s" % seq)
        body["cusid"] = self.merchantno
        body["appid"] = self.appid
        body["version"] = "11"
        body["trxamt"] = "1"
        body["reqsn"] = "pay" + self.getMsgSeq()
        body["paytype"] = "W01" # 微信:W01 支付宝:A01
        body["randomstr"] = self.getMsgSeq() + "pay"
        body["body"] = "apple"
        body["remark"] = "PyTest"
        body["notify_url"] = self.notifyurl
        sign = self.srcSign(body)
        body["sign"] = sign
        resp = self.processRequest(body, payUrl)  
        print "res:[%s]" %resp

    
    def query(self):
        body={}
        queryUrl = self.url + "/query"
        body["cusid"] = self.merchantno
        body["appid"] = self.appid
        body["version"] = "11"
        body["reqsn"] = "33011707131419510008100291"
        body["randomstr"] = self.getMsgSeq()
        sign = self.srcSign(body)  
        body["sign"] = sign
        resp = self.processRequest(body, queryUrl)
        print ("res:[%s]"%resp)

    def refund(self):
        body={}
        refundUrl = self.url + "/refund"
        body["cusid"] = self.merchantno
        body["appid"] = self.appid
        body["version"] = "11"
        body["trxamt"] = "1"
        body["reqsn"] = self.getMsgSeq() + "ref"
        body["oldreqsn"] = "33011707121716070010100001"
        body["randomstr"] = self.getMsgSeq()
        sign = self.srcSign(body)
        body["sign"] = sign
        resp = self.processRequest(body, refundUrl)
        print ("res:[%s]"%resp)
    
    def refundquery(self):
        body={}
        queryUrl = self.url + "/query"
        body["cusid"] = self.merchantno
        body["appid"] = self.appid
        body["version"] = "11"
        body["reqsn"] = "20170711175731ref"
        body["randomstr"] = self.getMsgSeq()
        sign = self.srcSign(body)  
        body["sign"] = sign
        resp = self.processRequest(body, queryUrl)
        print ("res:[%s]"%resp)
 
if __name__=='__main__':
    logging.config.fileConfig("logging.conf")
    logger = logging.getLogger("root")
    ins = TLPayIns()
    
    if(len(sys.argv) != 2):
        print "missing command."
        print "example: python tlpay.py order"
        exit(0)
    if sys.argv[1] == "pay":
        ins.pay()
    elif sys.argv[1] == "query":
        ins.query()
    elif sys.argv[1] == "refund":
        ins.refund()
    elif sys.argv[1] == "refundquery":
        ins.refundquery() 

