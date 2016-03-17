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
import types
import urlparse
import json

from enterprise.libs.proxies import Proxies
from . import settings
from enterprise.libs.CaptchaRecognition import CaptchaRecognition
import logging
from enterprise.libs.proxies import Proxies


class JiangxiCrawler(Crawler):
    """甘肃工商公示信息网页爬虫
    """
    # html数据的存储路径
    html_restore_path = settings.json_restore_path + '/jiangxi/'

    # 验证码图片的存储路径
    ckcode_image_path = settings.json_restore_path + '/jiangxi/ckcode.jpg'

    # 验证码文件夹
    ckcode_image_dir_path = settings.json_restore_path + '/jiangxi/'
    code_cracker = CaptchaRecognition('jiangxi')
    # 查询页面
    # search_page = html_restore_path + 'search_page.html'

    # 多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()
    urls = {'host': 'http://gsxt.jxaic.gov.cn',
            'main': 'http://gsxt.jxaic.gov.cn/ECPS/',
            'get_checkcode': 'http://gsxt.jxaic.gov.cn/ECPS/verificationCode.jsp?',
            'post_checkCode': 'http://gsxt.jxaic.gov.cn/ECPS/qyxxgsAction_checkVerificationCode.action?',
            'post_checkCode2': 'http://gsxt.jxaic.gov.cn/ECPS/qyxxgsAction_queryXyxx.action?',
            'ind_comm_pub_reg_basic': 'http://gsxt.jxaic.gov.cn/ECPS/qyxxgsAction_initQyjbqk.action?',
            'ind_comm_pub_reg_shareholder': 'http://gsxt.jxaic.gov.cn/ECPS/tzrczxxAction_init.action?',
            'ind_comm_pub_reg_modify': 'http://gsxt.jxaic.gov.cn/ECPS/qybgxxAction_init.action?',
            'ind_comm_pub_arch_key_persons': 'http://gsxt.jxaic.gov.cn/ECPS/qybaxxAction_zyryxx.action?',
            'ind_comm_pub_arch_branch': 'http://gsxt.jxaic.gov.cn/ECPS/qybaxxAction_fgsxx.action?',
            'ind_comm_pub_arch_liquidation': 'http://gsxt.jxaic.gov.cn/ECPS/qybaxxAction_qsxx.action?',
            'ind_comm_pub_movable_property_reg': 'http://gsxt.jxaic.gov.cn/ECPS/dcdyxxAction_init.action?',
            'ind_comm_pub_equity_ownership_reg': 'http://gsxt.jxaic.gov.cn/ECPS/gqczdjxxAction_gqczdjxx.action?',
            'ind_comm_pub_administration_sanction': 'http://gsxt.jxaic.gov.cn/ECPS/xzcfxxAction_initXzcfxx.action?',
            'ind_comm_pub_business_exception': 'http://gsxt.jxaic.gov.cn/ECPS/jyycxxAction_init.action?',
            'ind_comm_pub_serious_violate_law': 'http://gsxt.jxaic.gov.cn/ECPS/yzwfxxAction_init.action',
            'ind_comm_pub_spot_check': 'http://gsxt.jxaic.gov.cn/ECPS/ccjcxxAction_init.action?',
            'ent_pub_ent_annual_report': 'http://gsxt.jxaic.gov.cn/ECPS/qyNbxxAction_init.action??',
            'ent_pub_shareholder_capital_contribution': 'http://gsxt.jxaic.gov.cn/ECPS/qyTzrxxAction_init.action?',
            'ent_pub_equity_change': 'http://gsxt.jxaic.gov.cn/ECPS/qyGqbgxxAction_init.action?',
            'ent_pub_administration_license': 'http://gsxt.jxaic.gov.cn/ECPS/qyZzxkxxAction_init.action?',
            'ent_pub_knowledge_property': 'http://gsxt.jxaic.gov.cn/ECPS/qyZscqczxxAction_init.action?',
            'ent_pub_administration_sanction': 'http://gsxt.jxaic.gov.cn/ECPS/qyXzcfxxAction_initXzcfxx.action?',
            'ent_pub_reg_modify': 'http://gsxt.jxaic.gov.cn/ECPS/qyTzrxxAction_init.action?',
            'other_dept_pub_administration_license': 'http://gsxt.jxaic.gov.cn/ECPS/otherZzxkAction_init.action?',
            'other_dept_pub_administration_sanction': 'http://gsxt.jxaic.gov.cn/ECPS/otherXzcfAction_initXzcfxx.action?',
            'judical_assist_pub_equity_freeze': 'http://gsxt.jxaic.gov.cn/ECPS/sfxzAction_initSfxzMain.action?',
            'judical_assist_pub_shareholder_modify': 'http://gsxt.jxaic.gov.cn/ECPS/sfxzAction_initSfxzMain.action?',
            'report_baseinfo': 'http://gsxt.jxaic.gov.cn/ECPS/qyNbxxAction_qyjbxx.action?',
            'report_website': 'http://gsxt.jxaic.gov.cn/ECPS/qyNbxxAction_wzxx.action?',
            'report_shareholder': 'http://gsxt.jxaic.gov.cn/ECPS/qyNbxxAction_initMain.action?',
            'report_out_invest': 'http://gsxt.jxaic.gov.cn/ECPS/qyNbxxAction_dwtzxx.action?',
            'report_public_of_ent': 'http://gsxt.jxaic.gov.cn/ECPS/qyNbxxAction_qyzcxx.action?',
            'report_offer_security': 'http://gsxt.jxaic.gov.cn/ECPS/qyNbxxAction_dwdbxx.action?',
            'report_shareholder_change': 'http://gsxt.jxaic.gov.cn/ECPS/qyNbxxAction_gqbgxx.action?',
            'report_record_of_modifies': 'http://gsxt.jxaic.gov.cn/ECPS/qyNbxxAction_xgjlxx.action?',
            }

    def __init__(self, json_restore_path=None):
        """
        初始化函数
        Args:
            json_restore_path: json文件的存储路径，所有江苏的企业，应该写入同一个文件，因此在多线程爬取时设置相同的路径。同时，
             需要在写入文件的时候加锁
        Returns:
        """
        self.json_restore_path = json_restore_path
        self.parser = JiangxiParser(self)

        self.reqst = requests.Session()
        self.reqst.headers.update({
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})
        self.json_dict = {}
        p = Proxies()
        # p.filename = "/Users/princetechs5/crawler/nice-clawer/clawer/enterprise/libs/proxies/1457663081"
        self.proxies = p.get_proxies()
        self.timeout = 30
        self.ent_number = None
        self.results = None
        p = Proxies()
        self.proxies = p.get_proxies()

    def run(self, ent_number=0):
        crawler = JiangxiCrawler('./enterprise_crawler/jiangxi/jiangxi.json')

        crawler.ent_number = str(ent_number)
        if not os.path.exists(self.html_restore_path):
            os.makedirs(self.html_restore_path)

        crawler.json_dict = {}
        # get main page
        resp = self.reqst.get(JiangxiCrawler.urls['main'], proxies= self.proxies, timeout= 20)
        if resp.status_code != 200:
            logging.error('failed to get main page')
            return None
        page = crawler.crawl_check_page()
        if page is None:
            logging.error(
                'According to the registration number does not search to the company %s' % self.ent_number)
            return False
        crawler.results = crawler.parser.parse_search_page(page)
        if crawler.results is None:
            return False
        page = crawler.crawl_ind_comm_pub_reg_basic_pages()
        crawler.parser.parse_ind_comm_pub_basic_pages(page)
        page = crawler.crawl_ind_comm_pub_reg_shareholder_pages()
        crawler.parser.parse_ind_comm_pub_reg_shareholderes_pages(page)
        page = crawler.crawl_ind_comm_pub_reg_modify_pages()
        crawler.parser.parse_ind_comm_pub_reg_modify_pages(page)
        page = crawler.crawl_ind_comm_pub_arch_key_persons_pages()
        crawler.parser.parse_ind_comm_pub_arch_key_persons_pages(page)
        page = crawler.crawl_ind_comm_pub_arch_branch_pages()
        crawler.parser.parse_ind_comm_pub_arch_branch_pages(page)
        # page = crawler.crawl_ind_comm_pub_arch_liquidation_pages()
        page = crawler.crawl_ind_comm_pub_movable_property_reg_pages()
        crawler.parser.parse_ind_comm_pub_movable_property_reg_pages(page)
        page = crawler.crawl_ind_comm_pub_equity_ownership_reg_pages()
        crawler.parser.parse_ind_comm_pub_equity_ownership_reg_pages(page)
        page = crawler.crawl_ind_comm_pub_administration_sanction_pages()
        crawler.parser.parse_ent_pub_administration_sanction_pages(page)
        page = crawler.crawl_ind_comm_pub_business_exception_pages()
        crawler.parser.parse_ind_comm_pub_business_exception_pages(page)
        page = crawler.crawl_ind_comm_pub_serious_violate_law_pages()
        crawler.parser.parse_ind_comm_pub_serious_violate_law_pages(page)
        page = crawler.crawl_ind_comm_pub_spot_check_pages()
        crawler.parser.parse_ind_comm_pub_spot_check_pages(page)
        page = crawler.crawl_ent_pub_ent_annual_report_pages()
        crawler.parser.parse_ent_pub_ent_annual_report_pages(page)
        page = crawler.crawl_ent_pub_shareholder_capital_contribution_pages()
        crawler.parser.parse_ent_pub_shareholder_capital_contribution_pages(page)
        page = crawler.crawl_ent_pub_equity_change_pages()
        crawler.parser.parse_ent_pub_equity_change_pages(page)
        page = crawler.crawl_ent_pub_administration_license_pages()
        crawler.parser.parse_ent_pub_administration_license_pages(page)
        page = crawler.crawl_ent_pub_knowledge_property_pages()
        crawler.parser.parse_ent_pub_knowledge_property_pages(page)
        page = crawler.crawl_ent_pub_administration_sanction_pages()
        crawler.parser.parse_ent_pub_administration_sanction_pages(page)
        page = crawler.crawl_ent_pub_reg_modify_pages()
        crawler.parser.parse_ent_pub_reg_modify_pages(page)
        page = crawler.crawl_other_dept_pub_administration_license_pages()
        crawler.parser.parse_other_dept_pub_administration_license_pages(page)
        page = crawler.crawl_other_dept_pub_administration_sanction_pages()
        crawler.parser.parse_other_dept_pub_administration_sanction_pages(page)
        page = crawler.crawl_judical_assist_pub_equity_freeze_pages()
        crawler.parser.parse_judical_assist_pub_equity_freeze_pages(page)
        page = crawler.crawl_judical_assist_pub_shareholder_modify_pages()
        crawler.parser.parse_judical_assist_pub_shareholder_modify_pages(page)
        return json.dumps({ ent_number: crawler.json_dict})
        # 采用多线程，在写入文件时需要注意加锁
        # self.write_file_mutex.acquire()
        # CrawlerUtils.json_dump_to_file(self.json_restore_path, {crawler.ent_number: crawler.json_dict})
        # self.write_file_mutex.release()
        # return True

    def crawl_check_page(self):
        """爬取验证码页面，包括下载验证码图片以及破解验证码
        :return true or false
        """
        count = 0
        while count < 15:
            ck_code = self.crack_check_code(count)
            data = {'password': ck_code}
            resp = self.reqst.post(JiangxiCrawler.urls['post_checkCode'], data=data, proxies = self.proxies, timeout= 20)
            if resp.status_code != 200:
                logging.error("crawl post check page failed!")
                count += 1
                continue
            message_json = resp.content
            message = json.loads(str(message_json))
            if message.get('message') not in 'ok':
                count += 1
                continue
            search_data = {}
            search_data['isEntRecord'] = ''
            search_data['password'] = ck_code
            search_data['loginInfo.regno'] = ''
            search_data['loginInfo.entname'] = ''
            search_data['loginInfo.idNo'] = ''
            search_data['loginInfo.mobile'] = ''
            search_data['loginInfo.password'] = ''
            search_data['loginInfo.verificationCode'] = ''
            search_data['otherLoginInfo.name'] = ''
            search_data['otherLoginInfo.password'] = ''
            search_data['otherLoginInfo.verificationCode'] = ''
            search_data['selectValue'] = self.ent_number
            resp = self.reqst.post(JiangxiCrawler.urls['post_checkCode2'], data=search_data, proxies= self.proxies, timeout = 20)
            if resp.status_code != 200:
                count -= 1
                continue
            return resp.content
        return None

    def crack_check_code(self, count=None):
        """破解验证码
        :return 破解后的验证码
        """
        times = long(time.time())
        params = {}
        params['_'] = times

        resp = self.reqst.get(JiangxiCrawler.urls['get_checkcode'], params=params, proxies= self.proxies, timeout= 20)
        print 'image code', str(resp.status_code)
        if resp.status_code != 200:
            logging.error('failed to get get_checkcode')
            return None
        time.sleep(random.uniform(0.1, 1))
        self.write_file_mutex.acquire()
        if not path.isdir(self.ckcode_image_dir_path):
            os.makedirs(self.ckcode_image_dir_path)
        with open(self.ckcode_image_path, 'wb') as f:
            f.write(resp.content)
        if count is not None:
            with open(self.ckcode_image_dir_path + 'ckcode' + str(count) + '.jpg', 'wb') as f:
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

    def crawl_page_by_get_params(self, params=None, name='detail.html', url=None):
        """
        通过传入不同的参数获得不同的页面
        """
        resp = self.reqst.get(url=url, params=params, proxies= self.proxies, timeout= 20)
        # print str(resp.status_code)
        if resp.status_code != 200:
            logging.error('crawl page by url failed! url = %s' % url)
        page = resp.content
        time.sleep(random.uniform(0.1, 0.3))
        # if settings.save_html:
        #     CrawlerUtils.save_page_to_file(self.html_restore_path + name, page)
        return page

    def crawl_ind_comm_pub_reg_basic_pages(self):
        """
        """
        params = {}
        params['nbxh'] = self.results[0]
        params['qylx'] = self.results[1]
        url = JiangxiCrawler.urls['ind_comm_pub_reg_basic']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_ind_comm_pub_reg_shareholder_pages(self):
        """
            企业年报
        """
        params = {}
        params['nbxh'] = self.results[0]
        params['qylx'] = self.results[1]
        url = JiangxiCrawler.urls['ind_comm_pub_reg_shareholder']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_ind_comm_pub_reg_modify_pages(self):
        """
            企业年报
        """
        params = {}
        params['nbxh'] = self.results[0]
        params['qylx'] = self.results[1]
        url = JiangxiCrawler.urls['ind_comm_pub_reg_modify']
        page = self.crawl_page_by_get_params(params=params, url=url)

        return page

    def crawl_ind_comm_pub_arch_key_persons_pages(self):
        """
            企业年报
        """
        params = {}
        params['nbxh'] = self.results[0]
        params['qylx'] = self.results[1]
        url = JiangxiCrawler.urls['ind_comm_pub_arch_key_persons']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_ind_comm_pub_arch_branch_pages(self):
        """
            企业年报
        """
        params = {}
        params['nbxh'] = self.results[0]
        params['qylx'] = self.results[1]
        url = JiangxiCrawler.urls['ind_comm_pub_arch_branch']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_ind_comm_pub_arch_liquidation_pages(self):
        """
            企业年报
        """
        params = {}
        params['nbxh'] = self.results[0]
        params['qylx'] = self.results[1]
        url = JiangxiCrawler.urls['ind_comm_pub_arch_liquidation']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_ind_comm_pub_movable_property_reg_pages(self):
        """
            企业年报
        """
        params = {}
        params['nbxh'] = self.results[0]
        params['qymc'] = self.results[2]
        params['zch'] = self.results[3]
        url = JiangxiCrawler.urls['ind_comm_pub_movable_property_reg']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_ind_comm_pub_equity_ownership_reg_pages(self):
        """
            企业年报
        """
        params = {}
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['ind_comm_pub_equity_ownership_reg']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_ind_comm_pub_administration_sanction_pages(self):
        """

        """
        params = {}
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['ind_comm_pub_administration_sanction']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_ind_comm_pub_business_exception_pages(self):
        """

        """
        params = {}
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['ind_comm_pub_business_exception']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_ind_comm_pub_serious_violate_law_pages(self):
        """

        """
        params = {}
        url = JiangxiCrawler.urls['ind_comm_pub_serious_violate_law']
        page = self.crawl_page_by_get_params(url=url)
        return page

    def crawl_ind_comm_pub_spot_check_pages(self):
        """
        """
        params = {}
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['ind_comm_pub_spot_check']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_ent_pub_ent_annual_report_pages(self):
        """
        """
        params = {}
        params['nbxh'] = self.results[0]
        params['qymc'] = self.results[2]
        params['zch'] = self.results[3]
        url = JiangxiCrawler.urls['ent_pub_ent_annual_report']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_ent_pub_shareholder_capital_contribution_pages(self):
        """
        """
        params = {}
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['ent_pub_shareholder_capital_contribution']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_ent_pub_equity_change_pages(self):
        """
        """
        params = {}
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['ent_pub_equity_change']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_ent_pub_administration_license_pages(self):
        """
        """
        params = {}
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['ent_pub_administration_license']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_ent_pub_knowledge_property_pages(self):
        """
        """
        params = {}
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['ent_pub_knowledge_property']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_ent_pub_administration_sanction_pages(self):
        """
        """
        params = {}
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['ent_pub_administration_sanction']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_ent_pub_reg_modify_pages(self):
        """
        """
        params = {}
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['ent_pub_reg_modify']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_other_dept_pub_administration_license_pages(self):
        """
        """
        params = {}
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['other_dept_pub_administration_license']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_other_dept_pub_administration_sanction_pages(self):
        """
        """
        params = {}
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['other_dept_pub_administration_sanction']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_judical_assist_pub_equity_freeze_pages(self):
        """
        """
        params = {}
        params['nbxh'] = self.results[0]
        params['qylxFlag'] = self.results[4]
        url = JiangxiCrawler.urls['judical_assist_pub_equity_freeze']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_judical_assist_pub_shareholder_modify_pages(self):
        """
        """
        params = {}
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['judical_assist_pub_shareholder_modify']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_report_baseinfo_pages(self, year):
        """
        """
        params = {}
        params['gsryflag'] = ''
        params['njnd'] = year
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['report_baseinfo']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_report_website_pages(self, year):
        """
        """
        params = {}
        params['gsryflag'] = ''
        params['njnd'] = year
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['report_website']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_report_shareholder_pages(self, year):
        """
        """
        params = {}
        params['gsryflag'] = ''
        params['njnd'] = year
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['report_shareholder']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_report_out_invest_pages(self, year):
        """
        """
        params = {}
        params['gsryflag'] = ''
        params['njnd'] = year
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['report_out_invest']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_report_public_of_ent_pages(self, year):
        """
        """
        params = {}
        params['gsryflag'] = ''
        params['njnd'] = year
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['report_public_of_ent']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_report_offer_security_pages(self, year):
        """
        """
        params = {}
        params['gsryflag'] = ''
        params['njnd'] = year
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['report_offer_security']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_report_shareholder_change_pages(self, year):
        """
        """
        params = {}
        params['gsryflag'] = ''
        params['njnd'] = year
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['report_shareholder_change']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page

    def crawl_report_record_of_modifies_pages(self, year):
        """
        """
        params = {}
        params['gsryflag'] = ''
        params['njnd'] = year
        params['nbxh'] = self.results[0]
        url = JiangxiCrawler.urls['report_record_of_modifies']
        page = self.crawl_page_by_get_params(params=params, url=url)
        return page


class JiangxiParser(Parser):
    """甘肃工商页面的解析类
    """

    def __init__(self, crawler):
        self.crawler = crawler

    def parse_search_page(self, page):
        soup = BeautifulSoup(page, "html5lib")
        a_div = soup.find('div', {'id': 'div0'})
        dt = a_div.find('dt')
        if dt is None:
            return None
        a_link = dt.find('a')
        url = a_link.get('onclick')
        if url is None:
            return None
        pattern = re.compile(r"\'(.*?)\'", re.I | re.X)
        results = pattern.findall(url)
        return results

    def parse_ind_comm_pub_basic_pages(self, page):
        """解析工商基本公示信息-页面
        """
        page = str(page)
        soup = BeautifulSoup(page, 'html5lib',from_encoding='utf-8')
        # print page
        # 基本信息
        base_info_table = soup.find('table', {'class': 'detailsList'})
        # print str(base_info_table)
        base_trs = base_info_table.find_all('tr')

        ind_comm_pub_reg_basic = {}
        ind_comm_pub_reg_basic[u'统一社会信用代码/注册号'] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[1].find_all('td')[0].get_text())
        ind_comm_pub_reg_basic[u'名称'] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[1].find_all('td')[1].get_text())
        ind_comm_pub_reg_basic[u'类型'] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[2].find_all('td')[0].get_text())
        ind_comm_pub_reg_basic[u'法定代表人'] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[2].find_all('td')[1].get_text())
        ind_comm_pub_reg_basic[u'注册资本'] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[3].find_all('td')[0].get_text())
        ind_comm_pub_reg_basic[u'成立日期'] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[3].find_all('td')[1].get_text())
        ind_comm_pub_reg_basic[u'住所'] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[4].find('td').get_text())
        ind_comm_pub_reg_basic[u'营业期限自'] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[5].find_all('td')[0].get_text())
        ind_comm_pub_reg_basic[u'营业期限至'] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[5].find_all('td')[1].get_text())
        ind_comm_pub_reg_basic[u'经营范围'] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[6].find('td').get_text())
        ind_comm_pub_reg_basic[u'登记机关'] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[7].find_all('td')[0].get_text())
        ind_comm_pub_reg_basic[u'核准日期'] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[7].find_all('td')[1].get_text())
        ind_comm_pub_reg_basic[u'登记状态'] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[8].find('td').get_text())

        self.crawler.json_dict['ind_comm_pub_reg_basic'] = ind_comm_pub_reg_basic

    def parse_ind_comm_pub_reg_shareholderes_pages(self, page):
        # 投资人信息
        soup = BeautifulSoup(page, "html5lib")

        # 基本信息
        touziren_table = soup.find('table', {'class': 'detailsList'})
        ind_comm_pub_reg_shareholderes = []
        if touziren_table is not None:

            shareholder_trs = touziren_table.find_all('tr')
            if len(shareholder_trs) > 2:
                i = 2
                while i < len(shareholder_trs):
                    ind_comm_pub_reg_shareholder = {}
                    tds = shareholder_trs[i].find_all('td')
                    ind_comm_pub_reg_shareholder[u'股东类型'] = self.wipe_off_newline_and_blank_for_fe(
                        tds[0].get_text())
                    ind_comm_pub_reg_shareholder[u'股东'] = self.wipe_off_newline_and_blank_for_fe(
                        tds[1].get_text())
                    ind_comm_pub_reg_shareholder[u'证照/证件类型'] = self.wipe_off_newline_and_blank_for_fe(
                        tds[2].get_text())
                    ind_comm_pub_reg_shareholder[u'证照/证件号码'] = self.wipe_off_newline_and_blank_for_fe(
                        tds[3].get_text())
                    i += 1
                    ind_comm_pub_reg_shareholderes.append(ind_comm_pub_reg_shareholder)

        self.crawler.json_dict['ind_comm_pub_reg_shareholder'] = ind_comm_pub_reg_shareholderes

    def parse_ind_comm_pub_reg_modify_pages(self, page):
        soup = BeautifulSoup(page, "html5lib")
        biangeng_table = soup.find('table', {'class': 'detailsList'})
        # 变更信息
        if biangeng_table is None:
            return
        ind_comm_pub_reg_modifies = []
        modifies_trs = biangeng_table.find_all('tr')
        if len(modifies_trs) > 2:
            i = 2
            while i < len(modifies_trs):
                ind_comm_pub_reg_modify = {}
                tds = modifies_trs[i].find_all('td')
                if (len(tds) == 0):
                    break
                ind_comm_pub_reg_modify[u'变更事项'] = self.wipe_off_newline_and_blank_for_fe(tds[0].get_text())
                ind_comm_pub_reg_modify[u'变更前内容'] = self.wipe_off_newline_and_blank_for_fe(tds[1].get_text())
                ind_comm_pub_reg_modify[u'变更后内容'] = self.wipe_off_newline_and_blank_for_fe(tds[2].get_text())
                ind_comm_pub_reg_modify[u'变更日期'] = self.wipe_off_newline_and_blank_for_fe(tds[3].get_text())
                ind_comm_pub_reg_modifies.append(ind_comm_pub_reg_modify)
                i += 1
        self.crawler.json_dict['ind_comm_pub_reg_modify'] = ind_comm_pub_reg_modifies

    def parse_ind_comm_pub_arch_key_persons_pages(self, page):
        ck_string = '暂无数据'
        soup = BeautifulSoup(page, "html5lib")
        zyry_table = soup.find('table', {'class': 'detailsList'})
        ind_comm_pub_arch_key_persons = []
        key_persons = zyry_table.find_all('td')
        i = 0
        while i < len(key_persons):
            if len(key_persons) - i >= 3:
                break
            ind_comm_pub_arch_key_person = {}
            ind_comm_pub_arch_key_person[u'序号'] = key_persons[i].get_text()
            ind_comm_pub_arch_key_person[u'姓名'] = key_persons[i + 1].get_text()
            ind_comm_pub_arch_key_person[u'职务'] = key_persons[i + 2].get_text()
            i += 3
            ind_comm_pub_arch_key_persons.append(ind_comm_pub_arch_key_person)

        self.crawler.json_dict['ind_comm_pub_arch_key_persons'] = ind_comm_pub_arch_key_persons
        # 分支机构

    def parse_ind_comm_pub_arch_branch_pages(self, page):
        soup = BeautifulSoup(page, "html5lib")
        arch_branch_info = soup.find('table', {'class': 'detailsList'})
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
        # 动产抵押
        soup = BeautifulSoup(page, 'html5lib')
        movable_property_reg_info = soup.find('table', {'class': 'detailsList'})
        movable_property_reg_trs = movable_property_reg_info.find_all('tr')
        detail_movable_property_reg_infoes = []
        if len(movable_property_reg_trs) > 2:
            i = 2
            while i < len(movable_property_reg_trs):

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
                detail_movable_property_reg_info[u'详情'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[5].get_text())
                detail_movable_property_reg_infoes.append(detail_movable_property_reg_info)
                i += 1
        self.crawler.json_dict['ind_comm_pub_movable_property_reg'] = detail_movable_property_reg_infoes

    def parse_ind_comm_pub_equity_ownership_reg_pages(self, page):
        # 股权出质
        soup = BeautifulSoup(page, 'html5lib')
        equity_table = soup.find('table', {'class': 'detailsList'})
        equity_ownership_reges = []
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
        # 行政处罚
        soup = BeautifulSoup(page, 'html5lib')
        administration_sanction_info = soup.find('table', {'class': 'detailsList'})
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
                detail_administration_sanction_info[u'公示日期'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[6].get_text())
                detail_administration_sanction_info[u'详情'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[6].get_text())
                detail_administration_sanction_infoes.append(detail_administration_sanction_info)
                i += 1
        self.crawler.json_dict['ind_comm_pub_administration_sanction'] = detail_administration_sanction_infoes

    def parse_ind_comm_pub_business_exception_pages(self, page):
        """
            经营异常
            """
        soup = BeautifulSoup(page, 'html5lib')
        business_exception_info = soup.find('table', {'class': 'detailsList'})
        detail_business_exception_infoes = []
        business_exception_trs = business_exception_info.find_all('tr')
        if len(business_exception_trs) > 2:
            i = 2
            while i < len(business_exception_trs):
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
        # 严重违法
        soup = BeautifulSoup(page, 'html5lib')
        serious_violate_law_info = soup.find('table', {'class': 'detailsList'})
        serious_violate_law_trs = serious_violate_law_info.find_all('tr')
        detail_serious_violate_law_infoes = []
        if len(serious_violate_law_trs) > 2:
            i = 2
            while i < len(serious_violate_law_trs):

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

                detail_serious_violate_law_infoes.append(detail_serious_violate_law_info)
                i += 1
        self.crawler.json_dict['ind_comm_pub_serious_violate_law'] = detail_serious_violate_law_infoes

    def parse_ind_comm_pub_spot_check_pages(self, page):
        # 抽查检查
        soup = BeautifulSoup(page, 'html5lib')
        spot_check_info = soup.find('table', {'class': 'detailsList'})
        spot_check_trs = spot_check_info.find_all('tr')
        detail_spot_check_infoes = []
        if len(spot_check_trs) > 2:
            i = 2
            while i < len(spot_check_trs):
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
        # 股东出资
        soup = BeautifulSoup(page, 'html5lib')
        shareholder_capital_contributiones = []
        equity_table = soup.find_all('table', {'class': 'detailsList'})[0]
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
                shareholder_capital_contribution[u'实缴出资方式'] = self.wipe_off_newline_and_blank_for_fe(tds[6].get_text())
                shareholder_capital_contribution[u'实缴出资额'] = self.wipe_off_newline_and_blank_for_fe(tds[7].get_text())
                shareholder_capital_contribution[u'实缴出资日期'] = self.wipe_off_newline_and_blank_for_fe(tds[8].get_text())
                shareholder_capital_contribution[u'公示日期'] = self.wipe_off_newline_and_blank_for_fe(tds[8].get_text())

                shareholder_capital_contributiones.append(shareholder_capital_contribution)
                i += 1
        self.crawler.json_dict['ent_pub_shareholder_capital_contribution'] = shareholder_capital_contributiones

        # 企业变更信息
        reg_modify_info = soup.find_all('table', {'class': 'detailsList'})[1]
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
        qiyenianbao_table = soup.find('table', {'class': 'detailsList'})

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
                a_link = tds[1].find('a')
                if a_link is None:
                    j += 1
                    continue
                a_click = a_link.get('onclick')
                reportYear = str(a_click)[8:12]
                report_base_page = self.crawler.crawl_report_baseinfo_pages(reportYear)
                soup_base_info = BeautifulSoup(report_base_page, 'html5lib')
                base_info = soup_base_info.find('table', {'class': 'detailsList'})
                base_trs = base_info.find_all('tr')
                detail = {}
                detail_base_info = {}

                detail_base_info[u'注册号'] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[1].find_all('td')[0].get_text())
                detail_base_info[u'企业名称'] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[1].find_all('td')[1].get_text())
                detail_base_info[u'企业联系电话'] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[2].find_all('td')[0].get_text())
                detail_base_info[u'邮政编码'] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[2].find_all('td')[1].get_text())

                detail_base_info[u'企业通信地址'] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[3].find('td').get_text())

                detail_base_info[u'电子邮箱'] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[4].find_all('td')[0].get_text())
                detail_base_info[u'有限责任公司本年度是否发生股东股权转让'] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[4].find_all('td')[1].get_text())
                detail_base_info[u'企业登记状态'] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[5].find_all('td')[0].get_text())
                detail_base_info[u'是否有网站或网店'] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[5].find_all('td')[1].get_text())
                detail_base_info[u'企业是否有投资信息或购买其他公司股权'] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[6].find_all('td')[0].get_text())
                detail_base_info[u'从业人数'] = self.wipe_off_newline_and_blank_for_fe(
                    base_trs[6].find_all('td')[1].get_text())

                detail[u'企业基本信息'] = detail_base_info

                website_page = self.crawler.crawl_report_website_pages(reportYear)
                soup_website = BeautifulSoup(website_page, 'html5lib')
                website_info = soup_website.find('table', {'class': 'detailsList'})
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

                shareholder_page = self.crawler.crawl_report_shareholder_pages(reportYear)
                soup_shareholder = BeautifulSoup(shareholder_page, 'html5lib')
                shareholder_capital_contribution_info = soup_shareholder.find('table', {'class': 'detailsList'})
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

                report_out_invest = self.crawler.crawl_report_out_invest_pages(reportYear)
                soup_out_invest = BeautifulSoup(report_out_invest, 'html5lib')
                outbound_investment_info = soup_out_invest.find('table', {'class': 'detailsList'})
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

                report_public_of_ent = self.crawler.crawl_report_public_of_ent_pages(reportYear)
                soup_public_of_ent = BeautifulSoup(report_public_of_ent, 'html5lib')
                state_of_enterprise_assets_info = soup_public_of_ent.find('table', {'class': 'detailsList'})
                state_of_enterprise_assets_trs = state_of_enterprise_assets_info.find_all('tr')
                detail_state_of_enterprise_assets_infoes = {}
                detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[1].find_all('th')[
                    0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    state_of_enterprise_assets_trs[1].find_all('td')[0].get_text())
                detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[1].find_all('th')[
                    1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    state_of_enterprise_assets_trs[1].find_all('td')[1].get_text())
                detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[2].find_all('th')[
                    0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    state_of_enterprise_assets_trs[2].find_all('td')[0].get_text())
                detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[2].find_all('th')[
                    1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    state_of_enterprise_assets_trs[2].find_all('td')[1].get_text())
                detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[3].find_all('th')[
                    0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    state_of_enterprise_assets_trs[3].find_all('td')[0].get_text())
                detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[3].find_all('th')[
                    1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    state_of_enterprise_assets_trs[3].find_all('td')[1].get_text())
                detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[4].find_all('th')[
                    0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    state_of_enterprise_assets_trs[4].find_all('td')[0].get_text())
                detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[4].find_all('th')[
                    1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
                    state_of_enterprise_assets_trs[4].find_all('td')[1].get_text())

                detail[u'企业资产状况信息'] = detail_state_of_enterprise_assets_infoes
                report_offer_security = self.crawler.crawl_report_offer_security_pages(reportYear)
                soup_offer_security = BeautifulSoup(report_offer_security, 'html5lib')
                provide_guarantee_to_the_outside_info = soup_offer_security.find('table', {'class': 'detailsList'})
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

                report_shareholder_change = self.crawler.crawl_report_shareholder_change_pages(reportYear)
                soup_shareholder_change = BeautifulSoup(report_shareholder_change, 'html5lib')
                ent_pub_equity_change_info = soup_shareholder_change.find('table', {'class': 'detailsList'})
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
                report_record_of_modifies = self.crawler.crawl_report_record_of_modifies_pages(reportYear)
                soup_record_of_modifies = BeautifulSoup(report_record_of_modifies, 'html5lib')
                change_record_info = soup_record_of_modifies.find('table', {'class': 'detailsList'})
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

    def parse_ent_pub_reg_modify_pages(self, page):
        soup = BeautifulSoup(page, "html5lib")
        biangeng_table = soup.find('table', {'class': 'detailsList'})
        # 变更信息
        if biangeng_table is None:
            return
        ent_pub_reg_modifies = []
        modifies_trs = biangeng_table.find_all('tr')
        if len(modifies_trs) > 2:
            i = 2
            while i < len(modifies_trs):
                ent_pub_reg_modify = {}
                tds = modifies_trs[i].find_all('td')
                if (len(tds) == 0):
                    break
                ent_pub_reg_modify[u'序号'] = self.wipe_off_newline_and_blank_for_fe(tds[0].get_text())
                ent_pub_reg_modify[u'变更事项'] = self.wipe_off_newline_and_blank_for_fe(tds[1].get_text())
                ent_pub_reg_modify[u'变更时间'] = self.wipe_off_newline_and_blank_for_fe(tds[2].get_text())
                ent_pub_reg_modify[u'变更前内容'] = self.wipe_off_newline_and_blank_for_fe(tds[3].get_text())
                ent_pub_reg_modify[u'变更后内容'] = self.wipe_off_newline_and_blank_for_fe(tds[4].get_text())
                ent_pub_reg_modifies.append(ent_pub_reg_modify)
                i += 1
        self.crawler.json_dict['ent_pub_reg_modify'] = ent_pub_reg_modifies

    def parse_ent_pub_administration_license_pages(self, page):
        """
        企业-解析行政许可
        """
        soup = BeautifulSoup(page, 'html5lib')
        administration_license_info = soup.find('table', {'class': 'detailsList'})
        administration_license_trs = administration_license_info.find_all('tr')
        detail_administration_license_infoes = []
        if len(administration_license_trs) > 2:
            i = 2
            while i < len(administration_license_trs):
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
        administration_sanction_info = soup.find('table', {'class': 'detailsList'})
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
                detail_administration_sanction_info[u'行政处罚类型'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[2].get_text())
                detail_administration_sanction_info[u'行政处罚内容'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[3].get_text())
                detail_administration_sanction_info[u'作出行政处罚决定机关名称'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[4].get_text())
                detail_administration_sanction_info[u'作出行政处罚决定日期'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[5].get_text())
                detail_administration_sanction_info[u'公示日期'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[6].get_text())
                detail_administration_sanction_info[u'备注'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[7].get_text())
                detail_administration_sanction_infoes.append(detail_administration_sanction_info)
                i += 1
        self.crawler.json_dict['ind_comm_pub_administration_sanction'] = detail_administration_sanction_infoes

    def parse_ent_pub_equity_change_pages(self, page):
        """
            企业-股权变更
        """
        soup = BeautifulSoup(page, 'html5lib')
        equity_change_info = soup.find('table', {'class': 'detailsList'})
        equity_change_trs = equity_change_info.find_all('tr')
        detail_equity_change_infoes = []
        if len(equity_change_trs) > 2:
            i = 2
            while i < len(equity_change_trs):
                detail_equity_change_info = {}
                tds = equity_change_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                detail_equity_change_info[u'序号'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[0].get_text())
                detail_equity_change_info[u'股东'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[1].get_text())
                detail_equity_change_info[u'变更前股权比例'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[2].get_text())
                detail_equity_change_info[u'变更后股权比例'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[3].get_text())
                detail_equity_change_info[u'股权变更日期'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[4].get_text())
                detail_equity_change_info[u'公示日期'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[5].get_text())
                detail_equity_change_infoes.append(detail_equity_change_info)
                i += 1
        self.crawler.json_dict['ind_comm_pub_equity_change'] = detail_equity_change_infoes

    def parse_ent_pub_knowledge_property_pages(self, page):
        """
            企业-解析知识产权出质
        """
        soup = BeautifulSoup(page, 'html5lib')
        knowledge_property_info = soup.find('class', {'id': 'detailsList'})
        if knowledge_property_info is None:
            return

        knowledge_property_trs = knowledge_property_info.find_all('tr')
        detail_knowledge_property_infoes = []
        if len(knowledge_property_trs) > 2:
            i = 2
            while i < len(knowledge_property_trs):
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
        administration_license_info = soup.find('table', {'class': 'detailsList'})
        if administration_license_info is None:
            return
        administration_license_trs = administration_license_info.find_all('tr')
        detail_administration_license_infoes = []
        if len(administration_license_trs) > 2:
            i = 2
            while i < len(administration_license_trs):

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
                detail_administration_license_info[u'详情'] = self.wipe_off_newline_and_blank_for_fe(
                    tds[8].get_text())

                detail_administration_license_infoes.append(detail_administration_license_info)
                i += 1
                self.crawler.json_dict['other_dept_pub_administration_license'] = detail_administration_license_infoes

    def parse_other_dept_pub_administration_sanction_pages(self, page):
        """
        其他
        """
        soup = BeautifulSoup(page, 'html5lib')
        administration_sanction_info = soup.find('table', {'class': 'detailsList'})
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
        equity_freeze_div = soup.find('div', {'id': 'sifaxiezhu'})
        if equity_freeze_div is None:
            return
        equity_freeze_info = equity_freeze_div.find('table', {'class': 'detailsList'})
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
        shareholder_modify_div = soup.find('div', {'id': 'sifagudong'})
        if shareholder_modify_div is None:
            return
        shareholder_modify_info = shareholder_modify_div.find('table', {'class': 'detailsList'})
        shareholder_modify_trs = shareholder_modify_info.find_all('tr')
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
        self.crawler = JiangxiCrawler('./enterprise_crawler/jiangxi.json')
        self.parser = self.crawler.parser
        self.crawler.json_dict = {}
        self.crawler.ent_number = '152704000000508'

    def test_crawl_check_page(self):
        isOK = self.crawler.crawl_check_page()
        self.assertEqual(isOK, True)

"""
if __name__ == '__main__':

    # import sys

    # reload(sys)
    # sys.setdefaultencoding("utf-8")
    from CaptchaRecognition import CaptchaRecognition
    import run

    #
    run.config_logging()
    JiangxiCrawler.code_cracker = CaptchaRecognition('ningxia')
    crawler = JiangxiCrawler('./enterprise_crawler/jiangxi/jiangxi.json')
    enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/jiangxi.txt')
    # raw_input('hello')
    for ent_number in enterprise_list:
        ent_number = ent_number.rstrip('\n')
        print(
            '############   Start to crawl enterprise with id %s   ################\n' % ent_number)
        crawler.run(ent_number=ent_number)
"""
