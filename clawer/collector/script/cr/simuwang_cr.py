# encoding=utf-8

import logging
import re
import json
import urllib
import unittest
import traceback
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle
from bs4 import BeautifulSoup
import requests
import MySQLdb
import redis

import datetime
import gevent
from gevent import Greenlet                                                        # 如果要达到异步的效果，要添加这个猴子补丁
import gevent.monkey
gevent.monkey.patch_socket()

requests.packages.urllib3.disable_warnings()


'''MySQL，Redis参数设置'''

HOST = '10.0.1.3'                                                                  # 全局变量设置MySQL的HOST USER等
USER = 'cacti'
PASSWD = 'cacti'
PORT = 3306
MYSQL_DB = 'clawer'
STEP = 1                                                                           # 每个step取10个
ROWS = 10

REDIS_HOST = '10.0.0.3'                                                            # 全局变量，设置Redis的HOST，USER,TABLE
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_TABLE = 'simuwang'

DEBUG = False                                                                      # 是否开启DEBUG,True/False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")

'''主程序部分'''

def exe_time(func):
    def fnc(*args, **kwargs):
        start = datetime.datetime.now()
        # print "call "+ func.__name__ + "()..."
        print func.__name__ +" start :"+ str(start) +" " +str(args)
        func(*args, **kwargs)
        end = datetime.datetime.now()
        print func.__name__ +" end :"+ str(end)
    return fnc


class History(object):                                                             # 实现程序的可持续性，每次运行时读取上次

    def __init__(self):
        # self.company_num = 0                                                     # 初始化pickle中用作公司名称位置索引值
        self.total_page = 0
        self.current_page = 0

    def load(self):                                                                # redis记录的载入
        r = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT,db=REDIS_DB)
        if not r.hgetall(REDIS_TABLE):
            return
        r_dict = r.hgetall(REDIS_TABLE)
        self.total_page = int(r_dict.get("total_page"))
        self.current_page = int(r_dict.get("current_page"))


    def save(self):
        r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        r.hset(REDIS_TABLE, 'total_page', self.total_page)
        r.hset(REDIS_TABLE, 'current_page', self.current_page)
        # print r.hgetall(REDIS_TABLE)

        # with open(self.path, "w") as f:
        #     pickle.dump(self, f)

class Generator(object):

    HOST = "http://dc.simuwang.com/Screen/getData.html?"
    page = 1
    keyword = "广发银行"                                                                # example

    def __init__(self):                                                             # 对象实例化
        self.uris = set()
        self.args = set()
        self.history = History()
        self.history.load()
        self.enterprises = []
        self.step = STEP

    def search_url_with_batch(self):
        self.obtain_enterprises()
        tasks = []
        for company in self.enterprises:
            logging.debug("%s" % (company))
            # self.page_url(self.keyword);print "example测试";break                  # 使用example测试返回是否正常
            self.page_url(company)                                                  # 传参调用url构造函数

    def search_url_with_batch_asyn(self):
        self.obtain_enterprises()
        tasks = []
        for company in self.enterprises:
            logging.debug("%s" % (company))
            tasks.append(gevent.spawn(self.page_url, company))                      # url请求加入gevent任务中
        gevent.joinall(tasks)

    def obtain_enterprises(self):
        if self.history.current_page <= 0 and self.history.total_page <= 0:
            self._load_total_page()

        for _ in range(self.step):
            r = self.paginate(self.history.current_page, ROWS)
            self.history.current_page += 1
            self.history.total_page = r['total_page']

            for item in r['rows']:
                self.enterprises.append(item['name'])

            if self.history.current_page > self.history.total_page:
                self.history.current_page = 0
                self.history.total_page = 0
                break
        self.history.save()

    def _load_total_page(self, rows=ROWS):
        conn = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=MYSQL_DB, port=PORT, charset='utf8')
        sql = "select count(*) from enterprise_enterprise"
        cur = conn.cursor()
        count = cur.execute(sql)
        total_rows = cur.fetchone()[0]
        total_page = total_rows / rows
        self.history.current_page = 0
        self.history.total_page = total_page
        self.history.save()

    # @exe_time
    def page_url(self, current_company):

        for page_num in range(1, 10):                                              # 搜索结果翻页（第一页为0，1）
            params = "page=" + str(page_num)+ "&condition=fund_type%3A1%2C6%2C4%2C3%2C8%2C2%2C7%2C5%3Bsort_name"+\
                     "%3Aret_incep%3Bsort_asc%3Adesc%3Bkeyword%3A" + current_company+ "%3Bret%3Aret_incep%3B"
            url = "%s%s" % (self.HOST, params)
            headers = {
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:45.0) Gecko/20100101 Firefox/45.0",
                "Referer": "http://dc.simuwang.com/screen/index.html"}
            r = requests.get(url, verify=False, headers=headers, timeout=60)       # 浏览器代理请求url
            if r.status_code != 200:
                return
            js_content = re.sub(r"^<.*?>$", "", r.text)                            # 过滤HTML标签
            js_dict = json.loads(js_content)
            js_pager = js_dict.get("pager")
            page_count = int(js_pager.get("pagecount"))
            row_count = js_pager.get("rowcount")

            if row_count == 0:                                                     # 判定返回数据量为空的情况
                break

            js_list = js_dict.get("data")                                          # 获取data数据
            for i in range(0, len(js_list)):
                js_data = js_list[i]
                company = js_data.get("company_name")
                fund_id = js_data.get("fund_id")
                id = js_data.get("id")
                uri = "http://dc.simuwang.com/product/%s.html" % fund_id
                target = "%s%s%s%s%s" % (uri, " ", company," ",id)                 # 将url、公司、关键字重新组合
                self.uris.add(target)                                              # 将url加入uris中

            if page_num == page_count:                                             # 判定最后一页
                break
            # print self.uris

    def paginate(self, current_page, rows=10):
        conn = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=MYSQL_DB, port=PORT, charset='utf8')
        sql = "select count(*) from enterprise_enterprise"
        cur = conn.cursor()
        count = cur.execute(sql)
        total_rows = cur.fetchone()[0]
        total_page = total_rows / rows
        if current_page > total_page:
            current_page = 0
        sql = "select name from enterprise_enterprise limit %d, %d" % (current_page * rows, rows)
        count = cur.execute(sql)
        columns = [desc[0] for desc in cur.description]
        result = []
        for r in cur.fetchall():
            result.append(dict(zip(columns, r)))
        conn.close()

        # print 'rows:', result
        # print 'total_page:', total_page
        # print 'current_page:', current_page
        # print 'total_rows:', total_rows
        return {'rows': result, 'total_page': total_page, 'current_page': current_page, 'total_rows': total_rows}



class GeneratorTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    # @unittest.skip("skipping read from file")
    def test_obtain_enterprises(self):
        self.generator = Generator()
        self.generator.obtain_enterprises()
        for name in self.generator.enterprises:
            logging.debug("enterprise name is %s."%(name))

        self.assertGreater(len(self.generator.enterprises), 0)

    # @unittest.skip("skipping read from file")
    def test_mysql(self):
        generator = Generator()
        result = generator.paginate(0, 10)
        print result

    # @unittest.skip("skipping read from file")
    def test_generator_over_totalpage(self):
        generator = Generator()
        conn = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=MYSQL_DB, charset='utf8', port=PORT)
        sql = 'select count(*) from enterprise_enterprise'
        cur = conn.cursor()
        count = cur.execute(sql)
        total_rows = cur.fetchone()[0]
        total_page = total_rows / 10

        result = generator.paginate(total_page + 1, 10)
        print result
        self.assertEqual(result['current_page'], 0)

if __name__ == "__main__":

    if DEBUG:                                                                        # 如果DEBUG为True则进入测试单元
        unittest.main()
    else:
        generator = Generator()
        generator.search_url_with_batch()
        # generator.search_url_with_batch_asyn()                                     # 使用协程模块，并发加载

        for uri in generator.uris:
            str_uri = uri.encode("utf-8").split(" ")
            print json.dumps({"uri": str_uri[0], "args": (str_uri[1])})

