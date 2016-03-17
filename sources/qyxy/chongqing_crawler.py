#!/usr/bin/env python
# encoding=utf-8
import os
import requests
import time
import random
import threading
import unittest

ENT_CRAWLER_SETTINGS = os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS and ENT_CRAWLER_SETTINGS.find('settings_pro') >= 0:
    import settings_pro as settings
else:
    import settings

import os
from os import path
import requests
import time
import re
import random
import threading
import unittest
from bs4 import BeautifulSoup
from crawler import Crawler
from crawler import Parser
from crawler import CrawlerUtils
import types
import urlparse
import json as my_json


class ChongqingClawer(Crawler):
    """重庆工商公示信息网页爬虫
    """
    # html数据的存储路径
    html_restore_path = settings.html_restore_path + '/chongqing/'

    # 验证码图片的存储路径
    ckcode_image_path = settings.json_restore_path + '/chongqing/ckcode.jpg'

    # 验证码文件夹
    ckcode_image_dir_path = settings.json_restore_path + '/chongqing/'

    # 查询结果页面存储路径
    html_search_results_restore_path = html_restore_path + 'search_results.html'

    # 多线程爬取时往最后的json文件中写时的加锁保护
    urls = {
        'host': 'http://gsxt.cqgs.gov.cn',
        'get_checkcode': 'http://gsxt.cqgs.gov.cn/sc.action?width=130&height=40',
        'repost_checkcode': 'http://gsxt.cqgs.gov.cn/search_research.action',
        # 获得查询页面
        'post_checkcode': 'http://gsxt.cqgs.gov.cn/search.action',
        # 根据查询页面获得指定公司的数据
        'search_ent': 'http://gsxt.cqgs.gov.cn/search_getEnt.action',
        # 年报
        'year_report': 'http://gsxt.cqgs.gov.cn/search_getYearReport.action',
        # 年报详情
        'year_report_detail': 'http://gsxt.cqgs.gov.cn/search_getYearReportDetail.action',
        # 股权变更
        'year_daily_transinfo': 'http://gsxt.cqgs.gov.cn/search_getDaily.action',
        # 股东出资信息
        'year_daily_invsub': 'http://gsxt.cqgs.gov.cn/search_getDaily.action',
        # 行政处罚
        'year_daily_peninfo': 'http://gsxt.cqgs.gov.cn/search_getDaily.action',
        # 行政许可
        'year_daily_licinfo': 'http://gsxt.cqgs.gov.cn/search_getDaily.action',
        # 知识产权出质登记
        'year_daily_pleinfo': 'http://gsxt.cqgs.gov.cn/search_getDaily.action',
        # 其他行政许可信息
        'other_qlicinfo': 'http://gsxt.cqgs.gov.cn/search_getOtherSectors.action',
        # 其他行政处罚
        'other_qpeninfo': 'http://gsxt.cqgs.gov.cn/search_getOtherSectors.action',
        # 股权冻结信息
        'sfxz_page': 'http://gsxt.cqgs.gov.cn/search_getSFXZ.action',
        # 股东变更信息
        'sfxzgdbg_page': 'http://gsxt.cqgs.gov.cn/search_getSFXZGDBG.action',
    }
    write_file_mutex = threading.Lock()

    def __init__(self, json_restore_path):
        """
        初始化函数
        Args:
            json_restore_path: json文件的存储路径，所有重庆的企业，应该写入同一个文件，因此在多线程爬取时设置相同的路径。同时，
            需要在写入文件的时候加锁
        Returns:
        """
        # json 数据集
        # POST
        self.ent_number = None
        # GET
        self.ckcode = None
        self.json_ent_info = None
        self.json_sfxzgdbg = None
        self.json_sfxz = None
        self.json_other_qlicinfo = None
        self.json_other_qpeninfo = None
        self.json_year_report = None
        self.json_year_report_detail = None
        self.json_year_daily_transinfo = None
        self.json_year_daily_invsub = None
        self.json_year_daily_peninfo = None
        self.json_year_daily_licinfo = None
        self.json_year_daily_pleinfo = None
        self.json_dict = {}
        self.json_restore_path = json_restore_path
        self.parser = ChongqingParser(self)
        self.reqst = requests.Session()
        self.reqst.headers.update({
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

    def run(self, ent_number=0):
        crawler = ChongqingClawer('./enterprise_crawler/chongqing/chongqing.json')

        crawler.ent_number = str(ent_number)
        # 对每个企业都指定一个html的存储目录
        crawler.html_restore_path = self.html_restore_path + crawler.ent_number + '/'
        if settings.save_html and not os.path.exists(self.html_restore_path):
            CrawlerUtils.make_dir(self.html_restore_path)
        crawler.ent_number = str(ent_number)
        page = crawler.crawl_check_page()
        try:
            crawler.crawl_page_jsons(page)
            crawler.parser.parse_jsons()
            crawler.parser.merge_jsons()
        except Exception as e:
            # settings.logger.error('error')
            return False
        # 采用多线程，在写入文件时需要注意加锁
        self.write_file_mutex.acquire()
        CrawlerUtils.json_dump_to_file(self.json_restore_path, {crawler.ent_number: crawler.json_dict})
        self.write_file_mutex.release()
        return True


    def crawl_check_page(self):
        """爬取验证码页面，包括下载验证码图片以及破解验证码
        :return true or false
        """
        count = 0
        while count < 30:
            ck_code = self.crack_check_code()
            data = {'key':self.ent_number,'code':ck_code}
            resp = self.reqst.post(ChongqingClawer.urls['post_checkcode'], data=data)
            if resp.status_code != 200:
                settings.logger.error("crawl post check page failed!")
                count += 1
                continue
            return resp.content
        return None

    def crack_check_code(self):
        """破解验证码
        :return 破解后的验证码
        """
        resp = self.reqst.get(ChongqingClawer.urls['get_checkcode'])
        if resp.status_code != 200:
            settings.logger.error('failed to get get_checkcode')
            return None
        time.sleep(random.uniform(0.1, 0.2))
        self.write_file_mutex.acquire()
        if not path.isdir(self.ckcode_image_dir_path):
            os.makedirs(self.ckcode_image_dir_path)
        with open(self.ckcode_image_path, 'wb') as f:
            f.write(resp.content)

        try:
            ckcode = self.code_cracker.predict_result(self.ckcode_image_path)
            # ckcode = self.code_cracker.predict_result(self.ckcode_image_dir_path + 'image' + str(i) + '.jpg')
        except Exception as e:
            settings.logger.warn('exception occured when crack checkcode')
            ckcode = ('', '')
        finally:
            pass
        self.write_file_mutex.release()

        return ckcode[1]

    def crack_checkcode(self):
        """破解验证码
        :return 破解后的验证码
        """
        resp = self.reqst.get(ChongqingClawer.urls['get_checkcode'])
        if resp.status_code != 200:
            settings.logger.error('failed to get get_checkcode')
            print 'error'
            return None

        time.sleep(random.uniform(2, 4))

        self.write_file_mutex.acquire()
        self.ckcode_image_path = settings.json_restore_path + '/chongqing/ckcode.jpg'
        with open(self.ckcode_image_path, 'wb') as f:
            f.write(resp.content)
        self.write_file_mutex.release()

        try:
            ckcode = self.code_cracker.predict_result(self.ckcode_image_path)
        except Exception as e:
            settings.logger.warn('exception occured when crack checkcode')
            ckcode = ('', '')
        finally:
            pass

        return ckcode[1]

    def crawl_page_jsons(self,page):
        """获取所有界面的json数据"""
        data = self.parser.parse_search_results_pages(page)
        if data is not None:
            self.crawl_ent_info_json(data)
            self.crawl_year_report_json(data)

            self.crawl_year_report_detail_json(data)
            # print(self.json_year_report_detail)
            # time.sleep(0.1)
            self.crawl_sfxzgdbg_json(data)
            # print(self.json_sfxzgdbg)
            # time.sleep(0.1)
            self.crawl_sfxz_json(data)
            # print(self.json_sfxz)
            # time.sleep(0.1)
            self.crawl_year_daily_invsub_json(data)
            # print(self.json_year_daily_invsub)
            # time.sleep(0.1)
            self.crawl_year_daily_licinfo_json(data)
            # print(self.json_year_daily_licinfo)
            # time.sleep(0.1)
            self.crawl_year_daily_peninfo_json(data)
            # print(self.json_year_daily_peninfo)
            # time.sleep(0.1)
            self.crawl_year_daily_transinfo_json(data)
            # print(self.json_year_daily_transinfo)
            # time.sleep(0.1)
            self.crawl_year_daily_pleinfo_json(data)
            # print(self.json_year_daily_pleinfo)
            # time.sleep(0.1)
            self.crawl_other_qpeninfo_json(data)
            # print(self.json_other_qpeninfo)
            # time.sleep(0.1)
            self.crawl_other_qlicinfo_json(data)
            # print(self.json_other_qlicinfo)
        else:
            print('error')

    def crawl_ent_info_json(self, data, type=1):
        """企业详细信息"""
        params = {'entId': data.get('entId'), 'id': data.get('id'), 'type': type}
        json = self.reqst.get(ChongqingClawer.urls['search_ent'], params=params)
        if json.status_code == 200:
            json = json.content
            json = str(json)
            self.json_ent_info = json[6:]  # 去掉数据中的前六个字符保证数据为完整json格式数据
            if self.json_ent_info is None or 'base' not in self.json_ent_info:
                self.crawl_ent_info_json(data, type=10)  # 有些公司需要传过去的参数为 10
                # print(self.json_ent_info)

    def crawl_year_report_json(self, data):
        """年报数据"""
        params = {'id': data.get('id'), 'type': 1}
        json = self.reqst.get(ChongqingClawer.urls['year_report'], params=params)
        while json.status_code != 200:
            json = self.reqst.get(ChongqingClawer.urls['year_report'], params=params)
        json = json.content
        json = str(json)
        self.json_year_report = json[6:]  # 去掉数据中的前六个字符保证数据为完整json格式数据
        # print(self.json_year_report)

    def crawl_year_report_detail_json(self, data):
        """详细年报"""
        # TO DO 需要获得 year_report 中的年份信息
        while self.json_year_report is None:
            self.crawl_year_report_json(data)
        year_report = my_json.loads(self.json_year_report, encoding='utf-8')
        histories = year_report.get('history')
        for i in range(len(histories)):
            year = histories[i].get('year')
            params = {'id': data.get('id'), 'type': 1, 'year': str(year)}
            json = self.reqst.get(ChongqingClawer.urls['year_report_detail'], params=params)
            if json.status_code == 200:
                # 此页面响应结果直接就是 json
                self.json_year_report_detail = str(json.content)
                # print(self.json_year_report_detail)

    def crawl_year_daily_transinfo_json(self, data):
        """股权变更"""
        params = {'id': data.get('id'), 'jtype': 'transinfo'}
        json = self.reqst.get(ChongqingClawer.urls['year_daily_transinfo'], params=params)
        if json.status_code == 200:
            # 此页面响应结果直接就是 json
            json = json.content
            json = str(json)
            self.json_year_daily_transinfo = json[6:]
            # print(self.json_year_daily_transinfo)

    def crawl_year_daily_pleinfo_json(self, data):
        """行政许可"""
        params = {'id': data.get('id'), 'jtype': 'pleinfo'}
        json = self.reqst.get(ChongqingClawer.urls['year_daily_pleinfo'], params=params)
        if json.status_code == 200:
            # 此页面响应结果直接就是 json
            json = json.content
            json = str(json)
            self.json_year_daily_pleinfo = json[6:]
            # print(self.json_year_daily_pleinfo)

    def crawl_year_daily_invsub_json(self, data):
        """股东出资信息"""
        params = {'id': data.get('id'), 'jtype': 'invsub'}
        json = self.reqst.get(ChongqingClawer.urls['year_daily_invsub'], params=params)
        if json.status_code == 200:
            # 此页面响应结果直接就是 json
            json = json.content
            json = str(json)
            self.json_year_daily_invsub = json[6:]
            # print(self.json_year_daily_invsub)

    def crawl_year_daily_licinfo_json(self, data):
        """行政许可"""
        params = {'id': data.get('id'), 'jtype': 'licinfo'}
        json = self.reqst.get(ChongqingClawer.urls['year_daily_licinfo'], params=params)
        if json.status_code == 200:
            # 此页面响应结果直接就是 json
            json = json.content
            json = str(json)
            self.json_year_daily_licinfo = json[6:]
            # print(self.json_year_daily_licinfo)

    def crawl_year_daily_peninfo_json(self, data):
        """行政处罚"""
        params = {'id': data.get('id'), 'jtype': 'peninfo'}
        json = self.reqst.get(ChongqingClawer.urls['year_daily_peninfo'], params=params)
        if json.status_code == 200:
            # 此页面响应结果直接就是 json
            json = json.content
            json = str(json)
            self.json_year_daily_peninfo = json[6:]
            # print(self.json_year_daily_peninfo)

    def crawl_sfxzgdbg_json(self, data):
        """股东变更信息"""
        params = {'entId': data.get('entId'), 'id': data.get('id'), 'type': 1}
        json = self.reqst.get(ChongqingClawer.urls['sfxzgdbg_page'], params=params)
        if json.status_code == 200:
            # 此页面响应结果直接就是 json
            json = json.content
            json = str(json)
            self.json_sfxzgdbg = json[6:]
            # print(self.json_sfxzgdbg)

    def crawl_sfxz_json(self, data):
        """股权冻结信息"""
        params = {'entId': data.get('entId'), 'id': data.get('id'), 'type': 1}
        json = self.reqst.get(ChongqingClawer.urls['sfxz_page'], params=params)
        if json.status_code == 200:
            # 此页面响应结果直接就是 json
            json = json.content
            json = str(json)
            self.json_sfxz = json[6:]
            # print(self.json_sfxz)

    def crawl_other_qlicinfo_json(self, data):
        """股东出资信息"""
        params = {'entId': data.get('entId'), 'id': data.get('id'), 'qtype': 'Qlicinfo', 'type': 1}
        json = self.reqst.get(ChongqingClawer.urls['other_qlicinfo'], params=params)
        if json.status_code == 200:
            # 此页面响应结果直接就是 json
            json = json.content
            json = str(json)
            self.json_other_qlicinfo = json[6:]
            # print(self.json_other_qlicinfo)

    def crawl_other_qpeninfo_json(self, data):
        """股东出资信息"""
        params = {'entId': data.get('entId'), 'id': data.get('id'), 'qtype': 'Qpeninfo', 'type': 1}
        json = self.reqst.get(ChongqingClawer.urls['other_qpeninfo'], params=params)
        if json.status_code == 200:
            # 此页面响应结果直接就是 json
            json = json.content
            json = str(json)
            self.json_other_qpeninfo = json[6:]
            # print(self.json_other_qpeninfo)


class ChongqingParser(Parser):
    """重庆工商页面的解析类
    """

    def __init__(self, crawler):
        self.crawler = crawler

        self.ind_comm_pub_reg_basic = {}
        self.ind_comm_pub_reg_shareholder = None
        self.ind_comm_pub_reg_modify = None
        self.ind_comm_pub_arch_key_persons = None
        self.ind_comm_pub_arch_branch = None
        self.ind_comm_pub_arch_liquidation = None
        self.ind_comm_pub_movable_property_reg = None
        self.ind_comm_pub_equity_ownership_reg = None
        self.ind_comm_pub_administration_sanction = None
        self.ind_comm_pub_business_exception = None
        self.ind_comm_pub_serious_violate_law = None
        self.ind_comm_pub_spot_check = None
        self.ent_pub_shareholder_capital_contribution = None
        self.ent_pub_equity_change = None
        self.ent_pub_administration_license = None
        self.ent_pub_knowledge_property = None
        self.ent_pub_administration_sanction = None
        self.other_dept_pub_administration_license = None
        self.other_dept_pub_administration_sanction = None
        self.judical_assist_pub_equity_freeze = None
        self.judical_assist_pub_shareholder_modify = None

    def parse_search_results_pages(self, page):
        # 解析供查询页面, 获得工商信息页面POST值
        soup = BeautifulSoup(page, "html5lib")
        result = soup.find('div', {'id': 'result'})
        key_map = {}
        if result is None:
            return None
        item = result.find('div', {'class': 'item'})
        link = item.find('a')
        entId = link.get('data-entid')
        type = link.get('data-type')
        id = link.get('data-id')
        name = link.get_text()
        key_map['entId'] = entId
        key_map['type'] = type
        key_map['id'] = id
        key_map['name'] = name
        if key_map is not None:
            return key_map
        else:
            return None

    def parse_jsons(self):
        self.parse_json_ent_info()
        self.parse_json_year_report()
        self.parse_json_sfxzgdbg()
        self.parse_json_sfxz()
        self.parse_json_year_daily_peninfo()
        self.parse_json_year_daily_licinfo()
        self.parse_json_year_daily_invsub()
        self.parse_json_year_daily_pleinfo()
        self.parse_json_year_daily_transinfo()
        self.parse_json_year_report_detail()
        self.parse_json_other_qpeninfo()
        self.parse_json_other_qlicinfo()

    def merge_jsons(self):
        self.crawler.json_dict['ind_comm_pub_reg_basic'] = self.ind_comm_pub_reg_basic
        self.crawler.json_dict['ind_comm_pub_reg_shareholder'] = self.ind_comm_pub_reg_shareholder
        self.crawler.json_dict['ind_comm_pub_reg_modify'] = self.ind_comm_pub_reg_modify
        self.crawler.json_dict['ind_comm_pub_arch_key_persons'] = self.ind_comm_pub_arch_key_persons
        self.crawler.json_dict['ind_comm_pub_arch_branch'] = self.ind_comm_pub_arch_branch
        self.crawler.json_dict['ind_comm_pub_arch_liquidation'] = self.ind_comm_pub_arch_liquidation
        self.crawler.json_dict['ind_comm_pub_movable_property_reg'] = self.ind_comm_pub_movable_property_reg
        self.crawler.json_dict['ind_comm_pub_equity_ownership_reg'] = self.ind_comm_pub_equity_ownership_reg
        self.crawler.json_dict['ind_comm_pub_administration_sanction'] = self.ind_comm_pub_administration_sanction
        self.crawler.json_dict['ind_comm_pub_business_exception'] = self.ind_comm_pub_business_exception
        self.crawler.json_dict['ind_comm_pub_serious_violate_law'] = self.ind_comm_pub_serious_violate_law
        self.crawler.json_dict['ind_comm_pub_spot_check'] = self.ind_comm_pub_spot_check
        self.crawler.json_dict['ent_pub_shareholder_capital_contribution'] = self.ent_pub_shareholder_capital_contribution
        self.crawler.json_dict['ent_pub_equity_change'] = self.ent_pub_equity_change
        self.crawler.json_dict['ent_pub_administration_license'] = self.ent_pub_administration_license
        self.crawler.json_dict['ent_pub_knowledge_property'] = self.ent_pub_knowledge_property
        self.crawler.json_dict['ent_pub_administration_sanction'] = self.ent_pub_administration_sanction
        self.crawler.json_dict['other_dept_pub_administration_license'] = self.other_dept_pub_administration_license
        self.crawler.json_dict['other_dept_pub_administration_sanction'] = self.other_dept_pub_administration_sanction
        self.crawler.json_dict['judical_assist_pub_equity_freeze'] = self.judical_assist_pub_equity_freeze
        self.crawler.json_dict['judical_assist_pub_shareholder_modify'] = self.judical_assist_pub_shareholder_modify

    def check_key_is_exists(self, investor, sharehodler, newkey, oldkey):
        if oldkey in investor.keys():
            sharehodler[newkey] = str(investor[oldkey]).strip(' ')
        else:
            sharehodler[newkey] = None

    def parse_json_ent_info(self):
        # print self.crawler.json_ent_info
        if self.crawler.json_ent_info is None:
            return
        json_ent_info = my_json.loads(self.crawler.json_ent_info)
        # 公司基本信息
        base_info = json_ent_info.get('base')
        # print json_ent_info.keys()
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, u'注册资本', 'regcap')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, u'经营范围', 'opscope')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, u'注册号/统一社会信用代码', 'pripid')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, u'营业期限至', 'opto')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, u'注册号', 'regno')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, u'住所', 'dom')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, u'名称', 'entname')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, u'核准日期', 'apprdate')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, u'类型', 'enttype')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, u'类型', 'opstate')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, u'法定代表人', 'lerep')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, u'登记机关', 'regorg')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, u'成立日期', 'opfrom')
        # print(self.ind_comm_pub_reg_basic)

        # 股东基本信息
        investors = json_ent_info.get('investors')
        sharehodlers = []
        # print(investors)
        i = 0
        while i < len(investors):
            sharehodler = {}
            self.check_key_is_exists(investors[i], sharehodler, u'股东类型', 'invtype')
            self.check_key_is_exists(investors[i], sharehodler, u'证照/证件号码', 'oid')
            if len(investors[i].get('gInvaccon')) > 0:
                self.check_key_is_exists(investors[i].get('gInvaccon')[0], sharehodler, u'认缴出资日期', 'accondate')
                self.check_key_is_exists(investors[i], sharehodler, '认缴额（万元）', 'lisubconam')
                self.check_key_is_exists(investors[i].get('gInvaccon')[0], sharehodler, u'认缴出资方式', 'acconform')
                self.check_key_is_exists(investors[i].get('gInvaccon')[0], sharehodler, u'认缴出资额（万元）', 'acconam')
            self.check_key_is_exists(investors[i], sharehodler, u'实缴出资方式', 'liacconam')
            if len(investors[i].get('gInvsubcon')) > 0:
                self.check_key_is_exists(investors[i].get('gInvsubcon')[0], sharehodler, u'实缴出资方式', 'conform')
                self.check_key_is_exists(investors[i].get('gInvsubcon')[0], sharehodler, u'实缴出资日期', 'condate')
                self.check_key_is_exists(investors[i].get('gInvsubcon')[0], sharehodler, u'实缴出资额（万元）', 'subconam')
            self.check_key_is_exists(investors[i], sharehodler, u'股东', 'inv')
            self.check_key_is_exists(investors[i], sharehodler, u'证照/证件类型', 'blictype')
            sharehodlers.append(sharehodler)
            i = i + 1
        self.ind_comm_pub_reg_shareholder = sharehodlers

        # 变更信息
        modifies = []
        modify = {}
        alters = json_ent_info.get('alters')
        for alter in alters:
            self.check_key_is_exists(alter, modify, u'变更事项', 'altitem')
            self.check_key_is_exists(alter, modify, u'变更日期', 'altdate')
            self.check_key_is_exists(alter, modify, u'变更后内容', 'altaf')
            self.check_key_is_exists(alter, modify, u'变更后内容', 'altbe')
            modifies.append(modify)
        self.ind_comm_pub_reg_modify = modifies
        # for item in modifies:
        #     print item

        # 主要人物
        key_persons = []
        members = json_ent_info.get('members')
        i = 0
        while i < len(members):
            key_person = {}
            key_person[u'序号'] = i + 1
            self.check_key_is_exists(members[i], key_person, u'姓名', 'name')
            self.check_key_is_exists(members[i], key_person, u'职务', 'position')
            key_persons.append(key_person)
            i += 1
        self.ind_comm_pub_arch_key_persons = key_persons
        # print key_persons

        # 动产抵押
        movable_property_reges = []
        motages = json_ent_info.get('motage')
        i = 0
        while i < len(motages):
            # print(motages[i])
            movable_property_reg = {}
            movable_property_reg[u'序号'] = i + 1
            self.check_key_is_exists(motages[i], movable_property_reg, u'状态', '')
            self.check_key_is_exists(motages[i], movable_property_reg, u'登记日期', 'regidate')
            self.check_key_is_exists(motages[i], movable_property_reg, u'登记编号', 'morregcno')
            self.check_key_is_exists(motages[i], movable_property_reg, u'被担保债权数额', 'priclasecam')
            self.check_key_is_exists(motages[i], movable_property_reg, u'登记机关', 'regorg')
            movable_property_reges.append(movable_property_reg)
            i += 1
        self.ind_comm_pub_movable_property_reg = movable_property_reges
        # print(movable_property_reges)

        # 行政处罚
        administration_sanctions = []
        punishments = json_ent_info.get('punishments')
        i = 0
        while i < len(punishments):
            # print(punishments[i])
            administration_sanction = {}
            administration_sanction[u'序号'] = i + 1
            self.check_key_is_exists(punishments[i], administration_sanction, u'行政处罚内容', 'authcontent')
            self.check_key_is_exists(punishments[i], administration_sanction, u'作出行政处罚决定机关名称', 'penauth')
            self.check_key_is_exists(punishments[i], administration_sanction, u'违法行为类型', 'illegacttype')
            self.check_key_is_exists(punishments[i], administration_sanction, u'作出行政处罚决定日期', 'pendecissdate')
            self.check_key_is_exists(punishments[i], administration_sanction, u'行政处罚决定书文号', 'pendecno')
            administration_sanctions.append(administration_sanction)
            i += 1
        self.ind_comm_pub_administration_sanction = administration_sanctions
        # print(administration_sanctions)

        # 分支机构
        arch_branches = []
        brunchs = json_ent_info.get('brunchs')
        i = 0
        while i < len(brunchs):
            arch_branch = {}
            arch_branch[u'序号'] = i + 1
            self.check_key_is_exists(brunchs[i], arch_branch, u'登记机关', 'regorgname')
            self.check_key_is_exists(brunchs[i], arch_branch, u'注册号/统一社会信用代码', 'regno')
            self.check_key_is_exists(brunchs[i], arch_branch, u'名称', 'brname')
            arch_branches.append(arch_branch)
            i += 1
        self.ind_comm_pub_arch_branch = arch_branches
        # print(arch_branches)

        # 严重违法
        serious_violate_laws = []
        illegals = json_ent_info.get('illegals')
        i = 0
        while i < len(illegals):
            # print(illegals[i])
            serious_violate_law = {}
            serious_violate_law[u'序号'] = i + 1
            self.check_key_is_exists(illegals[i], serious_violate_law, u'移出严重违法企业名单原因', 'remexcpres')
            self.check_key_is_exists(illegals[i], serious_violate_law, u'列入严重违法企业名单原因', 'serillrea')
            self.check_key_is_exists(illegals[i], serious_violate_law, u'作出决定机关', 'decorg')
            self.check_key_is_exists(illegals[i], serious_violate_law, u'列入日期', 'lisdate')
            self.check_key_is_exists(illegals[i], serious_violate_law, u'移出日期', 'remdate')
            serious_violate_laws.append(serious_violate_law)
            i += 1
        self.ind_comm_pub_serious_violate_law = serious_violate_laws
        # print(serious_violate_laws)

        # 抽查检查
        spot_checkes = []
        ccjces = json_ent_info.get('ccjc')
        i = 0
        while i < len(ccjces):
            spot_check = {}
            spot_check[u'序号'] = i + 1
            self.check_key_is_exists(ccjces[i], spot_check, u'检查实施机关', 'insauth')
            self.check_key_is_exists(ccjces[i], spot_check, u'结果', 'insresname')
            self.check_key_is_exists(ccjces[i], spot_check, u'类型', 'instype')
            self.check_key_is_exists(ccjces[i], spot_check, u'公示日期', 'insdate')
            spot_checkes.append(spot_check)
            i += 1
        self.ind_comm_pub_spot_check = spot_checkes

        # 经营异常
        business_exceptiones = []
        qyjyes = json_ent_info.get('qyjy')
        i = 0
        while i < len(qyjyes):
            business_exception = {}
            business_exception[u'序号'] = i + 1
            self.check_key_is_exists(qyjyes[i], business_exception, u'移出经营异常名录原因', 'remexcpres')
            self.check_key_is_exists(qyjyes[i], business_exception, u'作出决定机关', 'decorg')
            self.check_key_is_exists(qyjyes[i], business_exception, u'列入经营异常名录原因', 'specause')
            self.check_key_is_exists(qyjyes[i], business_exception, u'列入日期', 'abntime')
            self.check_key_is_exists(qyjyes[i], business_exception, u'移出日期', 'remdate')
            business_exceptiones.append(business_exception)
            i += 1
        self.ind_comm_pub_business_exception = business_exceptiones

        # 清算
        arch_liquidationes = []
        accounts = json_ent_info.get('accounts')
        i = 0
        while i < len(accounts):
            arch_liquidation = {}
            arch_liquidation[u'序号'] = i + 1
            self.check_key_is_exists(accounts[i], arch_liquidation, u'清算组成员', 'persons')
            self.check_key_is_exists(accounts[i], arch_liquidation, u'清算组负责人', 'ligprincipal')
            business_exceptiones.append(arch_liquidation)
            i += 1
        self.ind_comm_pub_arch_liquidation = arch_liquidationes

        # 股权出质
        equity_ownership_reges = []
        stockes = json_ent_info.get('stock')
        i = 0
        while i < len(stockes):
            # print stockes[i]
            equity_ownership_reg = {}
            equity_ownership_reg[u'序号'] = i + 1
            self.check_key_is_exists(stockes[i], equity_ownership_reg, u'出质股权数额', 'pripid')
            self.check_key_is_exists(stockes[i], equity_ownership_reg, u'公示日期', 'equpledate')
            self.check_key_is_exists(stockes[i], equity_ownership_reg, u'状态', 'type')
            self.check_key_is_exists(stockes[i], equity_ownership_reg, u'质权人', 'imporg')
            self.check_key_is_exists(stockes[i], equity_ownership_reg, u'出质人', 'pledgor')
            self.check_key_is_exists(stockes[i], equity_ownership_reg, u'登记编号', 'equityno')
            self.check_key_is_exists(stockes[i], equity_ownership_reg, u'证照/证件号码', 'impno')
            equity_ownership_reges.append(equity_ownership_reg)
            i += 1
        self.ind_comm_pub_equity_ownership_reg = equity_ownership_reges

    def parse_json_year_report(self):
        pass

    def parse_json_sfxzgdbg(self):
        # print self.crawler.json_sfxzgdbg
        if self.crawler.json_sfxzgdbg is None:
            return
        json_sfxzgdbg = my_json.loads(self.crawler.json_sfxzgdbg)
        shareholder_modifies = []
        self.judical_assist_pub_shareholder_modify = shareholder_modifies
        # ========================
        # 暂时没有数据
        # 正式时需要添加序号
        # ========================
        # self.check_key_is_exists(,,'been_excute_name','inv')
        # self.check_key_is_exists(,,'share_num','froam')
        # self.check_key_is_exists(,,'excute_court','froauth')
        # self.check_key_is_exists(,,'assignee','alien')
        # =====================================================
        # print shareholder_modifies

    def parse_json_sfxz(self):
        # print self.crawler.json_sfxz
        json_sfxz = my_json.loads(self.crawler.json_sfxz)
        equity_freezes = []
        i = 0
        while i < len(json_sfxz):
            equity_freez = {}
            equity_freez[u'序号'] = i + 1
            self.check_key_is_exists(json_sfxz[i], equity_freez, u'状态', 'frozstate')
            self.check_key_is_exists(json_sfxz[i], equity_freez, u'被执行人', 'inv')
            self.check_key_is_exists(json_sfxz[i], equity_freez, u'股权数额', 'froam')
            self.check_key_is_exists(json_sfxz[i], equity_freez, u'执行法院', 'froauth')
            self.check_key_is_exists(json_sfxz[i], equity_freez, u'协助公示通知书文号', 'executeno')
            i += 1
        self.judical_assist_pub_equity_freeze = equity_freezes
        # print ' 股权冻结', equity_freezes

    def parse_json_year_daily_peninfo(self):
        pass

    def parse_json_year_daily_licinfo(self):
        pass

    def parse_json_year_daily_invsub(self):
        pass

    def parse_json_year_daily_pleinfo(self):
        pass

    def parse_json_year_daily_transinfo(self):
        pass

    def parse_json_year_report_detail(self):
        pass

    def parse_json_other_qpeninfo(self):
        # print self.crawler.json_other_qpeninfo
        json_other_qpeninfo = my_json.loads(self.crawler.json_other_qpeninfo)

    def parse_json_other_qlicinfo(self):
        # print self.crawler.json_other_qlicinfo
        json_other_qlicinfoes = my_json.loads(self.crawler.json_other_qlicinfo)
        administration_licenses = []
        i = 0
        while i < len(json_other_qlicinfoes):
            administration_license = {}
            administration_license['序号'] = i + 1
            self.check_key_is_exists(json_other_qlicinfoes[i], administration_license, '状态', 'type')
            self.check_key_is_exists(json_other_qlicinfoes[i], administration_license, '有效期至', 'valto')
            self.check_key_is_exists(json_other_qlicinfoes[i], administration_license, '许可内容', 'licitem')
            self.check_key_is_exists(json_other_qlicinfoes[i], administration_license, '许可文件名称', 'licname')
            self.check_key_is_exists(json_other_qlicinfoes[i], administration_license, '许可文件编号', 'licno')
            # 暂时没有确定
            self.check_key_is_exists(json_other_qlicinfoes[i], administration_license, '详情',
                                     'license_detail')
            self.check_key_is_exists(json_other_qlicinfoes[i], administration_license, '许可机关',
                                     'licanth')
            self.check_key_is_exists(json_other_qlicinfoes[i], administration_license, '有效期自', 'valfrom')
            administration_licenses.append(administration_license)
            i += 1
        self.other_dept_pub_administration_license = administration_licenses
        # print '行政许可===', administration_licenses


class TestParser(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        from CaptchaRecognition import CaptchaRecognition
        self.crawler = ChongqingClawer('./enterprise_crawler/chongqing.json')
        self.parser = self.crawler.parser
        ChongqingClawer.code_cracker = CaptchaRecognition('chongqing')
        self.crawler.json_dict = {}
        self.crawler.ent_number = '500232000003942'


if __name__ == '__main__':

    import sys
    reload(sys)
    sys.setdefaultencoding("utf-8")
    from CaptchaRecognition import CaptchaRecognition

    ChongqingClawer.code_cracker = CaptchaRecognition('chongqing')
    crawler = ChongqingClawer('./enterprise_crawler/chongqing/chongqing.json')
    start_time = time.localtime()
    enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/chongqing.txt')
    for ent_number in enterprise_list:
        ent_number = ent_number.rstrip('\n')
        print(
                '############   Start to crawl enterprise with id %s   ################\n' % ent_number)
        crawler.run(ent_number=ent_number)
