#encoding=utf-8
import json
import os
import logging
import pytest
import time
from django.test import TestCase

from enterprise.libs.guangdong_crawler import GuangdongClawer #, Crawler, Analyze
from enterprise.libs.Guangdong0 import Guangdong0
from enterprise.libs.common_func import get_proxy, read_ent_from_file, exe_time

import gevent
from gevent import Greenlet
import requests
import urllib
# 如果要达到异步的效果，就要添加这个猴子补丁
import gevent.monkey
gevent.monkey.patch_socket()

class TestGevent(TestCase):
    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    @exe_time
    def crawl_page(self, url):
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            print "status code is not 200!"
            return
        return res.content
    # 如果要达到异步的效果，就要添加这个猴子补丁 gevent.monkey.patch_socket()
    def test_asyn_crawl_page(self):
        ent_str = "http://www.szcredit.com.cn/web/GSZJGSPT/QyxyDetail.aspx?rid=30efb8bdcae04c1997102a72ecddcb09"
        threads = []
        rid = ent_str[ent_str.index("rid")+4: len(ent_str)]
        url = "http://www.szcredit.com.cn/web/GSZJGSPT/QyxyDetail.aspx?rid=" + rid
        threads.append( gevent.spawn(self.crawl_page, url) )
        url = "http://www.szcredit.com.cn/web/GSZJGSPT/QynbDetail.aspx?rid=" + rid
        threads.append( gevent.spawn(self.crawl_page, url) )
        url = "http://www.szcredit.com.cn/web/GSZJGSPT/QtbmDetail.aspx?rid=" + rid
        threads.append( gevent.spawn(self.crawl_page, url) )
        gevent.joinall(threads)

    @exe_time
    def fetch( self, pid):
        url = "http://clawer.princetechs.com/enterprise/api/get/all/"
        query = urllib.urlencode({'page':pid, 'rows': 10, 'sort': 'id', 'order': 'asc'})
        response = requests.get(url, query, timeout=10)
        result = response.content
        json_result = json.loads(result)
        total_ = json_result['rows']

        print('Process %s: ' % (pid))
        # ents.extend(total_)

    def test_asyn_fetch(self):
        threads = []
        for i in range(3):
            threads.append(gevent.spawn(self.fetch, i))
        gevent.joinall(threads)


class TestProxy(TestCase):
    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_proxy(self):
        result = get_proxy('guangdong')
        print result
        self.assertEqual(result.has_key('http'))

class TestGuangdong0(TestCase):
    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run_asyn(self):
        start_t = time.time()
        ent_str = "http://www.szcredit.com.cn/web/GSZJGSPT/QyxyDetail.aspx?rid=30efb8bdcae04c1997102a72ecddcb09"
        guangdong = Guangdong0()
        result = guangdong.run_asyn(ent_str)
        end_t = time.time()
        print "run asyn total time is %f s!"%(end_t - start_t)
        self.assertTrue(result)

    def test_run(self):
        start_t = time.time()
        ent_str = "http://www.szcredit.com.cn/web/GSZJGSPT/QyxyDetail.aspx?rid=30efb8bdcae04c1997102a72ecddcb09"
        guangdong = Guangdong0()
        result = guangdong.run(ent_str)
        end_t = time.time()
        print "run total time is %f s!"%(end_t - start_t)
        self.assertTrue(result)


    def test_gevent(self):
        g = Guangdong0()
        ent_str = "http://www.szcredit.com.cn/web/GSZJGSPT/QyxyDetail.aspx?rid=30efb8bdcae04c1997102a72ecddcb09"
        threads = []
        rid = ent_str[ent_str.index("rid")+4: len(ent_str)]
        url = "http://www.szcredit.com.cn/web/GSZJGSPT/QyxyDetail.aspx?rid=" + rid
        threads.append( gevent.spawn(g.crawler.crawl_ind_comm_pub_pages, url) )
        url = "http://www.szcredit.com.cn/web/GSZJGSPT/QynbDetail.aspx?rid=" + rid
        threads.append( gevent.spawn(g.crawler.crawl_ent_pub_pages, url) )
        url = "http://www.szcredit.com.cn/web/GSZJGSPT/QtbmDetail.aspx?rid=" + rid
        threads.append( gevent.spawn(g.crawler.crawl_other_dept_pub_pages, url) )

        gevent.joinall(threads)

    def test_run_time(self):
        ent_str = "http://www.szcredit.com.cn/web/GSZJGSPT/QyxyDetail.aspx?rid=30efb8bdcae04c1997102a72ecddcb09"
        guangdong = Guangdong0()

        start_t = time.time()
        result = guangdong.run_asyn(ent_str)
        end_t = time.time()
        total_asyn = end_t - start_t
        print "run asyn total time is %f s!"%(end_t - start_t)

        start_t = time.time()
        result = guangdong.run(ent_str)
        end_t = time.time()
        total = end_t - start_t
        print "run total time is %f s!"%(end_t - start_t)


        self.assertGreater(total, total_asyn)



class TestGuangdong(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    @pytest.mark.timeout(15)
    def test_guangdong1(self):
        ent_num = "222400000001337"
        guangdong = GuangdongClawer()
        data = guangdong.run(ent_num)
        print data
        self.assertIsNotNone(data)

    @pytest.mark.timeout(15)
    def test_guangdong0(self):
        ent_num = "440301112088791"
        guangdong = GuangdongClawer()
        data = guangdong.run(ent_num)
        print data
        self.assertIsNotNone(data)

    @pytest.mark.timeout(15)
    def test_guangdong2(self):
        ent_num = "440000000035814"
        guangdong = GuangdongClawer()
        data = guangdong.run(ent_num)
        print data
        self.assertIsNotNone(data)

    def test_guangdong(self):
        path = u"/Users/princetechs5/crawler/cr-clawer/sources/qyxy/enterprise_list/guangdong.txt"
        ents = read_ent_from_file(path)
        guangdong = GuangdongClawer()
        for ent in ents:
            logging.info("%s"%ent[0])
            guangdong.run(ent[2])

