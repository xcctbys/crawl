#encoding=utf-8
import json
import os
import logging
import pytest
import time
from django.test import TestCase
import unittest

from enterprise.libs.zhejiang_crawler import ZhejiangCrawler
from enterprise.libs.shandong_crawler import ShandongCrawler
from enterprise.libs.tianjin_crawler import TianjinCrawler
from enterprise.libs.hebei_crawler import HebeiCrawler
from enterprise.libs.shaanxi_crawler import ShaanxiCrawler
from enterprise.libs.heilongjiang_crawler import HeilongjiangClawer
from enterprise.libs.shanxi_crawler import ShanxiCrawler
from enterprise.libs.hainan_crawler import HainanCrawler
from enterprise.libs.xizang_crawler import XizangCrawler
from enterprise.libs.jilin_crawler import JilinCrawler
from enterprise.libs.zongju_crawler import ZongjuCrawler
from enterprise.libs.fujian_crawler import FujianCrawler
from enterprise.libs.hubei_crawler import HubeiCrawler
from enterprise.libs.hunan_crawler import HunanCrawler
from enterprise.libs.liaoning_crawler import LiaoningCrawler
from enterprise.libs.qinghai_crawler import QinghaiCrawler
from enterprise.libs.sichuan_crawler import SichuanCrawler
from enterprise.libs.henan_crawler import HenanCrawler
from enterprise.libs.chongqing_crawler import ChongqingCrawler
from enterprise.libs.jiangxi_crawler import JiangxiCrawler
from enterprise.libs.ningxia_crawler import NingxiaCrawler
from enterprise.libs.neimenggu_crawler import NeimengguCrawler
from enterprise.libs.gansu_crawler import GansuCrawler
from enterprise.libs.guizhou_crawler import GuizhouCrawler
from enterprise.libs.yunnan_crawler import YunnanCrawler
from enterprise.libs.xinjiang_crawler import XinjiangCrawler
from enterprise.libs.anhui_crawler import AnhuiCrawler
from enterprise.libs.guangxi_crawler import GuangxiCrawler
from enterprise.libs.shanghai_crawler import ShanghaiCrawler
from enterprise.libs.guangdong_crawler import GuangdongCrawler
#######
from enterprise.libs.tt_beijing_crawler import BeijingCrawler
from enterprise.libs.tt_jiangsu_crawler import JiangsuCrawler
from enterprise.libs.common_func import get_proxy, read_ent_from_file, exe_time, save_to_file

import gevent
from gevent import Greenlet
import requests
import urllib
# 如果要达到异步的效果，就要添加这个猴子补丁
import gevent.monkey

import re

# gevent.monkey.patch_socket()


class TestGuangdong(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Guangdong')
        if not os.path.exists(self.path):
            os.makedirs(self.path)
    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 广发证券股份有限公司,广东,222400000001337
        ent_str = '310000000016182'
        start =  time.time()
        Guangdong = GuangdongCrawler(self.path)
        result = Guangdong.run(ent_str)
        ent = time.time()
        print ent-start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)

        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'310000000016182')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'海通证券股份有限公司')
    def test_run_2(self):
        # 广发证券股份有限公司,广东,222400000001337
        ent_str = '222400000001337'
        start =  time.time()
        Guangdong = GuangdongCrawler(self.path)
        result = Guangdong.run(ent_str)
        ent = time.time()
        print ent-start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)

        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91440000126335439C')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'广发证券股份有限公司')

    def test_run_0(self):
        # 世纪证券有限责任公司,广东,440301102739085
        ent_str = '440301102739085'
        start =  time.time()
        Guangdong = GuangdongCrawler(self.path)
        result = Guangdong.run(ent_str)
        ent = time.time()
        print ent-start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)

        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91440300158263740T')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'世纪证券有限责任公司')

    def test_run_1(self):
        # 万联证券有限责任公司,广东,440101000017862
        ent_str = '440101000017862'
        start =  time.time()
        Guangdong = GuangdongCrawler(self.path)
        result = Guangdong.run(ent_str)
        ent = time.time()
        print ent-start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)

        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'914401017315412818')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'万联证券有限责任公司')

    def test_run_without_result(self):
        # 广发证券股份有限公司,广东,222400000001337
        ent_str = '10000000'
        Guangdong = GuangdongCrawler(self.path)
        result = Guangdong.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 广发证券股份有限公司,广东,222400000001337
        ent_str = u'广发证券股份有限公司'
        Guangdong = GuangdongCrawler(self.path)
        result = Guangdong.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 3)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91440000126335439C')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'广发证券股份有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.guangdong_crawler import GuangdongCrawler
            Guangdong = GuangdongCrawler('/tmp/')
            result = Guangdong.run('222400000001337')
        """
        pass


class TestShanghai(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Shanghai')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 海通证券股份有限公司,上海,310000000016182
        ent_str = '310000000016182'
        start = time.time()
        Shanghai = ShanghaiCrawler(self.path)
        result = Shanghai.run(ent_str)
        ent = time.time()
        print ent - start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)

        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'310000000016182')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'海通证券股份有限公司')

    def test_run_ent(self):
        ent_list=(
            # u'上海银行股份有限公司虹口支行',
            u'中国农业银行股份有限公司上海黄路支行',
            u'招商银行股份有限公司上海闵行支行',
            # u'上海悦禄资产管理中心(有限合伙)',
            u'交通银行股份有限公司上海六里支行',
            u'上海证券有限责任公司嘉定证券营业部',
            u'中国银行股份有限公司上海市中山北路支行',
            u'中国银行股份有限公司上海市南京西路第三支行',
            u'中国建设银行股份有限公司上海航华支行',
            u'上海国富永钦投资合伙企业(有限合伙)',
            u'上海亚商创业加速器投资中心(有限合伙)',
            u'上海浦东发展银行股份有限公司新桥支行',
            u'上海柏智投资管理中心(有限合伙)',
            u'上海益琛投资管理中心(有限合伙)',
            u'中国光大银行股份有限公司上海嘉定支行',
            u'上海联万投资管理中心(有限合伙)',
            u'上海秀界投资管理中心(有限合伙)',
            u'上海复鑫股权投资基金合伙企业(有限合伙)',
            u'上海琪韵投资管理事务所(普通合伙)',
            u'上海长鹰创业投资中心(有限合伙)',
            )
        Shanghai = ShanghaiCrawler(self.path)
        for ent in ent_list:
            result = Shanghai.run(ent)
            print result
            result = json.loads(result)
            for item in result:
                for k, v in item.items():
                    self.assertTrue(k)
                    self.assertTrue(v.get('ind_comm_pub_reg_basic'))
                    self.assertTrue(v.get('ind_comm_pub_reg_basic').get(u'名称'))
                    self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], ent)


    def test_run_without_result(self):
        # 海通证券股份有限公司,上海,310000000016182
        ent_str = '10000000'
        Shanghai = ShanghaiCrawler(self.path)
        result = Shanghai.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 海通证券股份有限公司,上海,310000000016182
        ent_str = u'海通证券股份有限公司'
        Shanghai = ShanghaiCrawler(self.path)
        result = Shanghai.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 3)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'310000000016182')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'海通证券股份有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.shanghai_crawler import ShanghaiCrawler
            Shanghai = ShanghaiCrawler('/tmp/')
            result = Shanghai.run('310000000016182')
        """
        pass


class TestGuangxi(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Guangxi')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 广西金融投资集团有限公司,广西壮族自治区,450000000014798
        ent_str = '450000000014798'
        start = time.time()
        Guangxi = GuangxiCrawler(self.path)
        result = Guangxi.run(ent_str)
        ent = time.time()
        print ent - start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)

        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91450000677718276R')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'广西金融投资集团有限公司')

    def test_run_without_result(self):
        # 广西金融投资集团有限公司,广西壮族自治区,450000000014798
        ent_str = '10000000'
        Guangxi = GuangxiCrawler(self.path)
        result = Guangxi.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 广西金融投资集团有限公司,广西壮族自治区,450000000014798
        ent_str = u'广西金融投资集团有限公司'
        Guangxi = GuangxiCrawler(self.path)
        result = Guangxi.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 3)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91450000677718276R')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'广西金融投资集团有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.guangxi_crawler import GuangxiCrawler
            Guangxi = GuangxiCrawler('/tmp/')
            result = Guangxi.run('450000000014798')
        """
        pass


class TestAnhui(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Anhui')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 华安证券股份有限公司,安徽,340000000002071
        ent_str = '340000000002071'
        start = time.time()
        Anhui = AnhuiCrawler(self.path)
        result = Anhui.run(ent_str)
        ent = time.time()
        print ent - start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)

        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91340000704920454F')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'华安证券股份有限公司')

    def test_run_without_result(self):
        # 华安证券股份有限公司,安徽,340000000002071
        ent_str = '10000000'
        Anhui = AnhuiCrawler(self.path)
        result = Anhui.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 华安证券股份有限公司,安徽,340000000002071
        ent_str = u'华安证券股份有限公司'
        Anhui = AnhuiCrawler(self.path)
        result = Anhui.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 3)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91340000704920454F')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'华安证券股份有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.anhui_crawler import AnhuiCrawler
            Anhui = AnhuiCrawler('/tmp/')
            result = Anhui.run('340000000002071')
        """
        pass


class TestXinjiang(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Xinjiang')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 新疆众和股份有限公司,新疆,650000040000431
        ent_str = '650000040000431'
        start = time.time()
        Xinjiang = XinjiangCrawler(self.path)
        result = Xinjiang.run(ent_str)
        ent = time.time()
        print ent - start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)

        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91650000228601291B')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'新疆众和股份有限公司')

    def test_run_without_result(self):
        # 新疆众和股份有限公司,新疆,650000040000431
        ent_str = '10000000'
        Xinjiang = XinjiangCrawler(self.path)
        result = Xinjiang.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 新疆众和股份有限公司,新疆,650000040000431
        ent_str = u'新疆众和股份有限公司'
        Xinjiang = XinjiangCrawler(self.path)
        result = Xinjiang.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 3)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91650000228601291B')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'新疆众和股份有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.xinjiang_crawler import XinjiangCrawler
            Xinjiang = XinjiangCrawler('/tmp/')
            result = Xinjiang.run('650000040000431')
        """
        pass


class TestYunnan(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Yunnan')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 云南云维股份有限公司,云南省,530000000002692
        ent_str = '530000000002692'
        start = time.time()
        Yunnan = YunnanCrawler(self.path)
        result = Yunnan.run(ent_str)
        ent = time.time()
        print ent - start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)

        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                # self.assertEqual(k, u'91110000710925892P')
                self.assertEqual(k, u'915300002919803007')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'云南云维股份有限公司')

    def test_run_without_result(self):
        # 云南云维股份有限公司,云南省,530000000002692
        ent_str = '10000000'
        Yunnan = YunnanCrawler(self.path)
        result = Yunnan.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 云南云维股份有限公司,云南省,530000000002692
        ent_str = u'云南云维股份有限公司'
        Yunnan = YunnanCrawler(self.path)
        result = Yunnan.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 3)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'915300002919803007')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'云南云维股份有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.yunnan_crawler import YunnanCrawler
            Yunnan = YunnanCrawler('/tmp/')
            result = Yunnan.run('530000000002692')
        """
        pass


class TestJiangsu(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Jiangsu')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 华泰证券股份有限公司,江苏,320000000000192
        ent_str = '320000000000192'
        start = time.time()
        Jiangsu = JiangsuCrawler(self.path)
        result = Jiangsu.run(ent_str)
        ent = time.time()
        print ent - start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)

        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                # self.assertEqual(k, u'91110000710925892P')
                self.assertEqual(k, u'320000000000192')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'华泰证券股份有限公司')

    def test_run_without_result(self):
        # 华泰证券股份有限公司,江苏,320000000000192
        ent_str = '10000000'
        Jiangsu = JiangsuCrawler(self.path)
        result = Jiangsu.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 华泰证券股份有限公司,江苏,320000000000192
        ent_str = u'华泰证券股份有限公司'
        Jiangsu = JiangsuCrawler(self.path)
        result = Jiangsu.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 3)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91110000710925892P')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'华泰证券股份有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.jiangsu_crawler import JiangsuCrawler
            Jiangsu = JiangsuCrawler('/tmp/')
            result = Jiangsu.run('320000000000192')
        """
        pass


class TestBeijing(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Beijing')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 首创证券有限责任公司,北京,110000007977503
        ent_str = '110000007977503'
        start = time.time()
        Beijing = BeijingCrawler(self.path)
        result = Beijing.run(ent_str)
        ent = time.time()
        print ent - start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)

        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                # self.assertEqual(k, u'91110000710925892P')
                self.assertEqual(k, u'110000007977503')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'首创证券有限责任公司')

    def test_run_without_result(self):
        # 首创证券有限责任公司,北京,110000007977503
        ent_str = '10000000'
        Beijing = BeijingCrawler(self.path)
        result = Beijing.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 首创证券有限责任公司,北京,110000007977503
        ent_str = u'首创证券有限责任公司'
        Beijing = BeijingCrawler(self.path)
        result = Beijing.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 3)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91110000710925892P')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'首创证券有限责任公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.beijing_crawler import BeijingCrawler
            Beijing = BeijingCrawler('/tmp/')
            result = Beijing.run('110000007977503')
        """
        pass


class TestGuizhou(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Guizhou')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 贵州长征天成控股股份有限公司,贵州省,520000000037463
        ent_str = '520000000037463'
        start = time.time()
        Guizhou = GuizhouCrawler(self.path)
        result = Guizhou.run(ent_str)
        ent = time.time()
        print ent - start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)

        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'520000000037463')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'贵州长征天成控股股份有限公司')

    def test_run_without_result(self):
        # 贵州长征天成控股股份有限公司,贵州省,520000000037463
        ent_str = '10000000'
        Guizhou = GuizhouCrawler(self.path)
        result = Guizhou.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 贵州长征天成控股股份有限公司,贵州省,520000000037463
        ent_str = u'贵州长征天成控股股份有限公司'
        Guizhou = GuizhouCrawler(self.path)
        result = Guizhou.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 1)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'520000000037463')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'贵州长征天成控股股份有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.guizhou_crawler import GuizhouCrawler
            Guizhou = GuizhouCrawler('/tmp/')
            result = Guizhou.run('520000000037463')
        """
        pass


class TestGansu(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Gansu')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 华龙证券股份有限公司,甘肃,620000000001727
        ent_str = '620000000001727'
        start = time.time()
        Gansu = GansuCrawler(self.path)
        result = Gansu.run(ent_str)
        ent = time.time()
        print ent - start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'620000000001727')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'华龙证券股份有限公司')

    def test_run_without_result(self):
        # 华龙证券股份有限公司,甘肃,620000000001727
        ent_str = '10000000'
        Gansu = GansuCrawler(self.path)
        result = Gansu.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 华龙证券股份有限公司,甘肃,620000000001727
        ent_str = u'华龙证券股份有限公司'
        Gansu = GansuCrawler(self.path)
        result = Gansu.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 3)


    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.gansu_crawler import GansuCrawler
            Gansu = GansuCrawler('/tmp/')
            result = Gansu.run('620000000001727')
            中国农业银行股份有限公司甘谷新兴支行
        """
        pass


class TestNeimenggu(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Neimenggu')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 内蒙古包钢钢联股份有限公司,内蒙古,150000000007124
        ent_str = '150000000007124'
        start = time.time()
        Neimenggu = NeimengguCrawler(self.path)
        result = Neimenggu.run(ent_str)
        ent = time.time()
        print ent - start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'911500007014649754')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'内蒙古包钢钢联股份有限公司')

    def test_run_without_result(self):
        # 内蒙古包钢钢联股份有限公司,内蒙古,150000000007124
        ent_str = '10000000'
        Neimenggu = NeimengguCrawler(self.path)
        result = Neimenggu.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 内蒙古包钢钢联股份有限公司,内蒙古,150000000007124
        ent_str = u'内蒙古包钢钢联股份有限公司'
        Neimenggu = NeimengguCrawler(self.path)
        result = Neimenggu.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 1)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'911500007014649754')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'内蒙古包钢钢联股份有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.neimenggu_crawler import NeimengguCrawler
            Neimenggu = NeimengguCrawler('/tmp/')
            result = Neimenggu.run('150000000007124')
        """
        pass


class TestJiangxi(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Jiangxi')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 中航证券有限公司,江西,360000110000996
        ent_str = '360000110000996'
        start = time.time()
        Jiangxi = JiangxiCrawler(self.path)
        result = Jiangxi.run(ent_str)
        ent = time.time()
        print ent - start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'913600007419861533')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'中航证券有限公司')

    def test_run_without_result(self):
        # 中航证券有限公司,江西,360000110000996
        ent_str = '10000000'
        Jiangxi = JiangxiCrawler(self.path)
        result = Jiangxi.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 中航证券有限公司,江西,360000110000996
        ent_str = u'中航证券有限公司'
        Jiangxi = JiangxiCrawler(self.path)
        result = Jiangxi.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 1)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'913600007419861533')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'中航证券有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.jiangxi_crawler import JiangxiCrawler
            Jiangxi = JiangxiCrawler('/tmp/')
            result = Jiangxi.run('360000110000996')
        """
        pass


class TestNingxia(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Ningxia')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 宁夏为民实业有限公司,宁夏,640200200005857
        ent_str = '640200200005857'
        start = time.time()
        Ningxia = NingxiaCrawler(self.path)
        result = Ningxia.run(ent_str)
        ent = time.time()
        print ent - start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91640200799946365Q')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'宁夏为民实业有限公司')

    def test_run_without_result(self):
        # 宁夏为民实业有限公司,宁夏,640200200005857
        ent_str = '10000000'
        Ningxia = NingxiaCrawler(self.path)
        result = Ningxia.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 宁夏为民实业有限公司,宁夏,640200200005857
        ent_str = u'宁夏为民实业有限公司'
        Ningxia = NingxiaCrawler(self.path)
        result = Ningxia.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 1)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91640200799946365Q')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'宁夏为民实业有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.ningxia_crawler import NingxiaCrawler
            Ningxia = NingxiaCrawler('/tmp/')
            result = Ningxia.run('640200200005857')
        """
        pass


class TestChongqing(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Chongqing')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 中房地产股份有限公司,重庆市,500000000006873
        ent_str = '500000000006873'
        start = time.time()
        Chongqing = ChongqingCrawler(self.path)
        result = Chongqing.run(ent_str)
        ent = time.time()
        print ent - start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'915000002028133840')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'中房地产股份有限公司')

    def test_run_without_result(self):
        # 中房地产股份有限公司,重庆市,500000000006873
        ent_str = '10000000'
        Chongqing = ChongqingCrawler(self.path)
        result = Chongqing.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 中房地产股份有限公司,重庆市,500000000006873
        ent_str = u'中房地产股份有限公司'
        Chongqing = ChongqingCrawler(self.path)
        result = Chongqing.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 1)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'915000002028133840')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'中房地产股份有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.chongqing_crawler import ChongqingCrawler
            Chongqing = ChongqingCrawler('/tmp/')
            result = Chongqing.run('500000000006873')
        """
        pass


class TestSichuan(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Sichuan')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 中信产业投资基金管理有限公司,四川省,510708000002128
        ent_str = '510708000002128'
        start = time.time()
        Sichuan = SichuanCrawler(self.path)
        result = Sichuan.run(ent_str)
        ent = time.time()
        print ent - start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'510708000002128')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'中信产业投资基金管理有限公司')

    def test_run_without_result(self):
        # 中信产业投资基金管理有限公司,四川省,510708000002128
        ent_str = '10000000'
        Sichuan = SichuanCrawler(self.path)
        result = Sichuan.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 中信产业投资基金管理有限公司,四川省,510708000002128
        ent_str = u'中信产业投资基金管理有限公司'
        Sichuan = SichuanCrawler(self.path)
        result = Sichuan.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 1)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'510708000002128')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'中信产业投资基金管理有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.sichuan_crawler import SichuanCrawler
            Sichuan = SichuanCrawler('/tmp/')
            result = Sichuan.run('510708000002128')
        """
        pass


class TestQinghai(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Qinghai')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 九州证券股份有限公司,青海,630000100019052
        ent_str = '630000100019052'
        Qinghai = QinghaiCrawler(self.path)
        result = Qinghai.run(ent_str)

        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'916300007105213377')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'九州证券股份有限公司')

    def test_run_without_result(self):
        # 九州证券股份有限公司,青海,630000100019052
        ent_str = '10000000'
        Qinghai = QinghaiCrawler(self.path)
        result = Qinghai.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 九州证券股份有限公司,青海,630000100019052
        ent_str = u'九州证券股份有限公司'
        Qinghai = QinghaiCrawler(self.path)
        result = Qinghai.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 1)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'916300007105213377')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'九州证券股份有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.qinghai_crawler import QinghaiCrawler
            Qinghai = QinghaiCrawler('/tmp/')
            result = Qinghai.run('630000100019052')
        """
        pass


class TestLiaoning(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Liaoning')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 东北制药集团股份有限公司,辽宁省,210100000035297
        ent_str = '210100000035297'
        Liaoning = LiaoningCrawler(self.path)
        result = Liaoning.run(ent_str)

        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'210100000035297')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'东北制药集团股份有限公司')

    def test_run_without_result(self):
        # 东北制药集团股份有限公司,辽宁省,210100000035297
        ent_str = '10000000'
        Liaoning = LiaoningCrawler(self.path)
        result = Liaoning.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 东北制药集团股份有限公司,辽宁省,210100000035297
        ent_str = u'东北制药集团股份有限公司'
        Liaoning = LiaoningCrawler(self.path)
        result = Liaoning.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 1)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'210100000035297')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'东北制药集团股份有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.liaoning_crawler import LiaoningCrawler
            Liaoning = LiaoningCrawler('/tmp/')
            result = Liaoning.run('210100000035297')
        """
        pass


class TestHunan(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Hunan')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 方正证券股份有限公司,湖南,330000000013908
        ent_str = '330000000013908'
        Hunan = HunanCrawler(self.path)
        result = Hunan.run(ent_str)

        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'914300001429279950')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'方正证券股份有限公司')

    def test_run_without_result(self):
        # 方正证券股份有限公司,湖南,330000000013908
        ent_str = '10000000'
        Hunan = HunanCrawler(self.path)
        result = Hunan.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 方正证券股份有限公司,湖南,330000000013908
        ent_str = u'方正证券股份有限公司'
        Hunan = HunanCrawler(self.path)
        result = Hunan.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 1)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'914300001429279950')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'方正证券股份有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.hunan_crawler import HunanCrawler
            Hunan = HunanCrawler('/tmp/')
            result = Hunan.run('330000000013908')
        """
        pass


class TestFujian(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Fujian')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 中国武夷实业股份有限公司,福建省,350000100029637
        ent_str = '350000100029637'
        Fujian = FujianCrawler(self.path)
        result = Fujian.run(ent_str)

        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91350000158143095K')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'中国武夷实业股份有限公司')

    def test_run_without_result(self):
        # 中国武夷实业股份有限公司,福建省,350000100029637
        ent_str = '10000000'
        Fujian = FujianCrawler(self.path)
        result = Fujian.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 中国武夷实业股份有限公司,福建省,350000100029637
        ent_str = u'中国武夷实业股份有限公司'
        Fujian = FujianCrawler(self.path)
        result = Fujian.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 1)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91350000158143095K')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'中国武夷实业股份有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.fujian_crawler import FujianCrawler
            Fujian = FujianCrawler('/tmp/')
            result = Fujian.run('350000100029637')
        """
        pass


class TestZongju(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Zongju')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 中信证券股份有限公司,总局,100000000018305
        ent_str = '100000000018305'
        Zongju = ZongjuCrawler(self.path)
        result = Zongju.run(ent_str)

        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'100000000018305')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'中信证券股份有限公司')

    def test_run_without_result(self):
        # 中信证券股份有限公司,总局,100000000018305
        ent_str = '10000000'
        Zongju = ZongjuCrawler(self.path)
        result = Zongju.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 中信证券股份有限公司,总局,100000000018305
        ent_str = u'中信证券股份有限公司'
        Zongju = ZongjuCrawler(self.path)
        result = Zongju.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 1)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'100000000018305')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'中信证券股份有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.zongju_crawler import ZongjuCrawler
            Zongju = ZongjuCrawler('/tmp/')
            result = Zongju.run('100000000018305')
        """
        pass


class TestJilin(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Jilin')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 东北证券股份有限公司,吉林,220000000005183
        ent_str = '220000000005183'
        Jilin = JilinCrawler(self.path)
        result = Jilin.run(ent_str)

        # print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'220000000005183')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'东北证券股份有限公司')
                self.assertTrue(v['ent_pub_administration_license'])

    def test_run_without_result(self):
        # 东北证券股份有限公司,吉林,220000000005183
        ent_str = '1410000'
        Jilin = JilinCrawler(self.path)
        result = Jilin.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 东北证券股份有限公司,吉林,220000000005183
        ent_str = u'东北证券股份有限公司'
        Jilin = JilinCrawler(self.path)
        result = Jilin.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 1)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'220000000005183')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'东北证券股份有限公司')

    def test_crawl_ent_pub_pages(self):
        url = "http://218.26.1.108/enterprisePublicity.jspx?id=CBFD78144885003A6DA5369BCB361A48"
        Jilin = JilinCrawler(self.path)
        # print Jilin.ckcode_image_path
        # print Jilin.proxies
        result = Jilin.crawl_ent_pub_pages(url)
        self.assertTrue(Jilin.json_dict['ent_pub_administration_license'])

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.jilin_crawler import JilinCrawler
            Jilin = JilinCrawler('/tmp/')
            result = Jilin.run('220000000005183')
        """
        pass


class TestHenan(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Henan')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run_with_multi_results(self):
        # 中信重工机械股份有限公司,河南省,410300110053941
        ent_str = '中信重工机械股份有限公司'
        Henan = HenanCrawler(self.path)
        result = Henan.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        self.assertEqual(len(result), 1)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'9141030067166633X2')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'中信重工机械股份有限公司')

    def test_run(self):
        # 中信重工机械股份有限公司,河南省,410300110053941
        ent_str = '410300110053941'
        Henan = HenanCrawler(self.path)
        result = Henan.run(ent_str)

        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'9141030067166633X2')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'中信重工机械股份有限公司')

    def test_run_without_result(self):
        # 中信重工机械股份有限公司,河南省,410300110053941
        ent_str = '9154000'
        Henan = HenanCrawler(self.path)
        result = Henan.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.henan_crawler import HenanCrawler
            Henan = HenanCrawler('/tmp/')
            result = Henan.run('410300110053941')
        """
        pass


class TestHubei(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Hubei')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 长江证券股份有限公司,湖北,420000000009482
        ent_str = '420000000009482'
        Hubei = HubeiCrawler(self.path)
        result = Hubei.run(ent_str)

        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'420000000009482')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'长江证券股份有限公司')

    def test_run_without_result(self):
        # 长江证券股份有限公司,湖北,420000000009482
        ent_str = '10000000'
        Hubei = HubeiCrawler(self.path)
        result = Hubei.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 长江证券股份有限公司,湖北,420000000009482
        ent_str = u'长江证券股份有限公司'
        Hubei = HubeiCrawler(self.path)
        result = Hubei.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 1)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'420000000009482')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'长江证券股份有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.hubei_crawler import HubeiCrawler
            Hubei = HubeiCrawler('/tmp/')
            result = Hubei.run('420000000009482')
        """
        pass


class TestHainan(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Hainan')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 金元证券股份有限公司,海南省,91460000742550597A
        ent_str = '91460000742550597A'
        Hainan = HainanCrawler(self.path)
        result = Hainan.run(ent_str)

        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91460000742550597A')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'金元证券股份有限公司')

    def test_run_with_multi_results(self):
        # 金元证券股份有限公司,海南省,91460000742550597A
        ent_str = '金元证券股份有限公司'
        Hainan = HainanCrawler(self.path)
        result = Hainan.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 1)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91460000742550597A')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'金元证券股份有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.hainan_crawler import HainanCrawler
            Hainan = HainanCrawler('/tmp/')
            result = Hainan.run('91460000742550597A')
        """
        pass


class TestShanxi(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Shanxi')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 临汾市热力供应有限公司,山西省,141000000031826
        ent_str = '141000000031826'
        Shanxi = ShanxiCrawler(self.path)
        result = Shanxi.run(ent_str)

        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'141000000031826')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'临汾市热力供应有限公司')
                self.assertTrue(v['ent_pub_administration_license'])

    def test_run_without_result(self):
        # 临汾市热力供应有限公司,山西省,141000000031826
        ent_str = '1410000'
        shanxi = ShanxiCrawler(self.path)
        result = shanxi.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        #
        ent_str = u'临汾市热力供应有限公司'
        shanxi = ShanxiCrawler(self.path)
        result = shanxi.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 1)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'141000000031826')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'临汾市热力供应有限公司')
                self.assertTrue(v['ent_pub_administration_license'])

    def test_crawl_ent_pub_pages(self):
        url = "http://218.26.1.108/enterprisePublicity.jspx?id=CBFD78144885003A6DA5369BCB361A48"
        Shanxi = ShanxiCrawler(self.path)
        # print Shanxi.ckcode_image_path
        # print Shanxi.proxies
        result = Shanxi.crawl_ent_pub_pages(url)
        self.assertTrue(Shanxi.json_dict['ent_pub_administration_license'])

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.shanxi_crawler import ShanxiCrawler
            shanxi = ShanxiCrawler('/tmp/')
            result = shanxi.run('141000000031826')
        """
        pass


class TestXizang(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Xizang')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run(self):
        # 西藏东方财富证券股份有限公司,西藏,91540000710910420Y
        ent_str = '91540000710910420Y'
        Xizang = XizangCrawler(self.path)
        result = Xizang.run(ent_str)

        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91540000710910420Y')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'西藏东方财富证券股份有限公司')

    def test_run_without_result(self):
        # 西藏东方财富证券股份有限公司,西藏,91540000710910420Y
        ent_str = '91540000710'
        Xizang = XizangCrawler(self.path)
        result = Xizang.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        ent_str = u'西藏东方财富证券股份有限公司'
        Xizang = XizangCrawler(self.path)
        result = Xizang.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 1)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91540000710910420Y')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'西藏东方财富证券股份有限公司')

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.xizang_crawler import XizangCrawler
            xizang = XizangCrawler('/tmp/')
            result = xizang.run('91540000710910420Y')
        """
        pass


class TestHeilongjiang(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Heilongjiang')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_run_with_multi_results(self):
        # 江海证券有限公司,黑龙江, 230100100019556
        ent_str = '江海证券有限公司'
        heilongjiang = HeilongjiangClawer(self.path)
        result = heilongjiang.run(ent_str)

        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'9123010075630766XX')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'江海证券有限公司')

    def test_run(self):
        # 江海证券有限公司,黑龙江, 230100100019556
        ent_str = '230100100019556'
        heilongjiang = HeilongjiangClawer(self.path)
        result = heilongjiang.run(ent_str)

        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'9123010075630766XX')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'江海证券有限公司')

    def test_run_without_result(self):
        # 江海证券有限公司,黑龙江, 230100100019556
        ent_str = '9154000'
        heilongjiang = HeilongjiangClawer(self.path)
        result = heilongjiang.run(ent_str)

        print result
        self.assertTrue(result)
        result = json.loads(result)
        for item in result:
            for k, v in item.items():
                self.assertFalse(v)

    def test_run_with_multi_results(self):
        # 江海证券有限公司,黑龙江, 230100100019556
        ent_str = u'江海证券有限公司'
        heilongjiang = HeilongjiangClawer(self.path)
        result = heilongjiang.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 1)

    def test_crawl_ent_pub_pages(self):
        url = 'http://gsxt.hljaic.gov.cn/enterprisePublicity.jspx?id=D2F788D2201B4BA04DAF76DCA49473B3'
        heilongjiang = HeilongjiangClawer(self.path)
        result = heilongjiang.crawl_ent_pub_pages(url)
        self.assertTrue(heilongjiang.json_dict['ent_pub_administration_license'])

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.heilongjiang_crawler import HeilongjiangClawer
            heilongjiang = HeilongjiangClawer('/tmp/')
            result = heilongjiang.run('230100100019556')
        """
        pass


class TestShaanxi(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Shaanxi')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_before_main_page(self):
        urls = {
            'host': 'http://xygs.snaic.gov.cn/',
            'webroot': 'http://xygs.snaic.gov.cn/',
            'page_search': 'http://xygs.snaic.gov.cn/ztxy.do?method=index&random=%d',
            'page_Captcha': 'http://xygs.snaic.gov.cn/ztxy.do?method=createYzm&dt=%d&random=%d',
            'page_showinfo': 'http://xygs.snaic.gov.cn/ztxy.do?method=list&djjg=&random=%d',
            'checkcode': 'http://xygs.snaic.gov.cn/ztxy.do?method=list&djjg=&random=%d',
        }

        ent_num = "610000400000319"
        Shaanxi = ShaanxiCrawler(self.path)
        Shaanxi.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'],
                                   ent_num)
        self.assertTrue(Shaanxi.ents.has_key('610000400000319'))
        self.assertEqual(Shaanxi.ents['610000400000319'], "openView('610000400000319','21','K')")

    def test_main_page(self):
        Shaanxi = ShaanxiCrawler(self.path)
        Shaanxi.ents = {'610000400000319': "openView('610000400000319','21','K')"}
        data = Shaanxi.crawl_page_main()

        self.assertEqual(type(data), list)
        for item in data:
            self.assertTrue(item.has_key("610000400000319"))
            print item['610000400000319']
            self.assertTrue(item['610000400000319'])

    def test_ind_comm_pub(self):
        Shaanxi = ShaanxiCrawler(self.path)
        url = "openView('610000400000319','21','K')"
        params = re.findall(r'\'(.*?)\'', url)
        url = "http://xygs.snaic.gov.cn/ztxy.do"
        pripid, enttype, others = params
        self.pripid = pripid
        data = {'maent.pripid': pripid, 'maent.entbigtype': enttype, 'random': int(time.time()), 'djjg': "", }
        Shaanxi.crawl_ind_comm_pub_pages(url, data)
        data = Shaanxi.json_dict
        print data
        self.assertTrue(data)
        self.assertTrue(data['ind_comm_pub_reg_basic'])
        self.assertEqual(data['ind_comm_pub_reg_basic'][u'名称'], u'陕西省天然气股份有限公司')

    def test_ent_pub(self):
        Shaanxi = ShaanxiCrawler(self.path)
        url = "openView('610000400000319','21','K')"
        params = re.findall(r'\'(.*?)\'', url)
        url = "http://xygs.snaic.gov.cn/ztxy.do"
        pripid, enttype, others = params
        Shaanxi.pripid = pripid
        data = {'maent.pripid': pripid, 'random': int(time.time())}
        Shaanxi.crawl_ent_pub_pages(url, data)
        data = Shaanxi.json_dict
        print data
        self.assertTrue(data)
        self.assertTrue(data['ent_pub_ent_annual_report'])
        for report in data['ent_pub_ent_annual_report']:
            self.assertTrue(report.has_key(u'详情'))
            details = report[u'详情']
            self.assertTrue(details.has_key(u'企业基本信息'))
            self.assertEqual(details[u'企业基本信息'][u'企业名称'], u'陕西省天然气股份有限公司')

    def test_run_with_multi_results(self):
        # 陕西省天然气股份有限公司,陕西省,610000400000319
        ent_str = '陕西省天然气股份有限公司'
        Shaanxi = ShaanxiCrawler(self.path)
        result = Shaanxi.run(ent_str)
        print result
        result = json.loads(result)
        self.assertEqual(len(result), 1)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'610000400000319')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'陕西省天然气股份有限公司')

    def test_run(self):
        # 陕西省天然气股份有限公司,陕西省,610000400000319
        ent_str = '610000400000319'
        Shaanxi = ShaanxiCrawler(self.path)
        result = Shaanxi.run(ent_str)

        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'610000400000319')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'陕西省天然气股份有限公司')

    def test_run_with_proxy():
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
                from enterprise.libs.shaanxi_crawler import ShaanxiCrawler
                Shaanxi = ShaanxiCrawler('/tmp/')
                result = Shaanxi.run('610000400000319')
        """
        pass


class TestHebei(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Hebei')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_before_main_page(self):
        urls = {
            'host': 'http://www.hebscztxyxx.gov.cn/notice/',
            'webroot': 'http://www.hebscztxyxx.gov.cn/',
            'page_search': 'http://www.hebscztxyxx.gov.cn/notice/',
            'page_Captcha': 'http://www.hebscztxyxx.gov.cn/notice/captcha?preset=&ra=',    # preset 有数字的话，验证码会是字母+数字的组合
            'page_showinfo': 'http://www.hebscztxyxx.gov.cn/notice/search/ent_info_list',
            'checkcode': 'http://www.hebscztxyxx.gov.cn/notice/security/verify_captcha',
        }

        ent_num = "130000000021709"
        Hebei = HebeiCrawler(self.path)
        Hebei.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'],
                                 ent_num)
        # print Hebei.ents
        self.assertTrue(Hebei.ents.has_key('130000000021709'))
        # print Hebei.ents['  130000000021709']
        self.assertEqual(
            Hebei.ents['130000000021709'],
            'http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=u9Abs75MdJjl94Li4fXsN.dDmlDUrpmY&tab=01')

    def test_main_page(self):
        Hebei = HebeiCrawler(self.path)
        Hebei.ents = {'130000000021709': '/platform/saic/viewBase.ftl?entId=349DDA405D520231E04400306EF52828'}
        data = Hebei.crawl_page_main()

        self.assertEqual(type(data), list)
        self.assertTrue(data[0].has_key('130000000021709'))

    def test_ind_comm_pub(self):
        Hebei = HebeiCrawler(self.path)
        Hebei.ents = {'130000000021709': '/platform/saic/viewBase.ftl?entId=349DDA405D520231E04400306EF52828'}
        url = "http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=u9Abs75MdJjl94Li4fXsN.dDmlDUrpmY&tab=01"
        corpid = url[url.rfind('corpid') + 7:]
        Hebei.corpid = corpid
        Hebei.crawl_ind_comm_pub_pages(url)
        data = Hebei.json_dict
        print data
        self.assertTrue(data)
        self.assertTrue(data['ind_comm_pub_reg_basic'])
        self.assertEqual(data['ind_comm_pub_reg_basic'][u'名称'], u'万向钱潮股份有限公司')

    def test_ent_pub(self):
        Hebei = HebeiCrawler(self.path)
        url = "http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=u9Abs75MdJjl94Li4fXsN.dDmlDUrpmY&tab=02"
        Hebei.crawl_ent_pub_pages(url)
        data = Hebei.json_dict
        print data
        self.assertTrue(data)
        self.assertTrue(data['ent_pub_ent_annual_report'])
        for report in data['ent_pub_ent_annual_report']:
            self.assertTrue(report.has_key(u'详情'))
            details = report[u'详情']
            self.assertTrue(details.has_key(u'企业基本信息'))
            self.assertEqual(details[u'企业基本信息'][u'企业名称'], u'万向钱潮股份有限公司')

    def test_run_with_multi_results(self):
        # 财达证券有限责任公司,河北,130000000021709
        ent_str = '财达证券有限责任公司'
        Hebei = HebeiCrawler(self.path)
        result = Hebei.run(ent_str)

        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        # 这个好多搜索结果，没有一个匹配。。。
        self.assertEqual(len(result), 1)

    def test_run(self):
        # 财达证券有限责任公司,河北,130000000021709
        ent_str = '130000000021709'
        start = time.time()
        Hebei = HebeiCrawler(self.path)
        result = Hebei.run(ent_str)
        ent = time.time()
        print ent - start
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'130000000021709')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'财达证券有限责任公司')

    def test_run_with_proxy():
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
                from enterprise.libs.hebei_crawler import HebeiCrawler
                Hebei = HebeiCrawler('/tmp/')
                result = Hebei.run('130000000021709')
        """
        pass


class TestTianjin(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Tianjin')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_before_main_page(self):
        urls = {
            'host': 'http://tjcredit.gov.cn',
            'page_search': 'http://tjcredit.gov.cn/platform/saic/index.ftl',
            'page_Captcha': 'http://tjcredit.gov.cn/verifycode',
            'page_showinfo': 'http://tjcredit.gov.cn/platform/saic/search.ftl',
            'checkcode': 'http://tjcredit.gov.cn/platform/saic/search.ftl',
        }

        ent_num = "120000000000165"
        Tianjin = TianjinCrawler(self.path)
        Tianjin.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'],
                                   ent_num)
        # print Tianjin.ents
        self.assertTrue(Tianjin.ents.has_key('911200001030645762'))
        # print Tianjin.ents['911200001030645762']
        self.assertEqual(Tianjin.ents['911200001030645762'],
                         '/platform/saic/viewBase.ftl?entId=349DDA405D520231E04400306EF52828')

    def test_main_page(self):
        Tianjin = TianjinCrawler(self.path)
        Tianjin.ents = {'911200001030645762': '/platform/saic/viewBase.ftl?entId=349DDA405D520231E04400306EF52828'}
        data = Tianjin.crawl_page_main()

        self.assertEqual(type(data), list)
        self.assertTrue(data[0].has_key('911200001030645762'))

    def test_ind_comm_pub(self):
        Tianjin = TianjinCrawler(self.path)
        Tianjin.ents = {'911200001030645762': '/platform/saic/viewBase.ftl?entId=349DDA405D520231E04400306EF52828'}
        url = "http://tjcredit.gov.cn/platform/saic/viewBase.ftl?entId=349DDA405D520231E04400306EF52828"
        corpid = url[url.rfind('corpid') + 7:]
        Tianjin.corpid = corpid
        Tianjin.crawl_ind_comm_pub_pages(url)
        data = Tianjin.json_dict
        print data
        self.assertTrue(data)
        self.assertTrue(data['ind_comm_pub_reg_basic'])
        self.assertEqual(data['ind_comm_pub_reg_basic'][u'名称'], u'万向钱潮股份有限公司')

    def test_ent_pub(self):
        Tianjin = TianjinCrawler(self.path)
        Tianjin.ents = {'911200001030645762': '/platform/saic/viewBase.ftl?entId=349DDA405D520231E04400306EF52828'}
        url = "http://gsxt.zjaic.gov.cn/annualreport/doViewAnnualReportIndex.do?corpid=1F4389B42BA72D7B087B5FCAA59AF03D8B5C651E18F67383802A4448359EEE76"
        corpid = url[url.rfind('corpid') + 7:]
        Tianjin.corpid = corpid
        Tianjin.crawl_ent_pub_pages(url)
        data = Tianjin.json_dict
        print data
        self.assertTrue(data)
        self.assertTrue(data['ent_pub_ent_annual_report'])
        for report in data['ent_pub_ent_annual_report']:
            self.assertTrue(report.has_key(u'详情'))
            details = report[u'详情']
            self.assertTrue(details.has_key(u'企业基本信息'))
            self.assertEqual(details[u'企业基本信息'][u'企业名称'], u'万向钱潮股份有限公司')

    def test_run(self):
        # 渤海证券股份有限公司,天津,120000000000165
        ent_str = '120000000000165'
        Tianjin = TianjinCrawler(self.path)
        result = Tianjin.run(ent_str)
        #
        # save_to_file(path ,result)
        print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'911200001030645762')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'渤海证券股份有限公司')

    def test_run_with_multi_results(self):
        # 渤海证券股份有限公司,天津,120000000000165
        ent_str = '渤海证券股份有限公司'
        Tianjin = TianjinCrawler(self.path)
        result = Tianjin.run(ent_str)

        # print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        # 天津情况比较特殊，在搜索结果后面会有 （内资公司法人）或 （外资公司法人），所以此单元测试不会通过
        self.assertEqual(len(result), 1)

    def test_run_with_proxy():
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
                from enterprise.libs.tianjin_crawler import TianjinCrawler
                Tianjin = TianjinCrawler('/tmp/')
                result = Tianjin.run('120000000000165')
        """
        pass


class TestZhejiang(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'zhejiang')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_before_main_page(self):
        urls = {
            'host': 'http://gsxt.zjaic.gov.cn/',
            'webroot': 'http://gsxt.zjaic.gov.cn',
            'page_search': 'http://gsxt.zjaic.gov.cn/zhejiang.jsp',
            'page_Captcha': 'http://gsxt.zjaic.gov.cn/common/captcha/doReadKaptcha.do',
            'page_showinfo': 'http://gsxt.zjaic.gov.cn/search/doGetAppSearchResult.do',
            'prefix_url_0': 'http://gsxt.zjaic.gov.cn/appbasicinfo/',
            'checkcode': 'http://gsxt.zjaic.gov.cn//search/doValidatorVerifyCode.do',
        }

        ent_num = "330000000050426"
        Zhejiang = ZhejiangCrawler(self.path)
        Zhejiang.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'],
                                    ent_num)
        # print Zhejiang.ents
        self.assertTrue(Zhejiang.ents.has_key('91330000142923441E'))
        # print Zhejiang.ents['91330000142923441E']
        self.assertEqual(
            Zhejiang.ents['91330000142923441E'],
            '/appbasicinfo/doViewAppBasicInfoByLog.do?corpid=1F4389B42BA72D7B087B5FCAA59AF03D8B5C651E18F67383802A4448359EEE76')

    def test_main_page(self):
        Zhejiang = ZhejiangCrawler(self.path)
        Zhejiang.ents = {
            '91330000142923441E':
            '/appbasicinfo/doViewAppBasicInfoByLog.do?corpid=1F4389B42BA72D7B087B5FCAA59AF03D8B5C651E18F67383802A4448359EEE76'
        }
        data = Zhejiang.crawl_page_main()

        self.assertEqual(type(data), list)
        self.assertTrue(data[0].has_key('91330000142923441E'))

    def test_ind_comm_pub(self):
        Zhejiang = ZhejiangCrawler(self.path)
        Zhejiang.ents = {
            '91330000142923441E':
            '/appbasicinfo/doViewAppBasicInfoByLog.do?corpid=1F4389B42BA72D7B087B5FCAA59AF03D8B5C651E18F67383802A4448359EEE76'
        }
        url = "http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=1F4389B42BA72D7B087B5FCAA59AF03D8B5C651E18F67383802A4448359EEE76"
        corpid = url[url.rfind('corpid') + 7:]
        Zhejiang.corpid = corpid
        Zhejiang.crawl_ind_comm_pub_pages(url)
        data = Zhejiang.json_dict
        print data
        self.assertTrue(data)
        self.assertTrue(data['ind_comm_pub_reg_basic'])
        self.assertEqual(data['ind_comm_pub_reg_basic'][u'名称'], u'万向钱潮股份有限公司')

    def test_ent_pub(self):
        Zhejiang = ZhejiangCrawler(self.path)
        Zhejiang.ents = {
            '91330000142923441E':
            '/appbasicinfo/doViewAppBasicInfoByLog.do?corpid=1F4389B42BA72D7B087B5FCAA59AF03D8B5C651E18F67383802A4448359EEE76'
        }
        url = "http://gsxt.zjaic.gov.cn/annualreport/doViewAnnualReportIndex.do?corpid=1F4389B42BA72D7B087B5FCAA59AF03D8B5C651E18F67383802A4448359EEE76"
        corpid = url[url.rfind('corpid') + 7:]
        Zhejiang.corpid = corpid
        Zhejiang.crawl_ent_pub_pages(url)
        data = Zhejiang.json_dict
        print data
        self.assertTrue(data)
        self.assertTrue(data['ent_pub_ent_annual_report'])
        for report in data['ent_pub_ent_annual_report']:
            self.assertTrue(report.has_key(u'详情'))
            details = report[u'详情']
            self.assertTrue(details.has_key(u'企业基本信息'))
            self.assertEqual(details[u'企业基本信息'][u'企业名称'], u'万向钱潮股份有限公司')

    def test_run(self):
        # 万向钱潮股份有限公司,浙江省,330000000050426
        ent_str = '330000000050426'
        Zhejiang = ZhejiangCrawler(self.path)
        result = Zhejiang.run(ent_str)
        #
        # save_to_file(path ,result)
        # print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'91330000142923441E')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'万向钱潮股份有限公司')

    def test_run_with_multi_results(self):
        # 万向钱潮股份有限公司,浙江省,330000000050426
        ent_str = '万向钱潮股份有限公司'
        Zhejiang = ZhejiangCrawler(self.path)
        result = Zhejiang.run(ent_str)
        #
        # save_to_file(path ,result)
        # print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        self.assertEqual(len(result), 1)

    def test_run_with_proxy():
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.zhejiang_crawler import ZhejiangCrawler
            zhejiang = ZhejiangCrawler('/tmp/')
            result = zhejiang.run(u'浙江南方集团公司')
            result = zhejiang.run('330000000050426')
        """
        pass


class TestShandong(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.path = os.path.join(os.getcwd(), 'Shandong')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_before_main_page(self):
        urls = {
            'host': 'http://218.57.139.24/pub/',
            'webroot': 'http://218.57.139.24/',
            'page_search': 'http://218.57.139.24/',
            'page_Captcha': 'http://218.57.139.24/securitycode',
            'page_showinfo': 'http://218.57.139.24/pub/indsearch',
            'checkcode': 'http://218.57.139.24/pub/indsearch',
        }
        ent_num = "370000018067809"
        shandong = ShandongCrawler(self.path)
        shandong.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'],
                                    ent_num)

        self.assertTrue(shandong.ents.has_key('91370000729246347A'))
        self.assertEqual(shandong.ents['91370000729246347A'],
                         'gsgsdetail/1223/6e0948678bfeed4ac8115d5cafef819ad6951a24f0c0188cd6c047570329c9b6')

    def test_main_page(self):
        shandong = ShandongCrawler(self.path)
        shandong.ents = {'91370000729246347A':
                         'gsgsdetail/1223/6e0948678bfeed4ac8115d5cafef819ad6951a24f0c0188cd6c047570329c9b6'}
        data = shandong.crawl_page_main()
        self.assertEqual(type(data), list)
        self.assertTrue(data[0].has_key('91370000729246347A'))

    def test_run(self):
        # 中泰证券股份有限公司,山东,370000018067809
        # 中信证券（山东）有限责任公司,山东,370200018021238
        ent_str = '370000018067809'
        shandong = ShandongCrawler(self.path)
        result = shandong.run(ent_str)
        # path = os.path.join(os.getcwd(), 'shandong.json')
        # save_to_file(path ,result)
        # print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'中泰证券股份有限公司')

    def test_run_with_multi_results(self):
        # 中泰证券股份有限公司,山东,370000018067809
        # 中信证券（山东）有限责任公司,山东,370200018021238
        ent_str = '中泰证券股份有限公司'
        shandong = ShandongCrawler(self.path)
        result = shandong.run(ent_str)
        # print result
        self.assertTrue(result)
        self.assertEqual(type(result), str)
        result = json.loads(result)
        self.assertEqual(type(result), list)
        self.assertEqual(len(result), 1)

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.shandong_crawler import ShandongCrawler
            shangdong = ShandongCrawler('/tmp/')
            result = shangdong.run('370000018067809')
        """
        pass
