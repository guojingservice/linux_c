#!/bin/env python
#-*- coding: utf-8 -*-

import sys,os
binpath = os.path.abspath(sys.argv[0])
bindir = os.path.dirname(binpath)
os.chdir(bindir)

import string,httplib,urllib,time,datetime
import json
import base64
import Crypto
from Crypto.Hash import SHA
sys.path.append("../common")
from common import *
from crypto import *
from urllib import quote
import logging
import logging.config
#########################参数设置区###############################
COMMON_CONFIG ={
    "merchantno":"888000000001582",
    "departmentno":"88800036",
    "url":"http://27.115.103.86:9814/quick/inform",
    "prikey":"MIICeAIBADANBgkqhkiG9w0BAQEFAASCAmIwggJeAgEAAoGBAMh3uo7OpIAU1BCJPAU0JfOBS8OfIfyLayYAtaezcaP/6PeVxxpMeHyQW29whYdsmFma71qOfqOPoWfwP7bZ5OWxtXRvpKJ/gTOLeJvfQPBBUs18YbZn3A81YqFxmFeBTU+YmuCPNaG7Q0HagoqIb1KK2QnhHQ+sSM0TvZUj6savAgMBAAECgYEAu+oHtcAc0Xc0xn9uBM66WIU1+RzdZfdmrEvz/EyoVPwZbKQ46/0M4G8NVuwaLzTrpusmPTPfoACOY3kAsK2V8tVBYH9ZhTrn5mS2gRXL8kj+MYtK4PaVWEPN5aIeY3dJJYbeSHvpZNy4slzV0WRbeZIXn1DVCfH0ZFMpa2eVxyECQQDsqXAoD0YIm9iPsYqXSjiL+fKNQPlJ3fZCm2bZZi7snoPMHFyDvioWMsL3EN/AgreMNiGGJvaNEpMeJwovAi7xAkEA2Nkrl/R8fLVi3XyxdeooUkvbDHq+ZyMaMIWoNxwag42kobxnm37/koF90+mOCQg/E+JBPACM3ULgbh6Y/MePnwJAAvQydC2MoDrhvxlmM3E3t3eNMXooImXk1vv9kqUV3No1puyLsxFCkThc+px5TnvTMqrSTExcM3KR54RxOhj64QJBAJFKAIFRV88eoN0RXL1KZDWviVZ1LvlfdX6pLqmt9L3Lu1B6MVjn4EjC5hGD3JyEn+6sm1SeccMVudVOPuautrUCQQCCCxD7tR6AjmhF+oA6Y2bKXUOthrABf7/qkZoBownYCpze6W0/P+9JkYgn74r6lAcNVPTIHLS8tgxovS6P8b0b",
    "fastpubkey1":"MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDId7qOzqSAFNQQiTwFNCXzgUvDnyH8i2smALWns3Gj/+j3lccaTHh8kFtvcIWHbJhZmu9ajn6jj6Fn8D+22eTlsbV0b6Sif4Ezi3ib30DwQVLNfGG2Z9wPNWKhcZhXgU1PmJrgjzWhu0NB2oKKiG9SitkJ4R0PrEjNE72VI+rGrwIDAQAB",
    "fastpubkey":"MIGJAoGBAMh3uo7OpIAU1BCJPAU0JfOBS8OfIfyLayYAtaezcaP/6PeVxxpMeHyQW29whYdsmFma71qOfqOPoWfwP7bZ5OWxtXRvpKJ/gTOLeJvfQPBBUs18YbZn3A81YqFxmFeBTU+YmuCPNaG7Q0HagoqIb1KK2QnhHQ+sSM0TvZUj6savAgMBAAE=",
}


#T_PUB = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDlxfIZD2xsGqmPSoh/AQ/4V8wscuiJPyu/KsUFtgPb1Z1IisNvCZNFh6xOshf4siB+vNK4tTc3UTRqCwOE4khthz4AR0xFgDp4WjwSUf8NzvPTsRXZgm6WqEYYm1KBD2FPpp3ZWGtGsM29S79j/stS4QvfEsqPdpTSoZCuoM2bywIDAQAB"
#T_PRI = "MIICXQIBAAKBgQDlxfIZD2xsGqmPSoh/AQ/4V8wscuiJPyu/KsUFtgPb1Z1IisNvCZNFh6xOshf4siB+vNK4tTc3UTRqCwOE4khthz4AR0xFgDp4WjwSUf8NzvPTsRXZgm6WqEYYm1KBD2FPpp3ZWGtGsM29S79j/stS4QvfEsqPdpTSoZCuoM2bywIDAQABAoGBAN8xRFWrcbogvAwAbk5QDd9CCYYzqEWJI0lylidSArWL7lgE0ooNVwz3GRzoSfi9rmrtqBLblGMbcjp/sE9oLsi+huX8bWhArdceB8OLaZPuO5qj0j4Ur9VxqV6yxzlq8Cq1YQGnKU3/r+I00f6Ivw+ej0aVc77aQA3Tes+qp7eBAkEA9/C+0XGEL94pY1rWXHhuUYvibPRzpq6PdRQhy05BwbO4e//Xev6aOK5i6vZpkEyiF1HiqICZR9/SzBSUiGW8EQJBAO0+BU2xCvX3zq7zPlvv/EFkoBXNAYWKW8Vy6m0ZcnZqiinIK9CsRVuD1M03YBSmtbACo69VmzYP/pTFOtbkZhsCQQCUzhtoDm4cYISMiccfpnPnY0IYzDng7uFQji2eHDCg9aEiYrFLsySSIi9h/1Pp8+RQhKe5I71bAr08GJnwpsZRAkBudqlbgmrbGlZXKZVIk5Z+EE9ltz3VIxYV+qriv62HK5ZHXBfiosPsl5aXMwh+tRz15lS2yAJsCsh8FtWNx20vAkA0ZHFW/M1JoJHJI+MMtqHpOR6eufb6HgNprEQzt+dJ39bS08fFmsYGVXXQL/nyre6XraAA6ty8OKsKoZPL3ARe"

T_PUB = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDId7qOzqSAFNQQiTwFNCXzgUvDnyH8i2smALWns3Gj/+j3lccaTHh8kFtvcIWHbJhZmu9ajn6jj6Fn8D+22eTlsbV0b6Sif4Ezi3ib30DwQVLNfGG2Z9wPNWKhcZhXgU1PmJrgjzWhu0NB2oKKiG9SitkJ4R0PrEjNE72VI+rGrwIDAQAB"
T_PRI = "MIICXgIBAAKBgQDId7qOzqSAFNQQiTwFNCXzgUvDnyH8i2smALWns3Gj/+j3lccaTHh8kFtvcIWHbJhZmu9ajn6jj6Fn8D+22eTlsbV0b6Sif4Ezi3ib30DwQVLNfGG2Z9wPNWKhcZhXgU1PmJrgjzWhu0NB2oKKiG9SitkJ4R0PrEjNE72VI+rGrwIDAQABAoGBALvqB7XAHNF3NMZ/bgTOuliFNfkc3WX3ZqxL8/xMqFT8GWykOOv9DOBvDVbsGi8066brJj0z36AAjmN5ALCtlfLVQWB/WYU65+ZktoEVy/JI/jGLSuD2lVhDzeWiHmN3SSWG3kh76WTcuLJc1dFkW3mSF59Q1Qnx9GRTKWtnlcchAkEA7KlwKA9GCJvYj7GKl0o4i/nyjUD5Sd32Qptm2WYu7J6DzBxcg74qFjLC9xDfwIK3jDYhhib2jRKTHicKLwIu8QJBANjZK5f0fHy1Yt18sXXqKFJL2wx6vmcjGjCFqDccGoONpKG8Z5t+/5KBfdPpjgkIPxPiQTwAjN1C4G4emPzHj58CQAL0MnQtjKA64b8ZZjNxN7d3jTF6KCJl5Nb7/ZKlFdzaNabsi7MRQpE4XPqceU570zKq0kxMXDNykeeEcToY+uECQQCRSgCBUVfPHqDdEVy9SmQ1r4lWdS75X3V+qS6prfS9y7tQejFY5+BIwuYRg9ychJ/urJtUnnHDFbnVTj7mrra1AkEAggsQ+7UegI5oRfqAOmNmyl1DrYawAX+/6pGaAaMJ2Aqc3ultPz/vSZGIJ++K+pQHDVT0yBy0vLYMaL0uj/G9Gw=="

class FastPayApi:
    def __init__(self):
        self.prikey = T_PRI
        self.fastpubkey = T_PUB
        self.merchantno = COMMON_CONFIG["merchantno"]
        self.departmentno = COMMON_CONFIG["departmentno"]
        self.url = COMMON_CONFIG["url"]
        self.httpHeader = {"Content-Type" : "application/octet-stream",
            "User-Agent": "Dalvik/1.6.0 (Linux; U; Android 4.2.2; NX40X Build/JDQ39)",
            "Accept-Encoding": "gzip"}
        self.crypto = CryptoHelper()
        self.prikeyob = self.crypto.importKey(self.prikey)
        self.pubkeyob = self.crypto.importKey(self.fastpubkey)
        self.http = HttpApi(logger)
        self.errorCode = 0
         
    def encodeBody(self, src):
        srcLen = len(src) 
        cutLen = 117
        if srcLen <= cutLen:
            return self.crypto.rsa_encrypt(src, self.pubkeyob)
        result = ""
        count = srcLen / cutLen
        modcount = srcLen % cutLen
        for i in range(0, count):
            itemStr = src[i*cutLen:i*cutLen + cutLen]
            itemEncode = self.crypto.rsa_encrypt_pure(itemStr, self.pubkeyob)
            print ("itemStr:[%s], itemLen:%d, encodeLen:%d"% (itemStr,len(itemStr),len(itemEncode)))
            result += itemEncode
        if modcount > 0:
            tempStr = src[count * cutLen: count * cutLen + modcount]
            #tempStr = "12"
            tempStrEncode = self.crypto.rsa_encrypt_pure(tempStr, self.pubkeyob)
            print ("itemStr:[%s], itemLen:%d, encodeLen:[%d]"% (tempStr,len(tempStr), len(tempStrEncode)))
            result += tempStrEncode
        return base64.b64encode(result)

    def decodeBody(self, src):
        cutLen = 128
        decodeSrc = base64.b64decode(src)
        count = len(decodeSrc) / cutLen
        result = ""
        for i in range(0, count):
            itemStr = decodeSrc[i*cutLen:i*cutLen + cutLen]
            decodeRe = self.crypto.rsa_decrypt_pure(itemStr, self.prikeyob)
            print ("Decode inputStrLen[%d], decodeItemResult:[%s]"%(len(itemStr), decodeRe))
            result += decodeRe
        return result
    
    def srcSign(self, src):
        signPure = self.crypto.sign(src, self.prikeyob, digest=SHA)
        print("======srcSign src:[%s], result:[%s]" %(src, signPure))
        return signPure

    def processRequest(self, body):
        srcText = json.dumps(body,ensure_ascii=False)
        signPure = self.crypto.sign(srcText, self.prikeyob, digest=SHA)
        print ("src:[%s] len:[%d], signresult:[%s]" %(srcText, len(srcText),signPure))
        bodyEncode = self.encodeBody(srcText)   
        print ("encoded:[%s], len:[%d]"% (bodyEncode, len(bodyEncode))) 

        print ("begin decode -------")
        decodeResult = self.decodeBody(bodyEncode)
        print ("result:[%s]" % decodeResult)
        sendBody = {"orgCode":self.departmentno, "sign":signPure, "body":bodyEncode}
        postBody = json.dumps(sendBody);
        print ("post:[%s]" % postBody)
        info, response = self.http.httpPostCall(self.url, postBody, False, self.httpHeader)
        if not response:
            return None
        return response

class FastPayIns(FastPayApi):
    def __init__(self):
        FastPayApi.__init__(self)
        self.name = "FastIns"
    
    def getMsgSeq(self):
        now = datetime.datetime.now()
        return "%s%04d%02d%02d%02d%02d%02d" %(self.name, now.year, now.month, now.day, now.hour, now.minute, now.second)    

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
            _file.writeline(cpOrderId)
            _file.writeline(orderTime)
            _file.writeline(smsOrderId)    

    def payInit(self):
        body = {}
        seq = self.getMsgSeq()
        orderId = ("fast_%s" % seq)
        body["MercCode"] = self.merchantno
        body["TranType"] = "300000"
        body["Phone"] = "13530749353"
        accountName = "郭靖"
        body["AccountName"] = accountName.decode("utf8").encode("utf8")
        body["CertNo"] = "421083199005220477"
        body["AccountNo"] = "6214837551855632"
        body["Password"] = ""
        body["OrderNum"] = orderId
        body["Cvn2"] = ""
        body["ExpDate"] = ""
        body["Amount"] = "1"
        body["ProductType"] = "T1_QUICK"
        body["OrderDesc"] = "pytest"
        body["OrderTime"] = self.getOrderTime()
        body["SubMercode"] = ""
        body["ExtData"] = ""
        resp = self.processRequest(body)  
        print "res:[%s]" %resp
        respDict = json.loads(resp)
        respSign = respDict["sign"]
        respBodyText = respDict["body"]
        respBodyTextDecode = self.decodeBody(respBodyText)
        print respBodyTextDecode
        print ("resp. body:[] sign:[%s]"%( respSign))
        respCalcSign = self.srcSign(respBodyTextDecode)
        print("sign:[%s], calcSign:[%s]"%(respSign, respCalcSign))
        respBodyDict = json.loads(respBodyTextDecode)
        if(respBodyDict["ResultCode"] == "0000"):
            print("payInit Success.")
            body["SmsOrderId"] = respBodyDict["SmsOrderNum"]
            self.saveInitData(body)
        else:
            print("payInit Failed. ErrMsg:[%s]"%respBodyDict["ErrMsg"]) 

    def payConfirm(self):
        body = {}
        seq = self.getMsgSeq()
        body["MercCode"] = self.merchantno
        body["TranType"] = "100000"
        body["Phone"] = "13530749353"
        body["PhoneVeriCode"] = "471820"
        body["SmsOrderNum"] = "1498532273995"
        body["AccountName"] = "郭靖"
        body["CertNo"] = "421083199005220477"
        body["AccountNo"] = "6214837551855632"
        body["Password"] = ""
        body["Cvn2"] = ""
        body["ExpDate"] = ""
        body["OrderNum"] = ""
        body["Amount"] = "1"
        body["ProductType"] = "T1_QUICK"
        body["OrderDesc"] = "pytest"
        body["OrderTime"] = ""
        body["SubMercode"] = ""
        body["ExtData"] = ""
        resp = self.processRequest(body)
        print ("res:[%s]" % resp)
        respDict = json.loads(resp)
        respSign = respDict["sign"]
        respBodyText = respDict["body"]
        respBodyTextDecode = self.decodeBody(respBodyText)
        print ("bodyText:[%s]" % respBodyTextDecode) 
    
    def queryOrder(self):
        body={}
        body["MercCode"] = ""
        body["TranType"] = "200000"
        body["OrderNum"] = ""
        
        resp = self.processRequest(body)
        respDict = json.loads(resp)
        print ("res:[%s]"%resp)
        print("bodyText:[%s]"% self.decodeBody(respDict["body"]))
 
if __name__=='__main__':
    logging.config.fileConfig("logging.conf")
    logger = logging.getLogger("root")
    ins = FastPayIns()
    ins.payInit()
    #ins.payConfirm()

    

