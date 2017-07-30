#!/bin/env python
#-*- coding: utf-8 -*-

import re
import os
import sys
import signal
import time
import logging
import MySQLdb
import subprocess 
from collections import defaultdict
from threading import Event
from threading import Thread
#from enum import Enum

sys.path.append(os.path.join(os.environ["ICE_HOME"], "python"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "python"))

import Ice
import Service
import const 
from crypto import CryptoHelper
from tail import Tail
from timeout import timeout 
from http import HTTPHandler

g_isQuit = False
g_quitEvent = Event()
g_reqList = [] #List<PayNotifyReq>
g_reqMap = {} #Map<msgSeq, PayNotifyReq>

const.CHECK_INTERNAL = 600

const.DB_IP = "172.17.16.55"
const.DB_PORT = 23306
const.DB_USER = "zyzxpay"
const.DB_PWD = "lVAdqFuhADvpZsYdfp1aGtY3PbtLxuHHJxxXnicHF5n1ZcmCGiSLfDhnLxr1MdsJXfma0cgs/ge+LDS3n/ngPa9kOp0b3yVITu68gyognL6zeIrWXcL6BR08OLV3V/y2DYTUzWRERvaK6HIiauq8R+H6nLXApoHGE/Ji+HsWaOA="
const.DB_NAME = "zyzxpay"

const.PRI_KEY = "MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBALurXuTqXGZYw46w6wIru2Re4EWFl7fz33xcloZT0GZ2kG4UyywKddUlV6GDXgrCWo51zJpo55qSrAYZ1kE0DTr+QIjyZxNKrA7vyE8JIa+rMEv2WUQZenqxUMfkUCWtQeugDp150XdRPCHe2qmis0GFFKLiBXgZrYolC4iqyhghAgMBAAECgYBETIL1lqFYEhfhl1t/58CEL885HfxwUw3TqbKSYnBmyeGYXnLurUPi9Xsl6bRRABiK3i4/R8x6QcTfV4nVIwdo//st5o3gB4x2OwxrtSM6zs15Dj3xLij4Ryi9B+Ad71kiuRknoGsIF+l5awo8Q5WCNShDo1O8lIsA6tPdrRiHbQJBAOoAdTNISNakp/i4DnWJqDzjduoW7yaezzzLStRSVYgUxn4DPx7s18KCyLoTFG6sNvZpVT6bC+aj76Xu5j1HnL8CQQDNT935v3vLiEID/Xi6KMdoB2OnUrpQGL+OqCexpOaCKH8sEhRwezz7xK3Vqwzp59+8KZ1vITj3YCQkaDPHUCMfAkBbCpaOvz7nk+RuVl35yPcVyYIIjae6JOuIQaf5d5cjfMHFYUn7pDZFzVB/ZND8RjCUKmMqGnTE5V9l9c7KZMRNAkACc/TT+gyxltQrFgkuODSBsqznH97n/BO10Z5/ydeTMIascR7bZS2KWIQ3LE8AMGwE5H5kCIKUugpUgQY1WGjDAkBOT8jiPcs0INUYkvGjYo9954q4WRNDnFxHagimP38IXea+nY6AnFfW/H61xL2zTC03dRVuOwRQOxPlQUW33QuA"
const.PUB_KEY = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC7q17k6lxmWMOOsOsCK7tkXuBFhZe38998XJaGU9BmdpBuFMssCnXVJVehg14KwlqOdcyaaOeakqwGGdZBNA06/kCI8mcTSqwO78hPCSGvqzBL9llEGXp6sVDH5FAlrUHroA6dedF3UTwh3tqporNBhRSi4gV4Ga2KJQuIqsoYIQIDAQAB"
const.REQ_REGEX = re.compile("^\[INFO \|[^|]*\|[^|]*\|[^|]*\|[^|]*\|([^\]]*)\]:NotifyPayResultReq : platid ([^\,]*), channelType ([^\,]*), payInfo ([^\,]*), result ([^\,]*), errCode [^\,]*, settleAmount ([^\,]*), orderId ([^\,]*), proVer [^\,]*, channelOrderId (.*)$", re.I)
const.RESP_REGEX = re.compile("^\[INFO \|[^|]*\|[^|]*\|[^|]*\|[^|]*\|([^\]]*)\]:NotifyPayResultReq : end$", re.I)
const.RESP1_REGEX = re.compile("^\[ERROR\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|([^\]]*)\]:payorder has processed.*", re.I)
const.RESP2_REGEX = re.compile("^\[ERROR\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|([^\]]*)\]:the same req is processing.*", re.I)

class PayNotifyReq(object):
    def __init__(self, msgSeq, platId, channelType, payInfo, result, settleAmount, orderId, channelOrderId=Ice.Unset): 
        self.msgSeq = msgSeq
        self.reqTime = time.time() 
        self.platId = int(platId)
        self.channelType = int(channelType)
        self.payInfo = payInfo
        self.result = int(result)
        self.settleAmount = int(settleAmount)
        self.orderId = orderId
        self.channelOrderId = channelOrderId
        self.reqTimes = 1

    def send(self):
        logging.info("send payment notify")
        try:
            ice = Ice.initialize(["--Ice.Config=" + os.environ["BILLING_HOME"] + "/conf/config.client"])
            paymentInternalPrx = Service.PaymentInternalPrx.uncheckedCast(ice.stringToProxy("paymentinternal"))
            req = Service.NotifyPayResultReq(platId=self.platId, msgSeq=self.msgSeq, channelType=self.channelType, orderId=self.orderId, result=Service.ENotifyResult.ResultOk, settleAmount=self.settleAmount, payInfo=self.payInfo, channelOrderId=self.channelOrderId)
            resp = paymentInternalPrx.notifyPayResult(req)
        except Exception, e:
            logging.info(e)
            return -1
        else:
            return 0 if (0 == resp.retCode) else -1

def showStats(sig, frame):
    logging.info("reqlist size %d" % len(g_reqList))
    logging.info("reqmap size %d" % len(g_reqMap))

def quitProcess(sig, frame):
    global g_isQuit
    global g_quitEvent

    g_isQuit = True
    signal.alarm(1)
    #g_quitEvent.set()

def waitQuit():
    global g_quitEvent

    g_quitEvent.wait()

    return 0

def getPassword(data):
    c = CryptoHelper()
    return c.rsa_decrypt(data, CryptoHelper.importKey(const.PRI_KEY))

def getLog():
    logging.info("start handlelog")
    while not g_isQuit:
        try:
            tail = Tail(os.environ["BILLING_HOME"] + "/logs/info.log")
            tail.register_calllback(getLogCallback)
            tail.set_key_string(["PaymentInternal"])
            tail.routine()
        except Exception, e:
            logging.info(e)
            time.sleep(5)
    logging.info("handlelog quit")

def getLogCallback(line):
    r = const.REQ_REGEX.findall(line)
    if len(r) > 0:
        m = r[0]
        if "0" != m[4]: return
        if g_reqMap.has_key(m[0]):
            req = g_reqMap[m[0]]
            req.reqTimes = req.reqTimes + 1
            return
        req = PayNotifyReq(m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7])
        g_reqList.append(req)
        g_reqMap[m[0]] = req
        return

    r = const.RESP_REGEX.findall(line) 
    
    if len(r) <= 0: r = const.RESP1_REGEX.findall(line) 
    if len(r) <= 0: r = const.RESP2_REGEX.findall(line) 
    if len(r) <= 0: return

    if not g_reqMap.has_key(r[0]): return

    req = g_reqMap[r[0]]
    req.reqTimes = req.reqTimes - 1

def handleExceptionOrder(req):
    logging.info("handle order, orderid %s" % req.orderId)
    ret = 0
    status = 0
    time.sleep(1)
    conn = MySQLdb.connect(host=const.DB_IP, user=const.DB_USER, passwd=getPassword(const.DB_PWD),db=const.DB_NAME,port=const.DB_PORT, charset='utf8')
    cur = conn.cursor()
    logging.info("select")
    rows = cur.execute("SELECT status FROM pay_order_ex WHERE orderid = %s", req.orderId)
    if 1 == rows: status = cur.fetchone()[0]
    cur.close()
    conn.close()
    if 1 == rows:
        if 1 == status:
            time.sleep(1)
        if 6 == status: 
            time.sleep(1)
            logging.info("update")
    	    conn = MySQLdb.connect(host=const.DB_IP, user=const.DB_USER, passwd=getPassword(const.DB_PWD),db=const.DB_NAME,port=const.DB_PORT, charset='utf8')
            cur = conn.cursor()
            rows = cur.execute("UPDATE pay_order_ex SET status = 0 WHERE orderid = %s", req.orderId)
            conn.commit()
    	    cur.close()
    	    conn.close()
    else:
        ret = -1

    if (0 == ret and 1 != status):
        ret = req.send()
        time.sleep(5)
        if (False):
	    time.sleep(3)
            i = 0
            while i < 5:
    	        conn = MySQLdb.connect(host=const.DB_IP, user=const.DB_USER, passwd=getPassword(const.DB_PWD),db=const.DB_NAME,port=const.DB_PORT, charset='utf8')
                cur = conn.cursor()
    	    	conn = MySQLdb.connect(host=const.DB_IP, user=const.DB_USER, passwd=getPassword(const.DB_PWD),db=const.DB_NAME,port=const.DB_PORT, charset='utf8')
                rows = cur.execute("SELECT status FROM pay_order_ex WHERE orderid = %s and status = 1", req.orderId)  
    	        cur.close()
    	        conn.close()

                if 1 == rows: break
                i = i + 1
                time.sleep(2)

    return ret;

def findExceptionOrder():
    if 0 == len(g_reqList): return

    ret = 0
    i = 0
    t = time.time()
    while i < len(g_reqList):
        req = g_reqList[i]
        if 0 == req.reqTimes:
            del g_reqList[i]
            del g_reqMap[req.msgSeq]
            continue
        
        if t - req.reqTime > const.CHECK_INTERNAL:
            try:
                logging.info("find exception order, orderid %s" % req.orderId)
                ret = handleExceptionOrder(req)
            except Exception, e:
                print e
                logging.info(e)
            else:
                if 0 == ret:
                    logging.info("handle order success, orderid %s" % req.orderId)
                    del g_reqList[i]
                    del g_reqMap[req.msgSeq]
                    i = i -1
        i = i + 1

def processGuard():
    global g_isQuit

    logging.basicConfig(level = logging.DEBUG,
            format = '%(asctime)s %(levelname)s %(message)s',
            datefmt = '%a, %d %b %Y %H:%M:%S',
            filename = './guard.log',
            filemode = 'a+')
    stdOut = open("./stdout.log", "a+")
    logging.info("start task process")
    taskProcess = subprocess.Popen(sys.argv[0], stdout=stdOut, stderr=stdOut, shell=True)
    while not g_isQuit:
        #rs = timeout(func = waitQuit, timeout = 1800, default = -1)
        time.sleep(1800)
        if not g_isQuit:
            if taskProcess.poll() is not None:            
                logging.info("task process is quit, restart")
                taskProcess = subprocess.Popen(sys.argv[0], stdout=stdOut, stderr=stdOut, shell=True)
            else:
                logging.info(".")
    
    logging.info("guard process quit")

def doHandleTask():
    global g_isQuit

    logging.basicConfig(level = logging.DEBUG,
            format = '%(asctime)s %(levelname)s %(message)s',
            datefmt = '%a, %d %b %Y %H:%M:%S',
            filename = './debug.log',
            filemode = 'a+')
    t = Thread(target=getLog)
    t.setDaemon(True)
    t.start()
    i = 0
    
    logging.info("start findExceptionOrder")
    while not g_isQuit:
        try:
            findExceptionOrder()
        except Exception, e:
            logging.info(e)

        i = i + 1
        time.sleep(const.CHECK_INTERNAL)

        if i > 10:
            i = 0
            logging.info(".")

    logging.info("findExceptionOrder quit")

def main():
    g_quitEvent.clear()
    signal.signal(signal.SIGQUIT, quitProcess)
    signal.signal(signal.SIGUSR1, showStats)

    if len(sys.argv) == 2:
        if sys.argv[1] == "-d":
            subprocess.Popen(sys.argv[0] + " deamon", shell=True)

            return
        elif sys.argv[1] == "deamon":
            processGuard()

            return
    
    doHandleTask() 

if "__main__" == __name__:
    main()
