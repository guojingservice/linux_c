#!/bin/env python
#-*- coding: utf-8 -*- 

import urllib
import urllib
import rsa
import json
import base64
import hashlib
import time
import xml.etree.ElementTree as ET
from time import clock_gettime


def http_get(url):
    with urllib.request.urlopen(url) as f:
#         open('resp.html', 'w').write(f.read().decode(encoding='utf_8')) 
        print(f.read().decode(encoding='utf_8'))
        print(f.status)
        print(f.reason)
                
        
def http_post(url, data):
    req = urllib.request.Request(url, data = data.encode(encoding='utf_8', errors='strict'), method='POST')
    with urllib.request.urlopen(req, ) as f:
            resp = f.read().decode(encoding='utf_8')
#        print(f.read().decode(encoding='utf_8'))
#        open('resp.html', 'w').write(f.read().decode(encoding='utf_8'))  
#         print(f.read(300).decode(encoding='gb2312'))
    print(f.status)
    print(f.reason)
    return resp

def genId(key):
    return key + '-' + time.strftime("%Y%m%d%H%M%S", time.localtime())

def getCurrTime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

 
def getPrivKey():
    keyfile = '''-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCoD+TnPKH1ma6z20YNbUSOfyeAf+0YQNOaC+gwcojHEgZjzSSZ
W5k99OdQYRh5FfDw1rq0YRIIZ/PEEu1+OelJJ3NZCAvgE7iumuDh78G2kLbT6G/r
d7eX1eXPWkUKbxXczgIuz1Tm305f3CdhRz2RrTjggiChlqeIrUE+hsMTwwIDAQAB
AoGAMHrNRCsIaUmYzMcvEQZ5JUXmxjmg0kM5BxHyO69+ZzZ642U07owuy2GPLG+l
2KAMrdyzZP8vbX9XITN4kNXxxjGapBRNHa/GU4Hap8X452e7muiCKLAVDoCpUMJn
pTRR73OCd9Web5hbmvtpscMzF/QsUnpWyNlhJL87YivZHmkCQQDcIy6Q0Q64dvNv
H7Eo9hVuYWvljJxUEvL900vDJJdPSZIqKUQY92ZUivdRT0S/cDvpwZTvWKU8GFRr
dRjX7jkPAkEAw3DpyveSSDsefpy6hk1Z0QftZHdeOJhanStzmgvU2leitQvGDfzo
kd6tFrDFdfTcOddSapY39fJrkYp6wqbyDQJBAIz/G7w1qrALwC/UpKwPsfpY+7qz
LQ3MdUaOJ2B990wZWz0V4T/8ddaAi5fQpb/YKwe1rab/qBWtn6SUA62KL5ECQGMe
4xPTV9dWVHL2Xgs7M7A2CwoHGDwv2NUZcnnQQlWyWIzlub7iY7mHa9W0NZFLbF3R
fLUeFqegGTopN3V9YgkCQG1GyZJ2ZFmkgHFnj9O9bhyDAJNcdr+4TeQe+OPk8IBE
OF2+2KqEcJfs4eUnAZaiQteDkxmxYpa5NTrIwdeHw48=
-----END RSA PRIVATE KEY-----'''.encode(encoding='utf_8', errors='strict')
    return rsa.PrivateKey.load_pkcs1(keyfile)  

def getAppId():
    return '500000185'

def getUrl():
    return 'http://192.168.114.5:8080'



def apiQuery(cpOrderId):
    print('apiQuery...')
    transdata = {
    'appid' : getAppId(),
    'cporderid' : cpOrderId
    }
    
    transdata_str = json.dumps(transdata)
    print(transdata_str)
#     transdata_str = '{"appid": "500000185","cporderid": "9000011111166_81"}'
    privKey = getPrivKey() 
    transdata_utf8 =  transdata_str.encode()
    signCode = rsa.sign(transdata_utf8, privKey, 'MD5')
    signCode_bs64 = base64.standard_b64encode(signCode)
    sign = signCode_bs64.decode()
#     print('signature:', sign)
    
    data = {
    'transdata' : transdata_str,
    'sign' : sign,
    'signtype' : 'RSA',
    }
    
    urlencodeCode = urllib.parse.urlencode(data)
    
    print('urlencodeCode:',  urllib.parse.unquote(urlencodeCode))
    print('urlencodeCode:',  urlencodeCode)
    print("-----------------------------")
#     resp = http_post('http://192.168.114.5:8080/api/queryresult', urlencodeCode) http://192.168.1.240:50024/api/order
#    resp = http_post('http://192.168.1.240:50024/api/queryresult', urlencodeCode)
    resp = http_post(getUrl() + '/api/queryresult', urlencodeCode)
    print('resp:', urllib.parse.unquote(resp))
    



def apiRefund(cporderid):
    print('apiRefund...')
   
    refundNo = genId('apiRefund')
    transdata = {
    'appid' : getAppId(),
    'refundno' : refundNo,
    'cporderid' : cporderid,
    'refundtime' : getCurrTime(),   
    'refundmoney' : 0.01,
    'refundreason' : 'aiptest',
    'notifyurl' : 'http://192.168.0.159:25015',
    }    
    transdata_str = json.dumps(transdata)
    print(transdata_str)

    privKey = getPrivKey() 
    transdata_utf8 =  transdata_str.encode()
    signCode = rsa.sign(transdata_utf8, privKey, 'MD5')
    signCode_bs64 = base64.standard_b64encode(signCode)
    sign = signCode_bs64.decode()
#     print('signature:', sign)
    
    data = {
    'transdata' : transdata_str,
    'sign' : sign,
    'signtype' : 'RSA',
    }
    
    urlencodeCode = urllib.parse.urlencode(data)
    
    print('urlencodeCode:',  urllib.parse.unquote_plus(urlencodeCode))
#     print('urlencodeCode:',  urlencodeCode)
    print("-----------------------------")
#     resp = http_post('http://192.168.114.5:8080/api/queryresult', urlencodeCode) http://192.168.1.240:50024/api/order
#    resp = http_post('http://192.168.1.240:50024/api/queryresult', urlencodeCode)
    resp = http_post(getUrl() + '/api/refund', urlencodeCode)
    print('resp:', urllib.parse.unquote_plus(resp))
    return refundNo





def cpSign():
    print('cpSign...')
    transdata_str = '''{"appid":"301017535","refundno":"20170255457","refundtime":"2017-05-25 17:04:40","refunddata":"2017052384335^取消订单^1.00","notifyurl":"http://app.iot.vpshop.net/notifies"}'''
    print(transdata_str)

    privKey = getPrivKey() 
    transdata_utf8 =  transdata_str.encode()
    signCode = rsa.sign(transdata_utf8, privKey, 'MD5')
    signCode_bs64 = base64.standard_b64encode(signCode)
    sign = signCode_bs64.decode()
    print('signature:', sign)
    
    data = {
    'transdata' : transdata_str,
    'sign' : sign,
    'signtype' : 'RSA',
    }
    

if __name__ == '__main__':
#    cpRoyalty(cporderId='1495619870531')
#     cpRefund()
#     queryCpRefund()
    
#     cpOrderId = apiOrder()
#     print(cpOrderId) # 32011703071418340004


#     apiQuery('9000011111166_94') #32011703071415430003
    
    
#     refundNo = apiRefund('9000011111166_89')
#     print(refundNo)
     
#     apiQueryRefund("apiRefund-20170306225702")
    cpSign()   
    
    
    
    
    
    
    
    
    
