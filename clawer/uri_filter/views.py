#!/usr/bin/env python
#coding=utf8
from django.shortcuts import render
import httplib, urllib

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

PORT_NUMBER = 8080
RES_FILE_DIR = "."

class myHandler(BaseHTTPRequestHandler):
  def do_POST(self):
    logging.warning(self.headers)
    form = cgi.FieldStorage(
      fp=self.rfile,
      headers=self.headers,
      environ={'REQUEST_METHOD':'POST',
          'CONTENT_TYPE':self.headers['Content-Type'],
          })

    file_name = self.get_data_string()
    path_name = '%s/%s.log' % (RES_FILE_DIR,file_name)
    fwrite = open(path_name,'a')

    fwrite.write("name=%s\n" % form.getvalue("name",""))
    fwrite.write("addr=%s\n" % form.getvalue("addr",""))
    fwrite.close()

    self.send_response(200)
    self.end_headers()
    self.wfile.write("Thanks for you post")

  def get_data_string(self):
    now = time.time()
    clock_now = time.localtime(now)
    cur_time = list(clock_now)
    date_string = "%d-%d-%d-%d-%d-%d" % (cur_time[0],
        cur_time[1],cur_time[2],cur_time[3],cur_time[4],cur_time[5])
    return date_string
try:
  server = HTTPServer(('', PORT_NUMBER), myHandler)
  print 'Started httpserver on port ' , PORT_NUMBER

  server.serve_forever()

except KeyboardInterrupt:
  print '^C received, shutting down the web server'
  server.socket.close()






def send_POST():
    httpClient = None
    try:
        params = urllib.urlencode({'name': 'Maximus', 'addr': "GZ"})
        headers = {"Content-type": "application/x-www-form-urlencoded"
              , "Accept": "text/plain"}

        httpClient = httplib.HTTPConnection("localhost", 8080, timeout=30)
        httpClient.request("POST", "/test0.html", params, headers)
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