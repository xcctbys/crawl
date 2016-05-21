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
from enterprise.libs.common_func import get_proxy, read_ent_from_file, exe_time,save_to_file

import gevent
from gevent import Greenlet
import requests
import urllib
# 如果要达到异步的效果，就要添加这个猴子补丁
import gevent.monkey

import re
# gevent.monkey.patch_socket()

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
        ent_str = u'证券股份有限公司'
        Jilin = JilinCrawler(self.path)
        result = Jilin.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 5)


    def test_crawl_ent_pub_pages(self):
        url ="http://218.26.1.108/enterprisePublicity.jspx?id=CBFD78144885003A6DA5369BCB361A48"
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
        ent_str = u'煤碳'
        shanxi = ShanxiCrawler(self.path)
        result = shanxi.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 5)


    def test_crawl_ent_pub_pages(self):
        url ="http://218.26.1.108/enterprisePublicity.jspx?id=CBFD78144885003A6DA5369BCB361A48"
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
        # 江海,黑龙江, 230100100019556
        ent_str = u'证券有限公司'
        heilongjiang = HeilongjiangClawer(self.path)
        result = heilongjiang.run(ent_str)

        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 5)

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
            'webroot' : 'http://xygs.snaic.gov.cn/',
            'page_search': 'http://xygs.snaic.gov.cn/ztxy.do?method=index&random=%d',
            'page_Captcha': 'http://xygs.snaic.gov.cn/ztxy.do?method=createYzm&dt=%d&random=%d',
            'page_showinfo': 'http://xygs.snaic.gov.cn/ztxy.do?method=list&djjg=&random=%d',
            'checkcode': 'http://xygs.snaic.gov.cn/ztxy.do?method=list&djjg=&random=%d',
        }

        ent_num = "610000400000319"
        Shaanxi = ShaanxiCrawler(self.path)
        Shaanxi.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        self.assertTrue(Shaanxi.ents.has_key('610000400000319'))
        self.assertEqual(Shaanxi.ents['610000400000319'], "openView('610000400000319','21','K')")

    def test_main_page(self):
        Shaanxi = ShaanxiCrawler(self.path)
        Shaanxi.ents={'610000400000319': "openView('610000400000319','21','K')"}
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
        pripid, enttype, others= params
        self.pripid = pripid
        data = {
                    'maent.pripid': pripid,
                    'maent.entbigtype' : enttype,
                    'random' : int(time.time()),
                    'djjg' : "",
                }
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
        pripid, enttype, others= params
        Shaanxi.pripid = pripid
        data = {'maent.pripid': pripid,'random' : int(time.time())}
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
            'webroot' : 'http://www.hebscztxyxx.gov.cn/',
            'page_search': 'http://www.hebscztxyxx.gov.cn/notice/',
            'page_Captcha': 'http://www.hebscztxyxx.gov.cn/notice/captcha?preset=&ra=', # preset 有数字的话，验证码会是字母+数字的组合
            'page_showinfo': 'http://www.hebscztxyxx.gov.cn/notice/search/ent_info_list',
            'checkcode':'http://www.hebscztxyxx.gov.cn/notice/security/verify_captcha',
        }

        ent_num = "130000000021709"
        Hebei = HebeiCrawler(self.path)
        Hebei.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        # print Hebei.ents
        self.assertTrue(Hebei.ents.has_key('130000000021709'))
        # print Hebei.ents['  130000000021709']
        self.assertEqual(Hebei.ents['130000000021709'], 'http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=u9Abs75MdJjl94Li4fXsN.dDmlDUrpmY&tab=01')

    def test_main_page(self):
        Hebei = HebeiCrawler(self.path)
        Hebei.ents={'130000000021709': '/platform/saic/viewBase.ftl?entId=349DDA405D520231E04400306EF52828'}
        data = Hebei.crawl_page_main()

        self.assertEqual(type(data), list)
        self.assertTrue(data[0].has_key('130000000021709'))

    def test_ind_comm_pub(self):
        Hebei = HebeiCrawler(self.path)
        Hebei.ents={'130000000021709': '/platform/saic/viewBase.ftl?entId=349DDA405D520231E04400306EF52828'}
        url = "http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=u9Abs75MdJjl94Li4fXsN.dDmlDUrpmY&tab=01"
        corpid = url[url.rfind('corpid')+7:]
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


    def test_run(self):
        # 财达证券有限责任公司,河北,130000000021709
        ent_str = '130000000021709'
        Hebei = HebeiCrawler(self.path)
        result = Hebei.run(ent_str)

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
            'checkcode':'http://tjcredit.gov.cn/platform/saic/search.ftl',
        }

        ent_num = "120000000000165"
        Tianjin = TianjinCrawler(self.path)
        Tianjin.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        # print Tianjin.ents
        self.assertTrue(Tianjin.ents.has_key('911200001030645762'))
        # print Tianjin.ents['911200001030645762']
        self.assertEqual(Tianjin.ents['911200001030645762'], '/platform/saic/viewBase.ftl?entId=349DDA405D520231E04400306EF52828')

    def test_main_page(self):
        Tianjin = TianjinCrawler(self.path)
        Tianjin.ents={'911200001030645762': '/platform/saic/viewBase.ftl?entId=349DDA405D520231E04400306EF52828'}
        data = Tianjin.crawl_page_main()

        self.assertEqual(type(data), list)
        self.assertTrue(data[0].has_key('911200001030645762'))

    def test_ind_comm_pub(self):
        Tianjin = TianjinCrawler(self.path)
        Tianjin.ents={'911200001030645762': '/platform/saic/viewBase.ftl?entId=349DDA405D520231E04400306EF52828'}
        url = "http://tjcredit.gov.cn/platform/saic/viewBase.ftl?entId=349DDA405D520231E04400306EF52828"
        corpid = url[url.rfind('corpid')+7:]
        Tianjin.corpid = corpid
        Tianjin.crawl_ind_comm_pub_pages(url)
        data = Tianjin.json_dict
        print data
        self.assertTrue(data)
        self.assertTrue(data['ind_comm_pub_reg_basic'])
        self.assertEqual(data['ind_comm_pub_reg_basic'][u'名称'], u'万向钱潮股份有限公司')

    def test_ent_pub(self):
        Tianjin = TianjinCrawler(self.path)
        Tianjin.ents={'911200001030645762': '/platform/saic/viewBase.ftl?entId=349DDA405D520231E04400306EF52828'}
        url = "http://gsxt.zjaic.gov.cn/annualreport/doViewAnnualReportIndex.do?corpid=1F4389B42BA72D7B087B5FCAA59AF03D8B5C651E18F67383802A4448359EEE76"
        corpid = url[url.rfind('corpid')+7:]
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
    def tearDown(self):
        TestCase.tearDown(self)

    def test_before_main_page(self):
        urls = {
            'host': 'http://gsxt.zjaic.gov.cn/',
            'webroot' : 'http://gsxt.zjaic.gov.cn',
            'page_search': 'http://gsxt.zjaic.gov.cn/zhejiang.jsp',
            'page_Captcha': 'http://gsxt.zjaic.gov.cn/common/captcha/doReadKaptcha.do',
            'page_showinfo': 'http://gsxt.zjaic.gov.cn/search/doGetAppSearchResult.do',
            'prefix_url_0':'http://gsxt.zjaic.gov.cn/appbasicinfo/',
            'checkcode':'http://gsxt.zjaic.gov.cn//search/doValidatorVerifyCode.do',
        }

        ent_num = "330000000050426"
        Zhejiang = ZhejiangCrawler(self.path)
        Zhejiang.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        # print Zhejiang.ents
        self.assertTrue(Zhejiang.ents.has_key('91330000142923441E'))
        # print Zhejiang.ents['91330000142923441E']
        self.assertEqual(Zhejiang.ents['91330000142923441E'], '/appbasicinfo/doViewAppBasicInfoByLog.do?corpid=1F4389B42BA72D7B087B5FCAA59AF03D8B5C651E18F67383802A4448359EEE76')

    def test_main_page(self):
        Zhejiang = ZhejiangCrawler(self.path)
        Zhejiang.ents={'91330000142923441E': '/appbasicinfo/doViewAppBasicInfoByLog.do?corpid=1F4389B42BA72D7B087B5FCAA59AF03D8B5C651E18F67383802A4448359EEE76'}
        data = Zhejiang.crawl_page_main()

        self.assertEqual(type(data), list)
        self.assertTrue(data[0].has_key('91330000142923441E'))

    def test_ind_comm_pub(self):
        Zhejiang = ZhejiangCrawler(self.path)
        Zhejiang.ents={'91330000142923441E': '/appbasicinfo/doViewAppBasicInfoByLog.do?corpid=1F4389B42BA72D7B087B5FCAA59AF03D8B5C651E18F67383802A4448359EEE76'}
        url = "http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=1F4389B42BA72D7B087B5FCAA59AF03D8B5C651E18F67383802A4448359EEE76"
        corpid = url[url.rfind('corpid')+7:]
        Zhejiang.corpid = corpid
        Zhejiang.crawl_ind_comm_pub_pages(url)
        data = Zhejiang.json_dict
        print data
        self.assertTrue(data)
        self.assertTrue(data['ind_comm_pub_reg_basic'])
        self.assertEqual(data['ind_comm_pub_reg_basic'][u'名称'], u'万向钱潮股份有限公司')

    def test_ent_pub(self):
        Zhejiang = ZhejiangCrawler(self.path)
        Zhejiang.ents={'91330000142923441E': '/appbasicinfo/doViewAppBasicInfoByLog.do?corpid=1F4389B42BA72D7B087B5FCAA59AF03D8B5C651E18F67383802A4448359EEE76'}
        url = "http://gsxt.zjaic.gov.cn/annualreport/doViewAnnualReportIndex.do?corpid=1F4389B42BA72D7B087B5FCAA59AF03D8B5C651E18F67383802A4448359EEE76"
        corpid = url[url.rfind('corpid')+7:]
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


    def test_run_with_proxy():
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.zhejiang_crawler import ZhejiangCrawler
            zhejiang = ZhejiangCrawler('/tmp/')
            result = zhejiang.run('330000000050426')
        """
        pass


class TestShandong(TestCase):

    def setUp(self):
        TestCase.setUp(self)
    def tearDown(self):
        TestCase.tearDown(self)

    def test_before_main_page(self):
        urls = {
            'host': 'http://218.57.139.24/pub/',
            'webroot' : 'http://218.57.139.24/',
            'page_search': 'http://218.57.139.24/',
            'page_Captcha': 'http://218.57.139.24/securitycode',
            'page_showinfo': 'http://218.57.139.24/pub/indsearch',
            'checkcode':'http://218.57.139.24/pub/indsearch',
        }
        ent_num = "370000018067809"
        shandong = ShandongCrawler('/tmp/')
        shandong.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)

        self.assertTrue(shandong.ents.has_key('91370000729246347A'))
        self.assertEqual(shandong.ents['91370000729246347A'], 'gsgsdetail/1223/6e0948678bfeed4ac8115d5cafef819ad6951a24f0c0188cd6c047570329c9b6')

    def test_main_page(self):
        shandong = ShandongCrawler('/tmp/')
        shandong.ents={'91370000729246347A': 'gsgsdetail/1223/6e0948678bfeed4ac8115d5cafef819ad6951a24f0c0188cd6c047570329c9b6'}
        data = shandong.crawl_page_main()
        self.assertEqual(type(data), list)
        self.assertTrue(data[0].has_key('91370000729246347A'))

    def test_run(self):
        # 中泰证券股份有限公司,山东,370000018067809
        # 中信证券（山东）有限责任公司,山东,370200018021238
        ent_str = '370000018067809'
        shandong = ShandongCrawler('/tmp/')
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

    def test_run_with_proxy(self):
        """
            由于使用python manage.py test 命令无法获取mysql中代理的数据，所以就通过python manage.py shell 命令执行。
            python manage.py shell
            from enterprise.libs.shandong_crawler import ShandongCrawler
            shangdong = ShandongCrawler('/tmp/')
            result = shangdong.run('370000018067809')
        """
        pass
