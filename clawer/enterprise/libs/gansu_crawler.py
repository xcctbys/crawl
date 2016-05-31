#!/usr/local/bin/python
# encoding=utf-8
import os
from os import path
import requests
import time
import re
import random
import threading
from bs4 import BeautifulSoup
import json
import logging

# from enterprise.libs.CaptchaRecognition import CaptchaRecognition
from crawler import Crawler
from crawler import Parser
import traceback
import unittest

from common_func import get_proxy


class GansuCrawler(object):
    """甘肃工商公示信息网页爬虫
    """
    # code_cracker = CaptchaRecognition('gansu')
    # 多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {
            'host': 'http://xygs.gsaic.gov.cn/',
            'first': 'http://xygs.gsaic.gov.cn/gsxygs/',
            'main': "http://xygs.gsaic.gov.cn/gsxygs/main.jsp",
            'get_checkcode': 'http://xygs.gsaic.gov.cn/gsxygs/securitycode.jpg?',
            'post_checkCode': 'http://xygs.gsaic.gov.cn/gsxygs/pub!list.do',
            'post_all_page': 'http://xygs.gsaic.gov.cn/gsxygs/pub!view.do',
            }

    def __init__(self, json_restore_path):
        """
        初始化函数
        Args:
            json_restore_path: json文件的存储路径，所有江苏的企业，应该写入同一个文件，因此在多线程爬取时设置相同的路径。同时，
             需要在写入文件的时候加锁
        Returns:
        """
        self.headers = {
            'Connection': "keep-alive",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language':' en-US,en;q=0.5',
            'Accept-Encoding':"gzip, deflate",
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'
        }
        self.reqst = requests.Session()
        self.reqst.headers.update(self.headers)
        self.json_restore_path = json_restore_path
        # html数据的存储路径
        self.html_restore_path = self.json_restore_path + '/gansu/'

        # 验证码图片的存储路径
        self.ckcode_image_path = self.json_restore_path + '/gansu/ckcode.jpg'

        # 验证码文件夹
        self.ckcode_image_dir_path = self.json_restore_path + '/gansu/'
        self.parser = GansuParser(self)

        self.method = None
        self.pripid = None
        self.ent_number = None
        self.timeout = (30, 20)
        self.proxies = get_proxy('gansu')

    def run(self, ent_number):
        print self.__class__.__name__
        logging.error('crawl %s.', self.__class__.__name__)
        self.ent_number = ent_number
        # 对每个企业都指定一个html的存储目录
        # self.html_restore_path = self.html_restore_path + self.ent_number + '/'
        # if self.save_html and not os.path.exists(self.html_restore_path):
        if not os.path.exists(self.html_restore_path):
            os.makedirs(self.html_restore_path)
        if self.proxies:
            print self.proxies
            self.reqst.proxies = self.proxies
        if not self.crawl_check_page():
            logging.error('crack check code failed, stop to crawl enterprise %s' % self.ent_number)
            return json.dumps([{self.ent_number: None}])

        sub_json_list = []
        for ent, data in self.ents.items():
            self.json_dict = {}
            self.regno = data['regno']
            self.entcate = data['entcate']
            self.main_page()
            sub_json_list.append({ent: self.json_dict})
        return json.dumps(sub_json_list)

    def main_page(self):
        page = self.crawl_ind_comm_pub_pages()
        if page is None:
            return False
        if not self.parse_search_page(page):
            return False
        self.parser.parse_ind_comm_pub_basic_pages(page)
        self.parser.parse_ind_comm_pub_arch_pages(page)
        self.parser.parse_ind_comm_pub_movable_property_reg_pages(page)
        self.parser.parse_ind_comm_pub_equity_ownership_reg_pages(page)
        self.parser.parse_ind_comm_pub_administration_sanction_pages(page)
        self.parser.parse_ind_comm_pub_business_exception_pages(page)
        self.parser.parse_ind_comm_pub_serious_violate_law_pages(page)
        self.parser.parse_ind_comm_pub_spot_check_pages(page)
        page = self.crawl_ent_pub_ent_pages()
        self.parser.parse_ent_pub_shareholder_capital_contribution_pages(page)
        self.parser.parse_ent_pub_ent_annual_report_pages(page)
        self.parser.parse_ent_pub_administration_license_pages(page)
        self.parser.parse_ent_pub_administration_sanction_pages(page)
        self.parser.parse_ent_pub_equity_change_pages(page)
        self.parser.parse_ent_pub_knowledge_property_pages(page)
        page = self.crawl_judical_assist_pub_pages()
        self.parser.parse_judical_assist_pub_equity_freeze_pages(page)
        self.parser.parse_judical_assist_pub_shareholder_modify_pages(page)

    def parse_search_page(self, page):
        soup = BeautifulSoup(page, "html5lib")
        li_div = soup.find('div', {'id': 'leftTabs'})
        li = li_div.find_all('li')[2]
        if li is None:
            return False
        url = li.get('onclick')
        if url is None:
            return False
        self.pripid = str(url).split("','")[1]
        return True

    def analyze_showInfo(self, page):
        soup = BeautifulSoup(page, "html5lib")
        divs = soup.find_all('div', attrs={'class': 'list'})
        if divs:
            count = 0
            Ent = {}
            for div in divs:
                count += 1
                data = {}
                ent = ""
                link = div.find('li')
                if link and link.find('a') and link.find('a').has_attr('id'):
                    data['regno'] = link.find('a')['id']
                if link and link.find('a') and link.find('a').has_attr('_entcate'):
                    data['entcate'] = link.find('a')['_entcate']
                profile = link.find_next_sibling()
                if profile and profile.span:
                    ent = profile.span.get_text().strip()
                name = link.find('a').get_text().strip()

                if name == self.ent_number or ent == self.ent_number:
                    Ent.clear()
                    Ent[ent] = data
                    break
                Ent[ent] = data
                if count == 3:
                    break
            self.ents = Ent
            return True
        return False

    def crawl_check_page(self):
        """爬取验证码页面，包括下载验证码图片以及破解验证码
        :return true or false
        """
        count = 0
        while count < 5:
            count += 1
            ck_code = self.crack_checkcode()
            # print ck_code
            ck_code = self.cookies.get('session_authcode', 0)
            print self.cookies
            data = {'authCodeQuery': ck_code, 'queryVal': self.ent_number}
            print data
            time.sleep(2)
            resp = requests.request('POST', GansuCrawler.urls['post_checkCode'],
                                   data=data,
                                   timeout=self.timeout,
                                   cookies=self.cookies)
            if resp.status_code != 200:
                logging.error("crawl post check page failed!")
                time.sleep(random.uniform(1, 3))
                continue
            if self.analyze_showInfo(resp.content):
                return True
            print "crawl counts = %d."%(count)
            time.sleep(random.uniform(1, 3))
        return False


    def crack_checkcode(self):
        """破解验证码
        :return 破解后的验证码
        """
        times = long(time.time())
        params = {}
        params['v'] = times

        resp = requests.request('GET', GansuCrawler.urls['get_checkcode'],
                              timeout=self.timeout
                            )
        if resp.status_code != 200:
            logging.error('failed to get get_checkcode')
            return None
        self.cookies=resp.cookies.get_dict()
        self.write_file_mutex.acquire()
        if not path.isdir(self.ckcode_image_dir_path):
            os.makedirs(self.ckcode_image_dir_path)
        with open(self.ckcode_image_path, 'wb') as f:
            f.write(resp.content)
        # try:
        #     ckcode = self.code_cracker.predict_result(self.ckcode_image_path)
        # except Exception as e:
        #     logging.warn('exception occured when crack checkcode')
        #     ckcode = ('', '')

        self.write_file_mutex.release()
        # return ckcode[1]
        return 0

    def crawl_page_by_post_data(self, data, name='detail.html', url=None):
        """
        通过传入不同的参数获得不同的页面
        """
        if url is None:
            resp = self.reqst.post(GansuCrawler.urls['post_all_page'],
                                   data=data,
                                   timeout=self.timeout,
                                   cookies=self.cookies)
        else:
            resp = self.reqst.post(url, data=data, timeout=self.timeout, cookies=self.cookies)
        if resp.status_code != 200:
            logging.error('crawl page by url failed! url = %s' % GansuCrawler.urls['post_all_page'])
        page = resp.content
        time.sleep(random.uniform(0.1, 0.3))
        return page

    def crawl_ind_comm_pub_pages(self):
        """爬取工商基本公示信息
        """
        data = {}
        data['regno'] = self.regno
        data['entcate'] = self.entcate
        page = self.crawl_page_by_post_data(data)
        return page

    def crawl_ent_pub_ent_pages(self):
        """
            企业年报
        """
        data = {}
        data['regno'] = self.regno
        data['pripid'] = self.pripid
        data['entcate'] = self.entcate
        url = 'http://xygs.gsaic.gov.cn/gsxygs/pub!viewE.do'
        page = self.crawl_page_by_post_data(data=data, url=url)
        return page

    def crawl_judical_assist_pub_pages(self):
        """
            司法协助-股权冻结
        """
        data = {}
        data['regno'] = self.regno
        data['pripid'] = self.pripid
        data['entcate'] = self.entcate
        url = 'http://xygs.gsaic.gov.cn/gsxygs/pub!viewS.do'
        page = self.crawl_page_by_post_data(data=data, url=url)
        return page


class GansuParser(Parser):
    """甘肃工商页面的解析类
    """

    def __init__(self, crawler):
        self.crawler = crawler

    def parse_ind_comm_pub_basic_pages(self, page):
        """解析工商基本公示信息-页面
        """
        soup = BeautifulSoup(page, "html5lib")

        # 基本信息
        base_info = soup.find('div', {'id': 'jibenxinxi'})
        base_info_table = base_info.find('table', {'class': 'detailsList'})
        base_trs = base_info_table.find_all('tr')
        ind_comm_pub_reg_basic = {}
        for base_tr in base_trs[1:]:
            ths = base_tr.find_all('th')
            tds = base_tr.find_all('td')
            if len(ths) != len(tds):
                continue
            for i in range(len(ths)):
                ind_comm_pub_reg_basic[ths[i].get_text().strip()] = (tds[i].get_text().strip())
        # print ind_comm_pub_reg_basic
        self.crawler.json_dict['ind_comm_pub_reg_basic'] = ind_comm_pub_reg_basic

        # 投资人信息
        ind_comm_pub_reg_shareholderes = []
        touziren_table = base_info.find('table', {'id': 'invTab'})
        if touziren_table is not None:

            shareholder_trs = touziren_table.find_all('tr')
            if len(shareholder_trs) > 2:
                i = 2
                while i < len(shareholder_trs) - 1:
                    ind_comm_pub_reg_shareholder = {}
                    tds = shareholder_trs[i].find_all('td')
                    ind_comm_pub_reg_shareholder[u'股东'] = (tds[0].get_text().strip())
                    ind_comm_pub_reg_shareholder[u'证照/证件类型'] = (tds[1].get_text().strip())
                    ind_comm_pub_reg_shareholder[u'证照/证件号码'] = (tds[2].get_text().strip())
                    ind_comm_pub_reg_shareholder[u'股东类型'] = (tds[3].get_text().strip())

                    a_link = tds[4].find('a')
                    if a_link is None:
                        i += 1
                        continue
                    a_click = a_link.get('onclick')
                    id = str(a_click)[57:89]
                    detail_data = {}
                    detail_data['entcate'] = self.crawler.entcate
                    detail_data['id'] = id
                    detail_data['parm'] = 'inv_info'
                    detail_data['pripid'] = self.crawler.pripid
                    detail_data['regno'] = self.crawler.ent_number
                    detail_url = 'http://xygs.gsaic.gov.cn/gsxygs/pub!getDetails.do'
                    detail_page = self.crawler.reqst.get(detail_url,
                                                         params=detail_data,
                                                         timeout=self.crawler.timeout,
                                                         cookies=self.crawler.cookies)
                    if detail_page.status_code != 200:
                        i += 1
                        continue
                    detail_soup = BeautifulSoup(detail_page.content, 'html5lib')
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
                        detail_detial[u'股东'] = (detail_tds[0].get_text().strip())
                        detail_detial[u'认缴额（万元)'] = (detail_tds[1].get_text().strip())
                        detail_detial[u'实缴额（万元)'] = (detail_tds[2].get_text().strip())
                        detail_list = []
                        detail_detial_tial = {}
                        detail_detial_tial[u'认缴出资方式'] = (detail_tds[3].get_text().strip())
                        detail_detial_tial[u'认缴出资额'] = (detail_tds[4].get_text().strip())
                        detail_detial_tial[u'认缴出资日期'] = (detail_tds[5].get_text().strip())
                        detail_detial_tial[u'实缴出资方式'] = (detail_tds[6].get_text().strip())
                        detail_detial_tial[u'实缴出资额'] = (detail_tds[7].get_text().strip())
                        detail_detial_tial[u'实缴出资日期'] = (detail_tds[8].get_text().strip())
                        detail_list.append(detail_detial_tial)
                        detail_detial['list'] = detail_list
                        shareholder_detail.append(detail_detial)
                    detail[u'股东及出资信息'] = shareholder_detail
                    ind_comm_pub_reg_shareholder[u'详情'] = detail
                    ind_comm_pub_reg_shareholderes.append(ind_comm_pub_reg_shareholder)
                    i += 1

        self.crawler.json_dict['ind_comm_pub_reg_shareholder'] = ind_comm_pub_reg_shareholderes
        # 变更信息

        biangeng_table = soup.find('table', {'id': 'changTab'})
        if biangeng_table is None:
            return
        ind_comm_pub_reg_modifies = []
        modifies_trs = biangeng_table.find_all('tr')
        if len(modifies_trs) > 2:
            i = 2
            while i < len(modifies_trs) - 1:
                ind_comm_pub_reg_modify = {}
                tds = modifies_trs[i].find_all('td')
                if (len(tds) == 0):
                    break
                ind_comm_pub_reg_modify[u'变更事项'] = (tds[0].get_text().strip())
                ind_comm_pub_reg_modify[u'变更前内容'] = (tds[1].get_text().strip())
                ind_comm_pub_reg_modify[u'变更后内容'] = (tds[2].get_text().strip())
                ind_comm_pub_reg_modify[u'变更日期'] = (tds[3].get_text().strip())
                ind_comm_pub_reg_modifies.append(ind_comm_pub_reg_modify)
                i += 1
        self.crawler.json_dict['ind_comm_pub_reg_modify'] = ind_comm_pub_reg_modifies

    def parse_ind_comm_pub_arch_pages(self, page):
        ck_string = u'暂无数据'
        soup = BeautifulSoup(page, 'html5lib')
        beian_div = soup.find('div', {'id': 'beian'})

        zyry_table = beian_div.find('table', {'id': 'perTab'})
        ind_comm_pub_arch_key_persons = []
        if zyry_table:
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

        detail_arch_branch_infoes = []
        arch_branch_info = beian_div.find('table', {'id': 'branTab'})
        if arch_branch_info:
            arch_branch_trs = arch_branch_info.find_all('tr')
            if len(arch_branch_trs) > 2:
                i = 2
                while i < len(arch_branch_trs) - 1:
                    detail_arch_branch_info = {}
                    tds = arch_branch_trs[i].find_all('td')
                    if len(tds) <= 0:
                        break
                    detail_arch_branch_info[u'序号'] = (tds[0].get_text().strip())
                    detail_arch_branch_info[u'注册号'] = (tds[1].get_text().strip())
                    detail_arch_branch_info[u'名称'] = (tds[2].get_text().strip())
                    detail_arch_branch_info[u'登记机关'] = (tds[3].get_text().strip())
                    detail_arch_branch_infoes.append(detail_arch_branch_info)
                    i += 1

        self.crawler.json_dict['ind_comm_pub_arch_branch'] = detail_arch_branch_infoes

        # 清算信息

    def parse_ind_comm_pub_movable_property_reg_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 动产抵押
        ck_string = '暂无数据'
        detail_movable_property_reg_infoes = []
        movable_property_reg_info = soup.find('table', {'id': 'moveTab'})
        if movable_property_reg_info:
            movable_property_reg_trs = movable_property_reg_info.find_all('tr')
            if len(movable_property_reg_trs) > 2:
                i = 2
                while i < len(movable_property_reg_trs):
                    if ck_string in movable_property_reg_info.get_text():
                        break
                    detail_movable_property_reg_info = {}
                    tds = movable_property_reg_trs[i].find_all('td')
                    if len(tds) <= 0:
                        break
                    detail_movable_property_reg_info[u'序号'] = (tds[0].get_text().strip())
                    detail_movable_property_reg_info[u'登记编号'] = (tds[1].get_text().strip())
                    detail_movable_property_reg_info[u'登记日期'] = (tds[2].get_text().strip())
                    detail_movable_property_reg_info[u'登记机关'] = (tds[3].get_text().strip())
                    detail_movable_property_reg_info[u'被担保债权数额'] = (tds[4].get_text().strip())
                    detail_movable_property_reg_info[u'状态'] = (tds[5].get_text().strip())
                    detail_movable_property_reg_infoes.append(detail_movable_property_reg_info)
                    i += 1
        self.crawler.json_dict['ind_comm_pub_movable_property_reg'] = detail_movable_property_reg_infoes

    def parse_ind_comm_pub_equity_ownership_reg_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 股权出质
        equity_ownership_reges = []
        equity_table = soup.find('table', {'id': 'stockTab'})
        if equity_table:
            ck_string = u'暂无数据'
            if ck_string in equity_table.get_text().strip():
                return
            equity_trs = equity_table.find_all('tr')
            if len(equity_trs) > 2:
                i = 2
                while i < len(equity_trs):
                    equity_ownership_reg = {}
                    tds = equity_trs[i].find_all('td')
                    if len(tds) <= 0:
                        break
                    equity_ownership_reg[u'序号'] = (tds[0].get_text().strip())
                    equity_ownership_reg[u'登记编号'] = (tds[1].get_text().strip())
                    equity_ownership_reg[u'出质人'] = (tds[2].get_text().strip())
                    equity_ownership_reg[u'证照/证件号码（类型'] = (tds[3].get_text().strip())
                    equity_ownership_reg[u'出质股权数额'] = (tds[4].get_text().strip())
                    equity_ownership_reg[u'质权人'] = (tds[5].get_text().strip())
                    equity_ownership_reg[u'证照/证件号码（类型'] = (tds[6].get_text().strip())
                    equity_ownership_reg[u'股权出质设立登记日期'] = (tds[7].get_text().strip())
                    equity_ownership_reg[u'状态'] = (tds[8].get_text().strip())
                    equity_ownership_reg[u'变化情况'] = None
                    equity_ownership_reges.append(equity_ownership_reg)
                    i += 1
        self.crawler.json_dict['ind_comm_pub_equity_ownership_reg'] = equity_ownership_reges

    def parse_ind_comm_pub_administration_sanction_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        ck_string = u'暂无数据'
        # 行政处罚
        detail_administration_sanction_infoes = []
        administration_sanction_info = soup.find('table', {'id': 'penTab'})
        if administration_sanction_info:
            administration_sanction_trs = administration_sanction_info.find_all('tr')
            if len(administration_sanction_trs) > 2:
                i = 2
                while i < len(administration_sanction_trs):
                    if ck_string in administration_sanction_info.get_text().strip():
                        break
                    detail_administration_sanction_info = {}
                    tds = administration_sanction_trs[i].find_all('td')
                    if len(tds) <= 0:
                        break
                    detail_administration_sanction_info[u'序号'] = (tds[0].get_text().strip())
                    detail_administration_sanction_info[u'行政处罚决定书文号'] = (tds[1].get_text().strip())
                    detail_administration_sanction_info[u'违法行为类型'] = (tds[2].get_text().strip())
                    detail_administration_sanction_info[u'行政处罚内容'] = (tds[3].get_text().strip())
                    detail_administration_sanction_info[u'作出行政处罚决定机关名称'] = (tds[4].get_text().strip())
                    detail_administration_sanction_info[u'作出行政处罚决定日期'] = (tds[5].get_text().strip())
                    detail_administration_sanction_info[u'公示日期'] = (tds[6].get_text().strip())
                    detail_administration_sanction_infoes.append(detail_administration_sanction_info)
                    i += 1
        self.crawler.json_dict['ind_comm_pub_administration_sanction'] = detail_administration_sanction_infoes

    def parse_ind_comm_pub_business_exception_pages(self, page):
        """
        经营异常
        """
        soup = BeautifulSoup(page, 'html5lib')
        ck_string = u'暂无数据'
        detail_business_exception_infoes = []
        business_exception_info = soup.find('table', {'id': 'excpTab'})
        if business_exception_info:
            business_exception_trs = business_exception_info.find_all('tr')
            if len(business_exception_trs) > 2:
                i = 2
                while i < len(business_exception_trs):
                    if ck_string in business_exception_info.get_text().strip():
                        break
                    detail_business_exception_info = {}
                    tds = business_exception_trs[i].find_all('td')
                    if len(tds) <= 0:
                        break
                    detail_business_exception_info[u'序号'] = (tds[0].get_text().strip())
                    detail_business_exception_info[u'列入经营异常名录原因'] = (tds[1].get_text.strip()(
                    ))
                    detail_business_exception_info[u'列入日期'] = (tds[2].get_text().strip())
                    detail_business_exception_info[u'移出经营异常名录原因'] = (tds[3].get_text.strip()(
                    ))
                    detail_business_exception_info[u'移出日期'] = (tds[4].get_text().strip())
                    detail_business_exception_info[u'作出决定机关'] = (tds[5].get_text().strip())
                    detail_business_exception_infoes.append(detail_business_exception_info)
                    i += 1
        self.crawler.json_dict['ind_comm_pub_business_exception'] = detail_business_exception_infoes

    def parse_ind_comm_pub_serious_violate_law_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 严重违法
        ck_string = u'暂无数据'
        detail_serious_violate_law_infoes = []
        serious_violate_law_info = soup.find('table', {'id': 'illegalTab'})
        if serious_violate_law_info:
            serious_violate_law_trs = serious_violate_law_info.find_all('tr')
            if len(serious_violate_law_trs) > 2:
                i = 2
                while i < len(serious_violate_law_trs):
                    if ck_string in serious_violate_law_info.get_text().strip():
                        break
                    detail_serious_violate_law_info = {}
                    tds = serious_violate_law_trs[i].find_all('td')
                    if len(tds) <= 0:
                        break
                    detail_serious_violate_law_info[u'序号'] = (tds[0].get_text().strip())
                    detail_serious_violate_law_info[u'列入严重违法企业名单原因'] = (tds[1].get_text().strip())
                    detail_serious_violate_law_info[u'列入日期'] = (tds[2].get_text().strip())
                    detail_serious_violate_law_info[u'移出严重违法企业名单原因'] = (tds[3].get_text().strip())
                    detail_serious_violate_law_info[u'移出日期'] = (tds[4].get_text().strip())
                    detail_serious_violate_law_info[u'作出决定机关'] = (tds[5].get_text().strip())
                    detail_serious_violate_law_infoes.append(detail_serious_violate_law_info)
                    i += 1
        self.crawler.json_dict['ind_comm_pub_serious_violate_law'] = detail_serious_violate_law_infoes

    def parse_ind_comm_pub_spot_check_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 抽查检查
        ck_string = u'暂无数据'
        detail_spot_check_infoes = []
        spot_check_info = soup.find('table', {'id': 'checkTab'})
        if spot_check_info:
            spot_check_trs = spot_check_info.find_all('tr')
            if len(spot_check_trs) > 2:
                i = 2
                while i < len(spot_check_trs):
                    if ck_string in spot_check_info.get_text().strip():
                        break
                    detail_spot_check_info = {}
                    tds = spot_check_trs[i].find_all('td')
                    if len(tds) <= 0:
                        break
                    detail_spot_check_info[u'序号'] = (tds[0].get_text().strip())
                    detail_spot_check_info[u'检查实施机关'] = (tds[1].get_text().strip())
                    detail_spot_check_info[u'类型'] = (tds[2].get_text().strip())
                    detail_spot_check_info[u'日期'] = (tds[3].get_text().strip())
                    detail_spot_check_info[u'结果'] = (tds[4].get_text().strip())
                    detail_spot_check_infoes.append(detail_spot_check_info)
                    i += 1
        self.crawler.json_dict['ind_comm_pub_spot_check'] = detail_spot_check_infoes

    def parse_ent_pub_shareholder_capital_contribution_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 股东出资
        shareholder_capital_contributiones = []
        touziren_div = soup.find('div', {'id': 'touziren'})
        equity_table = touziren_div.find('table', {'class': 'detailsList'})
        if equity_table:
            equity_trs = equity_table.find_all('tr')
            if len(equity_trs) > 3:
                i = 3
                while i < len(equity_trs) - 1:
                    tds = equity_trs[i].find_all('td')
                    shareholder_capital_contribution = {}
                    if len(tds) <= 0:
                        break
                    shareholder_capital_contribution[u'股东'] = (tds[0].get_text().strip())
                    shareholder_capital_contribution[u'认缴额'] = (tds[1].get_text().strip())
                    shareholder_capital_contribution[u'实缴额'] = (tds[2].get_text().strip())
                    shareholder_capital_contribution[u'认缴出资方式'] = (tds[3].get_text().strip())
                    shareholder_capital_contribution[u'认缴出资额'] = (tds[4].get_text().strip())
                    shareholder_capital_contribution[u'认缴出资日期'] = (tds[5].get_text().strip())
                    shareholder_capital_contribution[u'实缴出资方式'] = (tds[6].get_text().strip())
                    shareholder_capital_contribution[u'实缴出资额'] = (tds[7].get_text().strip())
                    shareholder_capital_contribution[u'实缴出资日期'] = (tds[8].get_text().strip())
                    shareholder_capital_contributiones.append(shareholder_capital_contribution)
                    i += 1
        self.crawler.json_dict['ent_pub_shareholder_capital_contribution'] = shareholder_capital_contributiones

        # 企业变更信息
        detail_reg_modify_infoes = []
        reg_modify_info = soup.find_all('table', {'class': 'detailsList'})[1]
        if reg_modify_info:
            reg_modify_trs = reg_modify_info.find_all('tr')
            if len(reg_modify_trs) > 2:
                i = 2
                while i < len(reg_modify_trs):
                    detail_reg_modify_info = {}
                    tds = reg_modify_trs[i].find_all('td')
                    if len(tds) <= 0:
                        break
                    detail_reg_modify_info[u'序号'] = (tds[0].get_text().strip())
                    detail_reg_modify_info[u'变更事项'] = (tds[1].get_text().strip())
                    detail_reg_modify_info[u'变更时间'] = (tds[2].get_text().strip())
                    detail_reg_modify_info[u'变更前'] = (tds[3].get_text().strip())
                    detail_reg_modify_info[u'变更后'] = (tds[4].get_text().strip())

                    detail_reg_modify_infoes.append(detail_reg_modify_info)
                    i += 1
        self.crawler.json_dict['ent_pub_reg_modify'] = detail_reg_modify_infoes

    def parse_ent_pub_ent_annual_report_pages(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        # 企业年报
        ent_pub_ent_annual_reportes = []
        qiyenianbao_div = soup.find('div', {'id': 'qiyenianbao'})
        qiyenianbao_table = qiyenianbao_div.find('table', {'class': 'detailsList'})
        if qiyenianbao_table:
            report_trs = qiyenianbao_table.find_all('tr')
            if len(report_trs) > 2:
                j = 2
                while j < len(report_trs):
                    tds = report_trs[j].find_all('td')
                    if len(tds) <= 1:
                        break
                    ent_pub_ent_annual_report = {}
                    ent_pub_ent_annual_report[u'序号'] = (tds[0].get_text().strip())
                    ent_pub_ent_annual_report[u'报送年度'] = ((tds[1].get_text().strip()) )
                    ent_pub_ent_annual_report[u'发布日期'] = (tds[2].get_text().strip())
                    a_link = tds[1].find('a')
                    if a_link is None:
                        j += 1
                        continue
                    a_click = a_link.get('onclick')
                    m = re.search("\'.*?\'", a_click)
                    if m:
                        postfix_url=m.group(0).strip("'")
                        detail_url = self.crawler.urls['host']+ postfix_url

                    print detail_url
                    detail_page = self.crawler.reqst.get(detail_url,
                                                         timeout=self.crawler.timeout,
                                                         cookies=self.crawler.cookies)
                    if detail_page.status_code != 200:
                        j += 1
                        continue
                    data = {}
                    report_page = detail_page.content
                    soup_reoprt = BeautifulSoup(report_page, 'html5lib')
                    detail = {}
                    detail_div = soup_reoprt.find('div', {'id': 'qufenkuang'})
                    if detail_div is None:
                        j += 1
                        continue
                    base_info = detail_div.find('table', {'class': 'detailsList'})
                    base_trs = base_info.find_all('tr')
                    detail_base_info = {}

                    for base_tr in base_trs[2:]:
                        ths = base_tr.find_all('th')
                        tds = base_tr.find_all('td')
                        if len(ths) != len(tds):
                            continue
                        for i in range(len(ths)):
                            detail_base_info[ths[i].get_text().strip()] = (tds[i].get_text().strip())

                    detail[u'企业基本信息'] = detail_base_info

                    detail_website_infoes = []
                    website_info = soup_reoprt.find('table', {'id': 'siteTab'})
                    if website_info:
                        website_trs = website_info.find_all('tr')
                        if len(website_trs) > 2:
                            i = 2
                            while i < len(website_trs):
                                detail_website_info = {}
                                tds = website_trs[i].find_all('td')
                                if len(tds) <= 0:
                                    break
                                detail_website_info[u'类型'] = (tds[0].get_text().strip())
                                detail_website_info[u'名称'] = (tds[1].get_text().strip())
                                detail_website_info[u'网址'] = (tds[2].get_text().strip())
                                detail_website_infoes.append(detail_website_info)
                                i += 1
                    detail[u'网站或网店信息'] = detail_website_infoes

                    shareholder_capital_contribution_info = soup_reoprt.find('table', {'id': 'invTab'})
                    detail_shareholder_capital_contribution_infoes = []
                    if shareholder_capital_contribution_info:
                        shareholder_capital_contribution_trs = shareholder_capital_contribution_info.find_all('tr')
                        if len(shareholder_capital_contribution_trs) > 2:
                            i = 2
                            while i < len(shareholder_capital_contribution_trs):
                                detail_shareholder_capital_contribution_info = {}
                                tds = shareholder_capital_contribution_trs[i].find_all('td')
                                if len(tds) <= 0:
                                    break
                                detail_shareholder_capital_contribution_info[u'股东'] = (tds[0].get_text().strip())
                                detail_shareholder_capital_contribution_info[u'认缴出资额'] = (tds[1].get_text().strip())
                                detail_shareholder_capital_contribution_info[u'认缴出资时间'] = (tds[2].get_text().strip())
                                detail_shareholder_capital_contribution_info[u'认缴出资方式'] = (tds[3].get_text().strip())
                                detail_shareholder_capital_contribution_info[u'实缴出资额'] = (tds[4].get_text().strip())
                                detail_shareholder_capital_contribution_info[u'出资时间'] = (tds[5].get_text().strip())
                                detail_shareholder_capital_contribution_info[u'出资方式'] = (tds[6].get_text().strip())
                                detail_shareholder_capital_contribution_infoes.append(
                                    detail_shareholder_capital_contribution_info)
                                i += 1
                    detail[u'股东及出资信息'] = detail_shareholder_capital_contribution_infoes

                    detail_outbound_investment_infoes = []
                    outbound_investment_info = soup_reoprt.find('table', {'id': 'invoutTab'})
                    if outbound_investment_info:
                        outbound_investment_trs = outbound_investment_info.find_all('tr')
                        if len(outbound_investment_trs) > 2:
                            i = 2
                            while i < len(outbound_investment_trs):
                                tds = outbound_investment_trs[i].find_all('tr')
                                if len(tds) <= 0:
                                    break
                                detail_outbound_investment_info = {}
                                detail_outbound_investment_info[u'投资设立企业或购买股权企业名称'] = (tds[0].get_text().strip())
                                detail_outbound_investment_info[u'注册号'] = (tds[1].get_text().strip())
                                detail_outbound_investment_infoes.append(detail_outbound_investment_info)
                                i += 1

                    detail[u'对外投资信息'] = detail_outbound_investment_infoes

                    detail_state_of_enterprise_assets_infoes = {}
                    state_of_enterprise_assets_info = soup_reoprt.find_all('table', {'class': 'detailsList'})[4]
                    if state_of_enterprise_assets_info and state_of_enterprise_assets_info.find('tr').get_text().strip() == u'企业资产状况信息':
                        state_of_enterprise_assets_trs = state_of_enterprise_assets_info.find_all('tr')
                        detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[1].find_all('th')[
                            0].get_text().strip()] = (state_of_enterprise_assets_trs[1].find_all('td')[0].get_text().strip())
                        detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[1].find_all('th')[
                            1].get_text().strip()] = (state_of_enterprise_assets_trs[1].find_all('td')[1].get_text().strip())
                        detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[2].find_all('th')[
                            0].get_text().strip()] = (state_of_enterprise_assets_trs[2].find_all('td')[0].get_text().strip())
                        detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[2].find_all('th')[
                            1].get_text().strip()] = (state_of_enterprise_assets_trs[2].find_all('td')[1].get_text().strip())
                        detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[3].find_all('th')[
                            0].get_text().strip()] = (state_of_enterprise_assets_trs[3].find_all('td')[0].get_text().strip())
                        detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[3].find_all('th')[
                            1].get_text().strip()] = (state_of_enterprise_assets_trs[3].find_all('td')[1].get_text().strip())
                        detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[4].find_all('th')[
                            0].get_text().strip()] = (state_of_enterprise_assets_trs[4].find_all('td')[0].get_text().strip())
                        detail_state_of_enterprise_assets_infoes[state_of_enterprise_assets_trs[4].find_all('th')[
                            1].get_text().strip()] = (state_of_enterprise_assets_trs[4].find_all('td')[1].get_text().strip())
                        detail[u'企业资产状况信息'] = detail_state_of_enterprise_assets_infoes

                    provide_guarantee_to_the_outside_info = soup_reoprt.find('table', {'id': 'guaTab'})
                    if provide_guarantee_to_the_outside_info:
                        provide_guarantee_to_the_outside_trs = provide_guarantee_to_the_outside_info.find_all('tr')
                        detail_provide_guarantee_to_the_outside_infoes = []
                        if len(provide_guarantee_to_the_outside_trs) > 2:
                            i = 2
                            while i < len(provide_guarantee_to_the_outside_trs):
                                detail_provide_guarantee_to_the_outside_info = {}
                                tds = provide_guarantee_to_the_outside_trs[i].find_all('td')
                                if len(tds) <= 0:
                                    break
                                detail_provide_guarantee_to_the_outside_info[u'债权人'] = (tds[0].get_text().strip())
                                detail_provide_guarantee_to_the_outside_info[u'债务人'] = (tds[1].get_text().strip())
                                detail_provide_guarantee_to_the_outside_info[u'主债权种类'] = (tds[2].get_text().strip())
                                detail_provide_guarantee_to_the_outside_info[u'主债权数额'] = (tds[3].get_text().strip())
                                detail_provide_guarantee_to_the_outside_info[u'履行债务的期限'] = (tds[4].get_text().strip())
                                detail_provide_guarantee_to_the_outside_info[u'保证的期间'] = (tds[5].get_text().strip())
                                detail_provide_guarantee_to_the_outside_info[u'保证的方式'] = (tds[6].get_text().strip())
                                detail_provide_guarantee_to_the_outside_info[u'保证担保的范围'] = (tds[7].get_text().strip())
                                detail_provide_guarantee_to_the_outside_infoes.append(detail_provide_guarantee_to_the_outside_info)
                                i += 1
                    detail[u'对外提供保证担保信息'] = detail_provide_guarantee_to_the_outside_infoes

                    detail_ent_pub_equity_change_infoes = []
                    ent_pub_equity_change_info = soup_reoprt.find('table', {'id': 'transTab'})
                    if ent_pub_equity_change_info:
                        ent_pub_equity_change_trs = ent_pub_equity_change_info.find_all('tr')
                        if len(ent_pub_equity_change_trs) > 2:
                            i = 2
                            while i < len(ent_pub_equity_change_trs):
                                detail_ent_pub_equity_change_info = {}
                                tds = ent_pub_equity_change_trs[i].find_all('td')
                                if len(tds) <= 0:
                                    break
                                detail_ent_pub_equity_change_info[u'股东'] = (tds[0].get_text().strip())
                                detail_ent_pub_equity_change_info[u'变更前股权比例'] = (tds[1].get_text().strip())
                                detail_ent_pub_equity_change_info[u'变更后股权比例'] = (tds[2].get_text().strip())
                                detail_ent_pub_equity_change_info[u'股权变更日期'] = (tds[3].get_text().strip())
                                detail_ent_pub_equity_change_infoes.append(detail_ent_pub_equity_change_info)
                                i += 1
                    detail[u'股权变更信息'] = detail_ent_pub_equity_change_infoes

                    detail_change_record_infoes = []
                    change_record_info = ent_pub_equity_change_info = soup_reoprt.find('table', {'id': 'modTab'})
                    if change_record_info:
                        change_record_trs = change_record_info.find_all('tr')
                        if len(change_record_trs) > 2:
                            i = 2
                            while i < len(change_record_trs):
                                detail_change_record_info = {}
                                tds = change_record_trs[i].find_all('td')
                                if len(tds) <= 0:
                                    break
                                detail_change_record_info[u'序号'] = (tds[0].get_text().strip())
                                detail_change_record_info[u'修改事项'] = (tds[1].get_text().strip())
                                detail_change_record_info[u'修改前'] = (tds[2].get_text().strip())
                                detail_change_record_info[u'修改后'] = (tds[3].get_text().strip())
                                detail_change_record_info[u'修改日期'] = (tds[4].get_text().strip())
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
        ck_string = u'暂无数据'
        detail_administration_license_infoes = []
        administration_license_div = soup.find('div', {'id': 'xingzhengxuke'})
        administration_license_info = administration_license_div.find('table', {'class': 'detailsList'})
        if administration_license_info:
            administration_license_trs = administration_license_info.find_all('tr')
            if len(administration_license_trs) > 2:
                i = 2
                while i < len(administration_license_trs):
                    if ck_string in administration_license_info.get_text().strip():
                        break
                    detail_administration_license_info = {}
                    tds = administration_license_trs[i].find_all('td')
                    if len(tds) <= 0:
                        break
                    detail_administration_license_info[u'序号'] = (tds[0].get_text().strip())
                    detail_administration_license_info[u'许可文件编号'] = (tds[1].get_text().strip())
                    detail_administration_license_info[u'许可文件名称'] = (tds[2].get_text().strip())
                    detail_administration_license_info[u'有效期自'] = (tds[3].get_text().strip())
                    detail_administration_license_info[u'有效期至'] = (tds[4].get_text().strip())
                    detail_administration_license_info[u'许可机关'] = (tds[5].get_text().strip())
                    detail_administration_license_info[u'许可内容'] = (tds[6].get_text().strip())
                    detail_administration_license_info[u'状态'] = (tds[7].get_text().strip())
                    detail_administration_license_info[u'公示日期'] = (tds[8].get_text().strip())
                    detail_administration_license_info[u'详情'] = (tds[9].get_text().strip())
                    detail_administration_license_infoes.append(detail_administration_license_info)
                    i += 1
        self.crawler.json_dict['ind_comm_pub_administration_license'] = detail_administration_license_infoes

    def parse_ent_pub_administration_sanction_pages(self, page):
        """
        企业-解析行政处罚
        """
        soup = BeautifulSoup(page, 'html5lib')
        ck_string = u'暂无数据'
        detail_administration_sanction_infoes = []
        administration_sanction_div = soup.find('div', {'id': 'xingzhengchufa'})
        administration_sanction_info = administration_sanction_div.find('table', {'class': 'detailsList'})
        if administration_sanction_info is None:
            return
        administration_sanction_trs = administration_sanction_info.find_all('tr')
        if len(administration_sanction_trs) > 2:
            i = 2
            while i < len(administration_sanction_trs):
                if ck_string in administration_sanction_info.get_text().strip():
                    break
                detail_administration_sanction_info = {}
                tds = administration_sanction_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                detail_administration_sanction_info[u'序号'] = (tds[0].get_text().strip())
                detail_administration_sanction_info[u'行政处罚决定书文号'] = (tds[1].get_text().strip())
                detail_administration_sanction_info[u'行政处罚类型'] = (tds[2].get_text().strip())
                detail_administration_sanction_info[u'行政处罚内容'] = (tds[3].get_text().strip())
                detail_administration_sanction_info[u'作出行政处罚决定机关名称'] = (tds[4].get_text().strip())
                detail_administration_sanction_info[u'作出行政处罚决定日期'] = (tds[5].get_text().strip())
                detail_administration_sanction_info[u'公示日期'] = (tds[6].get_text().strip())
                detail_administration_sanction_info[u'备注'] = (tds[7].get_text().strip())
                detail_administration_sanction_infoes.append(detail_administration_sanction_info)
                i += 1
        self.crawler.json_dict['ind_comm_pub_administration_sanction'] = detail_administration_sanction_infoes

    def parse_ent_pub_equity_change_pages(self, page):
        """
            企业-股权变更
        """
        soup = BeautifulSoup(page, 'html5lib')
        ck_string = u'暂无数据'
        detail_equity_change_infoes = []
        equity_change_div = soup.find('div', {'id': 'gudongguquan'})
        equity_change_info = equity_change_div.find('table', {'class': 'detailsList'})
        if equity_change_info is None:
            return
        equity_change_trs = equity_change_info.find_all('tr')
        if len(equity_change_trs) > 2:
            i = 2
            while i < len(equity_change_trs):
                if ck_string in equity_change_info.get_text().strip():
                    break
                detail_equity_change_info = {}
                tds = equity_change_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                detail_equity_change_info[u'序号'] = (tds[0].get_text().strip())
                detail_equity_change_info[u'股东'] = (tds[1].get_text().strip())
                detail_equity_change_info[u'变更前股权比例'] = (tds[2].get_text().strip())
                detail_equity_change_info[u'变更后股权比例'] = (tds[3].get_text().strip())
                detail_equity_change_info[u'股权变更日期'] = (tds[4].get_text().strip())
                detail_equity_change_info[u'填报时间'] = (tds[5].get_text().strip())
                detail_equity_change_infoes.append(detail_equity_change_info)
                i += 1
        self.crawler.json_dict['ind_comm_pub_equity_change'] = detail_equity_change_infoes

    def parse_ent_pub_knowledge_property_pages(self, page):
        """
            企业-解析知识产权出质
        """
        soup = BeautifulSoup(page, 'html5lib')
        ck_string = u'暂无数据'
        knowledge_property_div = soup.find('div', {'id': 'zhishichanquan'})
        knowledge_property_info = knowledge_property_div.find('class', {'id': 'detailsList'})
        if knowledge_property_info is None:
            return

        knowledge_property_trs = knowledge_property_info.find_all('tr')
        detail_knowledge_property_infoes = []
        if len(knowledge_property_trs) > 2:
            i = 2
            while i < len(knowledge_property_trs):
                if ck_string in knowledge_property_info.get_text().strip():
                    break
                detail_knowledge_property_info = {}
                tds = knowledge_property_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                detail_knowledge_property_info[u'序号'] = (tds[0].get_text().strip())
                detail_knowledge_property_info[u'注册号'] = (tds[1].get_text().strip())
                detail_knowledge_property_info[u'名称'] = (tds[2].get_text().strip())
                detail_knowledge_property_info[u'种类'] = (tds[3].get_text().strip())
                detail_knowledge_property_info[u'出质人名称'] = (tds[4].get_text().strip())
                detail_knowledge_property_info[u'质权人名称'] = (tds[5].get_text().strip())
                detail_knowledge_property_info[u'质权登记期限'] = (tds[6].get_text().strip())
                detail_knowledge_property_info[u'状态'] = (tds[7].get_text().strip())
                detail_knowledge_property_info[u'变化情况'] = (tds[8].get_text().strip())

                detail_knowledge_property_infoes.append(detail_knowledge_property_info)
                i += 1
        self.crawler.json_dict['ind_comm_pub_knowledge_property'] = detail_knowledge_property_infoes

    def parse_judical_assist_pub_equity_freeze_pages(self, page):
        """
        司法
        """
        soup = BeautifulSoup(page, 'html5lib')
        equity_freeze_div = soup.find('div', {'id': 'gqdj'})
        equity_freeze_info = equity_freeze_div.find('table', {'id': 'frzeTab'})
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
                detail_equity_freeze_info[u'序号'] = (tds[0].get_text().strip())
                detail_equity_freeze_info[u'被执行人'] = (tds[1].get_text().strip())
                detail_equity_freeze_info[u'股权数额'] = (tds[2].get_text().strip())
                detail_equity_freeze_info[u'执行法院'] = (tds[3].get_text().strip())
                detail_equity_freeze_info[u'协助公示通知书文号'] = (tds[4].get_text().strip())
                detail_equity_freeze_info[u'状态'] = (tds[5].get_text().strip())
                detail_equity_freeze_info[u'详情'] = (tds[6].get_text().strip())

                detail_equity_freeze_infoes.append(detail_equity_freeze_info)
                i += 1
        self.crawler.json_dict['judical_assist_pub_equity_freeze'] = detail_equity_freeze_infoes

    def parse_judical_assist_pub_shareholder_modify_pages(self, page):
        """
        司法
        """
        soup = BeautifulSoup(page, 'html5lib')
        detail_shareholder_modify_infoes = []
        shareholder_modify_div = soup.find('div', {'id': 'gqbg'})
        shareholder_modify_info = shareholder_modify_div.find('table', {'id': 'equAltTab'})
        if shareholder_modify_info is None:
            return
        shareholder_modify_trs = shareholder_modify_info.find_all('tr')
        if len(shareholder_modify_trs) > 2:
            i = 2
            while i < len(shareholder_modify_trs):
                detail_shareholder_modify_info = {}
                tds = shareholder_modify_trs[i].find_all('td')
                if len(tds) <= 0:
                    break
                detail_shareholder_modify_info[u'序号'] = (tds[0].get_text().strip())
                detail_shareholder_modify_info[u'被执行人'] = (tds[1].get_text().strip())
                detail_shareholder_modify_info[u'股权数额'] = (tds[2].get_text().strip())
                detail_shareholder_modify_info[u'受让人'] = (tds[3].get_text().strip())
                detail_shareholder_modify_info[u'执行法院'] = (tds[4].get_text().strip())
                detail_shareholder_modify_info[u'详情'] = (tds[5].get_text().strip())

                detail_shareholder_modify_infoes.append(detail_shareholder_modify_info)
                i += 1
        self.crawler.json_dict['judical_assist_pub_shareholder_modify'] = detail_shareholder_modify_infoes


class GeneratorTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def request_without_session(self, method, url, **kwargs):
        try:
            res = requests.request(method, url, **kwargs)
            if res.status_code != 200:
                print "not 200"
                return
            print res.content
        except Exception as e:
            print traceback.format_exc()
    @unittest.skip("skipping read from file")
    def test_crawl(self):
        captcha = 'http://xygs.gsaic.gov.cn/gsxygs/securitycode.jpg?v=1464660204507'
        res = requests.get(captcha)
        path = os.path.join(os.getcwd(), 'captcha.jpeg')
        with open(path, 'w') as f:
            f.write(res.content)
        Cookie =res.cookies.get_dict()
        # 休息2秒, 这个操蛋的问题困扰我2天了。永不为奴。
        time.sleep(2)
        print Cookie
        # Cookie = {'session_authcode': '6', 'JSESSIONID':'42B4333B56682B9C7965DF31D8B452E9'}
        url = 'http://xygs.gsaic.gov.cn/gsxygs/pub!list.do'
        data = {'queryVal':'620000000001727' , 'authCodeQuery' : Cookie.get('session_authcode', 0)}
        print data
        self.request_without_session('POST',url, data = data, cookies=Cookie)


    # @unittest.skip("ere")
    def test_gansu(self):
        path = os.getcwd()
        Gansu = GansuCrawler(path)
        # 621122000001709
        # 620000000001727
        result = Gansu.run('621122000001709')
        print result
        result = json.loads(result)
        self.assertEqual(type(result), list)
        for item in result:
            for k, v in item.items():
                self.assertEqual(k, u'621122000001709')
                self.assertTrue(v['ind_comm_pub_reg_basic'])
                self.assertEqual(v['ind_comm_pub_reg_basic'][u'名称'], u'华龙证券股份有限公司陇西证券营业部')

    @unittest.skip("123")
    def test_gansu_with_name(self):
        path = os.getcwd()
        Gansu = GansuCrawler(path)
        result = Gansu.run(u'华龙证券股份有限公司')
        self.assertTrue(result)
        result = json.loads(result)
        self.assertEqual(len(result), 3)
        print result



if __name__ == '__main__':
    unittest.main()
