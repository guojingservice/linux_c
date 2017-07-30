#!/bin/env python
#-*- coding: utf-8 -*- 

import urllib
import urllib2
from urllib import urlencode
from urllib import quote
import collections
from crypto import CryptoHelper
from Crypto.Hash import SHA

aliconfig = {
    "partner" : "2088221300012641",
    "private_key_path" : "key/rsa_private_key.pem",
    "public_key_path" : "key/alipay_public_key.pem",
    "sign_type" : "RSA",
    "input_charset" : "utf-8",
    "cacert" : "./cacert.pem",
    "service": "single_trade_query"
}


def getXmlText(src, key):
    keyStartStr = ("<%s>"%key)
    keyEndStr = ("</%s>"%key)
    start = src.find(keyStartStr)
    end = src.find(keyEndStr)
    if start == -1 or end == -1:
        return ""
    result = src[start + len(keyStartStr) : end]
    return result.strip();

def generateSign(reqMap):
    items = reqMap.items()
    items.sort()
    signsrc = ""
    for key,value in items:
        if reqMap[key] == "":
            continue
        signsrc += ("%s=%s&" %(key, reqMap[key]))
    signsrc = signsrc[0:-1]
    #print ("signsrc:%s" % (signsrc))
    cyhelper = CryptoHelper()
    key = cyhelper.importKeyFile(aliconfig["private_key_path"])
    sign = cyhelper.sign(signsrc, key, digest=SHA)
    return sign
    
def generateReqData(reqMap):
    items = reqMap.items()
    items.sort()
    reqsrc = ""
    for key, value in items:
        reqsrc += ("%s=%s&"%(key, quote(value)))
    reqsrc = reqsrc[0:-1]
    return reqsrc

def oneQueryOrder(reqMap):
    
    sign = generateSign(reqMap)
    reqUrl = "https://mapi.alipay.com/gateway.do?"
    reqMap["sign"] = sign
    reqMap["sign_type"] = "RSA"
    getParam = generateReqData(reqMap)
    getUrl = ("%s%s" %(reqUrl, getParam))
    #print getUrl
    req = urllib2.Request(getUrl)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res

def queryAliOrder(outTradeNo):
    out_trade_no = outTradeNo
    #out_trade_no = "33011702240005525294100250"
    reqMap = {}
    reqMap["service"] = aliconfig["service"]
    reqMap["partner"] = aliconfig["partner"]
    reqMap["out_trade_no"] = out_trade_no
    reqMap["_input_charset"] = aliconfig["input_charset"]

    res = oneQueryOrder(reqMap)

    #print res

    isSuccess = getXmlText(res, "is_success")
    #print isSuccess
    if isSuccess == "T":
        tradeNode = getXmlText(res, "trade")
        #print tradeNode
        outTradeNo = getXmlText(tradeNode, "out_trade_no")
        tradeNo = getXmlText(tradeNode, "trade_no")
        tradeStatus = getXmlText(tradeNode, "trade_status")
        totalFee = getXmlText(tradeNode, "total_fee")
        gmtPayment = getXmlText(tradeNode, "gmt_payment")  
        if gmtPayment == "":
            gmtPayment = getXmlText(tradeNode, "gmt_close")
        buyerEmail = getXmlText(tradeNode, "buyer_email")
        #print outTradeNo, tradeNo, tradeStatus, totalFee, gmtPayment, buyerEmail
        if tradeStatus == "TRADE_SUCCESS":
            fenPrice = totalFee.replace(".", "")
            print 1, outTradeNo, fenPrice, tradeNo, buyerEmail
    else:
        errorMsg = getXmlText(res, "error")
        print ("query failed. outTradeNo:[%s], error:[%s]"%(outTradeNo, errorMsg))

with open("./input_orderid.txt") as file_:
    line = file_.readline()
    while(line):
        line = line.strip()
        outTradeNo = line
        queryAliOrder(outTradeNo)        
        line = file_.readline()




