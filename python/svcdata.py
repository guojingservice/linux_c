
DBInfo = {"host":"192.168.0.168", "port":3306, "user":"pay", "passwd":"paytest", "db":"iapppay"}
CommonInfo = {"PlatId":10000, "BusPlatId":102}
SvcCommonInfo = {"device":100, "os":1, "version":"IAPPPAY_3.4.0_Android", "acid": "999", "country":"CHN", "lang":"CHS", "currency":"RMB"}

import Ice
import MySQLdb
import datetime,os
from crypto import *

class SvcApiBase():
    def __init__(self):
        self.ic = Ice.initialize(["--Ice.Config=" + os.environ["BILLING_HOME"] + "/conf/config.client"])
        #self.ic = Ice.initialize(["--Ice.Config=" + "./conf/config.client"])
        self.index = 0
        self.name = ""
        
    def getMsgSeq(self):
        now = datetime.datetime.now()
        self.index = (self.index + 1) % 1000
        return "%s%04d%02d%02d%02d%02d%02d%03d" %(self.name, now.year, now.month, now.day, now.hour, now.minute, now.second, self.index)


class SvcDatabase():
    def __init__(self):
        self.conn = MySQLdb.connect(host=DBInfo["host"], user=DBInfo["user"],passwd=DBInfo["passwd"],db=DBInfo["db"],port=DBInfo["port"], charset='utf8')
        self.platId = CommonInfo["PlatId"]
        self.busPlatId = CommonInfo["BusPlatId"]
        self.crypto = CryptoHelper()
        
    def __del__(self):
        self.conn.close()
        
    def setId(self, platId, busPlatId):
        self.platId = platId
        self.busPlatId = busPlatId
        
    def clearUser(self, name):
        cur = self.conn.cursor()
        rows = cur.execute("""select userid from user_base 
                        where loginname=%s and platid=%s""", (name, self.platId))
        if 0 == rows:
            # user not exist
            return
        userid = cur.fetchone()[0]        
        cur.execute("""delete from user_attr where userid=%s""", (userid,))
        cur.execute("""delete from user_voucher where userid=%s""", (userid, ))
        cur.execute("""delete from user_base_history where userid=%s""", (userid, ))
        cur.execute("""delete from user_attr_history where userid=%s""", (userid,))
        cur.execute("""delete from user_base where userid=%s""", (userid,))
        cur.execute("""delete from accountinfo where userid=%s""", (userid,))
        cur.execute("""delete from accountinfo_his where userid=%s""", (userid,))
        self.conn.commit()
        cur.close()
        
    def clearSilenceUser(self, terminal):
        cur = self.conn.cursor()
        rows = cur.execute("""select a.userid from user_base a, user_attr b 
                        where b.terminalid=%s and a.platid=%s and a.userid=b.userid""",
                        (terminal, self.platId))
        if 0 == rows:
            # user not exist
            return
        for i in range(0, rows):
            userid = cur.fetchone()[0]        
            cur.execute("""delete from user_attr where userid=%s""", (userid,))
            cur.execute("""delete from user_voucher where userid=%s""", (userid,))
            cur.execute("""delete from user_base_history where userid=%s""", (userid,))
            cur.execute("""delete from user_attr_history where userid=%s""", (userid,))
            cur.execute("""delete from user_base where userid=%s""", (userid,))
            cur.execute("""delete from accountinfo where userid=%s""", (userid,))
            cur.execute("""delete from accountinfo_his where userid=%s""", (userid,))            
            self.conn.commit()
        cur.close()       

    def addUser(self, username, password, amount = None, telUser=False, terminal = None):
        if not amount:
            amount = 0
        userType = 0
        if telUser:
            userType = 1
        
        now = datetime.datetime.now()
        nowstr = "%04d-%02d-%02d %02d:%02d:%02d" %(now.year, now.month, now.day, now.hour, now.minute, now.second)
        cur = self.conn.cursor()
        cur.execute("""insert into user_base(loginname, status, usertype, username, 
            usercheckflag, regtime, regsrc, systemid, platid) 
            values(%s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
            (username, "A", userType, username, 0, nowstr, 3, self.busPlatId, self.platId))
        userid = self.conn.insert_id()
        cur.execute("""insert into user_attr(userid, userpwdmd5, terminalid, pwdtype) 
                values(%s, %s, %s, %s)""", (userid, self.crypto.md5(password), None, 1))
        cur.execute("""INSERT INTO user_base_history(userid, loginname, status, 
        			usertype, grade, username, certtype, idcardno, 
        			usercheckflag, cityid, sex, regtime, regsrc, 
        			systemid, platid, updatetype, updatetime)
				SELECT userid, loginname, status, usertype, grade, username, 
        			certtype, idcardno, usercheckflag, cityid, sex, regtime, 
        			regsrc, systemid, platid, %s, %s
        		FROM user_base where userid=%s""", (0, nowstr, userid))
        cur.execute("""INSERT INTO user_attr_history(userid, userpwdmd5, israndom, 
        			pwdqid, pwdans, paypwdmd5, carrierid, terminalid, pwdtype, 
        			updatetype, updatetime)
        		SELECT userid, userpwdmd5, israndom, pwdqid, pwdans, paypwdmd5, 
        			carrierid, terminalid, pwdtype, %s, %s
                    FROM user_attr WHERE userid=%s""", (0, nowstr, userid))
        cur.execute("""insert into accountinfo(userid, accounttype, balance, status, lastchgtime)
                values(%s, %s, %s, %s, %s)""", (userid, 7, amount, "A", nowstr))
        cur.execute("""INSERT INTO accountinfo_his(opertype, transid, userid, 
	    			accounttype, lastbalance, balance, updatetime)
	    		SELECT %s, %s, userid, accounttype, 
	    			IFNULL(balance,0)-%s, balance, %s
	    		FROM accountinfo
	    		WHERE userid=%s AND accounttype=%s""", (2, userid, amount, userid, 7, nowstr))
        if terminal:
            # create voucher
            voucher = self.crypto.md5("%d|%s|%s" %(userid, terminal, self.crypto.md5(password)))
            cur.exeucte("""REPLACE INTO user_voucher(userid, terminalid, voucher, 
        			createtime) VALUES(%s, %s, %s, now())""", (userid, terminal, voucher))
        self.conn.commit()
        cur.close()
        return userid
        
    def addSilenceUser(self, terminal, amount = None):
        if not amount:
            amount = 0
        userType = 0
        
        now = datetime.datetime.now()
        nowstr = "%04d-%02d-%02d %02d:%02d:%02d" %(now.year, now.month, now.day, now.hour, now.minute, now.second)
        cur = self.conn.cursor()
        cur.execute("""insert into user_base(loginname, status, usertype, username, 
            usercheckflag, regtime, regsrc, systemid, platid) 
            values(%s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
            (None, "W", userType, None, 0, nowstr, 3, self.busPlatId, self.platId))
        userid = self.conn.insert_id()
        cur.execute("""insert into user_attr(userid, userpwdmd5, terminalid, pwdtype)
                values(%s, %s)""", (userid, None, terminal, 0))
        cur.execute("""INSERT INTO user_base_history(userid, loginname, status, 
        			usertype, grade, username, certtype, idcardno, 
        			usercheckflag, cityid, sex, regtime, regsrc, 
        			systemid, platid, updatetype, updatetime)
				SELECT userid, loginname, status, usertype, grade, username, 
        			certtype, idcardno, usercheckflag, cityid, sex, regtime, 
        			regsrc, systemid, platid, %s, %s, 
        		FROM user_base where userid=%s""", (0, nowstr, userid))
        cur.execute("""INSERT INTO user_attr_history(userid, userpwdmd5, israndom, 
        			pwdqid, pwdans, paypwdmd5, carrierid, terminalid, pwdtype, 
        			updatetype, updatetime)
        		SELECT userid, userpwdmd5, israndom, pwdqid, pwdans, paypwdmd5, 
        			carrierid, terminalid, pwdtype, %s, 5s,
                    FROM user_attr WHERE userid=%s""", (0, nowstr, userid))
        cur.execute("""insert into accountinfo(userid, accounttype, balance, status, lastchgtime)
                values(%s, %s, %s, %s, %s)""", (userid, 7, amount, "A", nowstr))
        cur.execute("""INSERT INTO accountinfo_his(opertype, transid, userid, 
	    			accounttype, lastbalance, balance, updatetime)
	    		SELECT %s, %s, userid, accounttype, 
	    			IFNULL(balance,0)-%s, balance, %s
	    		FROM accountinfo
	    		WHERE userid=%s AND accounttype=%s""", (2, userid, amount, userid, 7, nowstr))
        self.conn.commit()
        cur.close()
        return userid
        
    def getAccountInfo(self, userid):
        cur = self.conn.cursor()
        rows = cur.execute("""select paypwd, balance, status, nopwdlimit from accountinfo where userid=%s and accounttype=%s""", (userid, 7))
        if 0 == rows:
            # user not exist
            return 0
        result = cur.fetchone()
        cur.close()
        return {"paypwd":result[0], "balance":int(result[1]), "status":result[2], "nopwdlimit":int(result[3])}
        
    def getUserInfo(self, userid):
        cur = self.conn.cursor()
        rows = cur.execute("""SELECT a.loginname, a.status, a.usertype, a.platid, 
        			b.userpwdmd5, b.terminalid, b.pwdtype
                FROM user_base a, user_attr b 
                WHERE a.userid=%s
                    AND a.userid = b.userid""", (userid, ))
        if 0 == rows:
            # user not exist
            return 0
        result = cur.fetchone()        
        cur.close()
        return {"loginname":result[0], "status":result[1], "usertype":int(result[2]), "platid":int(result[3]),
            "userpwdmd5":result[4], "terminalid":result[5], "pwdtype":int(result[6])}
        
        
    
