#encoding=utf-8
import json
import os
import logging

import pytest

from django.test import TestCase

from enterprise.utils import EnterpriseDownload
from enterprise.libs.guangdong_crawler import GuangdongClawer
from enterprise.models import Enterprise, Province
from enterprise.libs.Guangdong0 import Guangdong0


from enterprise.libs.guangdong_crawler import read_ent_from_file
from enterprise.libs.common_func import *

class TestProxy(TestCase):
    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_proxy(self):
        result = get_proxy('GUANGDONG')
        print result
        self.assertEqual(result.has_key('http'))

class TestGuangdong0(TestCase):
    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run_asyn(self):
        ent_str = "http://www.szcredit.com.cn/web/GSZJGSPT/QyxyDetail.aspx?rid=30efb8bdcae04c1997102a72ecddcb09"
        guangdong = Guangdong0()
        guangdong.run_asyn(ent_str)

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

