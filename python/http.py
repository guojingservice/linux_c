#!/usr/bin/python
# -*- coding: utf-8 -*-  

import sys
import httplib
import urllib
import urllib2
import cookielib

reload(sys)
sys.setdefaultencoding('utf-8')

class HTTPRefererProcessor(urllib2.BaseHandler):
    def __init__(self):
        self.referer = None
    def http_request(self, request):
        if ((self.referer is not None) and
            not request.has_header("Referer")):
            request.add_unredirected_header("Referer", self.referer)
        return request
    def http_response(self, request, response):
        self.referer = response.geturl()
        return response
    https_request = http_request
    https_response = http_response 

class HTTPHandler():
    def __init__(self):
        cookie = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie), HTTPRefererProcessor())
        urllib2.install_opener(self.opener)

    def post(self, url, data, header = {}):
        request = urllib2.Request(
                url     = url,
                headers = header,
                data    = data)

        respone = self.opener.open(request)
        return respone

    def get(self, url, header, params = None):
        if params and (len(params) > 0):
            url += "?%s"
            url =  url % urllib.urlencode(params)
        request = urllib2.Request(
                url     = url,
                headers = header)

        respone = self.opener.open(request)
        return respone
