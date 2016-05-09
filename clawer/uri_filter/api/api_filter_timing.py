#coding=utf-8
#!/usr/bin/env python

import os

import redis

import hashlib
from django.conf import settings

import urlparse

try:
    redis_addr=urlparse.urlparse(settings.REDIS)
    redis_addr='redis://'+redis_addr[1]
    #print redis_addr
except:
    redis_addr = None



class TimingFilter(object):
    def __init__(self, redisdb, expire):

        self.expire = expire
        self.redisdb = redisdb
        #self._rediscontpool(redisdb, host='localhost', port= 6379)
        self._rediscontpool(redisdb)

    def _rediscontpool(self, redisdb):

        self.redisdb = redisdb
        #self.redispool = redis.StrictRedis(host = 'localhost',port=6379,db= redisdb)
        redisdbstr =str(redisdb)
        redis_url = redis_addr+'/'+redisdbstr
        #print redis_url
        self.redisconn = redis.StrictRedis.from_url(redis_url)

    def _md5(self,code):
        m2 = hashlib.md5()
        m2.update(code)

        return m2.hexdigest()


    def add(self, key):
        expire = self.expire
        redispool = self.redisconn

        """
        m = redispool.info()
        info= m.get('used_memory')
        #print info
        """

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

        return filter_list_unique
    else:
        for uri in uri_list:
            if timing_filter.add(uri) == True:
                pass
            else:
                filter_list_unique.append(uri)

        return  filter_list_unique






if __name__ == "__main__":

    uri_list = ['张','赵四','李','王','王二','赵','赵四','','',' ','w',' ','fafasfsfsf','fafsf2','ffa','2ee','2fddsf','ff']
    dingshilist = timing_filter_api('uri_generator',uri_list,200000)
    print "定时去重后"
    print  dingshilist





