# encoding=utf-8
""" example is http://gsxt.saic.gov.cn/
"""


import urllib
import json
import sys
import logging
import unittest
import requests
import os
import cPickle as pickle

import urlparse
import pwd
import traceback
import datetime
import MySQLdb
import redis


HOST = 'csciwlpc.mysql.rds.aliyuncs.com'                                           # 全局变量设置MySQL的HOST USER等
USER = 'plkj'
PASSWD = 'Password2016'
PORT = 3306
MYSQL_DB = 'csciwlpc'
STEP = 1                                                                           # 每个step取10个
ROWS = 10

REDIS_HOST = '13153c2b13894978.m.cnsza.kvstore.aliyuncs.com'                       # 全局变量，设置Redis的HOST，USER,TABLE
REDIS_PORT = 6379
REDIS_DB = 1
REDIS_USER = ""
REDIS_PWD = "Password123"
REDIS_TABLE = 'history_enterprise'

DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


class History(object):                                                             # 实现程序的可持续性，每次运行时读取上次

    def __init__(self):
        # self.company_num = 0                                                     # 初始化pickle中用作公司名称位置索引值
        self.total_page = 0
        self.current_page = 0

    def load(self):                                                                # redis记录的载入
        r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_USER+':'+REDIS_PWD)
        if not r.hgetall(REDIS_TABLE):
            return
        r_dict = r.hgetall(REDIS_TABLE)
        self.total_page = int(r_dict.get("total_page"))
        self.current_page = int(r_dict.get("current_page"))

    def save(self):
        r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_USER+':'+REDIS_PWD)
        r.hset(REDIS_TABLE, 'total_page', self.total_page)
        r.hset(REDIS_TABLE, 'current_page', self.current_page)
        #print r.hgetall(REDIS_TABLE)

choices = (
        u"安徽",
        u"北京",
        u"重庆",
        u"福建",
        u"甘肃",
        u"广东",
        u"广西",
        u"贵州",
        u"海南",
        u"河北",
        u"黑龙江",
        u"河南",
        u"湖北",
        u"湖南",
        u"江苏",
        u"江西",
        u"吉林",
        u"辽宁",
        u"内蒙古",
        u"宁夏",
        u"青海",
        u"陕西",
        u"山东",
        u"上海",
        u"山西",
        u"四川",
        u"天津",
        u"新疆",
        u"云南",
        u'浙江',
        u"总局",
        u"西藏",
    )

class Generator(object):
    def __init__(self):
        """
        source_url: http://clawer.princetechs.com/enterprise/api/get/all/?page=1&rows=10&sort=id&order=asc
        """
        # self.source_url = "http://clawer.princetechs.com/enterprise/api/get/all/"
        self.step = STEP
        self.history = History()
        self.history.load()
        self.enterprise_urls = []

    def obtain_enterprises(self):
        if self.history.current_page <= 0 and self.history.total_page <= 0:
            self._load_total_page()


        for _ in range(0, self.step):
            r = self.paginate(self.history.current_page)
            self.history.current_page += 1
            self.history.save()
            for item in r['rows']:
                self.enterprise_urls.append(self._pack_enterprise_url(item))

            if self.history.current_page >= self.history.total_page:
                self.history.current_page = 0
                self.history.total_page = 0
                break
        self.history.save()

    def _load_total_page(self,rows=ROWS):
        conn = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=MYSQL_DB, port=PORT, charset='utf8')
        sql = "select count(*) from enterprise_enterprise"
        cur = conn.cursor()
        count = cur.execute(sql)
        total_rows = cur.fetchone()[0]
        total_page = total_rows / rows
        self.history.current_page = 0
        self.history.total_page = total_page
        self.history.save()


    def _pack_enterprise_url(self, row):
        return u"enterprise://localhost/%s/%s/%s/" % (choices[row['province']-1], row['name'], row['register_no'])

    def paginate(self, current_page, rows=ROWS):
        conn = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=MYSQL_DB, port=PORT,charset='utf8')
        sql = "select count(*) from enterprise_enterprise"
        cur = conn.cursor()
        count = cur.execute(sql)
        total_rows =cur.fetchone()[0]
        total_page = total_rows/rows
        if current_page  > total_page:
            current_page = 0
        sql = "select * from enterprise_enterprise limit %d, %d"%(current_page*rows, rows)
        count = cur.execute(sql)

        columns = [desc[0] for desc in cur.description]
        result = []
        for r in cur.fetchall():
            # for v in r:
                # print str(v.encode('utf-8'))
            result.append(dict(zip(columns, r)))

        conn.close()

        return  {'rows': result, 'total_page':total_page, 'current_page': current_page, 'total_rows': total_rows}



class GeneratorTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_obtain_enterprise(self):
        self.generator = Generator()
        self.generator.obtain_enterprises()
        self.assertGreater(len(self.generator.enterprise_urls), 0)



if __name__ == "__main__":
    if DEBUG:
        unittest.main()

    generator = Generator()
    generator.obtain_enterprises()
    for uri in generator.enterprise_urls:
        print json.dumps({"uri":uri})
