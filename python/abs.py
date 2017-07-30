#!/bin/env python
#-*- coding: utf-8 -*-

#################################################################
#
#  Author：颜小刚
#
#################################################################

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
'''
URL = {
    "abs": "http://192.168.0.151:9990/abs",
    "cporder": "http://192.168.0.227:8080/paypai/order",
    "tokencheck": "http://192.168.0.227:8080/paypai/tokencheck",
    "onepaynotify" : "http://192.168.0.227:8080/notify/onepay"    
}
'''

DeviceInfo = {"platId":10000, "deviceType":100, "osType":1, 
            "terminalId":"742ea0af0fea4760b1c1cd67cccbd1b1", "acid":"999", 
            "version":"IAPPPAY_3.4.0_Android",
            "country":"CHN", "lang":"CHS", "currency":"RMB"}
'''
AppInfo = {"privateKey":"MIICXAIBAAKBgQCwDqNB3fC2FbmINIIOKq/4EjEqHnxlox2A4XybCGHAz1hwbthNKjYlIukmoQ0SKc3x7lmP0i9JBD3QHec1qve2BIdnzEIM1I5SfNAvinekMIFH7ECrqxReeHt4KlzBQdNZ8VdK0zxeeOTBAdaJJVlqS5ExS8F917rSClpMSevoBQIDAQABAoGBAI191hsTgWb1IryiZnt4NyAJjtWo1pTgeM+haIE4RUet3AfQLaomaImD+xj+igC09DyhL/10EGiALiVaQv1Qv+6EzxxOCrr6PX+CpNXe0Tm8vilDbvVjOYzc3KNQRUthmslJ0aH7yHcd10GtYQt/RDi0fHItWnmdW5w7DPK14tpBAkEA4rePBK1QebQEfnU9DrAE3yHwrL7px5SjoTBHYCbi+NcnTM+9o7eEVKo4iysv83nSpZHdYcaIcrwXzcia9EgtiQJBAMbMAGp1nTvKypNz6u6bhBIAmdGcaHmTTqyrg6CDtwmVqEq2re2v0uhdkc1gU/QoIUEMxz5nNy+38R4bmDisY50CQCY1c1gBcY+hRCSf05N3HMsSKEKkxjeJmG4g+dZ9l0EC2a+7TyWZVycBrRffRmyNOnAG/j1tPS/A/W4EAgFrbKkCQH1Y5i46SNEJth+xaIHZBzZ+sH5te6akzmerocxVINVnSv0JILQNOBQR47w2r9j0cLtefkcHt9Fbzynnxlx9vjUCQHRZXECC27Y5nnjL+TdIEp4h+m2XXLriTGMk3lnx2FeEl9uMPQwhttvhzoQqwwtIKToeF7mJiYx/QsYYMAwlLRg=", "id":"5000005684", "name":"TestApp01", 
"userid": "superbboy", "notify":"http://192.168.0.227:28080/notify"}
'''

AppInfo = {"privateKey":"MIICXAIBAAKBgQCs9FrLDMw/acHx5RD8vPjRUp7F/gnmaKIEcq8wHQZCC01QrpDnyXmqktOxkqVYLUpPT3BZNy6mOfc53XYGuin+hwOk6a9fU9zrNVN8zXlO/V/50+oWsPU+J8EQ6bVkHUgWZlg5GPcLwNvKAd7WElC8ZTf0tQhFzI5raajcOGrBwQIDAQABAoGAczRY/gPKUTsa6wvQIumlO5kzFWNAKO/ta9UQiJXswzVQDLwa3apAlrQyuoeaB4AzjVy201aEhkj6OtsfcR+0NDQzp/P24bivdKVcSswgiOb+oWgIOOLqm6be32V0zRLJ73l5UngL4hCjsC5L8i3hccE2XtzUCR/CuDqkNSs8SvkCQQDZl86VXQ2adJwDkd+AUFlxxxuWjyD9//5Z2AhCyVFzQdvyWEzee3b+S5ROfwpINAYGpO+uAPwl+tmyoXv2/hTLAkEAy3uBdqhxsu0mvNcWrZuuphJBt7vPIPakQEXRL4MfUlvhdcQbdpP21NmCN9YQfCGF8y/ClvTcw30D4oQQVBZ+IwJBAM265qv6Sz5aOph1d6hOUANvifoUYdFGFSrFQypCRix/fIHqUuOYQK22sAZ3vzT9WyU1FRij/cO7JdHrNNYW7XkCQE8yzv0EKtzdeQpfHTCNO7jfujxtGP1Xgi6R/g1kF7jSkjpoDdhlVtkZn5lj9B6cXap9mFtxCsv7yJtNk51m88kCQF8Lo1EfbvbPAWSN95MN4EO271lWLfMsomM1g9kK58oNPLTeaPibI1t3xA1h5u9I42SHPpf+RWmex+TTmKZ1XKQ=", "id":"500000185", "name":"演示商品", 
"userid": "superbboy", "notify":"http://192.168.0.227:28080/notify"}


WaresInfo = {"id": 1, "price":1, "private":"测试一下啊", "openprice":True}

SdkKey = {"ver":100, "seq":1, "publicKey":"MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCsv4pYUzLVXdYivl8EaLQRcj75yuEt/+OrcKXbVygQteO9EmqOU8bi5EHf4V4eCRFv26rfTz5UnAtoLfeYDHB0mchRh2GU6JzzcTPnslHJfI9ZZVBrUBxsbhH1s35cXxS5UGlZ6mu4CKP/SENBIttqOdWHILbDZVq/PqSRd9pLYQIDAQAB"}
'''
SdkKey = {"ver":100, "seq":1, "publicKey":"MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC17pr4P1MKHNGXyx4YXTuML3Uq5IUBxT6EgmbQ8GffYeCpU3/N168vbeZe6yZiHFsk7n+x+jzosezC5HPXK3nxNNi+f1mBfTxY9tO7lB3HFZVRa+eCL0osL+osPOi3NppGZIp8nrMpzSThugprj8pg8QoiY2DRhTVNAYkgw58f6QIDAQAB"}
'''
registerUser = False
billingLogin = True
# logintype can be: 1-password, 2-voucher
UserInfo = {"loginName":"superbboy", "password":"123456", "voucher":"", "loginType": 1}
PayInfo = {"type":16, "info":""}

loginToken = None
userId = None

transId = ""
fee=0
paytransid = ""

class Abs:
    def __init__(self):
        self.aesKey = "1234567890abcdef"
        self.appPrivKey = CryptoHelper.importKey(AppInfo["privateKey"])
        self.billingPubKey =  CryptoHelper.importKey(SdkKey["publicKey"])
        self.httpHeader = {"Content-Type" : "application/octet-stream",
            "User-Agent": "Dalvik/1.6.0 (Linux; U; Android 4.2.2; NX40X Build/JDQ39)",
            "Accept-Encoding": "gzip"}
        self.crypto = CryptoHelper()
        self.http = HttpApi(logger)
        self.tokenId = None
        self.errorCode = 0

    def processRequest(self, cmdid, body):
        request = {"PlatID":DeviceInfo["platId"], "CmdID":cmdid, "DeviceType": DeviceInfo["deviceType"],
                            "OsType":DeviceInfo["osType"], "TerminalID": DeviceInfo["terminalId"],
                            "ACID": DeviceInfo["acid"], "Country":DeviceInfo["country"], 
                            "Lang":DeviceInfo["lang"], "Currency":DeviceInfo["currency"],
                            "Version":DeviceInfo["version"], 
                            }
        if self.tokenId:
            request["TokenID"] = self.tokenId
        
        if body:
            request["Body"] = body

        # calc sign
        req_text = json.dumps(request, ensure_ascii=False)
        logger.info("req text:%s" %(req_text))
        
        req_sign = self.crypto.md5(req_text)
        logger.info("sign:%s" %(req_sign))
        http_request_body = {}
        http_request_body["data"] = self.crypto.aes_encrypt("%s#%s" %(req_sign, req_text), self.aesKey)
        http_request_body["encryptkey"] = "%03d%05d%s" %(SdkKey["ver"], SdkKey["seq"], 
                                    self.crypto.rsa_encrypt(self.aesKey, self.billingPubKey))       
            
        response_body = None
        info, response = self.http.httpPostCall(URL["abs"], json.dumps(http_request_body, ensure_ascii=False), False, self.httpHeader)
        if not response:
            return None
            
        jsondata = json.loads(response, object_hook=decode_dict)
        if "ErrorMsg" in jsondata:
            # common error 
            logger.error("Common error:%d %s" %(jsondata["RetCode"], jsondata["ErrorMsg"]))
            return None
            
        if "data" not in jsondata:
            logger.error("No data body")
            return None

        plain_data = self.crypto.aes_decrypt(jsondata["data"], self.aesKey).split("#")
        logger.info("resp sign:%s, response body:%s" %(plain_data[0], plain_data[1]))
        resp_sign = self.crypto.md5(plain_data[1])
        if plain_data[0] == resp_sign:
            logger.info("Signature matched")
        else:
            logger.error("Signature mismatched:resp[%s], calc[%s]"  %(plain_data[0], resp_sign))
            return None
            
        response_body = json.loads(plain_data[1], object_hook=decode_dict)
        self.errorCode = int(response_body["RetCode"])
        if self.errorCode != 0:            
            logger.error("Error: code:%s msg:%s" %(response_body["RetCode"], response_body["ErrMsg"]))
            return None
        if "TokenID" in response_body:
            self.tokenId = response_body["TokenID"]
        return response_body["Body"]

class PyClient(Abs):
    def __init__(self):
        Abs.__init__(self)
        pass
    
    def sendSms(self):
        body = {"VeriType":1, "PhoneNum":"13530749353"}
        res = self.processRequest(,body)
        print res

    def register(self):
        logger.info("===start register ===") 
        body = {"LoginName": UserInfo["loginName"], "PassWord": UserInfo["password"]}
        if billingLogin:
            body["AppID"] = AppInfo["id"]
        response = self.processRequest(12, body)
        if response != None:
            if response["LoginName"] != UserInfo["loginName"]:
                logger.error("mismatched loginname:req[%s], resp[%s]" %(UserInfo["loginName"], response["LoginName"]))
                response = None
            elif "LoginToken" not in response:
                logger.error("No LoginToken")
                response = None
            elif "Voucher" not in response:
                logger.error("No Voucher")
                response = None
            else:
                global loginToken, userId
                loginToken = response["LoginToken"]
                userId = response["UserID"]
                print loginToken, response["Voucher"], userId
                
        logger.info("====end register===")
        if response == None:
            raise OpException("register")
    
    
if __name__=='__main__':
    logging.config.fileConfig("logging.conf")
    logger = logging.getLogger("root")
   
    pyClient = PyClient()
    pyClient.sendSms()    

