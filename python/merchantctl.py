#!/bin/env python
#-*- coding: utf-8 -*-

import sys, os
import urllib
import urllib2
import json

binpath = os.path.abspath(sys.argv[0])
bindir = os.path.dirname(binpath)
os.chdir(bindir)

requestUrlBind = "http://192.168.0.159:25443/system/channelmerchant/bindcard"
requestUrlSetRate = "http://192.168.0.159:25443/system/channelmerchant/setrate"
requestUrlQueryRate = "http://192.168.0.159:25443/system/channelmerchant/queryrate"

merAddTemp = {
    "cpid":"500003",
    "name":"dev测试川菜馆",
    "shortname":"dev测试",
    "servicephone":"40010086",
    "business":"2015050700000010",
    "channel":401,
    "channelaccountid":76,
    "idcardname":"郭靖",
    "idcardno":"421083199005220478",
    "storeaddress":"南山区test",
    "idcardimgurl":"http://www.baidu.com",
    "storeimgurl":"http://www.baidu.com"
}


merBindTemp = {
    "channelmchid":"20170331120402027429",
    "channel":401,
    "channelaccountid": 76,
    "cardno":"6225880000119959",
    "cardholder":"丁蕊"
}
merBindTempFake = {
    "channelmchid":"20170331120xxx",
    "channel":401,
    "channelaccountid": 76,
    "cardno":"622588000011xxx",
    "cardholder":"丁ding"
}


merSetRateTemp = {
    "channelmchid" : "20170424174415024520",
    "channel":401,
    "channelaccountid": 76,
    "rate":"0.006"
}

merQueryRateTemp = {
    "channelmchid" : "20170717141328022137",
    "channel":401,
    "channelaccountid": 76,
}


def bindCard():
    url = requestUrlBind
    data = json.dumps(merBindTempFake)
    data = ("transdata=%s" % data)
    print ("post data:[%s]" % data)
    httpReq = urllib2.Request(url=url, data=data)
    resData = urllib2.urlopen(httpReq)
    res = resData.read()
    print("res:[%s]" % res)

def setRate():
    url = requestUrlSetRate
    data = json.dumps(merSetRateTemp)
    data = ("transdata=%s" % data)
    print ("post data:[%s]" % data)
    httpReq = urllib2.Request(url=url, data=data) 
    resData = urllib2.urlopen(httpReq)
    res = resData.read()
    print("res:[%s]" % res)

def queryRate():
    url = requestUrlQueryRate
    data = json.dumps(merQueryRateTemp)
    data = ("transdata=%s" % data)
    print ("post data:[%s]" % data)
    httpReq = urllib2.Request(url=url, data=data)
    resData = urllib2.urlopen(httpReq)
    res = resData.read()
    print("res:[%s]" % res)

def usage():
    print( "python merchantctl.py [add|modify|delete]" )

def addMerchant():
    url = "http://192.168.0.159:25443/system/channelmerchant/add"
    data = json.dumps(merAddTemp)
    data = ("transdata=%s" % data)
    print ("post data:%s" % data)
    httpReq = urllib2.Request(url=url, data=data)
    resData = urllib2.urlopen(httpReq)
    res = resData.read()
    print("res:[%s]" % res) 

if __name__=='__main__':
    if(len(sys.argv) != 2):
        print "command is missing"
        usage()
    if sys.argv[1] == "add":
        addMerchant()
    elif sys.argv[1] == "bind":
        bindCard()
    elif sys.argv[1] == "delete":
        pass
    elif sys.argv[1] == "setrate":
        setRate()
    elif sys.argv[1] == "queryrate":
        queryRate()
    else:
        pass
      
