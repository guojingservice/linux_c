#!/bin/env python
#-*- coding: utf-8 -*-

import re
import os
import sys
import signal
import time
import logging
import subprocess 
from threading import Event
#from enum import Enum

import const 
from timeout import timeout 
from http import HTTPHandler

g_isQuit = False
g_quitEvent = Event()

const.REFUND_STATUS_SUCCESS = "SUCCESS"
const.REFUND_STATUS_FAIL = "FAIL"
const.REFUND_STATUS_NOTSURE = "NOTSURE"
const.REFUND_STATUS_CHANGE = "CHANGE"
const.QUERY_REFUND_URL = "http://dev.iapppay.com:25080/weixin/pay/demo/refundquery.php"
const.REFUND_NOTIFY_URL = "http://172.17.15.250:20140/notify/manualrefund"
const.SUCCESS_DATA_TEMP = 'transdata={"appid":"5000020514","refundno":"%s","notifytime":"%s","succdata":"%s^%s"}'
const.FAIL_DATA_TEMP = 'transdata={"appid":"5000020514","refundno":"%s","notifytime":"%s","faildata":"%s^6001"}'
const.REFUND_STATUS_REGEX = re.compile("refund_status[^\s]*\s+:\s+([^\s]*)\s+", re.I)
const.TOTAL_FEE_REGEX = re.compile("total_fee[^\s]*\s+:\s+([^\s]*)\s+", re.I)

class RefundStatus():
    Process = 0
    Fail = 1
    Success = 2

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

def queryRefundStatus(refund):
    refund["amount"] = "0"
    httpHandler = HTTPHandler()
    res = httpHandler.post(url = const.QUERY_REFUND_URL, data = "out_trade_no=" + refund["orderid"])
    body = res.read()
    m = const.REFUND_STATUS_REGEX.findall(body)
    if len(m) == 0:
        return RefundStatus.Process

    status = m[0]

    if status == const.REFUND_STATUS_SUCCESS:
        refund["amount"] = const.TOTAL_FEE_REGEX.findall(body)[0]
        return RefundStatus.Success
    elif status == const.REFUND_STATUS_FAIL or status == const.REFUND_STATUS_NOTSURE or status == const.REFUND_STATUS_CHANGE:

        return RefundStatus.Fail
    else:
        return RefundStatus.Process

def sendNotify(status, batchNo, transId, amount = None):
    timeStr = time.strftime("%Y-%m-%d %H:%M:%S")
    if RefundStatus.Success == status:
        body = const.SUCCESS_DATA_TEMP % (batchNo, timeStr, transId, amount)
        logging.info("batchno %s  transid %s send success notify" % (batchNo, transId))
    elif RefundStatus.Fail == status:
        body = const.SUCCESS_DATA_TEMP % (batchNo, timeStr, transId)
        logging.info("batchno %s  transid %s send fail notify" % (batchNo, transId))

    httpHandler = HTTPHandler()
    logging.debug("notifydata : %s" % body)
    httpHandler.post(url = const.REFUND_NOTIFY_URL, data = body)

def queryRefund():
    logging.info("queryRefund")
    refund = {}
    refundFile = open("./refunddata", "r+")
    tempFile = open("./tempdata", "w+")
    completeFile = open("./complete", "a+")

    for line in refundFile.readlines():
        tmp = line.strip('\n')
        arr = tmp.split(",")
        refund["orderid"] = arr[2]
        logging.info("query orderid %s" % arr[2])
        status = queryRefundStatus(refund)
        if (RefundStatus.Process == status): 
            tempFile.write(line) 
            continue

        completeFile.write(line) 
        sendNotify(status, arr[0], arr[1], refund["amount"])

    refundFile.close()
    tempFile.close()
    completeFile.close()

    os.system('cp -rf ./tempdata ./refunddata')
    os.system('rm -rf ./tempdata')

def doQueryTask():
    global g_isQuit

    logging.basicConfig(level = logging.DEBUG,
            format = '%(asctime)s %(levelname)s %(message)s',
            datefmt = '%a, %d %b %Y %H:%M:%S',
            filename = './debug.log',
            filemode = 'a+')

    logging.info("start query refund")
    while not g_isQuit:
        queryRefund()
        #timeout(func = waitQuit, timeout = 1800, default = -1)
        logging.info("query finish, sleep...")
        time.sleep(1800)
    logging.info("stop query refund")

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
    
def main():
    g_quitEvent.clear()
    signal.signal(signal.SIGQUIT, quitProcess)

    if len(sys.argv) == 2:
        if sys.argv[1] == "-d":
            subprocess.Popen(sys.argv[0] + " deamon", shell=True)

            return
        elif sys.argv[1] == "deamon":
            processGuard()

            return

    doQueryTask()

if "__main__" == __name__:
    main()
