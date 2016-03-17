#!/usr/bin/env python
# encoding=utf-8
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
import parse_table
import types
import urlparse
import json

ENT_CRAWLER_SETTINGS = os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS and ENT_CRAWLER_SETTINGS.find('settings_pro') >= 0:
    import settings_pro as settings
else:
    import settings


class XinjiangClawer(Crawler):
    """新疆工商公示信息网页爬虫
    """
    # html数据的存储路径
    html_restore_path = settings.html_restore_path + '/xinjiang/'

    # 验证码图片的存储路径
    ckcode_image_path = settings.json_restore_path + '/xinjiang/ckcode.jpg'

    # 验证码文件夹
    ckcode_image_dir_path = settings.json_restore_path + '/xinjiang/'

    # 查询页面
    search_page = html_restore_path + 'search_page.html'

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
        self.parser = XinjiangParser(self)

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
        crawler = XinjiangClawer('./enterprise_crawler/xinjiang/xinjiang.json')
        crawler.ent_number = str(ent_number)
        # 对每个企业都指定一个html的存储目录
        self.html_restore_path = self.html_restore_path + crawler.ent_number + '/'
        if settings.save_html and not os.path.exists(self.html_restore_path):
            CrawlerUtils.make_dir(self.html_restore_path)

        page = self.crawl_check_page()
        if page is None:
            settings.logger.error(
                'According to the registration number does not search to the company %s' % self.ent_number)
            return False
        page = crawler.crawl_ind_comm_pub_basic_pages(page)
        if page is None:
            return False
        crawler.parser.parse_ind_comm_pub_basic_pages(page)
        page = crawler.crawl_ind_comm_pub_arch_pages()
        crawler.parser.parse_ind_comm_pub_arch_pages(page)
        page = crawler.crawl_ind_comm_pub_movable_property_reg_pages()
        crawler.parser.parse_ind_comm_pub_movable_property_reg_pages(page)
        page = crawler.crawl_ind_comm_pub_equity_ownership_reg_pages()
        crawler.parser.parse_ind_comm_pub_equity_ownership_reg_pages(page)
        page = crawler.crawl_ind_comm_pub_administration_sanction_pages()
        crawler.parser.parse_ind_comm_pub_administration_sanction_pages(page)
        page = crawler.crawl_ind_comm_pub_business_exception_pages()
        crawler.parser.parse_ind_comm_pub_business_exception_pages(page)
        page = crawler.crawl_ind_comm_pub_serious_violate_law_pages()
        crawler.parser.parse_ind_comm_pub_serious_violate_law_pages(page)
        page = crawler.crawl_ind_comm_pub_spot_check_pages()
        crawler.parser.parse_ind_comm_pub_spot_check_pages(page)
        page = crawler.crawl_ent_pub_shareholder_capital_contribution_pages()
        crawler.parser.parse_ent_pub_shareholder_capital_contribution_pages(page)
        page = crawler.crawl_ent_pub_ent_annual_report_pages()
        crawler.parser.parse_ent_pub_ent_annual_report_pages(page)
        page = crawler.crawl_ent_pub_administration_license_pages()
        crawler.parser.parse_ent_pub_administration_license_pages(page)
        page = crawler.crawl_ent_pub_administration_sanction_pages()
        crawler.parser.parse_ent_pub_administration_sanction_pages(page)
        page = crawler.crawl_ent_pub_equity_change_pages()
        crawler.parser.parse_ent_pub_equity_change_pages(page)
        page = crawler.crawl_ent_pub_knowledge_property_pages()
        crawler.parser.parse_ent_pub_knowledge_property_pages(page)
        page = crawler.crawl_other_dept_pub_administration_license_pages()
        crawler.parser.parse_other_dept_pub_administration_license_pages(page)
        page = crawler.crawl_other_dept_pub_administration_sanction_pages()
        crawler.parser.parse_other_dept_pub_administration_sanction_pages(page)
        page = crawler.crawl_judical_assist_pub_equity_freeze_pages()
        crawler.parser.parse_judical_assist_pub_equity_freeze_pages(page)
        page = crawler.crawl_judical_assist_pub_shareholder_modify_pages()
        crawler.parser.parse_judical_assist_pub_shareholder_modify_pages(page)

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
            data = {'currentPageNo': 1, 'yzm': ck_code, 'maent.entname': self.ent_number, 'pName': self.ent_number,
                    'BA_ZCH': self.ent_number}
            params = {}
            params['method'] = 'list'
            params['djjg'] = ''
            params['random'] = long(time.time())
            resp = self.reqst.post(XinjiangClawer.urls['post_checkCode'], data=data, params=params)

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
        times = long(time.time())
        params = {}
        params['method'] = 'createYzm'
        params['dt'] = times
        params['random'] = times

        resp = self.reqst.get(XinjiangClawer.urls['get_checkcode'], params=params)
        if resp.status_code != 200:
            settings.logger.error('failed to get get_checkcode')
            return None
        time.sleep(random.uniform(0.1, 0.2))
        self.write_file_mutex.acquire()
        if not path.isdir(self.ckcode_image_dir_path):
            os.makedirs(self.ckcode_image_dir_path)
        with open(self.ckcode_image_path, 'wb') as f:
            f.write(resp.content)

        # Test
        # with open(self.ckcode_image_dir_path + 'image' + str(i) + '.jpg', 'wb') as f:
        #     f.write(resp.content)

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

    def crawl_page_by_post_data(self, data, name='detail.html'):
        """
        通过传入不同的参数获得不同的页面
        """
        resp = self.reqst.post(XinjiangClawer.urls['post_all_page'], data=data)
        if resp.status_code != 200:
            settings.logger.error('crawl page by url failed! url = %s' % XinjiangClawer.urls['post_all_page'])
        page = resp.content
        time.sleep(random.uniform(0.1, 0.3))
        if settings.save_html:
            CrawlerUtils.save_page_to_file(self.html_restore_path + name, page)
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
        # if biangeng_table is None:
        #     return
        # ind_comm_pub_reg_modifies = []
        # modifies_trs = biangeng_table.find_all('tr')
        # if len(modifies_trs) > 2:
        #     i = 2
        #     while i < len(modifies_trs) - 1:
        #         ind_comm_pub_reg_modify = {}
        #         tds = modifies_trs[i].find_all('td')
        #         if (len(tds) == 0):
        #             break
        #         ind_comm_pub_reg_modify[u'变更事项'] = self.wipe_off_newline_and_blank_for_fe(tds[0].get_text())
        #         ind_comm_pub_reg_modify[u'变更前内容'] = self.wipe_off_newline_and_blank_for_fe(tds[1].get_text())
        #         ind_comm_pub_reg_modify[u'变更后内容'] = self.wipe_off_newline_and_blank_for_fe(tds[2].get_text())
        #         ind_comm_pub_reg_modify[u'变更日期'] = self.wipe_off_newline_and_blank_for_fe(tds[3].get_text())
        #         ind_comm_pub_reg_modifies.append(ind_comm_pub_reg_modify)
        #         i += 1
        self.crawler.json_dict['ind_comm_pub_reg_modify'] = parse_table.parse_table_A(biangeng_table)

    def parse_ind_comm_pub_arch_pages(self, page):
        ck_string = '暂无数据'
        soup = BeautifulSoup(page, 'html5lib')
        beian_div = soup.find('div', {'id': 'beian'})
        zyry_table = beian_div.find('table', {'id': 'table_ry1'})
        ind_comm_pub_arch_key_persons = []
        key_persons = zyry_table.find_all('td')
        i = 0
        while i < len(key_persons) - 3:
            if (len(key_persons) < 3):
                break
            ind_comm_pub_arch_key_person = {}
            ind_comm_pub_arch_key_person[u'序号'] = key_persons[i].get_text()
            ind_comm_pub_arch_key_person[u'姓名'] = key_persons[i + 1].get_text()
            ind_comm_pub_arch_key_person[u'职务'] = key_persons[i + 2].get_text()
            i += 3
            ind_comm_pub_arch_key_persons.append(ind_comm_pub_arch_key_person)

        self.crawler.json_dict['ind_comm_pub_arch_key_persons'] = ind_comm_pub_arch_key_persons
        # 分支机构

        arch_branch_info = beian_div.find('table', {'id': 'table_fr2'})
        arch_branch_trs = arch_branch_info.find_all('tr')
        detail_arch_branch_infoes = []
        if len(arch_branch_trs) > 2:
            i = 2
            while i < len(arch_branch_trs) - 1:
                detail_arch_branch_info = {}
                tds = arch_branch_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                detail_arch_branch_info[u'序号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[0].get_text())
                detail_arch_branch_info[u'注册号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[1].get_text())
                detail_arch_branch_info[u'名称'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[2].get_text())
                detail_arch_branch_info[u'登记机关'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[3].get_text())
                detail_arch_branch_infoes.append(detail_arch_branch_info)
                i += 1

        self.crawler.json_dict['ind_comm_pub_arch_branch'] = detail_arch_branch_infoes


        # 清算信息

    def parse_ind_comm_pub_movable_property_reg_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 动产抵押
        ck_string = '暂无数据'
        movable_property_reg_info = soup.find('table', {'id': 'table_dc'})
        movable_property_reg_trs = movable_property_reg_info.find_all('tr')
        detail_movable_property_reg_infoes = []
        if len(movable_property_reg_trs) > 2:
            i = 2
            while i < len(movable_property_reg_trs):
                if ck_string in movable_property_reg_info.get_text():
                    break
                detail_movable_property_reg_info = {}
                tds = movable_property_reg_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                detail_movable_property_reg_info[u'序号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[0].get_text())
                detail_movable_property_reg_info[u'登记编号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[1].get_text())
                detail_movable_property_reg_info[u'登记日期'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[2].get_text())
                detail_movable_property_reg_info[u'登记机关'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[3].get_text())
                detail_movable_property_reg_info[u'被担保债权数额'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[4].get_text())
                detail_movable_property_reg_info[u'状态'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[5].get_text())
                detail_movable_property_reg_infoes.append(detail_movable_property_reg_info)
                i += 1
        self.crawler.json_dict['ind_comm_pub_movable_property_reg'] = detail_movable_property_reg_infoes

    def parse_ind_comm_pub_equity_ownership_reg_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 股权出质
        equity_ownership_reges = []
        equity_table = soup.find('table', {'id': 'table_gq'})
        ck_string = '暂无数据'
        if ck_string in equity_table.get_text():
            return
        equity_trs = equity_table.find_all('tr')
        if len(equity_trs) > 2:
            i = 2
            while i < len(equity_trs):
                equity_ownership_reg = {}
                tds = equity_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                equity_ownership_reg[u'序号'] = self.wipe_off_newline_and_blank_for_fe(tds[0].get_text())
                equity_ownership_reg[u'登记编号'] = self.wipe_off_newline_and_blank_for_fe(tds[1].get_text())
                equity_ownership_reg[u'出质人'] = self.wipe_off_newline_and_blank_for_fe(tds[2].get_text())
                equity_ownership_reg[u'证照/证件号码（类型'] = self.wipe_off_newline_and_blank_for_fe(tds[3].get_text())
                equity_ownership_reg[u'出质股权数额'] = self.wipe_off_newline_and_blank_for_fe(tds[4].get_text())
                equity_ownership_reg[u'质权人'] = self.wipe_off_newline_and_blank_for_fe(tds[5].get_text())
                equity_ownership_reg[u'证照/证件号码（类型'] = self.wipe_off_newline_and_blank_for_fe(tds[6].get_text())
                equity_ownership_reg[u'股权出质设立登记日期'] = self.wipe_off_newline_and_blank_for_fe(tds[7].get_text())
                equity_ownership_reg[u'状态'] = self.wipe_off_newline_and_blank_for_fe(tds[8].get_text())
                equity_ownership_reg[u'变化情况'] = None
                equity_ownership_reges.append(equity_ownership_reg)
                i += 1
        self.crawler.json_dict['ind_comm_pub_equity_ownership_reg'] = equity_ownership_reges

    def parse_ind_comm_pub_administration_sanction_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        ck_string = '暂无数据'
        # 行政处罚
        administration_sanction_info = soup.find('table', {'id': 'table_gscfxx'})
        administration_sanction_trs = administration_sanction_info.find_all('tr')
        detail_administration_sanction_infoes = []
        if len(administration_sanction_trs) > 2:
            i = 2
            while i < len(administration_sanction_trs):
                if ck_string in administration_sanction_info.get_text():
                    break
                detail_administration_sanction_info = {}
                tds = administration_sanction_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                detail_administration_sanction_info[u'序号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[0].get_text())
                detail_administration_sanction_info[u'行政处罚决定书文号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[1].get_text())
                detail_administration_sanction_info[u'违法行为类型'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[2].get_text())
                detail_administration_sanction_info[u'行政处罚内容'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[3].get_text())
                detail_administration_sanction_info[u'作出行政处罚决定机关名称'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[4].get_text())
                detail_administration_sanction_info[u'作出行政处罚决定日期'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[5].get_text())
                detail_administration_sanction_info[u'公示日期'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[6].get_text())
                detail_administration_sanction_infoes.append(detail_administration_sanction_info)
                i += 1
        self.crawler.json_dict['ind_comm_pub_administration_sanction'] = detail_administration_sanction_infoes

    def parse_ind_comm_pub_business_exception_pages(self, page):
        """
        经营异常
        """
        soup = BeautifulSoup(page, 'html5lib')
        ck_string = '暂无数据'
        business_exception_info = soup.find('table', {'id': 'table_yc'})
        business_exception_trs = business_exception_info.find_all('tr')
        detail_business_exception_infoes = []
        if len(business_exception_trs) > 2:
            i = 2
            while i < len(business_exception_trs):
                if ck_string in business_exception_info.get_text():
                    break
                detail_business_exception_info = {}
                tds = business_exception_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                detail_business_exception_info[u'序号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[0].get_text())
                detail_business_exception_info[u'列入经营异常名录原因'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[1].get_text())
                detail_business_exception_info[u'列入日期'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[2].get_text())
                detail_business_exception_info[u'移出经营异常名录原因'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[3].get_text())
                detail_business_exception_info[u'移出日期'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[4].get_text())
                detail_business_exception_info[u'作出决定机关'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[5].get_text())
                detail_business_exception_infoes.append(detail_business_exception_info)
                i += 1
        self.crawler.json_dict['ind_comm_pub_business_exception'] = detail_business_exception_infoes

    def parse_ind_comm_pub_serious_violate_law_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 严重违法
        ck_string = '暂无数据'
        serious_violate_law_info = soup.find('table', {'id': 'table_wfxx'})
        serious_violate_law_trs = serious_violate_law_info.find_all('tr')
        detail_serious_violate_law_infoes = []
        if len(serious_violate_law_trs) > 2:
            i = 2
            while i < len(serious_violate_law_trs):
                if ck_string in serious_violate_law_info.get_text():
                    break
                detail_serious_violate_law_info = {}
                tds = serious_violate_law_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                detail_serious_violate_law_info[u'序号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[0].get_text())
                detail_serious_violate_law_info[u'列入严重违法企业名单原因'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[1].get_text())
                detail_serious_violate_law_info[u'列入日期'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[2].get_text())
                detail_serious_violate_law_info[u'移出严重违法企业名单原因'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[3].get_text())
                detail_serious_violate_law_info[u'移出日期'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[4].get_text())
                detail_serious_violate_law_info[u'作出决定机关'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[5].get_text())
                detail_serious_violate_law_infoes.append(detail_serious_violate_law_info)
                i += 1
        self.crawler.json_dict['ind_comm_pub_serious_violate_law'] = detail_serious_violate_law_infoes

    def parse_ind_comm_pub_spot_check_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 抽查检查
        ck_string = '暂无数据'
        spot_check_info = soup.find('table', {'id': 'table_ccjc'})
        spot_check_trs = spot_check_info.find_all('tr')
        detail_spot_check_infoes = []
        if len(spot_check_trs) > 2:
            i = 2
            while i < len(spot_check_trs):
                if ck_string in spot_check_info.get_text():
                    break
                detail_spot_check_info = {}
                tds = spot_check_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                detail_spot_check_info[u'序号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[0].get_text())
                detail_spot_check_info[u'检查实施机关'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[1].get_text())
                detail_spot_check_info[u'类型'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[2].get_text())
                detail_spot_check_info[u'日期'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[3].get_text())
                detail_spot_check_info[u'结果'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[4].get_text())
                detail_spot_check_infoes.append(detail_spot_check_info)
                i += 1
        self.crawler.json_dict['ind_comm_pub_spot_check'] = detail_spot_check_infoes

    def parse_ent_pub_shareholder_capital_contribution_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 股东出资
        shareholder_capital_contributiones = []
        equity_table = soup.find('table', {'id': 'table_qytzr'})
        equity_trs = equity_table.find_all('tr')
        if len(equity_trs) > 3:
            i = 3
            while i < len(equity_trs) - 1:
                tds = equity_trs[i].find_all('td')
                shareholder_capital_contribution = {}
                if len(tds) <= 0:
                    break
                shareholder_capital_contribution[u'股东'] = self.wipe_off_newline_and_blank_for_fe(tds[0].get_text())
                shareholder_capital_contribution[u'认缴额'] = self.wipe_off_newline_and_blank_for_fe(tds[1].get_text())
                shareholder_capital_contribution[u'实缴额'] = self.wipe_off_newline_and_blank_for_fe(tds[2].get_text())
                shareholder_capital_contribution[u'认缴出资方式'] = self.wipe_off_newline_and_blank_for_fe(tds[3].get_text())
                shareholder_capital_contribution[u'认缴出资额'] = self.wipe_off_newline_and_blank_for_fe(tds[4].get_text())
                shareholder_capital_contribution[u'认缴出资日期'] = self.wipe_off_newline_and_blank_for_fe(tds[5].get_text())
                shareholder_capital_contribution[u'认缴公示日期'] = self.wipe_off_newline_and_blank_for_fe(tds[6].get_text())
                shareholder_capital_contribution[u'实缴出资方式'] = self.wipe_off_newline_and_blank_for_fe(tds[7].get_text())
                shareholder_capital_contribution[u'实缴出资额'] = self.wipe_off_newline_and_blank_for_fe(tds[8].get_text())
                shareholder_capital_contribution[u'实缴出资额'] = self.wipe_off_newline_and_blank_for_fe(tds[9].get_text())
                shareholder_capital_contribution[u'实缴出资日期'] = self.wipe_off_newline_and_blank_for_fe(tds[10].get_text())
                if (len(tds) >= 12):
                    shareholder_capital_contribution[u'实缴公示日期'] = self.wipe_off_newline_and_blank_for_fe(tds[11].get_text())

                shareholder_capital_contributiones.append(shareholder_capital_contribution)
                i += 1
        self.crawler.json_dict['ent_pub_shareholder_capital_contribution'] = shareholder_capital_contributiones

        # 企业变更信息
        reg_modify_info = soup.find('table', {'id': 'table_tzrxxbg'})
        reg_modify_trs = reg_modify_info.find_all('tr')
        detail_reg_modify_infoes = []
        if len(reg_modify_trs) > 2:
            i = 2
            while i < len(reg_modify_trs):
                detail_reg_modify_info = {}
                tds = reg_modify_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                detail_reg_modify_info[u'序号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[0].get_text())
                detail_reg_modify_info[u'变更事项'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[1].get_text())
                detail_reg_modify_info[u'变更时间'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[2].get_text())
                detail_reg_modify_info[u'变更前'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[3].get_text())
                detail_reg_modify_info[u'变更后'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[4].get_text())

                detail_reg_modify_infoes.append(detail_reg_modify_info)
                i += 1
        self.crawler.json_dict['ent_pub_reg_modify'] = detail_reg_modify_infoes

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
                website_trs = website_info.find_all('tr')
                detail_website_infoes = []
                if len(website_trs) > 2:
                    i = 2
                    while i < len(website_trs):
                        detail_website_info = {}
                        tds = website_trs[i].find_all('td')
                        if len(tds) <= 0:
                            break
                        detail_website_info[u'类型'] = self.wipe_off_newline_and_blank_for_fe(tds[0].get_text())
                        detail_website_info[u'名称'] = self.wipe_off_newline_and_blank_for_fe(tds[1].get_text())
                        detail_website_info[u'网址'] = self.wipe_off_newline_and_blank_for_fe(tds[2].get_text())
                        detail_website_infoes.append(detail_website_info)
                        i += 1

                detail[u'网站或网店信息'] = detail_website_infoes

                shareholder_capital_contribution_info = soup_reoprt.find('table', {'id': 'table_tzrxx'})
                shareholder_capital_contribution_trs = shareholder_capital_contribution_info.find_all('tr')
                detail_shareholder_capital_contribution_infoes = []
                if len(shareholder_capital_contribution_trs) > 2:
                    i = 2
                    while i < len(shareholder_capital_contribution_trs):
                        detail_shareholder_capital_contribution_info = {}
                        tds = shareholder_capital_contribution_trs[i].find_all('td')
                        if len(tds) <= 0:
                            break
                        detail_shareholder_capital_contribution_info[u'股东'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[0].get_text())
                        detail_shareholder_capital_contribution_info[u'认缴出资额'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[1].get_text())
                        detail_shareholder_capital_contribution_info[
                            u'认缴出资时间'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[2].get_text())
                        detail_shareholder_capital_contribution_info[
                            u'认缴出资方式'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[3].get_text())
                        detail_shareholder_capital_contribution_info[u'实缴出资额'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[4].get_text())
                        detail_shareholder_capital_contribution_info[u'出资时间'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[5].get_text())
                        detail_shareholder_capital_contribution_info[u'出资方式'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[6].get_text())
                        detail_shareholder_capital_contribution_infoes.append(
                            detail_shareholder_capital_contribution_info)
                        i += 1
                detail[u'股东及出资信息'] = detail_shareholder_capital_contribution_infoes

                outbound_investment_info = soup_reoprt.find('table', {'id': 'table_tzxx'})
                outbound_investment_trs = outbound_investment_info.find_all('tr')
                detail_outbound_investment_infoes = []
                if len(outbound_investment_trs) > 2:
                    i = 2
                    while i < len(outbound_investment_trs):
                        tds = outbound_investment_trs[i].find_all('tr')
                        if len(tds) <= 0:
                            break
                        detail_outbound_investment_info = {}
                        detail_outbound_investment_info[u'投资设立企业或购买股权企业名称'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[0].get_text())
                        detail_outbound_investment_info[u'注册号'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[1].get_text())
                        detail_outbound_investment_infoes.append(detail_outbound_investment_info)
                        i += 1

                detail[u'对外投资信息'] = detail_outbound_investment_infoes

                # state_of_enterprise_assets_info = soup_reoprt.find('table', {'id': 't05'})
                # state_of_enterprise_assets_trs = state_of_enterprise_assets_info.find_all('tr')
                # detail_state_of_enterprise_assets_infoes = {}
                # detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[1].find_all('th')[
                #     0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                #         state_of_enterprise_assets_trs[1].find_all('td')[0].get_text())
                # detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[1].find_all('th')[
                #     1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                #         state_of_enterprise_assets_trs[1].find_all('td')[1].get_text())
                # detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[2].find_all('th')[
                #     0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                #         state_of_enterprise_assets_trs[2].find_all('td')[0].get_text())
                # detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[2].find_all('th')[
                #     1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                #         state_of_enterprise_assets_trs[2].find_all('td')[1].get_text())
                # detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[3].find_all('th')[
                #     0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                #         state_of_enterprise_assets_trs[3].find_all('td')[0].get_text())
                # detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[3].find_all('th')[
                #     1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                #         state_of_enterprise_assets_trs[3].find_all('td')[1].get_text())
                # detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[4].find_all('th')[
                #     0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                #         state_of_enterprise_assets_trs[4].find_all('td')[0].get_text())
                # detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[4].find_all('th')[
                #     1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                #         state_of_enterprise_assets_trs[4].find_all('td')[1].get_text())
                #
                # detail[u'企业资产状况信息'] = detail_state_of_enterprise_assets_infoes

                provide_guarantee_to_the_outside_info = soup_reoprt.find('table', {'id': 'table_dbxx'})
                provide_guarantee_to_the_outside_trs = provide_guarantee_to_the_outside_info.find_all('tr')
                detail_provide_guarantee_to_the_outside_infoes = []
                if len(provide_guarantee_to_the_outside_trs) > 2:
                    i = 2
                    while i < len(provide_guarantee_to_the_outside_trs):
                        detail_provide_guarantee_to_the_outside_info = {}
                        tds = provide_guarantee_to_the_outside_trs[i].find_all('td')
                        if len(tds) <= 0:
                            break
                        detail_provide_guarantee_to_the_outside_info[u'债权人'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[0].get_text())
                        detail_provide_guarantee_to_the_outside_info[u'债务人'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[1].get_text())
                        detail_provide_guarantee_to_the_outside_info[u'主债权种类'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[2].get_text())
                        detail_provide_guarantee_to_the_outside_info[u'主债权数额'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[3].get_text())
                        detail_provide_guarantee_to_the_outside_info[
                            u'履行债务的期限'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[4].get_text())
                        detail_provide_guarantee_to_the_outside_info[u'保证的期间'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[5].get_text())
                        detail_provide_guarantee_to_the_outside_info[u'保证的方式'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[6].get_text())
                        detail_provide_guarantee_to_the_outside_info[
                            u'保证担保的范围'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[7].get_text())
                        detail_provide_guarantee_to_the_outside_infoes.append(
                            detail_provide_guarantee_to_the_outside_info)
                        i += 1
                detail[u'对外提供保证担保信息'] = detail_provide_guarantee_to_the_outside_infoes

                ent_pub_equity_change_info = soup_reoprt.find('table', {'id': 'table_gqbg'})
                ent_pub_equity_change_trs = ent_pub_equity_change_info.find_all('tr')
                detail_ent_pub_equity_change_infoes = []
                if len(ent_pub_equity_change_trs) > 2:
                    i = 2
                    while i < len(ent_pub_equity_change_trs):
                        detail_ent_pub_equity_change_info = {}
                        tds = ent_pub_equity_change_trs[i].find_all('td')
                        if len(tds) <= 0:
                            break
                        detail_ent_pub_equity_change_info[u'股东'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[0].get_text())
                        detail_ent_pub_equity_change_info[u'变更前股权比例'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[1].get_text())
                        detail_ent_pub_equity_change_info[u'变更后股权比例'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[2].get_text())
                        detail_ent_pub_equity_change_info[u'股权变更日期'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[3].get_text())
                        detail_ent_pub_equity_change_infoes.append(detail_ent_pub_equity_change_info)
                        i += 1
                detail[u'股权变更信息'] = detail_ent_pub_equity_change_infoes

                change_record_info = ent_pub_equity_change_info = soup_reoprt.find('table', {'id': 'table_bgxx'})
                change_record_trs = change_record_info.find_all('tr')
                detail_change_record_infoes = []
                if len(change_record_trs) > 2:
                    i = 2
                    while i < len(change_record_trs):
                        detail_change_record_info = {}
                        tds = change_record_trs[i].find_all('td')
                        if len(tds) <= 0:
                            break
                        detail_change_record_info[u'序号'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[0].get_text())
                        detail_change_record_info[u'修改事项'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[1].get_text())
                        detail_change_record_info[u'修改前'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[2].get_text())
                        detail_change_record_info[u'修改后'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[3].get_text())
                        detail_change_record_info[u'修改日期'] = self.wipe_off_newline_and_blank_for_fe(
                            tds[4].get_text())
                        detail_change_record_infoes.append(detail_change_record_info)
                        i += 1
                detail[u'修改记录'] = detail_change_record_infoes
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
        administration_license_trs = administration_license_info.find_all('tr')
        detail_administration_license_infoes = []
        if len(administration_license_trs) > 2:
            i = 2
            while i < len(administration_license_trs):
                if ck_string in administration_license_info.get_text():
                    break
                detail_administration_license_info = {}
                tds = administration_license_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                detail_administration_license_info[u'序号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[0].get_text())
                detail_administration_license_info[u'许可文件编号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[1].get_text())
                detail_administration_license_info[u'许可文件名称'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[2].get_text())
                detail_administration_license_info[u'有效期自'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[3].get_text())
                detail_administration_license_info[u'有效期至'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[4].get_text())
                detail_administration_license_info[u'许可机关'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[5].get_text())
                detail_administration_license_info[u'许可内容'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[6].get_text())
                detail_administration_license_info[u'状态'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[7].get_text())
                detail_administration_license_info[u'公示日期'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[8].get_text())
                detail_administration_license_info[u'详情'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[9].get_text())
                detail_administration_license_infoes.append(detail_administration_license_info)
                i += 1
        self.crawler.json_dict['ind_comm_pub_administration_license'] = detail_administration_license_infoes

    def parse_ent_pub_administration_sanction_pages(self, page):
        """
        企业-解析行政处罚
        """
        soup = BeautifulSoup(page, 'html5lib')
        ck_string = '暂无数据'
        administration_sanction_info = soup.find('table', {'id': 'table_qyxzcf'})
        if administration_sanction_info is None:
            return
        # administration_sanction_trs = administration_sanction_info.find_all('tr')
        # detail_administration_sanction_infoes = []
        # if len(administration_sanction_trs) > 2:
        #     i = 2
        #     while i < len(administration_sanction_trs):
        #         if ck_string in administration_sanction_info.get_text():
        #             break
        #         detail_administration_sanction_info = {}
        #         tds = administration_sanction_trs[i].find_all('td')
        #         if len(tds) <= 0:
        #             break
        #         detail_administration_sanction_info[u'序号'] = self.wipe_off_newline_and_blank_for_fe(
        #             tds[0].get_text())
        #         detail_administration_sanction_info[u'行政处罚决定书文号'] = self.wipe_off_newline_and_blank_for_fe(
        #             tds[1].get_text())
        #         detail_administration_sanction_info[u'行政处罚类型'] = self.wipe_off_newline_and_blank_for_fe(
        #             tds[2].get_text())
        #         detail_administration_sanction_info[u'行政处罚内容'] = self.wipe_off_newline_and_blank_for_fe(
        #             tds[3].get_text())
        #         detail_administration_sanction_info[u'作出行政处罚决定机关名称'] = self.wipe_off_newline_and_blank_for_fe(
        #             tds[4].get_text())
        #         detail_administration_sanction_info[u'作出行政处罚决定日期'] = self.wipe_off_newline_and_blank_for_fe(
        #             tds[5].get_text())
        #         detail_administration_sanction_info[u'公示日期'] = self.wipe_off_newline_and_blank_for_fe(
        #             tds[6].get_text())
        #         detail_administration_sanction_info[u'备注'] = self.wipe_off_newline_and_blank_for_fe(
        #             tds[7].get_text())
        #         detail_administration_sanction_infoes.append(detail_administration_sanction_info)
        #         i += 1
        # self.crawler.json_dict['ind_comm_pub_administration_sanction'] = detail_administration_sanction_infoes
        self.crawler.json_dict['ind_comm_pub_administration_sanction'] = parse_table.parse_table_A(administration_sanction_info)

    def parse_ent_pub_equity_change_pages(self, page):
        """
            企业-股权变更
        """
        soup = BeautifulSoup(page, 'html5lib')
        ck_string = '暂无数据'
        equity_change_info = soup.find('table', {'id': 'table_tzrbgxx'})
        # equity_change_trs = equity_change_info.find_all('tr')
        # detail_equity_change_infoes = []
        # if len(equity_change_trs) > 2:
        #     i = 2
        #     while i < len(equity_change_trs):
        #         if ck_string in equity_change_info.get_text():
        #             break
        #         detail_equity_change_info = {}
        #         tds = equity_change_trs[i].find_all('td')
        #         if len(tds) <= 0:
        #             break
        #         detail_equity_change_info[u'序号'] = self.wipe_off_newline_and_blank_for_fe(
        #             tds[0].get_text())
        #         detail_equity_change_info[u'股东'] = self.wipe_off_newline_and_blank_for_fe(
        #             tds[1].get_text())
        #         detail_equity_change_info[u'变更前股权比例'] = self.wipe_off_newline_and_blank_for_fe(
        #             tds[2].get_text())
        #         detail_equity_change_info[u'变更后股权比例'] = self.wipe_off_newline_and_blank_for_fe(
        #             tds[3].get_text())
        #         detail_equity_change_info[u'股权变更日期'] = self.wipe_off_newline_and_blank_for_fe(
        #             tds[4].get_text())
        #         detail_equity_change_info[u'填报时间'] = self.wipe_off_newline_and_blank_for_fe(
        #             tds[5].get_text())
        #         detail_equity_change_infoes.append(detail_equity_change_info)
        #         i += 1
        self.crawler.json_dict['ind_comm_pub_equity_change'] = parse_table.parse_table_A(equity_change_info)

    def parse_ent_pub_knowledge_property_pages(self, page):
        """
            企业-解析知识产权出质
        """
        soup = BeautifulSoup(page, 'html5lib')
        ck_string = '暂无数据'
        knowledge_property_info = soup.find('table', {'id': 'table_zscq'})
        if knowledge_property_info is None:
            return
        knowledge_property_trs = knowledge_property_info.find_all('tr')
        detail_knowledge_property_infoes = []
        if len(knowledge_property_trs) > 2:
            i = 2
            while i < len(knowledge_property_trs):
                if ck_string in knowledge_property_info.get_text():
                    break
                detail_knowledge_property_info = {}
                tds = knowledge_property_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                detail_knowledge_property_info[u'序号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[0].get_text())
                detail_knowledge_property_info[u'注册号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[1].get_text())
                detail_knowledge_property_info[u'名称'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[2].get_text())
                detail_knowledge_property_info[u'种类'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[3].get_text())
                detail_knowledge_property_info[u'出质人名称'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[4].get_text())
                detail_knowledge_property_info[u'质权人名称'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[5].get_text())
                detail_knowledge_property_info[u'质权登记期限'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[6].get_text())
                detail_knowledge_property_info[u'状态'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[7].get_text())
                detail_knowledge_property_info[u'公示日期'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[8].get_text())
                detail_knowledge_property_info[u'变化情况'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[9].get_text())
                detail_knowledge_property_infoes.append(detail_knowledge_property_info)
                i += 1
        self.crawler.json_dict['ind_comm_pub_knowledge_property'] = detail_knowledge_property_infoes

    def parse_other_dept_pub_administration_license_pages(self, page):
        """
        其他
        """
        soup = BeautifulSoup(page, 'html5lib')
        ck_string = '暂无数据'
        administration_license_info = soup.find('table', {'id': 'table_xzxkother'})
        administration_license_trs = administration_license_info.find_all('tr')
        detail_administration_license_infoes = []
        if len(administration_license_trs) > 2:
            i = 2
            while i < len(administration_license_trs):
                if ck_string in administration_license_info.get_text():
                    break
                detail_administration_license_info = {}
                tds = administration_license_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                detail_administration_license_info[u'序号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[0].get_text())
                detail_administration_license_info[u'许可文件编号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[1].get_text())
                detail_administration_license_info[u'许可文件名称'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[2].get_text())
                detail_administration_license_info[u'有效期自'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[3].get_text())
                detail_administration_license_info[u'有效期至'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[4].get_text())
                detail_administration_license_info[u'许可机关'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[5].get_text())
                detail_administration_license_info[u'状态'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[6].get_text())

                detail_administration_license_infoes.append(detail_administration_license_info)
                i += 1
        self.crawler.json_dict['other_dept_pub_administration_license'] = detail_administration_license_infoes

    def parse_other_dept_pub_administration_sanction_pages(self, page):
        """
        其他
        """
        soup = BeautifulSoup(page, 'html5lib')
        administration_sanction_info = soup.find('table', {'id': 'table_qtxzcf'})
        if administration_sanction_info is None:
            return
        administration_sanction_trs = administration_sanction_info.find_all('tr')
        detail_administration_sanction_infoes = []
        if len(administration_sanction_trs) > 2:
            i = 2
            while i < len(administration_sanction_trs):
                detail_administration_sanction_info = {}
                tds = administration_sanction_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                detail_administration_sanction_info[u'序号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[0].get_text())
                detail_administration_sanction_info[u'行政处罚决定书文号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[1].get_text())
                detail_administration_sanction_info[u'违法行为类型'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[2].get_text())
                detail_administration_sanction_info[u'行政处罚内容'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[3].get_text())
                detail_administration_sanction_info[u'作出行政处罚决定机关名称'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[4].get_text())
                detail_administration_sanction_info[u'作出行政处罚决定日期'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[5].get_text())

                detail_administration_sanction_infoes.append(detail_administration_sanction_info)
                i += 1
        self.crawler.json_dict['other_dept_pub_administration_sanction'] = detail_administration_sanction_infoes

    def parse_judical_assist_pub_equity_freeze_pages(self, page):
        """
        司法
        """
        soup = BeautifulSoup(page, 'html5lib')
        equity_freeze_info = soup.find('table', {'id': 'table_gqdj'})
        equity_freeze_trs = equity_freeze_info.find_all('tr')
        if equity_freeze_trs is None:
            return
        detail_equity_freeze_infoes = []
        if len(equity_freeze_trs) > 2:
            i = 2
            while i < len(equity_freeze_trs):
                detail_equity_freeze_info = {}
                tds = equity_freeze_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                detail_equity_freeze_info[u'序号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[0].get_text())
                detail_equity_freeze_info[u'被执行人'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[1].get_text())
                detail_equity_freeze_info[u'股权数额'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[2].get_text())
                detail_equity_freeze_info[u'执行法院'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[3].get_text())
                detail_equity_freeze_info[u'协助公示通知书文号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[4].get_text())
                detail_equity_freeze_info[u'状态'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[5].get_text())
                detail_equity_freeze_info[u'详情'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[6].get_text())

                detail_equity_freeze_infoes.append(detail_equity_freeze_info)
                i += 1
        self.crawler.json_dict['judical_assist_pub_equity_freeze'] = detail_equity_freeze_infoes

    def parse_judical_assist_pub_shareholder_modify_pages(self, page):
        """
        司法
        """
        soup = BeautifulSoup(page, 'html5lib')

        shareholder_modify_info = soup.find('table', {'id': 'table_gdbg'})
        if shareholder_modify_info is None:
            return
        shareholder_modify_trs = shareholder_modify_info.find_all('tr')
        if shareholder_modify_trs is None:
            return
        detail_shareholder_modify_infoes = []
        if len(shareholder_modify_trs) > 2:
            i = 2
            while i < len(shareholder_modify_trs):
                detail_shareholder_modify_info = {}
                tds = shareholder_modify_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                detail_shareholder_modify_info[u'序号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[0].get_text())
                detail_shareholder_modify_info[u'被执行人'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[1].get_text())
                detail_shareholder_modify_info[u'股权数额'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[2].get_text())
                detail_shareholder_modify_info[u'受让人'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[3].get_text())
                detail_shareholder_modify_info[u'执行法院'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[4].get_text())
                detail_shareholder_modify_info[u'详情'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[5].get_text())

                detail_shareholder_modify_infoes.append(detail_shareholder_modify_info)
                i += 1
        self.crawler.json_dict['judical_assist_pub_shareholder_modify'] = detail_shareholder_modify_infoes


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


if __name__ == '__main__':
    from CaptchaRecognition import CaptchaRecognition
    import run

    run.config_logging()
    XinjiangClawer.code_cracker = CaptchaRecognition('xinjiang')
    crawler = XinjiangClawer('./enterprise_crawler/xinjiang/xinjiang.json')
    enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/xinjiang.txt')
    i = 0
    for ent_number in enterprise_list:
        ent_number = ent_number.rstrip('\n')
        settings.logger.info(
            '############   Start to crawl enterprise with id %s   ################\n' % ent_number)
        crawler.run(ent_number=ent_number)
