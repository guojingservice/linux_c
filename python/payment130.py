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

	def call_payOrder_pay(self, accountId, payType, amount, waresName, transId, feeId, price, payInfo=Ice.Unset, needEntrustPay=Ice.Unset, payChannel=Ice.Unset, exPayInfo=Ice.Unset, isBind=Ice.Unset):
		channel = []
		channel.append(payChannel)
		req = Service.PayOrderReq(CommonInfo["PlatId"], CommonInfo["BusPlatId"], 0, self.getMsgSeq(), orderType=Service.PayOrderType.POTPay, accountId=accountId, payType=payType, amount=amount, payInfo=payInfo, needEntrustPay=needEntrustPay, payChannel=channel, waresName=waresName, transId=transId, feeId=feeId, price=price,isBind=isBind, exPayInfo=exPayInfo)
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

	def call_refund(self, batchRefundNo, payChannel, orderIdMap = {}):
		req = Service.RefundReq(CommonInfo["PlatId"], CommonInfo["BusPlatId"], 0, self.getMsgSeq(), batchRefundNo=batchRefundNo, payChannel=payChannel, orderIdMap=orderIdMap)
		resp = self.prx.refund(req)
		return resp

class PaymentTest(unittest.TestCase):
	def test_weibo_pay(self):
		username = "8571"
		password = "123456"
		paytype = 403
		amount = 1
		waresName = "购物测试"
		now = datetime.datetime.now()
		transId = "TEST%04d%02d%02d%02d%02d%02d%03d" %(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond / 1000)
		feeId = "168500000001"
		price = 1
		accountId = 1375530002
        	exPayInfo = {"appid":"5000006577"}
        	payInfo = "{\"openid\":\"33011611021602470005100251\"}"
        	payOrderResp = svcApi.call_payOrder_pay(accountId, paytype, amount, waresName, transId, feeId, price, payInfo, payChannel=130, exPayInfo=exPayInfo, isBind=0)
        	print payOrderResp.payParam
        	print payOrderResp
        	self.assertEqual(payOrderResp.retCode, 0)
        	self.assertTrue(len(payOrderResp.orderId) > 0)
		
	def test_query_pay(self):
		orderId="33011611111730340003100001"
		queryOrderResp = svcApi.call_queryPayOrder(orderId)
		print queryOrderResp
		self.assertEqual(queryOrderResp.retCode, 0)
		self.assertEqual(queryOrderResp.status, 3)
		
	def test_refund(self):
		payChannel = 103
		now = datetime.datetime.now()
		orderIdMap = {"33011609061920260002100001":"test_refund"}
		now = datetime.datetime.now()
		refundId = "%s%04d%02d%02d%02d%02d%02d%03d" % ("refund_zxhz",now.year, now.month, now.day, now.hour, now.minute, now.second, 1)
		refundResp = svcApi.call_refund(refundId, payChannel, orderIdMap);
		print refundResp
		self.assertEqual(refundResp.retCode, 0)
		

if __name__=='__main__':
	# 清理数据
	db = SvcDatabase()
	svcApi = PaymentSvcApi()

	unittest.main()

