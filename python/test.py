#!/bin/env python
#-*- coding: utf-8 -*-

import sys, os
binpath = os.path.abspath(sys.argv[0])
bindir = os.path.dirname(binpath)
os.chdir(bindir)

sys.path.append(os.path.join(os.environ["ICE_HOME"], "python"))
sys.path.append(os.path.join(bindir, "python"))
sys.path.append(os.path.join(bindir, "common"))

import datetime, time

import Ice
import Service
import traceback
import unittest
from svcdata import *

class PaymentSvcApi(SvcApiBase):
    def __init__(self):
        SvcApiBase.__init__(self)
        self.name = "Payment"    
        self.prx = Service.PaymentPrx.uncheckedCast(self.ic.stringToProxy("payment"))
        self.prx_internal = Service.PaymentInternalPrx.uncheckedCast(self.ic.stringToProxy("paymentinternal"))
                
    def call_payOrder_charge(self, accountId, payType, amount, payInfo=Ice.Unset, needEntrustPay=Ice.Unset):
        req = Service.PayOrderReq(CommonInfo["PlatId"], CommonInfo["BusPlatId"], 0, self.getMsgSeq(), orderType=Service.PayOrderType.POTCharge, accountId=accountId, payType=payType, amount=amount, payInfo=payInfo, needEntrustPay=needEntrustPay)
        resp = self.prx.payOrder(req)        
        return resp        

    def call_payOrder_pay(self, accountId, payType, amount, waresName, transId, feeId, price, payInfo=Ice.Unset, needEntrustPay=Ice.Unset, isThirdVir=Ice.Unset, exPayInfo=Ice.Unset,payChannel=Ice.Unset):
        req = Service.PayOrderReq(CommonInfo["PlatId"], CommonInfo["BusPlatId"], 0, self.getMsgSeq(), orderType=Service.PayOrderType.POTPay, accountId=accountId, payType=payType, amount=amount, payInfo=payInfo, needEntrustPay=needEntrustPay, waresName=waresName, transId=transId, feeId=feeId, price=price, isThirdVir=isThirdVir, exPayInfo=exPayInfo, payChannel=payChannel)
        resp = self.prx.payOrder(req)        
        return resp        
        
    def call_queryPayOrder(self, orderId, retryTimes=3, retryInterval=0.2):
        for i in range(0, retryTimes):
            req = Service.QueryPayOrderReq(CommonInfo["PlatId"], CommonInfo["BusPlatId"], 0, self.getMsgSeq(), orderId = orderId)
            resp = self.prx.queryPayOrder(req)   
            if resp.retCode == 0 and resp.status == 0:
                time.sleep(retryInterval)
            else:
                break;
        return resp
    
    def call_getPayChannel(self, osType, deviceType):
        req = Service.GetPayChannelReq(CommonInfo["PlatId"], CommonInfo["BusPlatId"], 0, self.getMsgSeq(), osType = osType, deviceType = deviceType)
        resp = self.prx.getPayChannel(req)        
        return resp                

    def call_queryRefund(self, refundOrderId):
        req = Service.QueryRefundReq(CommonInfo["PlatId"], CommonInfo["BusPlatId"], 0, self.getMsgSeq(), refundOrderId = refundOrderId)
        resp = self.prx.queryRefund(req)        
        return resp
    
class PaymentTest():
        
    def test_pay(self):        
        paytype = 4
        amount = 1
        waresName = "爱贝测试商品"
        now = datetime.datetime.now()
        transId = "TRANS%04d%02d%02d%02d%02d%02d%03d" %(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond / 1000)
        feeId = "168500000001"
        price = amount
        accountId = 14382323
        exPayInfo = {}
        exPayInfo[Service.EXAPPID] = "500000185"
        paychannel = [106]
        payInfo = '{"cardtype":"22","cardno":"1455226552486236","cardamount":100,"cardpwd":"1455252663399255"}'
        #payInfo = '{"callback_url":"http://219.143.16.178:32100/h5/callback/S/P/4/001A154ll7d8m5p7wayein04hi35dwbhuiklkzl3iwbc0x3vyewvln0399437sx7sjzebqm7o3s975w/103/32011511271711000004/5000001436","merchant_url":"http://219.143.16.178:32100/h5/callback/F/P/4/001A154ll7d8m5p7wayein04hi35dwbhuiklkzl3iwbc0x3vyewvln0399437sx7sjzebqm7o3s975w/103/32011511271711000004/5000001436"}'
        
        print payOrderResp.retCode
        print payOrderResp.orderId
        print payOrderResp.payChannel

    def test_query(self, orderId):
        queryResp = svcApi.call_queryPayOrder(orderId)
        print queryResp.retCode
        print queryResp.status
        print queryResp.result        

    def test_queryRefund(self, refundOrderId):
        queryResp = svcApi.call_queryRefund(refundOrderId)
        print queryResp.retCode
        print queryResp.amount
        print queryResp.result

    def test_payOrder(self):
        paytype = 403
        amount = 1
        waresName = "爱贝测试商品"
        now = datetime.datetime.now()
        transId = "TRANS%04d%02d%02d%02d%02d%02d%03d" %(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond / 1000)
        needEntrustPay=Ice.Unset
        waresName="gjjtestwares"
        feeId = "168500000001"
        price = amount
        isThirdVir=Ice.Unset
        accountId = 14382323
        exPayInfo = {}
        exPayInfo[Service.EXAPPID] = "300440381"
        paychannel = [103]
        payInfo = '{"cardtype":"22","cardno":"1455226552486236","cardamount":100,"cardpwd":"1455252663399255"}'
        payResp = svcApi.call_payOrder_pay(accountId, paytype,amount, waresName, transId, feeId,price, payChannel=paychannel)

        print payResp
    
    def test_payOrderH5(self):
        paytype = 403
        amount = 1
        waresName = "爱贝测试商品"
        now = datetime.datetime.now()
        transId = "TRANS%04d%02d%02d%02d%02d%02d%03d" %(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond / 1000)
        needEntrustPay=Ice.Unset
        waresName="gjjtestwares"
        feeId = "168500000001"
        price = amount
        isThirdVir=Ice.Unset
        accountId = 14382323
        exPayInfo = {}
        exPayInfo[Service.EXAPPID] = "300440381"
        paychannel = [154]
        payInfo = '{"cardtype":"22","cardno":"1455226552486236","cardamount":100,"cardpwd":"1455252663399255"}'
        payResp = svcApi.call_payOrder_pay(accountId, paytype,amount, waresName, transId, feeId,price, payChannel=paychannel)

        print payResp
        
        

    def test_payOrder_weixinpc(self):
        paytype = 403
        amount = 1
        waresName = "爱贝测试商品"
        now = datetime.datetime.now()
        transId = "TRANS%04d%02d%02d%02d%02d%02d%03d" %(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond / 1000)
        needEntrustPay=Ice.Unset
        waresName="gjjtestwares"
        feeId = "168500000001"
        price = amount
        isThirdVir=Ice.Unset
        accountId = 14382323
        exPayInfo = {}
        #exPayInfo[Service.EXAPPID] = "300440381"
        exPayInfo[Service.EXAPPID] = "5000006577"
        paychannel = [121]
        #payInfo = '{"cardtype":"22","cardno":"1455226552486236","cardamount":100,"cardpwd":"1455252663399255"}'
        payInfo = ""
        payResp = svcApi.call_payOrder_pay(accountId, paytype,amount, waresName, transId, feeId,price, exPayInfo=exPayInfo,payChannel=paychannel)

        print payResp

    def test_payOrder_weixinmsJS(self):
        paytype = 403
        amount = 1
        waresName = "爱贝测试商品"
        now = datetime.datetime.now()
        transId = "TRANS%04d%02d%02d%02d%02d%02d%03d" %(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond / 1000)
        needEntrustPay=Ice.Unset
        waresName="gjjtestwares"
        feeId = "168500000001"
        price = amount
        isThirdVir=Ice.Unset
        accountId = 14382323
        exPayInfo = {}
        exPayInfo[Service.EXAPPID] = "300440381"
        paychannel = [120]
        payInfo = '{"callback_url":"22"}'
        payResp = svcApi.call_payOrder_pay(accountId, paytype,amount, waresName, transId, feeId,price, payChannel=paychannel)

        print payResp

       
    def test_payOrder_qqwalleth5(self):
        paytype = 116
        amount = 1
        waresName = "爱贝测试商品"
        now = datetime.datetime.now()
        transId = "TRANS%04d%02d%02d%02d%02d%02d%03d" %(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond / 1000)
        needEntrustPay=Ice.Unset
        waresName="GJTEST-t1"
        feeId = "168500000001"
        price = amount
        isThirdVir=Ice.Unset
        accountId = 14382323
        exPayInfo = {}
        exPayInfo[Service.EXAPPID] = "5000006577"
        paychannel = [173]
        payInfo = ""
        payResp = svcApi.call_payOrder_pay(accountId, paytype,amount, waresName, transId, feeId,price, exPayInfo=exPayInfo, payChannel=paychannel)
        print payResp
    
    def test_payOrder_paalipc(self):
        paytype = 401
        amount = 1
        waresName = "爱贝测试商品"
        now = datetime.datetime.now()
        transId = "TRANS%04d%02d%02d%02d%02d%02d%03d" %(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond / 1000)
        needEntrustPay=Ice.Unset
        waresName="GJTEST-t1"
        feeId = "168500000001"
        price = amount
        isThirdVir=Ice.Unset
        accountId = 14382323
        exPayInfo = {}
        exPayInfo[Service.EXAPPID] = "5000006578"
        paychannel = [169]
        payInfo = ""
        payResp = svcApi.call_payOrder_pay(accountId, paytype,amount, waresName, transId, feeId,price, exPayInfo=exPayInfo, payChannel=paychannel)
        print payResp
    
    def test_payOrder_paweixinpc(self):
        paytype = 403
        amount = 1
        waresName = "爱贝测试商品"
        now = datetime.datetime.now()
        transId = "TRANS%04d%02d%02d%02d%02d%02d%03d" %(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond / 1000)
        needEntrustPay=Ice.Unset
        waresName="GJTEST-t1"
        feeId = "168500000001"
        price = amount
        isThirdVir=Ice.Unset
        accountId = 14382323
        exPayInfo = {}
        exPayInfo[Service.EXAPPID] = "5000006577"
        paychannel = [121]
        payInfo = ""
        payResp = svcApi.call_payOrder_pay(accountId, paytype,amount, waresName, transId, feeId,price, exPayInfo=exPayInfo, payChannel=paychannel)
        print payResp

    def test_payOrder_paalicard(self):
        paytype = 401
        amount = 1
        waresName = "爱贝测试商品"
        now = datetime.datetime.now()
        transId = "TRANS%04d%02d%02d%02d%02d%02d%03d" %(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond / 1000)
        needEntrustPay=Ice.Unset
        waresName="GJTEST-t1"
        feeId = "168500000001"
        price = amount
        isThirdVir=Ice.Unset
        accountId = 14382323
        exPayInfo = {}
        exPayInfo[Service.EXAPPID] = "5000006577"
        exPayInfo["terminalid"] = "xxx12345"
        exPayInfo["cporderid"] = ("%s%s"%(transId, "1234"))
        exPayInfo["AppAuthCode"] = "286492266875491622"
        paychannel = [172]
        payInfo = ""
        payResp = svcApi.call_payOrder_pay(accountId, paytype,amount, waresName, transId, feeId,price, exPayInfo=exPayInfo, payChannel=paychannel)
        print payResp

    def test_payOrder_zxhzweixinpc(self):
        paytype = 403
        amount = 1
        waresName = "爱贝测试商品"
        now = datetime.datetime.now()
        transId = "TRANS%04d%02d%02d%02d%02d%02d%03d" %(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond / 1000)
        needEntrustPay=Ice.Unset
        waresName="GJTEST-t1"
        feeId = "168500000001"
        price = amount
        isThirdVir=Ice.Unset
        accountId = 14382323
        exPayInfo = {}
        exPayInfo[Service.EXAPPID] = "5000006577"
        exPayInfo["terminalid"] = "xxx12345"
        exPayInfo["cporderid"] = ("%s%s"%(transId, "1234"))
        paychannel = [121]
        payInfo = ""
        payResp = svcApi.call_payOrder_pay(accountId, paytype,amount, waresName, transId, feeId,price, exPayInfo=exPayInfo, payChannel=paychannel)
        print payResp


    def test_payOrder_custom(self):
        paytype = 401
        amount = 1
        waresName = "爱贝测试商品"
        now = datetime.datetime.now()
        transId = "TRANS%04d%02d%02d%02d%02d%02d%03d" %(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond / 1000)
        needEntrustPay=Ice.Unset
        waresName="GJTEST-t1"
        feeId = "168500000001"
        price = amount
        isThirdVir=Ice.Unset
        accountId = 14382323
        exPayInfo = {}
        exPayInfo[Service.EXAPPID] = "5000006577"
        exPayInfo["terminalid"] = "xxx12345"
        exPayInfo["cporderid"] = ("%s%s"%(transId, "1234"))
        paychannel = [169]
        payInfo = ""
        payResp = svcApi.call_payOrder_pay(accountId, paytype,amount, waresName, transId, feeId,price, exPayInfo=exPayInfo, payChannel=paychannel)
        print payResp


def main():
    # 清理数据
    global svcApi
    svcApi = PaymentSvcApi()
    payment = PaymentTest()
   
    payment.test_payOrder_custom() 
    #payment.test_payOrder_paalicard()
    #payment.test_payOrder_paweixinpc();
    #payment.test_payOrder_zxhzweixinpc();    

    #payment.test_payOrder_paalipc();
    #payment.test_payOrder_qqwalleth5();
    #payment.test_payOrder_weixinmsJS()
    #payment.test_payOrderH5()
    #payment.test_queryRefund(sys.argv[1])
    #payment.test_payOrder()
    #payment.test_payOrder_weixinpc()
    #if (len(sys.argv) == 1) :
    #    payment.test_pay()
   # elif (len(sys.argv) == 2) :
     #   payment.test_query(sys.argv[1])

if __name__=='__main__':        
    main()
