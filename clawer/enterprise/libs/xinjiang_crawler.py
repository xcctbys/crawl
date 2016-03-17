#!/usr/bin/env python
# encoding=utf-8
import os
import time
import re
import random
import logging
import requests
import unittest
from os import path
import threading

from bs4 import BeautifulSoup
import json
from . import settings
from .crawler import Crawler
from .crawler import Parser
from .crawler import CrawlerUtils
import parse_table
import types
import urlparse
import json
from enterprise.libs.CaptchaRecognition import CaptchaRecognition



class XinjiangClawer(Crawler):
    """新疆工商公示信息网页爬虫
    """

    # 多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {'host': 'http://www.nmgs.gov.cn:7001/aiccips',
            'get_checkcode': 'http://gsxt.xjaic.gov.cn:7001/ztxy.do?',
            'post_checkCode': 'http://gsxt.xjaic.gov.cn:7001/ztxy.do?',
            'post_all_page': 'http://gsxt.xjaic.gov.cn:7001/ztxy.do',
            'ind_comm_pub_skeleton': 'http://www.nmgs.gov.cn:7001/aiccips/GSpublicity/GSpublicityList.html',
            }

    def __init__(self, json_restore_path):
        """
        初始化函数
        Args:
            json_restore_path: json文件的存储路径，所有江苏的企业，应该写入同一个文件，因此在多线程爬取时设置相同的路径。同时，
             需要在写入文件的时候加锁
        Returns:
        """

        self.json_restore_path = json_restore_path
        if os.path.exists(self.json_restore_path) is False:
            os.makedirs(self.json_restore_path, 0775)
        self.parser = XinjiangParser(self)
        self.credit_ticket = None

        self.html_restore_path = os.path.join(self.json_restore_path, "/xinjiang/")
        if os.path.exists(self.html_restore_path) is False:
            os.makedirs(self.html_restore_path, 0775)
        #验证码图片的存储路径
        self.ckcode_image_path = os.path.join(self.html_restore_path, 'ckcode.jpg')
        self.code_cracker = CaptchaRecognition("xinjiang")
        self.json_restore_path = json_restore_path

        self.reqst = requests.Session()
        self.reqst.headers.update({
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})
        self.method = None
        self.djjg = ''
        self.maent_pripid = None
        self.maent_entbigtype = None
        self.json_dict = {}
        self.ent_number = None

    def run(self, ent_number=0):
        self.ent_number = str(ent_number)
        page = self.crawl_check_page()
        if page is None:
            logging.error(
                'According to the registration number does not search to the company %s' % self.ent_number)
            return False
        page = self.crawl_ind_comm_pub_basic_pages(page)
        if page is None:
            return False
        self.parser.parse_ind_comm_pub_basic_pages(page)
        page = self.crawl_ind_comm_pub_arch_pages()
        self.parser.parse_ind_comm_pub_arch_pages(page)
        page = self.crawl_ind_comm_pub_movable_property_reg_pages()
        self.parser.parse_ind_comm_pub_movable_property_reg_pages(page)
        page = self.crawl_ind_comm_pub_equity_ownership_reg_pages()
        self.parser.parse_ind_comm_pub_equity_ownership_reg_pages(page)
        page = self.crawl_ind_comm_pub_administration_sanction_pages()
        self.parser.parse_ind_comm_pub_administration_sanction_pages(page)
        page = self.crawl_ind_comm_pub_business_exception_pages()
        self.parser.parse_ind_comm_pub_business_exception_pages(page)
        page = self.crawl_ind_comm_pub_serious_violate_law_pages()
        self.parser.parse_ind_comm_pub_serious_violate_law_pages(page)
        page = self.crawl_ind_comm_pub_spot_check_pages()
        self.parser.parse_ind_comm_pub_spot_check_pages(page)
        page = self.crawl_ent_pub_shareholder_capital_contribution_pages()
        self.parser.parse_ent_pub_shareholder_capital_contribution_pages(page)
        page = self.crawl_ent_pub_ent_annual_report_pages()
        self.parser.parse_ent_pub_ent_annual_report_pages(page)
        page = self.crawl_ent_pub_administration_license_pages()
        self.parser.parse_ent_pub_administration_license_pages(page)
        page = self.crawl_ent_pub_administration_sanction_pages()
        self.parser.parse_ent_pub_administration_sanction_pages(page)
        page = self.crawl_ent_pub_equity_change_pages()
        self.parser.parse_ent_pub_equity_change_pages(page)
        page = self.crawl_ent_pub_knowledge_property_pages()
        self.parser.parse_ent_pub_knowledge_property_pages(page)
        page = self.crawl_other_dept_pub_administration_license_pages()
        self.parser.parse_other_dept_pub_administration_license_pages(page)
        page = self.crawl_other_dept_pub_administration_sanction_pages()
        self.parser.parse_other_dept_pub_administration_sanction_pages(page)
        page = self.crawl_judical_assist_pub_equity_freeze_pages()
        self.parser.parse_judical_assist_pub_equity_freeze_pages(page)
        page = self.crawl_judical_assist_pub_shareholder_modify_pages()
        self.parser.parse_judical_assist_pub_shareholder_modify_pages(page)

        # 采用多线程，在写入文件时需要注意加锁
        return json.dumps({self.ent_number: self.json_dict})


    def crawl_check_page(self):
        """爬取验证码页面，包括下载验证码图片以及破解验证码
        :return true or false
        """
        count = 0
        while count < 30:
            ck_code = self.crack_check_code()
            data = {'currentPageNo': 1, 'yzm': ck_code, 'maent.entname': self.ent_number, 'pName': self.ent_number,
                    'BA_ZCH': self.ent_number}
            params = {}
            params['method'] = 'list'
            params['djjg'] = ''
            params['random'] = long(time.time())
            resp = self.reqst.post(XinjiangClawer.urls['post_checkCode'], data=data, params=params)

            if resp.status_code != 200:
                logging.error("crawl post check page failed!")
                count += 1
                continue

            return resp.content
        return None

    def crack_check_code(self):
        """破解验证码
        :return 破解后的验证码
        """
        times = long(time.time())
        params = {}
        params['method'] = 'createYzm'
        params['dt'] = times
        params['random'] = times

        resp = self.reqst.get(XinjiangClawer.urls['get_checkcode'], params=params)
        if resp.status_code != 200:
            logging.error('failed to get get_checkcode')
            return None
        time.sleep(random.uniform(0.1, 0.2))
        self.write_file_mutex.acquire()

        with open(self.ckcode_image_path, 'wb') as f:
            f.write(resp.content)

        # Test
        # with open(self.ckcode_image_dir_path + 'image' + str(i) + '.jpg', 'wb') as f:
        #     f.write(resp.content)

        try:
            ckcode = self.code_cracker.predict_result(self.ckcode_image_path)
            # ckcode = self.code_cracker.predict_result(self.ckcode_image_dir_path + 'image' + str(i) + '.jpg')
        except Exception as e:
            logging.warn('exception occured when crack checkcode')
            ckcode = ('', '')
        finally:
            pass
        self.write_file_mutex.release()

        return ckcode[1]

    def crawl_page_by_post_data(self, data, name='detail.html'):
        """
        通过传入不同的参数获得不同的页面
        """
        resp = self.reqst.post(XinjiangClawer.urls['post_all_page'], data=data)
        if resp.status_code != 200:
            logging.error('crawl page by url failed! url = %s' % XinjiangClawer.urls['post_all_page'])
        page = resp.content
        time.sleep(random.uniform(0.1, 0.3))
        return page

    def crawl_ind_comm_pub_basic_pages(self, page):
        """爬取工商基本公示信息
        """
        isOk = self.parser.parse_search_page(page)
        count = 0
        while not isOk:
            page = self.crawl_check_page()
            isOk = self.parser.parse_search_page(page)
            count += 1
            if count > 10:
                return None
        data = {}
        data['method'] = 'qyInfo'
        data['djjg'] = ''
        data['maent.pripid'] = self.maent_pripid
        data['maent.entbigtype'] = self.maent_entbigtype
        data['random'] = long(time.time())
        page = self.crawl_page_by_post_data(data)
        return page

    def crawl_ind_comm_pub_arch_pages(self):
        """爬取工商备案公示信息
        """
        data = {}
        data['method'] = 'baInfo'
        data['czmk'] = 'czmk2'
        data['maent.pripid'] = self.maent_pripid
        data['random'] = long(time.time())
        page = self.crawl_page_by_post_data(data)
        return page

    def crawl_ind_comm_pub_movable_property_reg_pages(self):
        """
            工商-动产信息页面爬取
        """
        data = {}
        data['method'] = 'dcdyInfo'
        data['czmk'] = 'czmk4'
        data['maent.pripid'] = self.maent_pripid
        data['random'] = long(time.time())
        page = self.crawl_page_by_post_data(data)
        return page

    def crawl_ind_comm_pub_equity_ownership_reg_pages(self):
        """
            工商-股权出质
        """
        data = {}
        data['method'] = 'gqczxxInfo'
        data['czmk'] = 'czmk4'
        data['maent.pripid'] = self.maent_pripid
        data['random'] = long(time.time())
        page = self.crawl_page_by_post_data(data)
        return page

    def crawl_ind_comm_pub_administration_sanction_pages(self):
        """
            工商-行政处罚
        """
        data = {}
        data['method'] = 'cfInfo'
        data['czmk'] = 'czmk3'
        data['maent.pripid'] = self.maent_pripid
        data['random'] = long(time.time())
        page = self.crawl_page_by_post_data(data)
        return page

    def crawl_ind_comm_pub_business_exception_pages(self):
        """
            工商-经营异常
        """
        data = {}
        data['method'] = 'jyycInfo'
        data['czmk'] = 'czmk6'
        data['maent.pripid'] = self.maent_pripid
        data['random'] = long(time.time())
        page = self.crawl_page_by_post_data(data)
        return page

    def crawl_ind_comm_pub_serious_violate_law_pages(self):
        """
            工商-严重违法
        """
        data = {}
        data['method'] = 'yzwfInfo'
        data['czmk'] = 'czmk14'
        data['maent.pripid'] = self.maent_pripid
        data['random'] = long(time.time())
        page = self.crawl_page_by_post_data(data)
        return page

    def crawl_ind_comm_pub_spot_check_pages(self):
        """
            工商-抽查检查
        """
        data = {}
        data['method'] = 'ccjcInfo'
        data['czmk'] = 'czmk7'
        data['maent.pripid'] = self.maent_pripid
        data['random'] = long(time.time())
        page = self.crawl_page_by_post_data(data)
        return page

    def crawl_ent_pub_ent_annual_report_pages(self):
        """
            企业年报
        """
        data = {}
        data['method'] = 'qygsInfo'
        data['czmk'] = 'czmk8'
        data['maent.pripid'] = self.maent_pripid
        data['random'] = long(time.time())
        page = self.crawl_page_by_post_data(data)
        return page

    def crawl_ent_pub_shareholder_capital_contribution_pages(self):
        """
            企业-出资人比例
        """
        data = {}
        data['method'] = 'qygsForTzrxxInfo'
        data['czmk'] = 'czmk12'
        data['maent.pripid'] = self.maent_pripid
        data['random'] = long(time.time())
        page = self.crawl_page_by_post_data(data)
        return page

    def crawl_ent_pub_equity_change_pages(self):
        """
            企业-股权变更信息
        """
        data = {}
        data['method'] = 'qygsForTzrbgxxInfo'
        data['czmk'] = 'czmk15'
        data['maent.pripid'] = self.maent_pripid
        data['random'] = long(time.time())
        page = self.crawl_page_by_post_data(data)
        return page

    def crawl_ent_pub_administration_license_pages(self):
        """
            企业-行政许可
        """
        data = {}
        data['method'] = 'qygsForXzxkInfo'
        data['czmk'] = 'czmk10'
        data['maent.pripid'] = self.maent_pripid
        data['random'] = long(time.time())
        page = self.crawl_page_by_post_data(data)
        return page

    def crawl_ent_pub_administration_sanction_pages(self):
        """
            企业-行政处罚
        """
        data = {}
        data['method'] = 'qygsForXzcfInfo'
        data['czmk'] = 'czmk13'
        data['maent.pripid'] = self.maent_pripid
        data['random'] = long(time.time())
        page = self.crawl_page_by_post_data(data)
        return page

    def crawl_ent_pub_knowledge_property_pages(self):
        """
            企业-知识产权出质
        """
        data = {}
        data['method'] = 'qygsForZzcqInfo'
        data['czmk'] = 'czmk11'
        data['maent.pripid'] = self.maent_pripid
        data['random'] = long(time.time())
        page = self.crawl_page_by_post_data(data)
        return page

    def crawl_other_dept_pub_administration_license_pages(self):
        """
            其他部门行政许可信息
        """
        data = {}
        data['method'] = 'qtgsInfo'
        data['czmk'] = 'czmk9'
        data['maent.pripid'] = self.maent_pripid
        data['random'] = long(time.time())
        page = self.crawl_page_by_post_data(data)
        return page

    def crawl_other_dept_pub_administration_sanction_pages(self):
        """
            其他部门行政处罚信息
        """
        data = {}
        data['method'] = 'qtgsForCfInfo'
        data['czmk'] = 'czmk16'
        data['maent.pripid'] = self.maent_pripid
        data['random'] = long(time.time())
        page = self.crawl_page_by_post_data(data)
        return page

    def crawl_judical_assist_pub_equity_freeze_pages(self):
        """
            司法协助-股权冻结
        """
        data = {}
        data['method'] = 'sfgsInfo'
        data['czmk'] = 'czmk17'
        data['maent.pripid'] = self.maent_pripid
        data['random'] = long(time.time())
        page = self.crawl_page_by_post_data(data)
        return page

    def crawl_judical_assist_pub_shareholder_modify_pages(self):
        """
            司法协助-股权变更
        """
        data = {}
        data['method'] = 'sfgsbgInfo'
        data['czmk'] = 'czmk18'
        data['maent.pripid'] = self.maent_pripid
        data['random'] = long(time.time())
        page = self.crawl_page_by_post_data(data)
        return page


class XinjiangParser(Parser):
    """新疆工商页面的解析类
    """

    def __init__(self, crawler):
        self.crawler = crawler

    def parse_search_page(self, page):
        soup = BeautifulSoup(page, "html5lib")
        a_li = soup.find('li', {'class', 'font16'})
        if a_li is None:
            return False
        a_link = a_li.find('a')
        if a_link is None:
            return False
        url = a_link.get('onclick')
        if url is None:
            return False
        self.crawler.maent_pripid = str(url)[10:-11]
        self.crawler.maent_entbigtype = str(url)[29:-6]
        return True

    def parse_ind_comm_pub_basic_pages(self, page):
        """解析工商基本公示信息-页面
        """
        soup = BeautifulSoup(page, "html5lib")

        # 基本信息
        base_info = soup.find('div', {'id': 'jibenxinxi'})
        if base_info is None:
            return
        base_info_table = base_info.find('table', {'class': 'detailsList'})
        base_trs = base_info_table.find_all('tr')
        ind_comm_pub_reg_basic = {}
        ind_comm_pub_reg_basic[base_trs[1].find_all('th')[0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[1].find_all('td')[0].get_text())
        ind_comm_pub_reg_basic[base_trs[1].find_all('th')[1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[1].find_all('td')[1].get_text())
        ind_comm_pub_reg_basic[base_trs[2].find_all('th')[0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[2].find_all('td')[0].get_text())
        ind_comm_pub_reg_basic[base_trs[2].find_all('th')[1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[2].find_all('td')[1].get_text())
        ind_comm_pub_reg_basic[base_trs[3].find_all('th')[0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[3].find_all('td')[0].get_text())
        ind_comm_pub_reg_basic[base_trs[3].find_all('th')[1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[3].find_all('td')[1].get_text())
        ind_comm_pub_reg_basic[base_trs[4].find('th').get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[4].find('td').get_text())
        ind_comm_pub_reg_basic[base_trs[5].find_all('th')[0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[5].find_all('td')[0].get_text())
        ind_comm_pub_reg_basic[base_trs[5].find_all('th')[1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[5].find_all('td')[1].get_text())
        ind_comm_pub_reg_basic[base_trs[6].find('th').get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[6].find('td').get_text())
        ind_comm_pub_reg_basic[base_trs[7].find_all('th')[0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[7].find_all('td')[0].get_text())
        ind_comm_pub_reg_basic[base_trs[7].find_all('th')[1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[7].find_all('td')[1].get_text())
        ind_comm_pub_reg_basic[base_trs[8].find('th').get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[8].find('td').get_text())

        self.crawler.json_dict['ind_comm_pub_reg_basic'] = ind_comm_pub_reg_basic

        # 投资人信息
        ind_comm_pub_reg_shareholderes = []
        touziren_table = base_info.find('table', {'id': 'table_fr'})
        if touziren_table is not None:

            shareholder_trs = touziren_table.find_all('tr')
            if len(shareholder_trs) > 2:
                i = 2
                while i < len(shareholder_trs) - 1:
                    ind_comm_pub_reg_shareholder = {}
                    tds = shareholder_trs[i].find_all('td')
                    ind_comm_pub_reg_shareholder[u'股东'] = self.wipe_off_newline_and_blank_for_fe(
                        tds[0].get_text())
                    ind_comm_pub_reg_shareholder[u'证照/证件类型'] = self.wipe_off_newline_and_blank_for_fe(
                        tds[1].get_text())
                    ind_comm_pub_reg_shareholder[u'证照/证件号码'] = self.wipe_off_newline_and_blank_for_fe(
                        tds[2].get_text())
                    ind_comm_pub_reg_shareholder[u'股东类型'] = self.wipe_off_newline_and_blank_for_fe(
                        tds[3].get_text())

                    a_link = tds[4].find('a')
                    if a_link is None:
                        i += 1
                        continue
                    a_click = a_link.get('onclick')
                    maent_xh = str(a_click)[10:28]
                    detail_data = {}
                    detail_data['method'] = 'tzrCzxxDetial'
                    detail_data['maent.pripid'] = self.crawler.maent_pripid
                    detail_data['maent.xh'] = maent_xh
                    detail_data['random'] = long(time.time())
                    detail_page = self.crawler.crawl_page_by_post_data(detail_data)
                    detail_soup = BeautifulSoup(detail_page, 'html5lib')
                    detail_table = detail_soup.find('table', {'class': 'detailsList'})
                    if detail_table is None:
                        i += 1
                        continue
                    detail_trs = detail_table.find_all('tr')
                    detail_tds = detail_trs[3].find_all('td')
                    detail = {}
                    shareholder_detail = []
                    if len(detail_tds) >= 8:
                        detail_detial = {}
                        detail_detial[u'股东'] = self.wipe_off_newline_and_blank(detail_tds[0].get_text())
                        detail_detial[u'认缴额（万元)'] = self.wipe_off_newline_and_blank(detail_tds[1].get_text())
                        detail_detial[u'实缴额（万元)'] = self.wipe_off_newline_and_blank(detail_tds[2].get_text())
                        detail_list = []
                        big_num = 0
                        if len(detail_tds[3].find_all('li')) > big_num:
                            big_num = len(detail_tds[3].find_all('li'))
                        if len(detail_tds[4].find_all('li')) > big_num:
                            big_num = len(detail_tds[4].find_all('li'))
                        if len(detail_tds[5].find_all('li')) > big_num:
                            big_num = len(detail_tds[5].find_all('li'))
                        if len(detail_tds[6].find_all('li')) > big_num:
                            big_num = len(detail_tds[6].find_all('li'))
                        if len(detail_tds[7].find_all('li')) > big_num:
                            big_num = len(detail_tds[7].find_all('li'))
                        if len(detail_tds[8].find_all('li')) > big_num:
                            big_num = len(detail_tds[8].find_all('li'))
                        k = 0
                        while k < big_num:
                            detail_detial_tial = {}
                            if len(detail_tds[3].find_all('li')) > k:
                                detail_detial_tial[u'认缴出资'] = self.wipe_off_newline_and_blank(
                                    detail_tds[3].find_all('li')[k].get_text())
                            if len(detail_tds[4].find_all('li')) > k:
                                detail_detial_tial[u'认缴出资额'] = self.wipe_off_newline_and_blank(
                                    detail_tds[4].find_all('li')[k].get_text())
                            if len(detail_tds[5].find_all('li')) > k:
                                detail_detial_tial[u'认缴出资日期'] = self.wipe_off_newline_and_blank(
                                    detail_tds[5].find_all('li')[k].get_text())
                            if len(detail_tds[6].find_all('li')) > k:
                                detail_detial_tial[u'实缴出资'] = self.wipe_off_newline_and_blank(
                                    detail_tds[6].find_all('li')[k].get_text())
                            if len(detail_tds[7].find_all('li')) > k:
                                detail_detial_tial[u'实缴出资额'] = self.wipe_off_newline_and_blank(
                                    detail_tds[7].find_all('li')[k].get_text())
                            if len(detail_tds[8].find_all('li')) > k:
                                detail_detial_tial[u'实缴出资日期'] = self.wipe_off_newline_and_blank(
                                    detail_tds[8].find_all('li')[k].get_text())
                            detail_list.append(detail_detial_tial)
                            k += 1
                        detail_list.append(detail_detial_tial)
                        detail_detial['list'] = detail_list
                        shareholder_detail.append(detail_detial)
                    detail[u'股东及出资信息'] = shareholder_detail
                    ind_comm_pub_reg_shareholder[u'详情'] = detail
                    ind_comm_pub_reg_shareholderes.append(ind_comm_pub_reg_shareholder)
                    i += 1

        self.crawler.json_dict['ind_comm_pub_reg_shareholder'] = ind_comm_pub_reg_shareholderes
        # 变更信息

        biangeng_div = soup.find('div', {'id': 'biangeng'})
        biangeng_table = biangeng_div.find('table', {'id': 'table_bg'})
        self.crawler.json_dict['ind_comm_pub_reg_modify'] = parse_table.parse_table_A(biangeng_table)

    def parse_ind_comm_pub_arch_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        beian_div = soup.find('div', {'id': 'beian'})
        zyry_table = beian_div.find('table', {'id': 'table_ry1'})

        self.crawler.json_dict['ind_comm_pub_arch_key_persons'] = parse_table.parse_table_A(zyry_table)
        # 分支机构

        arch_branch_info = beian_div.find('table', {'id': 'table_fr2'})
        self.crawler.json_dict['ind_comm_pub_arch_branch'] = parse_table.parse_table_A(arch_branch_info)


        # 清算信息

    def parse_ind_comm_pub_movable_property_reg_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 动产抵押
        movable_property_reg_info = soup.find('table', {'id': 'table_dc'})
        self.crawler.json_dict['ind_comm_pub_movable_property_reg'] = parse_table.parse_table_A(
            movable_property_reg_info)

    def parse_ind_comm_pub_equity_ownership_reg_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 股权出质
        equity_ownership_reges = []
        equity_table = soup.find('table', {'id': 'table_gq'})
        self.crawler.json_dict['ind_comm_pub_equity_ownership_reg'] = parse_table.parse_table_A(equity_table)

    def parse_ind_comm_pub_administration_sanction_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 行政处罚
        administration_sanction_info = soup.find('table', {'id': 'table_gscfxx'})
        self.crawler.json_dict['ind_comm_pub_administration_sanction'] = parse_table.parse_table_A(
            administration_sanction_info)

    def parse_ind_comm_pub_business_exception_pages(self, page):
        """
        经营异常
        """
        soup = BeautifulSoup(page, 'html5lib')
        business_exception_info = soup.find('table', {'id': 'table_yc'})
        self.crawler.json_dict['ind_comm_pub_business_exception'] = parse_table.parse_table_A(business_exception_info)

    def parse_ind_comm_pub_serious_violate_law_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 严重违法
        serious_violate_law_info = soup.find('table', {'id': 'table_wfxx'})
        self.crawler.json_dict['ind_comm_pub_serious_violate_law'] = parse_table.parse_table_A(serious_violate_law_info)

    def parse_ind_comm_pub_spot_check_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 抽查检查
        spot_check_info = soup.find('table', {'id': 'table_ccjc'})
        self.crawler.json_dict['ind_comm_pub_spot_check'] = parse_table.parse_table_A(spot_check_info)

    def parse_ent_pub_shareholder_capital_contribution_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 股东出资
        shareholder_capital_contributiones = []
        equity_table = soup.find('table', {'id': 'table_qytzr'})
        self.crawler.json_dict['ent_pub_shareholder_capital_contribution'] = parse_table.parse_table_A(equity_table)
        # 企业变更信息
        reg_modify_info = soup.find('table', {'id': 'table_tzrxxbg'})
        self.crawler.json_dict['ent_pub_reg_modify'] = parse_table.parse_table_A(reg_modify_info)

    def parse_ent_pub_ent_annual_report_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 企业年报
        qiyenianbao_table = soup.find('table', {'id': 't30'})
        report_trs = qiyenianbao_table.find_all('tr')
        ent_pub_ent_annual_reportes = []
        if len(report_trs) > 2:
            j = 2
            while j < len(report_trs):
                tds = report_trs[j].find_all('td')
                if len(tds) <= 1:
                    break
                ent_pub_ent_annual_report = {}
                ent_pub_ent_annual_report[u'序号'] = self.wipe_off_newline_and_blank_for_fe(tds[0].get_text())
                ent_pub_ent_annual_report[u'报送年度'] = self.wipe_off_newline_and_blank_for_fe(
                    (str(tds[1].get_text())[1:]))
                ent_pub_ent_annual_report[u'发布日期'] = self.wipe_off_newline_and_blank_for_fe((tds[2].get_text()))
                detail_data = {}
                data = {}
                detail_data['method'] = 'ndbgDetail'
                detail_data['maent.pripid'] = self.crawler.maent_pripid
                detail_data['maent.nd'] = int(str(ent_pub_ent_annual_report[u'报送年度'])[0:4])
                detail_data['random'] = long(time.time())
                report_page = self.crawler.crawl_page_by_post_data(detail_data)
                soup_reoprt = BeautifulSoup(report_page, 'html5lib')
                detail = {}
                detail_div = soup_reoprt.find('div', {'id': 'qufenkuang'})
                if detail_div is None:
                    j += 1
                    continue
                base_info = detail_div.find('table', {'class': 'detailsList'})
                base_trs = base_info.find_all('tr')
                detail_base_info = {}

                detail_base_info[base_trs[2].find_all('th')[0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[2].find_all('td')[0].get_text())
                detail_base_info[base_trs[2].find_all('th')[1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[2].find_all('td')[1].get_text())
                detail_base_info[base_trs[3].find_all('th')[0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[3].find_all('td')[0].get_text())
                detail_base_info[base_trs[3].find_all('th')[1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[3].find_all('td')[1].get_text())
                detail_base_info[base_trs[4].find('th').get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[4].find('td').get_text())
                detail_base_info[base_trs[5].find_all('th')[0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[5].find_all('td')[0].get_text())
                detail_base_info[base_trs[5].find_all('th')[1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[5].find_all('td')[1].get_text())
                detail_base_info[base_trs[6].find_all('th')[0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[6].find_all('td')[0].get_text())
                detail_base_info[base_trs[6].find_all('th')[1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[6].find_all('td')[1].get_text())
                detail_base_info[base_trs[7].find_all('th')[0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[7].find_all('td')[0].get_text())
                detail_base_info[base_trs[7].find_all('th')[1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[7].find_all('td')[1].get_text())

                detail[u'企业基本信息'] = detail_base_info

                website_info = soup_reoprt.find('table', {'id': 'table_wzxx'})
                detail[u'网站或网店信息'] = parse_table.parse_table_A(website_info)

                shareholder_capital_contribution_info = soup_reoprt.find('table', {'id': 'table_tzrxx'})
                detail[u'股东及出资信息'] = parse_table.parse_table_A(shareholder_capital_contribution_info)

                outbound_investment_info = soup_reoprt.find('table', {'id': 'table_tzxx'})
                detail[u'对外投资信息'] = parse_table.parse_table_A(outbound_investment_info)
                provide_guarantee_to_the_outside_info = soup_reoprt.find('table', {'id': 'table_dbxx'})
                detail[u'对外提供保证担保信息'] = parse_table.parse_table_A(provide_guarantee_to_the_outside_info)

                ent_pub_equity_change_info = soup_reoprt.find('table', {'id': 'table_gqbg'})
                detail[u'股权变更信息'] = parse_table.parse_table_A(ent_pub_equity_change_info)

                change_record_info = ent_pub_equity_change_info = soup_reoprt.find('table', {'id': 'table_bgxx'})
                detail[u'修改记录'] = parse_table.parse_table_A(change_record_info)
                ent_pub_ent_annual_report[u'详情'] = detail
                j += 1
                ent_pub_ent_annual_reportes.append(ent_pub_ent_annual_report)
        self.crawler.json_dict['ent_pub_ent_annual_report'] = ent_pub_ent_annual_reportes

    def parse_ent_pub_administration_license_pages(self, page):
        """
        企业-解析行政许可
        """
        soup = BeautifulSoup(page, 'html5lib')
        ck_string = '暂无数据'
        administration_license_info = soup.find('table', {'id': 'table_xzxk'})
        self.crawler.json_dict['ind_comm_pub_administration_license'] = parse_table.parse_table_A(
            administration_license_info)

    def parse_ent_pub_administration_sanction_pages(self, page):
        """
        企业-解析行政处罚
        """
        soup = BeautifulSoup(page, 'html5lib')
        ck_string = '暂无数据'
        administration_sanction_info = soup.find('table', {'id': 'table_qyxzcf'})
        self.crawler.json_dict['ind_comm_pub_administration_sanction'] = parse_table.parse_table_A(
            administration_sanction_info)

    def parse_ent_pub_equity_change_pages(self, page):
        """
            企业-股权变更
        """
        soup = BeautifulSoup(page, 'html5lib')
        equity_change_info = soup.find('table', {'id': 'table_tzrbgxx'})
        self.crawler.json_dict['ind_comm_pub_equity_change'] = parse_table.parse_table_A(equity_change_info)

    def parse_ent_pub_knowledge_property_pages(self, page):
        """
            企业-解析知识产权出质
        """
        soup = BeautifulSoup(page, 'html5lib')
        knowledge_property_info = soup.find('table', {'id': 'table_zscq'})
        self.crawler.json_dict['ind_comm_pub_knowledge_property'] = parse_table.parse_table_A(knowledge_property_info)

    def parse_other_dept_pub_administration_license_pages(self, page):
        """
        其他
        """
        soup = BeautifulSoup(page, 'html5lib')
        administration_license_info = soup.find('table', {'id': 'table_xzxkother'})
        self.crawler.json_dict['other_dept_pub_administration_license'] = parse_table.parse_table_A(
            administration_license_info)

    def parse_other_dept_pub_administration_sanction_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        administration_sanction_info = soup.find('table', {'id': 'table_qtxzcf'})
        self.crawler.json_dict['other_dept_pub_administration_sanction'] = parse_table.parse_table_A(
            administration_sanction_info)

    def parse_judical_assist_pub_equity_freeze_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        equity_freeze_info = soup.find('table', {'id': 'table_gqdj'})
        self.crawler.json_dict['judical_assist_pub_equity_freeze'] = parse_table.parse_table_A(equity_freeze_info)

    def parse_judical_assist_pub_shareholder_modify_pages(self, page):
        """
        司法
        """
        soup = BeautifulSoup(page, 'html5lib')
        shareholder_modify_info = soup.find('table', {'id': 'table_gdbg'})
        self.crawler.json_dict['judical_assist_pub_shareholder_modify'] = parse_table.parse_table_A(
            shareholder_modify_info)


class TestParser(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.crawler = XinjiangClawer('./enterprise_crawler/xinjiang.json')
        self.parser = self.crawler.parser
        self.crawler.json_dict = {}
        self.crawler.ent_number = '152704000000508'

    def test_crawl_check_page(self):
        isOK = self.crawler.crawl_check_page()
        self.assertEqual(isOK, True)


# if __name__ == '__main__':
#     from CaptchaRecognition import CaptchaRecognition
#     import run
#
#     run.config_logging()
#     XinjiangClawer.code_cracker = CaptchaRecognition('xinjiang')
#     crawler = XinjiangClawer('./enterprise_crawler/xinjiang/xinjiang.json')
#     enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/xinjiang.txt')
#     i = 0
#     for ent_number in enterprise_list:
#         ent_number = ent_number.rstrip('\n')
#         logging.info(
#             '############   Start to crawl enterprise with id %s   ################\n' % ent_number)
#         crawler.run(ent_number=ent_number)
