#!/usr/bin/env python
#coding=utf8
from django.shortcuts import render
import httplib, urllib
import request
import json
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
"""
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import cgi
import logging
import time
from Django.http import HttpResponse

PORT_NUMBER = 8080
RES_FILE_DIR = "."

class myHandler(BaseHTTPRequestHandler):

  def doPost(self):
    logging.warning(self.headers)
    form = cgi.FieldStorage(
      fp=self.rfile,
      headers=self.headers,
      environ={'REQUEST_METHOD':'POST',
          'CONTENT_TYPE':self.headers['Content-Type'],
          })
"""
    input =self.rfile.read()
    datas =self.rfile.read(int(self.headers['content-length']))

    response = urllib2.urlopen(url).read()
    response = json.loads(response)
    test = response["test"]


    path_name = '%s/%s.log' % (RES_FILE_DIR,file_name)
    fwrite = open(path_name,'a')

    fwrite.write("name=%s\n" % form.getvalue("name",""))
    fwrite.write("addr=%s\n" % form.getvalue("addr",""))
    fwrite.close()

    #if  request.method == 'POST'
        req = simplejson.loads(request.raw_post_data)
        username = req['username']
        datas = req['datas']
    #return HttpResponse(json.dumps(response_data), content_type='application/json')

    self.send_response(200)
    self.end_headers()
    self.wfile.write("Thanks for you post")
"""

try:
  server = HTTPServer(('', PORT_NUMBER), myHandler)
  print 'Started httpserver on port ' , PORT_NUMBER

  server.serve_forever()

except KeyboardInterrupt:
  print '^C received, shutting down the web server'
  server.socket.close()




def sendPost(uri_list):
    httpClient = None
    try:
        encoded_json_list = json.dumps(uri_list)
        #headers = {"Content-type": "application/x-www-form-urlencoded"
              , "Accept": "text/plain"}
        #  "multipart/form-data"
        headers = {"Content-type": "application/json"
              , "Accept": "text/json"}
        httpClient = httplib.HTTPConnection("localhost", 8080, timeout=30)
        httpClient.request("POST", "/test0.html", encoded_json_list, headers)
        response = httpClient.getresponse()
        print response.status
        print response.reason
        print response.read()
        print response.getheaders() #获取头信息
    except Exception, e:
        print e
    finally:
        if httpClient:
            httpClient.close()