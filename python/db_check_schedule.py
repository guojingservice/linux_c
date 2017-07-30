#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys, os
binpath = os.path.abspath(sys.argv[0])
bindir = os.path.dirname(binpath)
os.chdir(bindir)

import datetime,time,fnmatch
import logging
import logging.config
import re
import MySQLdb
import sys,os
import const

sys.path.append(os.path.join(os.environ["ICE_HOME"], "python"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "python"))


import Service
import Ice
from crypto import CryptoHelper



const.DB_IP = "172.17.16.55"
const.DB_PORT = 23306
const.DB_USER = "zyzxpay"
const.DB_PWD = "lVAdqFuhADvpZsYdfp1aGtY3PbtLxuHHJxxXnicHF5n1ZcmCGiSLfDhnLxr1MdsJXfma0cgs/ge+LDS3n/ngPa9kOp0b3yVITu68gyognL6zeIrWXcL6BR08OLV3V/y2DYTUzWRERvaK6HIiauq8R+H6nLXApoHGE/Ji+HsWaOA="
const.DB_NAME = "zyzxpay"
const.KEY_LOG = "the same req is processing, orderid"
const.PRI_KEY = "MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBALurXuTqXGZYw46w6wIru2Re4EWFl7fz33xcloZT0GZ2kG4UyywKddUlV6GDXgrCWo51zJpo55qSrAYZ1kE0DTr+QIjyZxNKrA7vyE8JIa+rMEv2WUQZenqxUMfkUCWtQeugDp150XdRPCHe2qmis0GFFKLiBXgZrYolC4iqyhghAgMBAAECgYBETIL1lqFYEhfhl1t/58CEL885HfxwUw3TqbKSYnBmyeGYXnLurUPi9Xsl6bRRABiK3i4/R8x6QcTfV4nVIwdo//st5o3gB4x2OwxrtSM6zs15Dj3xLij4Ryi9B+Ad71kiuRknoGsIF+l5awo8Q5WCNShDo1O8lIsA6tPdrRiHbQJBAOoAdTNISNakp/i4DnWJqDzjduoW7yaezzzLStRSVYgUxn4DPx7s18KCyLoTFG6sNvZpVT6bC+aj76Xu5j1HnL8CQQDNT935v3vLiEID/Xi6KMdoB2OnUrpQGL+OqCexpOaCKH8sEhRwezz7xK3Vqwzp59+8KZ1vITj3YCQkaDPHUCMfAkBbCpaOvz7nk+RuVl35yPcVyYIIjae6JOuIQaf5d5cjfMHFYUn7pDZFzVB/ZND8RjCUKmMqGnTE5V9l9c7KZMRNAkACc/TT+gyxltQrFgkuODSBsqznH97n/BO10Z5/ydeTMIascR7bZS2KWIQ3LE8AMGwE5H5kCIKUugpUgQY1WGjDAkBOT8jiPcs0INUYkvGjYo9954q4WRNDnFxHagimP38IXea+nY6AnFfW/H61xL2zTC03dRVuOwRQOxPlQUW33QuA"
const.PUB_KEY = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC7q17k6lxmWMOOsOsCK7tkXuBFhZe38998XJaGU9BmdpBuFMssCnXVJVehg14KwlqOdcyaaOeakqwGGdZBNA06/kCI8mcTSqwO78hPCSGvqzBL9llEGXp6sVDH5FAlrUHroA6dedF3UTwh3tqporNBhRSi4gV4Ga2KJQuIqsoYIQIDAQAB"


class NotifyorderHandler:
    def __init__(self, monitor_dir = None):
        self.monitor_dir = monitor_dir        
        self.interval = 300
        self.index = 1
        self.name = "dbcheck"
        self.last_check_time = None
        self.last_checkpoint_time = None
        self.checkpoint_time = None
        self.last_load_checktime = None  #上次从数据库载入orderid的截止时间
        self.time_format = "%Y-%m-%d %X"
        self.match_rules = re.compile("^\[ERROR\|([^|]*)\|[^|]*\|[^|]*\|[^|]*\|([^\]]*)\]:the same req is processing, orderid ([0-9]*)", re.I)
        self.log_time_rules = re.compile("^\[[^|]*\|([^.]*)\.[^|]*\|.*", re.I)
        self.next_ids = []
        self.idmaps = {}
    
    def __pushids(ids=[]):
        for id in ids:
            self.idmaps[id] = 1 
       
    def __get_passwd(self, data):
        c = CryptoHelper()
        return c.rsa_decrypt(data, CryptoHelper.importKey(const.PRI_KEY)) 
        
    def __get_handle_files(self, now):
        last = now - self.interval
        now_time = datetime.datetime.fromtimestamp(now)
        
        files = []
        file_to_mktime = {}
        for file in os.listdir(self.monitor_dir):
            if fnmatch.fnmatch(file, 'debug.log') \
            or fnmatch.fnmatch(file, 'debug.%04d-%02d-%02d-%02d.*.log' %(now_time.year, now_time.month, now_time.day, now_time.hour)) \
            or fnmatch.fnmatch(file, 'debug.%04d-%02d-%02d-%02d.*.log' %(now_time.year, now_time.month, now_time.day, now_time.hour-1)):
                full_file = os.path.join(self.monitor_dir, file)
                file_mktime = str(os.stat(full_file).st_mtime)
                file_mktime_int = os.stat(full_file).st_mtime
                if not self.last_checkpoint_time and file_mktime_int < self.last_checkpoint_time:
                    logger.info("file:%s already checked, just skip!"%file)
                else:
                    file_to_mktime[full_file] = file_mktime
        sorted_file_to_mktime = sorted(file_to_mktime.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        limit_count = 3
        start_count = 0
        for key, value in sorted_file_to_mktime:
            if start_count >= limit_count:
                break
            files.append(key)
            start_count = start_count +1
        return files
        
    def __handle_files(self, files):
        orderIds = []
        orderIdMap = {}
        for file in files:
            logger.info("handling file[%s]..." % file) 
            with open(file) as file_:
                while True:
                    line = file_.readline()
                    if line == "":
                        break;
                    line = line.strip()
                    #logger.info("handler line:%s"%line)
                    #只处理包含 该关键字的
                    if line.find(const.KEY_LOG) != -1:
                        logger.info("match line:%s" % line)
                        r_times = self.log_time_rules.findall(line)
                        if len(r_times) != 1:
                            logger.error("regex log time failed! input:[%s]" % line)
                            continue
                        log_time_str = r_times[0]
                        log_time_unix = time.mktime(time.strptime(log_time_str, "%Y-%m-%d %H:%M:%S"))
                        if(log_time_unix > self.checkpoint_time):
                            logger.info("reach to checkpoint time, checkpointtime:[%s], logtime:[%s], skip the rest of the file..."%
                                            (str(self.checkpoint_time), str(log_time_unix)))
                            break;
                        #save the orderid to orderIds
                        r_infos = self.match_rules.findall(line)
                        if len(r_infos) != 1:
                            logger.error("regex matched unexpected result. input :[%s]"%line)
                            continue
                        l_infos = r_infos[0]
                        orderId = l_infos[2]
                        if orderId not in orderIdMap.keys():    
                            orderIds.append(orderId)
                            orderIdMap[orderId] = 1                                              
        return orderIds

    def __get_msg_seq(self):
        now = datetime.datetime.now()
        self.index = (self.index + 1) % 1000
        return "%s%04d%02d%02d%02d%02d%02d%03d" %(self.name, now.year, now.month, now.day, now.hour, now.minute, now.second, self.index)

    def __handler_ice_orderquery(self, orderId):
        logger.info("begin order query, orderId:[%s]" % orderId)
        ic = Ice.initialize(["--Ice.Config=" + os.environ["BILLING_HOME"] + "/conf/config.client"])
        payment_prx = Service.PaymentPrx.uncheckedCast(ic.stringToProxy("payment"))
        req = Service.QueryPayOrderReq(10025, 101, 0, self.__get_msg_seq(), orderId = orderId)
        resp = payment_prx.queryPayOrder(req)
        if resp and resp.retCode == 0:
            logger.info("query order:[%s] success"%orderId)
        else:
            logger.error("query order:[%s] failed!" % orderId)
        #logger.info("query result:[%s]" % str(resp))
    
    def __handler_orderIds(self, orderIds):
        if len(orderIds) <= 0:
            return None
        for orderId in orderIds:
            logger.info("begin handle orderid:[%s]"%orderId)
            status = -1
            conn = MySQLdb.connect(host=const.DB_IP, user=const.DB_USER, passwd=self.__get_passwd(const.DB_PWD),db=const.DB_NAME,port=const.DB_PORT, charset='utf8')
            cur = conn.cursor()
            logger.info("select") 
            rows = cur.execute("SELECT `status` from pay_order_ex WHERE orderid = %s", orderId)
            if 1 == rows: status = cur.fetchone()
            cur.close()
            conn.close()
            if status == -1:
                logger.error("select failed! orderId:[%s]" % orderId)
                continue
            if status == 6:
                logger.info("order[%s] status callback,change to 0"%orderId)
                conn = MySQLdb.connect(host=const.DB_IP, user=const.DB_USER, passwd=self.__get_passwd(const.DB_PWD),db=const.DB_NAME,port=const.DB_PORT, charset='utf8')
                cur = conn.cursor()
                rows = cur.execute("UPDATE pay_order_ex SET `status` = 0 WHERE orderid = %s", orderId)        
                conn.commit()
                cur.close()
                conn.close() 
            self.__handler_ice_orderquery(orderId)  
    
    def preHandle(orderIds):
        self.next_ids.extend(orderIds)
    
    def handleOrder():
        if len(self.next_ids) <= 0:
            logger.info("none orderid needed handle, wait next try...")
        self.__handler_orderIds(orderIds)         

    def routine(self, check_time=None):
        #处理上次load出来的订单号
        self.handleOrder()
        if not check_time:
            check_time = time.time()
        else:
            check_time = time.mktime(time.strptime(check_time, '%Y-%m-%d %H:%M'))
        #设置检查点，任何超过这个时间点的日志都不会处理,即使发生切日志
        self.checkpoint_time = time.time()
        handle_files = self.__get_handle_files(check_time)
        logger.info("prepare to handle [%s]..." %(str(handle_files)))
        orderIds = self.__handle_files(handle_files)
        logger.info("collected orderIds:[%s]" % str(orderIds))
        if(len(orderIds) <= 0):
            logger.info("none orderid collected, wait next try...")
        else:
            self.__handler_orderIds(orderIds)
   
    def handleOrderId(self, orderId):
        logger.info("begin handle orderid:[%s]" % orderId)
        conn = MySQLdb.connect(host=const.DB_IP, user=const.DB_USER, passwd=self.__get_passwd(const.DB_PWD),db=const.DB_NAME,port=const.DB_PORT, charset='utf8')
        status = -1
        cur = conn.cursor()
        rows = cur.execute("SELECT `status` from pay_order_ex WHERE orderid = %s", orderId)
        if 1 == rows: status = cur.fetchone()
        cur.close()
        conn.close()
        if status == -1:
            logger.error("select failed. orderId:[%s]" % orderId)
        elif status == 6:
            logger.info("orderid:[%s] need handle, change status to 0" % orderId)
            conn = MySQLdb.connect(host=const.DB_IP, user=const.DB_USER, passwd=self.__get_passwd(const.DB_PWD),db=const.DB_NAME,port=const.DB_PORT, charset='utf8')
            cur = conn.cursor()
            rows = cur.execute("UPDATE pay_order_ex SET `status` = 0 WHERE orderid = %s", orderId)
            conn.commit()
            cur.close()
            conn.close()
            self.__handler_ice_orderquery(orderId) 
        else:
            logger.info("orderid:[%s] become nomal. skip operation." % orderId)
 
    def handleLastOrders(self):
        if(len(self.idmaps) <= 0):
            logger.info("idmaps is empty.skip this round.")
        else:
            for orderid in self.idmaps.keys():
                logger.info("prepare to handle orderid:[%s]..." % orderid)
                self.handleOrderId(orderid)
            self.idmaps = {} 
    
    def routine_db(self, check_time=None):
        #处理上次load出来的订单号
        self.handleLastOrders()  
        ids = self.loadOrderIdFromDb()
        if(len(ids) <= 0):
            logger.info("not detect orderids skip...")
        else:
            self.__pushids(ids) 
         
        
    def loadOrderIdFromDb(self):
        logger.info("Begin to load orderid from db...")
        ids = []
        startTime = None
        if not self.last_load_checktime:
            now = datetime.datetime.now()
            startTime = ("%04d-%02d-%02d %02d:%02d:%02d"%(now.year, now.month, now.day,now.hour, 0,0))
        else:
            startTime = time.strftime(self.time_format, time.localtime(self.last_load_checktime))
        nowUnix = time.time()
        endTime = time.strftime(self.time_format, time.localtime(nowUnix))
        logger.info("starttime:[%s], endtime:[%s]" % (startTime, endTime))
        conn = MySQLdb.connect(host=const.DB_IP, user=const.DB_USER, passwd=self.__get_passwd(const.DB_PWD),db=const.DB_NAME,port=const.DB_PORT, charset='utf8')
        cur = conn.cursor()
        rows = cur.execute("select orderid from pay_order_ex where paytime > \"%s\" and paytime < \"%s\" and `status` = 6"
                        % (startTime, endTime))
        if(rows > 0):
            results = cur.fetchall()
            for info in result:
                ids.append(str(info))
        cur.close()
        conn.close()
        #print ("rows:[%d]" % rows)
        return ids
             

    def run(self, check_time = None):
        logger.info("Beginging to run the redo py...")
        logger.info("file checking will happen every %s seconds" % str(self.interval))
        while True:
            try:
                self.routine(check_time)
            except Exception, e:
                logger.info("exception occured :[%s]" % str(e))
            time.sleep(self.interval)
    
    def run_db(self):
        logger.info("Begining to run the db check py...")
        logger.info("check will be run over every %s seconds" % str(self.interval))
        while True:
            try:
                self.routine_db()
            except Exception, e:
                logger.info("exception occured:[%s]" % str(e))
            time.sleep(self.interval)

if __name__=='__main__':
    logging.config.fileConfig("logging_redo.conf")
    logger = logging.getLogger("redo")
    handler = NotifyorderHandler()
    check_time = None
    if len(sys.argv) > 2:
        check_time = sys.argv[2]    
    handler.run_db()
        


