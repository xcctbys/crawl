#!/usr/bin/env python
#coding=utf8
from django.shortcuts import render
import httplib, urllib
import request
import jsonimport cgi
import logging
import time

"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
"""
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
from Django.http import HttpResponse
from __future__ import unicode_literals
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt





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



""" 'DEBUG = True' 这个 DEBUG 的值改为 false"""
"""django，如果没改过默认设置，在传输post表单的时候是要经过csrf校验的
装饰器@csrf_exempt来装饰view中的函数以避过csrf"""






"""客户端"""
def http_post(values):
    json_data = json.dumps(values)
    try:
        req = urllib2.Request(post_server,json_data)   #生成页面请求的完整数据
        response = urllib2.urlopen(req)    # 发送页面请求
    except urllib2.HTTPError,error:
        print "ERROR: ",error.read()





"""服务端"""
@csrf_exempt
def recv_data(request):
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        return received_json_data
    else:
        print 'abc'


