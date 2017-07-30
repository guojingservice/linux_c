#!/bin/env python
#-*- coding: utf-8 -*-

import sys,os
binpath = os.path.abspath(sys.argv[0])
bindir = os.path.dirname(binpath)
os.chdir(bindir)

import string,httplib,urllib,time,datetime
import json
sys.path.append("../common")
from common import *
from crypto import *
from urllib import quote
import logging
import logging.config


#########################参数设置区###############################
URL = {
    "abs": "http://10.0.2.15:8080/abs",
    "cporder": "http://10.0.2.15:8080/paypai/order",
    "tokencheck": "http://10.0.2.15:8080/paypai/tokencheck",
}

DeviceInfo = {"platId":10000, "deviceType":100, "osType":1, 
            "terminalId":"742ea0af0fea4760b1c1cd67cccbd1b1", "acid":"999", 
            "version":"IAPPPAY_3.4.0_Android",
            "country":"CHN", "lang":"CHS", "currency":"RMB"}

AppInfo = {"privateKey":"MIICXAIBAAKBgQCs9FrLDMw/acHx5RD8vPjRUp7F/gnmaKIEcq8wHQZCC01QrpDnyXmqktOxkqVYLUpPT3BZNy6mOfc53XYGuin+hwOk6a9fU9zrNVN8zXlO/V/50+oWsPU+J8EQ6bVkHUgWZlg5GPcLwNvKAd7WElC8ZTf0tQhFzI5raajcOGrBwQIDAQABAoGAczRY/gPKUTsa6wvQIumlO5kzFWNAKO/ta9UQiJXswzVQDLwa3apAlrQyuoeaB4AzjVy201aEhkj6OtsfcR+0NDQzp/P24bivdKVcSswgiOb+oWgIOOLqm6be32V0zRLJ73l5UngL4hCjsC5L8i3hccE2XtzUCR/CuDqkNSs8SvkCQQDZl86VXQ2adJwDkd+AUFlxxxuWjyD9//5Z2AhCyVFzQdvyWEzee3b+S5ROfwpINAYGpO+uAPwl+tmyoXv2/hTLAkEAy3uBdqhxsu0mvNcWrZuuphJBt7vPIPakQEXRL4MfUlvhdcQbdpP21NmCN9YQfCGF8y/ClvTcw30D4oQQVBZ+IwJBAM265qv6Sz5aOph1d6hOUANvifoUYdFGFSrFQypCRix/fIHqUuOYQK22sAZ3vzT9WyU1FRij/cO7JdHrNNYW7XkCQE8yzv0EKtzdeQpfHTCNO7jfujxtGP1Xgi6R/g1kF7jSkjpoDdhlVtkZn5lj9B6cXap9mFtxCsv7yJtNk51m88kCQF8Lo1EfbvbPAWSN95MN4EO271lWLfMsomM1g9kK58oNPLTeaPibI1t3xA1h5u9I42SHPpf+RWmex+TTmKZ1XKQ=", "id":"500000185", "name":"演示商品", 
"userid": "superbboy", "notify":"http://192.168.0.227:28080/notify"}


WaresInfo = {"id": 1, "price":1, "private":"测试一下啊", "openprice":True}


transId = ""
fee=0
paytransid = ""

CMD2URL = {
    "114":"http://192.168.0.159:25443/payapi/singlerefund",
    "115":"http://192.168.0.159:25443/payapi/querysinglerefund",
    "110":"http://192.168.0.159:25443/openid/openidcheck"
}

class Cp:
    def __init__(self):
        self.aesKey = "1234567890abcdef"
        self.appPrivKey = CryptoHelper.importKey(AppInfo["privateKey"])
        self.httpHeader = {"Content-Type" : "application/octet-stream",
            "User-Agent": "Dalvik/1.6.0 (Linux; U; Android 4.2.2; NX40X Build/JDQ39)",
            "Accept-Encoding": "gzip"}
        self.crypto = CryptoHelper()
        self.http = HttpApi(logger)
        self.tokenId = None
        self.errorCode = 0
        self.appId = AppInfo["id"]
         
        

    def processRequest(self, cmdid, body):
        logger.info("start %d..."%cmdid)
        bodyText = json.dumps(body)
        bodySign = self.crypto.sign(bodyText, self.appPrivKey)
        logger.info("bodyText:[%s] bodySign:[%s]" % (bodyText, bodySign))
        sendBody = {"transdata":bodyText, "sign":bodySign, "signtype":"RSA"} 
        postBody = urllib.urlencode(sendBody)
        print ("post:[%s]" % postBody)
        info, response = self.http.httpPostCall(CMD2URL[str(cmdid)], postBody, False, self.httpHeader)
        if not response:
            return None
        return response

class CpApi(Cp):
    def __init__(self):
        Cp.__init__(self)
        self.name = "PyCp"
    
    def getMsgSeq(self):
        now = datetime.datetime.now()
        return "%s%04d%02d%02d%02d%02d%02d" %(self.name, now.year, now.month, now.day, now.hour, now.minute, now.second)    
    def getNowStr(self):
        now = datetime.datetime.now()
        nowStr = str(now)
        return nowStr[:nowStr.find(".")]
        

    def cpOrder(self):
        pass
    
    def cpSingleRefund(self):
        cmd = 114
        refundno = self.getMsgSeq() 
        cporderid = "1495619870531"
        refundtime = self.getNowStr()        
        body={"appid":self.appId,
              "refundno":refundno,
              "cporderid":cporderid,
              "refundtime":refundtime,
              "refundremark":"pytest",
              "refundamount":0.01,
              "notifyurl":"www.baidu.com",
              "backroyaltys":[{"payer":"2088912535882191","remark":"pytest","amount":0.01}]
              }
        res = self.processRequest(cmd, body)
        print("res:[%s]"% urllib.unquote_plus(res))
    
    def cpSingleRefundQuery(self):
        cmd = 115
        body={
            "appid":self.appId,
            "refundno":"PyCp20170606182340",
            "cporderid":"1495619870531"
        }
        res = self.processRequest(cmd, body)
        print("res:[%s]" % urllib.unquote_plus(res))

    def cpOpenidTokenCheck(self):
        cmd = 110    
        body={
            "logintoken":"6600713292fa731a3d596b05ba121aaa",
            "appid":"500000185"
        }
        res = self.processRequest(cmd, body)
        print("res:[%s]" % urllib.unquote_plus(res)) 
 
if __name__=='__main__':
    logging.config.fileConfig("logging.conf")
    logger = logging.getLogger("root")
    cpApiIns = CpApi()
    #cpApiIns.cpSingleRefund()
    #cpApiIns.cpSingleRefundQuery()
    cpApiIns.cpOpenidTokenCheck()

    

