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


class NeimengguClawer(Crawler):
    """内蒙古工商公示信息网页爬虫
    """

    urls = {'host': 'http://www.nmgs.gov.cn:7001/aiccips',
            'get_checkcode': 'http://www.nmgs.gov.cn:7001/aiccips/verify.html?random=0.48031352812604344',
            'post_checkCode': 'http://www.nmgs.gov.cn:7001/aiccips/CheckEntContext/checkCode.html',
            'post_checkCode2': 'http://www.nmgs.gov.cn:7001/aiccips/CheckEntContext/showInfo.html',
            'ind_comm_pub_skeleton': 'http://www.nmgs.gov.cn:7001/aiccips/GSpublicity/GSpublicityList.html',
            # 工商-备案信息页面
            'ind_comm_pub_arch_page': 'http://www.nmgs.gov.cn:7001/aiccips/GSpublicity/GSpublicityList.html?service=entCheckInfo',
            # 工商-动产登记页面
            'ind_comm_pub_movable_property_reg_page': 'http://www.nmgs.gov.cn:7001/aiccips/GSpublicity/GSpublicityList.html?service=pleInfo',
            # 工商-股权出质信息页面
            'ind_comm_pub_equity_ownership_reg_page': 'http://www.nmgs.gov.cn:7001/aiccips/GSpublicity/GSpublicityList.html?service=curStoPleInfo',
            # 工商-行政处罚
            'ind_comm_pub_administration_sanction_page': 'http://www.nmgs.gov.cn:7001/aiccips/GSpublicity/GSpublicityList.html?service=cipPenaltyInfo',
            # 工商经营异常
            'ind_comm_pub_business_exception_page': 'http://www.nmgs.gov.cn:7001/aiccips/GSpublicity/GSpublicityList.html?service=cipUnuDirInfo',
            # 严重违法
            'ind_comm_pub_serious_violate_law_page': 'http://www.nmgs.gov.cn:7001/aiccips/GSpublicity/GSpublicityList.html?service=cipBlackInfo',
            # 抽查检查
            'ind_comm_pub_spot_check_page': 'http://www.nmgs.gov.cn:7001/aiccips/GSpublicity/GSpublicityList.html?service=cipSpotCheInfo',
            # =======================
            # 企业公示信息
            # 企业年报
            'ent_pub_ent_annual_report_page': 'http://www.nmgs.gov.cn:7001/aiccips/BusinessAnnals/BusinessAnnalsList.html',
            # 企业投资人出资比例
            'ent_pub_shareholder_capital_contribution_page': 'http://www.nmgs.gov.cn:7001/aiccips/ContributionCapitalMsg.html',
            # 股权变更信息
            'ent_pub_equity_change_page': 'http://www.nmgs.gov.cn:7001/aiccips/GDGQTransferMsg/shareholderTransferMsg.html',
            # 行政许可信息
            'ent_pub_administration_license_page': 'http://www.nmgs.gov.cn:7001/aiccips/AppPerInformation.html',
            # 知识产权出资登记
            'ent_pub_knowledge_property_page': 'http://www.nmgs.gov.cn:7001/aiccips/intPropertyMsg.html',
            # 行政处罚信息
            'ent_pub_administration_sanction_page': 'http://www.nmgs.gov.cn:7001/aiccips/XZPunishmentMsg.html',
            # =======================
            # 其他部门公示信息
            # 行政许可信息
            # 行政处罚信息
            'other_dept_pub_page': 'http://www.nmgs.gov.cn:7001/aiccips/OtherPublicity/otherDeptInfo.html',

            # ========================
            # 司法协助公示信息
            # 股权冻结信息
            # 股东变更信息
            'judical_assist_pub_page': 'http://www.nmgs.gov.cn:7001/aiccips/OtherPublicity/highCourt.html',

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
        self.parser = NeimengguParser(self)
        self.credit_ticket = None
        # html数据的存储路径
        self.html_restore_path = os.path.join(self.json_restore_path, "neimenggu")
        if os.path.exists(self.html_restore_path) is False:
            os.makedirs(self.html_restore_path, 0775)
        # 验证码图片的存储路径
        self.ckcode_image_path = os.path.join(self.html_restore_path, 'ckcode.jpg')
        self.code_cracker = CaptchaRecognition("neimenggu")
        self.json_restore_path = json_restore_path

        self.reqst = requests.Session()
        self.reqst.headers.update({
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})
        self.ent_number = None
        self.entNo = None
        self.entType = None
        self.regOrg = None
        self.json_dict = {}

    def run(self, ent_number=0):

        self.ent_number = str(ent_number)
        page = self.crawl_check_page()
        if page is None:
            logging.error(
                'According to the registration number does not search to the company %s' % self.ent_number)
            return False
        page = self.crawl_ind_comm_pub_basic_pages(page)
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
        page = self.crawl_other_dept_pub_pages()
        self.parser.parse_other_dept_pub_pages(page)
        page = self.crawl_judical_assist_pub_pages()
        self.parser.parse_judical_assist_pub_pages(page)

        return json.dumps({self.ent_number: self.json_dict})

    def crawl_check_page(self):
        """爬取验证码页面，包括下载验证码图片以及破解验证码
        :return true or false
        """
        count = 0
        while count < 30:
            ck_code = self.crack_check_code()
            data = {'code': ck_code, 'textfield': self.ent_number}
            resp = self.reqst.post(NeimengguClawer.urls['post_checkCode'], data=data)

            if resp.status_code != 200:
                logging.error("crawl post check page failed!")
                count += 1
                continue
            back_json = json.loads(resp.content)
            if int(back_json.get('flag')) != 1:
                continue
                count += 1
            textfield = json.loads(resp.content).get('textfield')
            data2 = {'textfield': textfield, 'code': ck_code}
            # print(textfield)
            resp = self.reqst.post(NeimengguClawer.urls['post_checkCode2'], data=data2)
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
        # main_url = 'http://www.nmgs.gov.cn:7001/aiccips/'
        # resp = self.reqst.get(main_url)
        # print(resp.status_code== 200)

        data = {'random', random.uniform(0.0, 1.0)}
        resp = self.reqst.get(NeimengguClawer.urls['get_checkcode'])
        if resp.status_code != 200:
            logging.error('failed to get get_checkcode')
            return None
        time.sleep(random.uniform(1, 2))

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

        return ckcode[1]

    def crawl_page_by_url(self, url, data=None, name='detail.html', method='GET'):
        """根据url直接爬取页面
        """
        if method == 'GET':
            if data is None:
                resp = self.reqst.get(url)
            else:
                resp = self.reqst.get(url, data=data)
        else:
            if data is None:
                resp = self.reqst.post(url)
            else:
                resp = self.reqst.post(url, data=data)
        if resp.status_code != 200:
            logging.error('crawl page by url failed! url = %s' % url)
        page = resp.content
        time.sleep(random.uniform(0.2, 1))
        # if settings.save_html:
        #     CrawlerUtils.save_page_to_file(self.html_restore_path + name, page)
        return page

    def crawl_ind_comm_pub_basic_pages(self, page):
        """爬取工商基本公示信息
        """
        url = self.parser.parse_search_page(page)
        page = self.crawl_page_by_url(url)
        return page

    def crawl_ind_comm_pub_arch_pages(self):
        """爬取工商备案公示信息
        """
        data = {'entNo': self.entNo, 'entType': self.entType, 'regOrg': self.regOrg}
        page = self.crawl_page_by_url(NeimengguClawer.urls['ind_comm_pub_arch_page'], data=data, method='POST')
        return page

    def crawl_ind_comm_pub_movable_property_reg_pages(self):
        """
            工商-动产信息页面爬取
        """
        data = {'entNo': self.entNo, 'entType': self.entType, 'regOrg': self.regOrg}
        page = self.crawl_page_by_url(NeimengguClawer.urls['ind_comm_pub_movable_property_reg_page'], data=data,
                                      method='POST')
        return page

    def crawl_ind_comm_pub_equity_ownership_reg_pages(self):
        """
            工商-股权出质
        """
        data = {'entNo': self.entNo, 'entType': self.entType, 'regOrg': self.regOrg}
        page = self.crawl_page_by_url(NeimengguClawer.urls['ind_comm_pub_equity_ownership_reg_page'], data=data,
                                      method='POST')
        return page

    def crawl_ind_comm_pub_administration_sanction_pages(self):
        """
            工商-行政处罚
        """
        data = {'entNo': self.entNo, 'entType': self.entType, 'regOrg': self.regOrg}
        page = self.crawl_page_by_url(NeimengguClawer.urls['ind_comm_pub_administration_sanction_page'], data=data,
                                      method='POST')
        return page

    def crawl_ind_comm_pub_business_exception_pages(self):
        """
            工商-行政处罚
        """
        data = {'entNo': self.entNo, 'entType': self.entType, 'regOrg': self.regOrg}
        page = self.crawl_page_by_url(NeimengguClawer.urls['ind_comm_pub_business_exception_page'], data=data,
                                      method='POST')
        return page

    def crawl_ind_comm_pub_serious_violate_law_pages(self):
        """
            工商-严重违法
        """
        data = {'entNo': self.entNo, 'entType': self.entType, 'regOrg': self.regOrg}
        page = self.crawl_page_by_url(NeimengguClawer.urls['ind_comm_pub_serious_violate_law_page'], data=data,
                                      method='POST')
        return page

    def crawl_ind_comm_pub_spot_check_pages(self):
        """
            工商-抽查检查
        """
        data = {'entNo': self.entNo, 'entType': self.entType, 'regOrg': self.regOrg}
        page = self.crawl_page_by_url(NeimengguClawer.urls['ind_comm_pub_spot_check_page'], data=data,
                                      method='POST')
        return page

    def crawl_ent_pub_ent_annual_report_pages(self):
        """
            企业年报
        """
        data = {'entNo': self.entNo, 'entType': self.entType, 'regOrg': self.regOrg}
        page = self.crawl_page_by_url(NeimengguClawer.urls['ent_pub_ent_annual_report_page'], data=data,
                                      method='POST')
        return page

    def crawl_ent_pub_shareholder_capital_contribution_pages(self):
        """
            企业-出资人比例
        """
        data = {'entNo': self.entNo, 'entType': self.entType, 'regOrg': self.regOrg}
        page = self.crawl_page_by_url(NeimengguClawer.urls['ent_pub_shareholder_capital_contribution_page'], data=data,
                                      method='POST')
        return page

    def crawl_ent_pub_equity_change_pages(self):
        """
            企业-股权变更信息
        """
        data = {'entNo': self.entNo, 'entType': self.entType, 'regOrg': self.regOrg}
        page = self.crawl_page_by_url(NeimengguClawer.urls['ent_pub_equity_change_page'], data=data,
                                      method='POST')
        return page

    def crawl_ent_pub_administration_license_pages(self):
        """
            企业-行政许可
        """
        data = {'entNo': self.entNo, 'entType': self.entType, 'regOrg': self.regOrg}
        page = self.crawl_page_by_url(NeimengguClawer.urls['ent_pub_administration_license_page'], data=data,
                                      method='POST')
        return page

    def crawl_ent_pub_administration_sanction_pages(self):
        """
            企业-行政处罚
        """
        data = {'entNo': self.entNo, 'entType': self.entType, 'regOrg': self.regOrg}
        page = self.crawl_page_by_url(NeimengguClawer.urls['ent_pub_administration_sanction_page'], data=data,
                                      method='POST')
        return page

    def crawl_ent_pub_knowledge_property_pages(self):
        """
            企业-知识产权出质
        """
        data = {'entNo': self.entNo, 'entType': self.entType, 'regOrg': self.regOrg}
        page = self.crawl_page_by_url(NeimengguClawer.urls['ent_pub_knowledge_property_page'], data=data,
                                      method='POST')
        return page

    def crawl_other_dept_pub_pages(self):
        """
            其他部门公示信息
        """
        data = {'entNo': self.entNo, 'entType': self.entType, 'regOrg': self.regOrg}
        page = self.crawl_page_by_url(NeimengguClawer.urls['other_dept_pub_page'], data=data,
                                      method='POST')
        return page

    def crawl_judical_assist_pub_pages(self):
        """
            其他部门公示信息
        """
        data = {'entNo': self.entNo, 'entType': self.entType, 'regOrg': self.regOrg}
        page = self.crawl_page_by_url(NeimengguClawer.urls['judical_assist_pub_page'], data=data,
                                      method='POST')
        return page


class NeimengguParser(Parser):
    """内蒙古工商页面的解析类
    """

    def __init__(self, crawler):
        self.crawler = crawler

    def parse_search_page(self, page):
        soup = BeautifulSoup(page, "html5lib")
        list = soup.find('div', {'class', 'list'})
        href = list.find('li', {'class', 'font16'})
        a = href.find('a')
        url = a.get('href')
        base = 'http://www.nmgs.gov.cn:7001/aiccips/CheckEntContext/showInfo.html'
        return urlparse.urljoin(base, url)

    def parse_ind_comm_pub_basic_pages(self, page):
        """解析工商基本公示信息-页面
        """
        ck_string = '暂无数据'
        soup = BeautifulSoup(page, "html5lib")
        input_entNO = soup.find('input', {'id': 'entNo'})
        self.crawler.entNo = input_entNO.get('value')
        input_entType = soup.find('input', {'id': 'entType'})
        self.crawler.entType = input_entType.get('value')
        input_regOrg = soup.find('input', {'id': 'regOrg'})
        self.crawler.regOrg = input_regOrg.get('value')

        # 基本信息
        base_info = soup.find('table', {'id': 'baseinfo'})
        base_trs = base_info.find_all('tr')
        ind_comm_pub_reg_basic = {}
        ind_comm_pub_reg_basic[base_trs[1].find('th').get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[1].find('td').get_text())
        ind_comm_pub_reg_basic[base_trs[2].find_all('th')[0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[2].find_all('td')[0].get_text())
        ind_comm_pub_reg_basic[base_trs[2].find_all('th')[1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[2].find_all('td')[1].get_text())
        ind_comm_pub_reg_basic[base_trs[3].find_all('th')[0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[3].find_all('td')[0].get_text())
        ind_comm_pub_reg_basic[base_trs[3].find_all('th')[1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[3].find_all('td')[1].get_text())
        ind_comm_pub_reg_basic[base_trs[4].find_all('th')[0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[4].find_all('td')[0].get_text())
        ind_comm_pub_reg_basic[base_trs[4].find_all('th')[1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[4].find_all('td')[1].get_text())
        ind_comm_pub_reg_basic[base_trs[5].find('th').get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[5].find('td').get_text())
        ind_comm_pub_reg_basic[base_trs[6].find_all('th')[0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[6].find_all('td')[0].get_text())
        ind_comm_pub_reg_basic[base_trs[6].find_all('th')[1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[6].find_all('td')[1].get_text())
        ind_comm_pub_reg_basic[base_trs[7].find('th').get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[7].find('td').get_text())
        ind_comm_pub_reg_basic[base_trs[8].find_all('th')[0].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[8].find_all('td')[0].get_text())
        ind_comm_pub_reg_basic[base_trs[8].find_all('th')[1].get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[8].find_all('td')[1].get_text())
        ind_comm_pub_reg_basic[base_trs[9].find('th').get_text()] = self.wipe_off_newline_and_blank_for_fe(
            base_trs[9].find('td').get_text())
        self.crawler.json_dict['ind_comm_pub_reg_basic'] = ind_comm_pub_reg_basic

        # 投资人信息
        ind_comm_pub_reg_shareholderes = []
        touziren_table = soup.find('table', {'id': 'touziren'})
        if touziren_table is not None:
            if ck_string in touziren_table.get_text():
                pass
            else:
                touziren_div = soup.find('div', {'id': 'invInfo'})
                multi_number_string = str(
                    touziren_div.find_all('table', {'class': 'detailsList'})[1].find('th').get_text()).replace('<',
                                                                                                               '').replace(
                    '>', '').replace('\n', '').replace(' ', '').strip('>').strip('\n').strip('<').strip('>').strip(
                    ' ')
                multi_number = int(multi_number_string[6:7])
                ind_comm_pub_arch_key_persons = []
                if multi_number > 1:
                    i = 1
                    url = 'http://www.nmgs.gov.cn:7001/aiccips/GSpublicity/invInfoPage.html'
                    url_data = {'pageNo': i, 'entNo': self.crawler.entNo, 'regOrg': self.crawler.regOrg}
                    mutli_page = self.crawler.crawl_page_by_url(url, data=url_data, method="POST")
                    mutli_json = json.loads(mutli_page)
                    list = mutli_json.get('list')
                    for item in list:
                        ind_comm_pub_reg_shareholder = {}
                        ind_comm_pub_reg_shareholder[u'股东类型'] = self.wipe_off_newline_and_blank_for_fe(
                            item.get('invType'))
                        ind_comm_pub_reg_shareholder[u'股东'] = self.wipe_off_newline_and_blank_for_fe(item.get('inv'))
                        ind_comm_pub_reg_shareholder[u'证照/证件类型'] = self.wipe_off_newline_and_blank_for_fe(
                            item.get('certName'))
                        ind_comm_pub_reg_shareholder[u'证照/证件号码'] = self.wipe_off_newline_and_blank_for_fe(
                            item.get('certNo'))
                        ind_comm_pub_reg_shareholder[u'详情'] = None
                        ind_comm_pub_reg_shareholderes.append(ind_comm_pub_reg_shareholder)
                else:
                    if touziren_table is not None:
                        shareholder_trs = touziren_table.find_all('tr')
                        for i in range(len(shareholder_trs)):
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
                            ind_comm_pub_reg_shareholder[u'详情'] = None
                            ind_comm_pub_reg_shareholderes.append(ind_comm_pub_reg_shareholder)

        self.crawler.json_dict['ind_comm_pub_reg_shareholder'] = ind_comm_pub_reg_shareholderes
        # 变更信息

        biangeng_div = soup.find('div', {'id': 'biangeng'})
        biangeng_table = biangeng_div.find('table', {'class': 'detailsList'})
        self.crawler.json_dict['ind_comm_pub_reg_modify'] = parse_table.parse_table_A(biangeng_table)

    def parse_ind_comm_pub_arch_pages(self, page):
        ck_string = '暂无数据'
        soup = BeautifulSoup(page, 'html5lib')
        zyry_div = soup.find('div', {'id': 'zyry'})
        zyry_table = zyry_div.find_all('table', {'class': 'detailsList'})[0]

        if ck_string in zyry_table.get_text():
            pass
        else:
            multi_number_string = str(
                zyry_div.find_all('table', {'class': 'detailsList'})[1].find('th').get_text()).replace('<',
                                                                                                       '').replace(
                '>', '').replace('\n', '').replace(' ', '').strip('>').strip('\n').strip('<').strip('>').strip(' ')
            multi_number = int(multi_number_string[6:7])
            ind_comm_pub_arch_key_persons = []
            key_persons = zyry_table.find_all('td')
            if multi_number > 1:
                i = 1
                url = 'http://www.nmgs.gov.cn:7001/aiccips/GSpublicity/vipInfoPage'
                url_data = {'pageNo': i, 'entNo': self.crawler.entNo, 'regOrg': self.crawler.regOrg}
                mutli_page = self.crawler.crawl_page_by_url(url, data=url_data, method="POST")
                mutli_json = json.loads(mutli_page)
                list = mutli_json.get('list')
                for item in list:
                    ind_comm_pub_arch_key_person = {}
                    ind_comm_pub_arch_key_person[u'序号'] = i
                    ind_comm_pub_arch_key_person[u'姓名'] = item.get('name')
                    ind_comm_pub_arch_key_person[u'职务'] = item.get('position')
                    ind_comm_pub_arch_key_persons.append(ind_comm_pub_arch_key_person)
                    i += 1
            else:
                i = 0
                while i < len(key_persons) - 3:
                    ind_comm_pub_arch_key_person = {}
                    if (len(key_persons) < 3):
                        break
                    ind_comm_pub_arch_key_person[u'序号'] = key_persons[i].get_text()
                    ind_comm_pub_arch_key_person[u'姓名'] = key_persons[i + 1].get_text()
                    ind_comm_pub_arch_key_person[u'职务'] = key_persons[i + 2].get_text()
                    i += 3
                    ind_comm_pub_arch_key_persons.append(ind_comm_pub_arch_key_person)

        self.crawler.json_dict['ind_comm_pub_arch_key_persons'] = ind_comm_pub_arch_key_persons
        # 分支机构

        arch_branch_div = soup.find('div', {'id': 'branch'})
        arch_branch_info = arch_branch_div.find_all('table', {'class': 'detailsList'})[0]

        detail_arch_branch_infoes = []
        if ck_string in arch_branch_info.get_text():
            pass
        else:
            multi_number_string = str(
                arch_branch_div.find_all('table', {'class': 'detailsList'})[1].find('th').get_text()).replace('<',
                                                                                                              '').replace(
                '>', '').replace('\n', '').replace(' ', '').strip('>').strip('\n').strip('<').strip('>').strip(' ')
            multi_number = int(multi_number_string[6:7])
            arch_branch_trs = arch_branch_info.find_all('tr')
            if multi_number < 2:
                if len(arch_branch_trs) > 2:
                    i = 2
                    while i < len(arch_branch_trs):
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
            else:
                i = 1
                url = 'http://www.nmgs.gov.cn:7001/aiccips/GSpublicity/braInfoPage'
                url_data = {'pageNo': i, 'entNo': self.crawler.entNo, 'regOrg': self.crawler.regOrg}
                mutli_page = self.crawler.crawl_page_by_url(url, data=url_data, method="POST")
                mutli_json = json.loads(mutli_page)
                list = mutli_json.get('list')
                for item in list:
                    ind_comm_pub_arch_key_person = {}
                    ind_comm_pub_arch_key_person[u'序号'] = i
                    ind_comm_pub_arch_key_person[u'注册号'] = item.get('regNo')
                    ind_comm_pub_arch_key_person[u'名称'] = item.get('brName')
                    ind_comm_pub_arch_key_person[u'登记机关'] = item.get('regOrg')
                    ind_comm_pub_arch_key_persons.append(ind_comm_pub_arch_key_person)
                    i += 1

        self.crawler.json_dict['ind_comm_pub_arch_branch'] = detail_arch_branch_infoes


        # 清算信息

    def parse_ind_comm_pub_movable_property_reg_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 动产抵押
        movable_property_reg_info = soup.find('table', {'class': 'detailsList'})
        self.crawler.json_dict['ind_comm_pub_movable_property_reg'] = parse_table.parse_table_A(movable_property_reg_info)

    def parse_ind_comm_pub_equity_ownership_reg_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 股权出质
        equity_table = soup.find('table', {'class': 'detailsList'})
        self.crawler.json_dict['ind_comm_pub_equity_ownership_reg'] = parse_table.parse_table_A(equity_table)

    def parse_ind_comm_pub_administration_sanction_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 行政处罚
        administration_sanction_info = soup.find('table', {'class': 'detailsList'})
        self.crawler.json_dict['ind_comm_pub_administration_sanction'] = parse_table.parse_table_A(administration_sanction_info)

    def parse_ind_comm_pub_business_exception_pages(self, page):
        """
        经营异常
        """
        soup = BeautifulSoup(page, 'html5lib')
        business_exception_info = soup.find('table', {'class': 'detailsList'})
        self.crawler.json_dict['ind_comm_pub_business_exception'] = parse_table.parse_table_A(business_exception_info)

    def parse_ind_comm_pub_serious_violate_law_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 严重违法
        serious_violate_law_info = soup.find('table', {'class': 'detailsList'})
        self.crawler.json_dict['ind_comm_pub_serious_violate_law'] = parse_table.parse_table_A(serious_violate_law_info)

    def parse_ind_comm_pub_spot_check_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 抽查检查
        spot_check_info = soup.find('table', {'class': 'detailsList'})
        self.crawler.json_dict['ind_comm_pub_spot_check'] = parse_table.parse_table_A(spot_check_info)

    def parse_ent_pub_shareholder_capital_contribution_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 股东出资
        shareholder_capital_contributiones = []
        equity_table = soup.find_all('table', {'class': 'detailsList'})[0]
        self.crawler.json_dict['ent_pub_shareholder_capital_contribution'] = parse_table.parse_table_A(equity_table)

        # 企业变更信息
        reg_modify_info = soup.find('table', {'class': 'detailsList'})
        self.crawler.json_dict['ent_pub_reg_modify'] = parse_table.parse_table_A(reg_modify_info)

    def parse_ent_pub_ent_annual_report_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 企业年报
        qiyenianbao_table = soup.find('table', {'id': 'detailsList'})
        if qiyenianbao_table is None or ck_string in qiyenianbao_table.get_text():
            return
        report_trs = qiyenianbao_table.find_all('tr')
        ent_pub_ent_annual_reportes = []
        j = 1
        while j < len(report_trs):
            tds = report_trs[j].find_all('td')
            if len(tds) <= 1:
                break
            ent_pub_ent_annual_report = {}
            ent_pub_ent_annual_report[u'序号'] = self.wipe_off_newline_and_blank_for_fe(tds[0].get_text())
            ent_pub_ent_annual_report[u'报送年度'] = self.wipe_off_newline_and_blank_for_fe((str(tds[1].get_text())[1:]))
            ent_pub_ent_annual_report[u'发布日期'] = self.wipe_off_newline_and_blank_for_fe((tds[2].get_text()))
            detail_url = tds[1].find('a').get('href')
            report_page = self.crawler.crawl_page_by_url(detail_url)
            soup_reoprt = BeautifulSoup(report_page, 'html5lib')
            detail = {}
            base_info = soup_reoprt.find_all('table', {'class': 'detailsList'})
            base_trs = base_info[1].find_all('tr')
            detail_base_info = {}
            detail_base_info[base_trs[0].find('th').get_text()] = str(base_trs[0].find('td').get_text()).strip(
                '\n').strip(' ').strip('\n')
            detail_base_info[base_trs[1].find_all('th')[0].get_text()] = str(
                base_trs[1].find_all('td')[0].get_text()).strip('\n').strip(' ').strip('\n')
            detail_base_info[base_trs[1].find_all('th')[1].get_text()] = str(
                base_trs[1].find_all('td')[1].get_text()).strip('\n').strip(' ').strip('\n')
            detail_base_info[base_trs[2].find_all('th')[0].get_text()] = str(
                base_trs[2].find_all('td')[0].get_text()).strip('\n').strip(' ').strip('\n')
            detail_base_info[base_trs[2].find_all('th')[1].get_text()] = str(
                base_trs[2].find_all('td')[1].get_text()).strip('\n').strip(' ').strip('\n')
            detail_base_info[base_trs[3].find('th').get_text()] = str(base_trs[3].find('td').get_text()).strip(
                '\n').strip(' ').strip('\n')
            detail_base_info[base_trs[4].find_all('th')[0].get_text()] = str(
                base_trs[4].find_all('td')[0].get_text()).strip('\n').strip(' ').strip('\n')
            detail_base_info[base_trs[4].find_all('th')[1].get_text()] = str(
                base_trs[4].find_all('td')[1].get_text()).strip('\n').strip(' ').strip('\n')
            detail_base_info[base_trs[5].find_all('th')[0].get_text()] = str(
                base_trs[5].find_all('td')[0].get_text()).strip('\n').strip(' ').strip('\n')
            detail_base_info[base_trs[5].find_all('th')[1].get_text()] = str(
                base_trs[5].find_all('td')[1].get_text()).strip('\n').strip(' ').strip('\n')
            detail_base_info[base_trs[6].find_all('th')[0].get_text()] = str(
                base_trs[6].find_all('td')[0].get_text()).strip('\n').strip(' ').strip('\n')
            detail_base_info[base_trs[6].find_all('th')[1].get_text()] = str(
                base_trs[6].find_all('td')[1].get_text()).strip('\n').strip(' ').strip('\n')
            detail[u'企业基本信息'] = detail_base_info

            website_info = soup_reoprt.find('table', {'id': 't02'})
            detail[u'网站或网店信息'] = parse_table.parse_table_A(website_info)

            shareholder_capital_contribution_info = soup_reoprt.find('table', {'id': 't03'})
            detail[u'股东及出资信息'] = parse_table.parse_table_A(shareholder_capital_contribution_info)

            outbound_investment_info = soup_reoprt.find('table', {'id': 't04'})
            outbound_investment_trs = outbound_investment_info.find_all('tr')
            detail_outbound_investment_infoes = []
            if len(outbound_investment_trs) > 2:
                i = 2
                while i < len(outbound_investment_trs):
                    if ck_string in outbound_investment_info.get_text():
                        break
                    tds = outbound_investment_trs[i].find_all('tr')
                    if len(tds) <= 0:
                        break
                    detail_outbound_investment_info = {}
                    detail_outbound_investment_info[u'投资设立企业或购买股权企业名称'] = self.wipe_off_newline_and_blank_for_fe(
                        tds[0].get_text())
                    detail_outbound_investment_info[u'注册号'] = self.wipe_off_newline_and_blank_for_fe(tds[1].get_text())
                    detail_outbound_investment_infoes.append(detail_outbound_investment_info)
                    i += 1

            detail[u'对外投资信息'] = detail_outbound_investment_infoes

            state_of_enterprise_assets_info = soup_reoprt.find('table', {'id': 't05'})
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

            provide_guarantee_to_the_outside_info = soup_reoprt.find_all('table')[6]
            detail[u'对外提供保证担保信息'] = parse_table.parse_table_A(provide_guarantee_to_the_outside_info)

            ent_pub_equity_change_info = soup_reoprt.find_all('table')[7]
            detail[u'股权变更信息'] = parse_table.parse_table_A(ent_pub_equity_change_info)

            change_record_info = soup_reoprt.find_all('table')[8]
            detail[u'修改记录'] = parse_table.parse_table_A(change_record_info)

            correction_statement_info = soup_reoprt.find_all('table')[9]
            detail[u'年报信息更正声明'] = parse_table.parse_table_A(correction_statement_info)
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
        administration_license_info = soup.find('table', {'class': 'detailsList'})
        self.crawler.json_dict['ind_comm_pub_administration_license'] = parse_table.parse_table_A(administration_license_info)

    def parse_ent_pub_administration_sanction_pages(self, page):
        """
        企业-解析行政处罚
        """
        soup = BeautifulSoup(page, 'html5lib')
        ck_string = '暂无数据'
        administration_sanction_info = soup.find('table', {'class': 'detailsList'})
        self.crawler.json_dict['ind_comm_pub_administration_sanction'] = parse_table.parse_table_A(administration_sanction_info)

    def parse_ent_pub_equity_change_pages(self, page):
        """
            企业-股权变更
        """
        soup = BeautifulSoup(page, 'html5lib')
        ck_string = '暂无数据'
        equity_change_info = soup.find('table', {'class': 'detailsList'})

        self.crawler.json_dict['ind_comm_pub_equity_change'] = parse_table.parse_table_A(equity_change_info)

    def parse_ent_pub_knowledge_property_pages(self, page):
        """
            企业-解析知识产权出质
        """
        soup = BeautifulSoup(page, 'html5lib')
        ck_string = '暂无数据'
        knowledge_property_info = soup.find('table', {'class': 'detailsList'})

        self.crawler.json_dict['ind_comm_pub_knowledge_property'] = parse_table.parse_table_A(knowledge_property_info)

    def parse_other_dept_pub_pages(self, page):
        """
        其他
        """
        soup = BeautifulSoup(page, 'html5lib')
        ck_string = '暂无数据'
        administration_license_info = soup.find('div', {'id': 'czcf'})
        self.crawler.json_dict['other_dept_pub_administration_license'] = parse_table.parse_table_A(administration_license_info)

        administration_sanction_info = soup.find('div', {'id': 'xzxk'})
        self.crawler.json_dict['other_dept_pub_administration_sanction'] = parse_table.parse_table_A(administration_sanction_info)

    def parse_judical_assist_pub_pages(self, page):
        """
        司法
        """
        soup = BeautifulSoup(page, 'html5lib')
        equity_freeze_info = soup.find('div', {'id': 'czcf'})
        self.crawler.json_dict['judical_assist_pub_equity_freeze'] = parse_table.parse_table_A(equity_freeze_info)

        shareholder_modify_info = soup.find('div', {'id': 'xzxk'})

        self.crawler.json_dict['judical_assist_pub_shareholder_modify'] = parse_table.parse_table_A(
            shareholder_modify_info)


class TestParser(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.crawler = NeimengguClawer('./enterprise_crawler/neimenggu.json')
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
#     NeimengguClawer.code_cracker = CaptchaRecognition('neimenggu')
#     crawler = NeimengguClawer('./enterprise_crawler/neimenggu/neimenggu.json')
#     enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/neimenggu.txt')
#
#     for ent_number in enterprise_list:
#         ent_number = ent_number.rstrip('\n')
#         logging.info(
#                 '############   Start to crawl enterprise with id %s   ################\n' % ent_number)
#         crawler.run(ent_number=ent_number)
