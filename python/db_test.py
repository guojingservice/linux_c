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



const.DB_IP = "192.168.0.168"
const.DB_PORT = 3306
const.DB_USER = "pay"
const.DB_PWD = "paytest"
const.DB_NAME = "iapppay"


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
    
    def db_test(self):
        conn = MySQLdb.connect(host=const.DB_IP, user=const.DB_USER, passwd=const.DB_PWD,db=const.DB_NAME,port=const.DB_PORT, charset='utf8')
        cur = conn.cursor()
        startTime = "2017-06-01 00:00:00"
        endTime = "2017-07-05 00:00:00"
        ids = []
        rows = cur.execute("select orderid from pay_order_ex where paytime > \"%s\" and paytime < \"%s\" and `status` = 6"
                        % (startTime, endTime))
        if(rows > 0):
            results = cur.fetchall()
            for info in results:
                ids.append(str(info))
                print info[0]
        print rows
        cur.close()
        conn.close()
        

if __name__=='__main__':
    handler = NotifyorderHandler()
    handler.db_test()
        


