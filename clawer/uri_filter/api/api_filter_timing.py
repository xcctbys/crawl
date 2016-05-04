#coding=utf-8
#!/usr/bin/env python

import os
import json
import hashlib
import datetime
import sys
import time
import redis

import hashlib

class TimingFilter(object):
    def __init__(self, redisdb, expire):
        print redisdb
        print '######redis db###'
        self.expire = expire
        self.redisdb = redisdb
        self._rediscontpool(redisdb, host='localhost', port= 6379)

    def _rediscontpool(self, redisdb, host, port):
        pool = redis.Redis(host, port, redisdb)
        self.redisdb = redisdb
        self.redispool = redis.StrictRedis(host = 'localhost',port=6379,db= redisdb)

    def _md5(self,code):
        m2 = hashlib.md5()
        m2.update(code)
        print m2.hexdigest()
        return m2.hexdigest()


    def add(self, key):
        expire = self.expire
        redispool = self.redispool
        print redispool
        print "-------redispool----"

        m = redispool.info()
        info= m.get('used_memory')
        print info
        print "--------memory-------"

        md5str = self._md5(key)
        expire = self.expire

        flag = redispool.get(md5str)
        if flag:
            return True
        else:
            redispool.set(md5str,1)
            redispool.expire(md5str, expire)
            return False



def timing_filter_api(filter_type, uri_list =[], duration =20):

    if filter_type == 'uri_generator':
        redisdb = 1
        tablename = 'uri_generator'
    elif filter_type == 'uri_parse':
        redisdb = 2
        tablename = 'uri_parse'

    elif filter_type == 'ip':
        redisdb = 3
        tablename = 'ip'
    else :
        redisdb = 4
        tablename = filter_type

    #expire = duration*60*60
    #小时和秒
    expire = duration

    timing_filter = TimingFilter(redisdb, expire)

    filter_list_unique = []

    if uri_list == []:
        print "#####定时去重后###"
        print  filter_list_unique
        return filter_list_unique
    else:
        for uri in uri_list:
            if timing_filter.add(uri) == True:
                pass
            else:
                filter_list_unique.append(uri)

        print "定时去重后  ############"
        print filter_list_unique
        return  filter_list_unique






if __name__ == "__main__":
    # import doctest
    # doctest.testmod()
    #uri_list = ['wwww.baidu.com','wwww.baidu.com','wwww.princetechs.com','wwww.hao.com','wwww.clawr.com']
    uri_list = ['张','赵四','李','王','王二','赵','赵四','','',' ','w',' ','fafasfsfsf','fafsf2']
    dingshilist = timing_filter_api('uri_generator',uri_list,20)
    print "定时去重后"
    print  dingshilist





