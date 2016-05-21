#encoding=utf-8
import json
import os
import logging
import pytest
import time
from django.test import TestCase
import unittest

from enterprise.libs.guangdong_crawler import GuangdongClawer #, Crawler, Analyze
from enterprise.libs.Guangdong0 import Guangdong0
from enterprise.libs.Guangdong1 import Guangdong1
from enterprise.libs.Guangdong2 import Guangdong2
from enterprise.libs.common_func import get_proxy, read_ent_from_file, exe_time

import gevent
from gevent import Greenlet
import requests
import urllib
# 如果要达到异步的效果，就要添加这个猴子补丁
import gevent.monkey
gevent.monkey.patch_socket()

import ghost


def get_cookie( url):
    g = ghost.Ghost()
    cookiestr = ""
    with g.start() as se:
        mycookielist=[]
        page, extra_resources = se.open(url,method='get',wait=True,encode_url=True, user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:46.0) Gecko/20100101 Firefox/46.0")
        for element in se.cookies:
            mycookielist.append(element.toRawForm().split(";"))

        cookiestr = reduce(lambda x, y: x[0]+ ";" + y[0], mycookielist)
    return cookiestr

class TestGhost(TestCase):
    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_get_cookie(self):
        url = "http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo_cPlFMHz7UORGuPsot6Ab+gyFHBRDGmiqdLAvpr4C7UU=-7PUW92vxF0RgKhiSE63aCw=="
        cookiestr = get_cookie(url)
        print cookiestr
        self.assertGreater(cookiestr.indexOf('__jsluid'), -1)
        self.assertGreater(cookiestr.indexOf('__jsl_clearance'), -1)


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
        self.assertTrue(result['ind_comm_pub_reg_basic'])
        self.assertEqual(result['ind_comm_pub_reg_basic'][u'名称'], u'世纪证券有限责任公司')

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

class TestGuangdong1(TestCase):
    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run_asyn(self):
        # 万联证券有限责任公司,广东,440101000017862

        start_t = time.time()
        ent_str = "http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo_cPlFMHz7UORGuPsot6Ab+gyFHBRDGmiqdLAvpr4C7UU=-7PUW92vxF0RgKhiSE63aCw=="
        guangdong = Guangdong1()
        result = guangdong.run_asyn(ent_str)
        end_t = time.time()
        print "run asyn total time is %f s!"%(end_t - start_t)

        self.assertTrue(result)
        self.assertTrue(result['ind_comm_pub_reg_basic'])
        self.assertEqual(result['ind_comm_pub_reg_basic'][u'名称'], u'万联证券有限责任公司')

    def test_run(self):
        ent_str = '440101000017862'
        guangdong = GuangdongClawer()
        result = guangdong.run(ent_str)
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertTrue(result[ent_str])
        self.assertTrue(result[ent_str]['ind_comm_pub_reg_basic'])
        self.assertEqual(result[ent_str]['ind_comm_pub_reg_basic'][u'名称'], u'万联证券有限责任公司')

class TestGuangdong2(TestCase):
    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run_asyn(self):
        # 广发证券股份有限公司,广东,222400000001337
        start_t = time.time()
        ent_str = "http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo_GmjYOaEEX9Xx3eeM0JcrtOywZcfQzs3Ry0M6NPS1/iCr+cQwm+oHVoPBzdIqEiYb-7vusEl1hPU+qjV70QwcUXQ=="
        guangdong = Guangdong2()
        result = guangdong.run_asyn(ent_str)
        end_t = time.time()
        print "run asyn total time is %f s!"%(end_t - start_t)

        self.assertTrue(result)
        print result
        self.assertTrue(result['ind_comm_pub_reg_basic'])
        self.assertEqual(result['ind_comm_pub_reg_basic'][u'名称'], u'广发证券股份有限公司')

    def test_run(self):
        # 广发证券股份有限公司,广东,222400000001337
        start_t = time.time()
        ent_str = "http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo_GmjYOaEEX9Xx3eeM0JcrtOywZcfQzs3Ry0M6NPS1/iCr+cQwm+oHVoPBzdIqEiYb-7vusEl1hPU+qjV70QwcUXQ=="
        guangdong = Guangdong2()
        result = guangdong.run(ent_str)
        end_t = time.time()
        print "run asyn total time is %f s!"%(end_t - start_t)
        self.assertTrue(result)
        print result
        # self.assertTrue(result['ent_pub_ent_annual_report'])
        # self.assertEqual(result['ind_comm_pub_reg_basic'][u'名称'], u'广发证券股份有限公司')

    # 单元测试无法从mysql数据库获取代理，原因：单元测试会创建临时的test数据库，数据库里面没有内容。
    @unittest.skip("skipping read from file")
    def test_run_with_proxy(self):
        ent_str = '222400000001337'
        guangdong = GuangdongClawer()
        result = guangdong.run(ent_str)
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertTrue(result[ent_str])
        self.assertTrue(result[ent_str]['ind_comm_pub_reg_basic'])
        self.assertEqual(result[ent_str]['ind_comm_pub_reg_basic'][u'名称'], u'广发证券股份有限公司')

class TestGuangdong(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Guangdong')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

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

    def test_run_guangdong0_with_multi_results(self):
        ent_str = '世纪证券有限责任公司'
        guangdong = GuangdongClawer(self.path)
        result = guangdong.run(ent_str)
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)

        self.assertEqual(type(result), list)
        self.assertEqual(len(result), 1)
        # for item in result:
        #     for k, v in item.items():
        #         self.assertEqual(k, u'91440300158263740T')
        #         self.assertTrue(v.has_key('ind_comm_pub_reg_basic'))
        #         self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'世纪证券有限责任公司')

    def test_run_guangdong0(self):
        ent_str = '440301102739085'
        guangdong = GuangdongClawer(self.path)
        result = guangdong.run(ent_str)
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)

        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91440300158263740T')
                self.assertTrue(v.has_key('ind_comm_pub_reg_basic'))
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'世纪证券有限责任公司')

    def test_run_guangdong2(self):
        ent_str = '222400000001337'
        guangdong = GuangdongClawer(self.path)
        result = guangdong.run(ent_str)
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)

        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91440000126335439C')
                self.assertTrue(v.has_key('ind_comm_pub_reg_basic'))
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'广发证券股份有限公司')

