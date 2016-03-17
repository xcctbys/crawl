#!/usr/bin/env python
#encoding=utf-8
import requests
import json
import os
import time
import re
import random
import urllib
import unittest
import threading
import copy
from datetime import datetime, timedelta
from . import settings
from enterprise.libs.CaptchaRecognition import CaptchaRecognition
import logging
from bs4 import BeautifulSoup
from crawler import Crawler
from crawler import CrawlerUtils
from crawler import Parser
from enterprise.libs.proxies import Proxies


class JiangsuCrawler(Crawler):
    """江苏工商公示信息网页爬虫
    """
    #html数据的存储路径
    html_restore_path = settings.json_restore_path + '/jiangsu/'

    #验证码图片的存储路径
    ckcode_image_path = settings.json_restore_path + '/jiangsu/ckcode.jpg'
    code_cracker = CaptchaRecognition('jiangsu')
    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {'host': 'www.jsgsj.gov.cn',
            'official_site': 'http://www.jsgsj.gov.cn:58888/province/',
            'get_checkcode': 'http://www.jsgsj.gov.cn:58888/province/rand_img.jsp?type=7',
            'post_checkcode': 'http://www.jsgsj.gov.cn:58888/province/infoQueryServlet.json?queryCinfo=true',
            'ind_comm_pub_skeleton': 'http://www.jsgsj.gov.cn:58888/ecipplatform/inner_ci/ci_queryCorpInfor_gsRelease.jsp',
            'ent_pub_skeleton': 'http://www.jsgsj.gov.cn:58888/ecipplatform/inner_ci/ci_queryCorpInfo_qyRelease.jsp',
            'other_dept_pub_skeleton': 'http://www.jsgsj.gov.cn:58888/ecipplatform/inner_ci/ci_queryCorpInfo_qtbmRelease.jsp',
            'judical_assist_pub_skeleton': 'http://www.jsgsj.gov.cn:58888/ecipplatform/inner_ci/ci_queryJudicialAssistance.jsp',
            'annual_report_skeleton': 'http://www.jsgsj.gov.cn:58888/ecipplatform/reportCheck/company/cPublic.jsp',

            'ci_enter': 'http://www.jsgsj.gov.cn:58888/ecipplatform/ciServlet.json?ciEnter=true',
            'common_enter': 'http://www.jsgsj.gov.cn:58888/ecipplatform/commonServlet.json?commonEnter=true',
            'nb_enter': 'http://www.jsgsj.gov.cn:58888/ecipplatform/nbServlet.json?nbEnter=true',
            'ci_detail': 'http://www.jsgsj.gov.cn:58888/ecipplatform/ciServlet.json?ciDetail=true'
            }

    def __init__(self, json_restore_path= None):
        """
        初始化函数
        Args:
            json_restore_path: json文件的存储路径，所有江苏的企业，应该写入同一个文件，因此在多线程爬取时设置相同的路径。同时，
             需要在写入文件的时候加锁
        Returns:
        """
        self.proxies = Proxies().get_proxies()
        self.json_restore_path = json_restore_path

        self.parser = JiangsuParser(self)
        self.reqst = requests.Session()
        self.reqst.headers.update({
                'Accept': 'text/html, application/xhtml+xml, */*',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})
        self.corp_org = ''
        self.corp_id = ''
        self.corp_seq_id = ''
        self.common_enter_post_data = {}
        self.ci_enter_post_data = {}
        self.nb_enter_post_data = {}
        self.post_info = {
            'ind_comm_pub_reg_basic': {'url_type': 'ci_enter', 'post_type': 'ci_enter', 'specificQuery': 'basicInfo'},
            'ind_comm_pub_reg_shareholder': {'url_type': 'ci_enter', 'post_type': 'ci_enter_with_recordline', 'specificQuery': 'investmentInfor'},
            'ind_comm_pub_reg_modify': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'biangeng'},
            'ind_comm_pub_arch_key_persons': {'url_type': 'ci_enter', 'post_type': 'ci_enter_with_recordline', 'specificQuery': 'personnelInformation'},
            'ind_comm_pub_arch_branch': {'url_type': 'ci_enter', 'post_type': 'ci_enter_with_recordline', 'specificQuery': 'branchOfficeInfor'},
            #'ind_comm_pub_arch_liquadition': {'url_type': 'ci_enter', 'post_type': 'common_enter', 'specificQuery': 'qsfzr'},
            'ind_comm_pub_movable_property_reg': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'dongchan'},
            'ind_comm_pub_equity_ownership_reg': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'guquanchuzhi'},
            'ind_comm_pub_administration_sanction': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'chufa'},
            'ind_comm_pub_business_exception': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'abnormalInfor'},
            #'ind_comm_pub_serious_violate_law': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'xxx'},
            'ind_comm_pub_spot_check': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'checkup'},

            'ind_comm_pub_reg_shareholder_detail': {'url_type': 'ci_detail', 'post_type': 'ci_detail', 'specificQuery': 'investorInfor'},

            'ent_pub_annual_report': {'url_type': 'nb_enter', 'post_type': 'nb_enter', 'propertiesName': 'query_report_list'},
            'annual_report_detail': {'url_type': 'nb_enter', 'post_type': 'nb_enter'},
            'ent_pub_shareholder_capital_contribution': {'url_type': 'nb_enter', 'post_type': 'nb_enter', 'propertiesName': 'query_tzcz'},
            'ent_pub_administrative_license': {'url_type': 'nb_enter', 'post_type': 'nb_enter', 'propertiesName': 'query_xzxk'},
            'ent_pub_knowledge_property': {'url_type': 'nb_enter', 'post_type': 'nb_enter', 'propertiesName': 'query_zscq'},
            'ent_pub_administration_sanction': {'url_type': 'nb_enter', 'post_type': 'nb_enter', 'propertiesName': 'query_xzcf'},

            'other_dept_pub_administration_license': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'xingzheng'},
            'other_dept_pub_administration_sanction': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'xingzhengchufa'},

            'judical_assist_pub_equity_freeze': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'gqdjList'},
            'judical_assist_pub_shareholder_modify': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'gdbgList'}
        }

    def run(self, ent_number=0):
        if not os.path.exists(self.html_restore_path):
            os.makedirs(self.html_restore_path)

        return Crawler.run(self, ent_number)
        '''
        self.ent_number = str(ent_number)
        #对每个企业都指定一个html的存储目录
        self.html_restore_path = self.html_restore_path + self.ent_number + '/'
        if settings.save_html and not os.path.exists(self.html_restore_path):
            CrawlerUtils.make_dir(self.html_restore_path)

        self.json_dict = {}

        if not self.crawl_check_page():
            settings.logger.error('crack check code failed, stop to crawl enterprise %s' % self.ent_number)
            return False

        self.crawl_ind_comm_pub_pages()
        self.crawl_ent_pub_pages()
        self.crawl_other_dept_pub_pages()
        self.crawl_judical_assist_pub_pub_pages()

        #采用多线程，在写入文件时需要注意加锁
        self.write_file_mutex.acquire()
        CrawlerUtils.json_dump_to_file(self.json_restore_path, {self.ent_number: self.json_dict})
        self.write_file_mutex.release()
        return True
        '''

    def crawl_check_page(self):
        """爬取验证码页面，包括下载验证码图片以及破解验证码
        :return true or false
        """
        resp = self.crawl_page_by_url(self.urls['official_site'])
        if not resp:
            logging.error("crawl the first page page failed!\n")
            return False
        count = 0
        while count < 15:
            count += 1
            ckcode = self.crack_checkcode()
            if not ckcode[1]:
                logging.error("crawl checkcode failed! count number = %d\n"%(count))
                continue
            data = {'name': self.ent_number, 'verifyCode': ckcode[1]}
            resp = self.crawl_page_by_url_post(self.urls['post_checkcode'], data=data)

            if resp.find("onclick") >= 0 and self.parse_post_check_page(resp):
                return True
            else:
                logging.error("crawl post check page failed! count number = %d\n"%(count))
            time.sleep(random.uniform(5, 8))
        return False

    def get_page_data(self, page_name, real_post_data=None):
        """获取页面数据，通过页面名称，和post_data， 江苏的页面中几乎全部都是post方式来获取数据
        """
        url = self.urls[self.post_info[page_name].get('url_type')]
        logging.info('get %s, url:\n%s\n' % (page_name, url))
        if real_post_data:
            return self.get_pages(url, real_post_data)

        if self.post_info[page_name].get('post_type') == 'ci_enter':
            self.ci_enter_post_data['specificQuery'] = self.post_info[page_name].get('specificQuery')
            post_data = self.ci_enter_post_data
        elif self.post_info[page_name].get('post_type') == 'ci_enter_with_recordline':
            self.ci_enter_with_record_line_post_data['specificQuery'] = self.post_info[page_name].get('specificQuery')
            post_data = self.ci_enter_with_record_line_post_data
        elif self.post_info[page_name].get('post_type') == 'common_enter':
            self.common_enter_post_data['propertiesName'] = self.post_info[page_name].get('propertiesName')
            post_data = self.common_enter_post_data
        elif self.post_info[page_name].get('post_type') == 'ci_detail':
            self.ci_detail_post_data['specificQuery'] = self.post_info[page_name].get('specificQuery')
            post_data = self.ci_detail_post_data
        elif self.post_info[page_name].get('post_type') == 'nb_enter':
            self.nb_enter_post_data['propertiesName'] = self.post_info[page_name].get('propertiesName')
            post_data = self.nb_enter_post_data
        return self.get_pages(url, post_data)

    def crawl_ind_comm_pub_pages(self):
        """爬取工商公示信息
        """
        if not self.parser.ind_comm_pub_skeleton_built:
            page = self.crawl_skeleton_page('ind_comm_pub_skeleton')
            if not page:
                logging.error('crawl ind comm pub skeleton failed!')
                return False
            self.parser.parse_page('ind_comm_pub_skeleton', page)

        for item in ('ind_comm_pub_reg_basic',          # 登记信息-基本信息
                     'ind_comm_pub_reg_shareholder',   # 股东信息
                     'ind_comm_pub_reg_modify',
                     'ind_comm_pub_arch_key_persons',  # 备案信息-主要人员信息
                     'ind_comm_pub_arch_branch',      # 备案信息-分支机构信息
                     #'ind_comm_pub_arch_liquidation', # 备案信息-清算信息, 网页中没有
                     'ind_comm_pub_movable_property_reg', # 动产抵押登记信息
                     #'ind_comm_pub_equity_ownership_reg', # 股权出置登记信息
                     'ind_comm_pub_administration_sanction', # 行政处罚信息
                     #'ind_comm_pub_business_exception',  # 经营异常信息 , 网页中不存在
                     #'ind_comm_pub_serious_violate_law',  # 严重违法信息
                     'ind_comm_pub_spot_check'):        # 抽查检查信息

            page_data = self.get_page_data(item)
            self.json_dict[item] = self.parser.parse_page(item, page_data)

    def crawl_ent_pub_pages(self):
        """爬取企业公示信息
        """
        if not self.parser.ent_pub_skeleton_built:
            page = self.crawl_skeleton_page('ent_pub_skeleton')
            if not page:
                logging.error('crawl ent pub skeleton failed!')
                return False
            self.parser.parse_page('ent_pub_skeleton', page)

        if not self.parser.annual_report_skeleton_built:
            page = self.crawl_skeleton_page('annual_report_skeleton')
            if not page:
                logging.error('crawl annual report skeleton failed!')
                return False
            self.parser.parse_page('annual_report_skeleton', page)

        for item in ('ent_pub_annual_report',
                    #'ent_pub_shareholder_capital_contribution', #企业投资人出资比例
                    #'ent_pub_equity_change', #股权变更信息
                    'ent_pub_administrative_license',#行政许可信息
                    'ent_pub_knowledge_property', #知识产权出资登记
                    #'ent_pub_administration_sanction' #行政许可信息
                    ):
            page_data = self.get_page_data(item)
            self.json_dict[item] = self.parser.parse_page(item, page_data)

    def crawl_other_dept_pub_pages(self):
        """爬取其他部门公示信息
        """
        if not self.parser.other_dept_pub_skeleton_built:
            page = self.crawl_skeleton_page('other_dept_pub_skeleton')
            if not page:
                logging.error('crawl other dept pub skeleton failed!')
                return False
            self.parser.parse_page('other_dept_pub_skeleton', page)

        for item in ('other_dept_pub_administration_license',   #行政许可信息
                    'other_dept_pub_administration_sanction'    #行政处罚信息
        ):
            page_data = self.get_page_data(item)
            self.json_dict[item] = self.parser.parse_page(item, page_data)

    def crawl_judical_assist_pub_pub_pages(self):
        """爬取司法协助信息
        """
        if not self.parser.judical_assist_pub_skeleton_built:
            page = self.crawl_skeleton_page('judical_assist_pub_skeleton')
            if not page:
                logging.error('crawl judical assist skeleton failed!')
                return False
            self.parser.parse_page('judical_assist_pub_skeleton', page)

        for item in ('judical_assist_pub_equity_freeze',    #股权冻结信息
                    'judical_assist_pub_shareholder_modify' #股东变更信息
        ):
            page_data = self.get_page_data(item)
            self.json_dict[item] = self.parser.parse_page(item, page_data)

    def get_pages(self, url, post_data):
        """获取网页数据
        Args:
            url: url地址
            post_data: post方式获取数据，返回的如果是一个列表，则将列表的所有元素都获得才返回
        Returns:
        """
        resp = self.crawl_page_by_url_post(url, data=post_data)
        if not resp:
            logging.error('get all pages of a section failed!')
            return
        else:
            json_obj = json.loads(resp)
            if type(json_obj) == dict and json_obj.get('total', None) and int(json_obj.get('total')) > 5:
                post_data['pageSize'] = json_obj.get('total')
                resp = self.crawl_page_by_url_post(url, data=post_data)
                if not resp :
                    logging.error('get all pages of a section failed!')
                    return
        return resp

    def crawl_skeleton_page(self, name):
        """爬取网页表格的框架页面，在江苏的网页中， 工商公示信息, 企业公示信息，其他部门公示信息，司法协助信息
        所有的tab页面中的表格结构都在一个最开始的页面中给出
        """
        url = self.urls[name]
        post_data = {'org': self.corp_org, 'id': self.corp_id, 'seq_id': self.corp_seq_id,
                     'reg_no': self.ent_number, 'name': self.ent_number,
                     'containContextPath': 'ecipplatform', 'corp_name': self.ent_number}
        resp = self.crawl_page_by_url_post(url, data=post_data)
        if not resp :
            logging.error('crawl %s page failed, error code.\n' % (name))
            return False
        return resp

    def parse_post_check_page(self, page):
        """解析提交验证码之后的页面，提取所需要的信息，比如corp id等
        Args:
            page: 提交验证码之后的页面
        """
        m = re.search(r'onclick=\\\"\w+\(\'([\w\./]+)\',\'(\w*)\',\'(\w*)\',\'(\w*)\',\'(\w*)\',\'(\w*)\',\'(\w*)\'\)', page)
        if m:
            self.corp_org = m.group(2)
            self.corp_id = m.group(3)
            self.corp_seq_id = m.group(4)
            self.common_enter_post_data = {
                'showRecordLine': '1',
                'specificQuery': 'commonQuery',
                'propertiesName': '',
                'corp_org': self.corp_org,
                'corp_id': self.corp_id,
                'pageNo': '1',
                'pageSize': '5'
            }
            self.ci_enter_post_data = {
                'org': self.corp_org,
                'id': self.corp_id,
                'seq_id': self.corp_seq_id,
                'specificQuery': ''
            }
            self.ci_enter_with_record_line_post_data = {
                'CORP_ORG': self.corp_org,
                'CORP_ID': self.corp_id,
                'CORP_SEQ_ID': self.corp_seq_id,
                'specificQuery': '',
                'pageNo': '1',
                'pageSize': '5',
                'showRecordLine': '1'
            }
            self.ci_detail_post_data = {
                'ORG': self.corp_org,
                'ID': '',
                'CORP_ORG': self.corp_org,
                'CORP_ID': self.corp_id,
                'SEQ_ID': '',
                'REG_NO': self.ent_number,
                'specificQuery': ''
            }
            self.nb_enter_post_data = {
                'ID': '',
                'REG_NO': self.ent_number,
                'showRecordLine': '0',
                'specificQuery': 'gs_pb',
                'propertiesName': '',
                'pageNo': '1',
                'pageSize': '5',
                'ADMIT_MAIN': '08'
            }
            return True
        return False

    def crack_checkcode(self):
        """破解验证码
        :return 破解后的验证码
        """
        resp = self.crawl_page_by_url(self.urls['get_checkcode'])
        if not resp :
            logging.error('Failed, exception occured when getting checkcode')
            return ('', '')
        time.sleep(random.uniform(2, 4))

        self.write_file_mutex.acquire()
        ckcode = ('', '')
        with open(self.ckcode_image_path, 'wb') as f:
            f.write(resp)
        try:
            ckcode = self.code_cracker.predict_result(self.ckcode_image_path)
        except Exception as e:
            logging.error('exception occured when crack checkcode')
            ckcode = ('', '')
        finally:
            pass
        self.write_file_mutex.release()
        return ckcode

    def crawl_page_by_url(self, url):
        """根据url直接爬取页面
        """
        try:
            resp = self.reqst.get(url, proxies= self.proxies)
            if resp.status_code != 200:
                logging.error('crawl page by url failed! url = %s' % url)
            page = resp.content
            time.sleep(random.uniform(0.2, 1))
            # if saveingtml:
            #     CrawlerUtils.save_page_to_file(self.html_restore_path + 'detail.html', page)
            return page
        except Exception as e:
            logging.error("crawl page by url exception %s"%(type(e)))

        return None

    def crawl_page_by_url_post(self, url, data):
        """ 根据url和post数据爬取页面
        """
        r = self.reqst.post(url, data, proxies = self.proxies)
        time.sleep(random.uniform(0.2, 1))
        if r.status_code != 200:
            logging.error(u"Getting page by url with post:%s\n, return status %s\n"% (url, r.status_code))
            return False
        return r.content

    def get_annual_report_detail(self, report_year, report_id):
        """获取企业年报的详细信息
        """
        annual_report_detail = {}
        post_data = self.nb_enter_post_data
        post_data['ID'] = report_id
        post_data['showRecordLine'] = '0'
        post_data['OPERATE_TYPE'] = '2'
        post_data['propertiesName'] = 'query_basicInfo'
        page_data = self.get_page_data('annual_report_detail', post_data)
        annual_report_detail[u'企业基本信息'] = self.parser.parse_page('annual_report_ent_basic_info', page_data)
        annual_report_detail[u'企业资产状况信息'] = self.parser.parse_page('annual_report_ent_property_info', page_data)

        post_data['showRecordLine'] = '1'
        post_data['propertiesName'] = 'query_websiteInfo'
        page_data = self.get_page_data('annual_report_detail', post_data)
        annual_report_detail[u'网站或网店信息'] = self.parser.parse_page('annual_report_web_info', page_data)

        post_data['propertiesName'] = 'query_investInfo'
        page_data = self.get_page_data('annual_report_detail', post_data)
        annual_report_detail[u'对外投资信息'] = self.parser.parse_page('annual_report_investment_abord_info', page_data)

        post_data['MAIN_ID'] = report_id
        post_data['OPERATE_TYPE'] = '1'
        post_data['TYPE'] = 'NZGS'
        post_data['ADMIT_MAIN'] = '08'
        post_data['propertiesName'] = 'query_stockInfo'
        page_data = self.get_page_data('annual_report_detail', post_data)
        annual_report_detail[u'股东及出资信息'] = self.parser.parse_page('annual_report_shareholder_info', page_data)

        post_data['propertiesName'] = 'query_InformationSecurity'
        page_data = self.get_page_data('annual_report_detail', post_data)
        annual_report_detail[u'对外提供保证担保信息'] = self.parser.parse_page('annual_report_external_guarantee_info', page_data)

        post_data['propertiesName'] = 'query_RevisionRecord'
        page_data = self.get_page_data('annual_report_detail', post_data)
        annual_report_detail[u'修改记录'] = self.parser.parse_page('annual_report_modify_record', page_data)
        return annual_report_detail


class JiangsuParser(Parser):
    """江苏页面的解析类"""
    def __init__(self, crawler):
        """初始化函数
        Args:
            crawler: 该解析器所属于的爬取器。crawler和parser相互对应
        """
        self.crawler = crawler
        #各种表格架构是否已经构建好
        self.ind_comm_pub_skeleton_built = False
        self.ent_pub_skeleton_built = False
        self.other_dept_pub_skeleton_built = False
        self.judical_assist_pub_skeleton_built = False
        self.annual_report_skeleton_built = False
        #指定各个网页所属于的表格类型，便于解析
        self.parse_table_items = {}

    def parse_page(self, name, page):
        """解析页面，给外部调用的接口"""
        if not page:
            return {}
        if name in ('ind_comm_pub_skeleton', 'ent_pub_skeleton', 'other_dept_pub_skeleton', 'judical_assist_pub_skeleton', 'annual_report_skeleton'):
            return self.parse_skeleton_page(name, page)
        elif name == 'ent_pub_annual_report':
            return self.parse_annual_report_page(page)
        elif name == 'annual_report_shareholder_info':
            return self.parse_annual_report_shareholder_info(page)
        else:
            return self.parse_general_page(name, page)

    def parse_annual_report_page(self, page):
        """解析年报页面"""
        json_obj = json.loads(page)
        annual_report_data = []
        if type(json_obj) == list:
            for ele in json_obj:
                annual_report = {}
                annual_report[u'报送年度'] = ele.get('REPORT_RESULT')
                annual_report[u'发布日期'] = ele.get('REPORT_DATE')
                report_id = ele.get('ID')
                report_year = ele.get('REPORT_RESULT').strip(u'年度报告')
                annual_report[u'详情'] = self.crawler.get_annual_report_detail(report_year, report_id)
                annual_report_data.append(copy.copy(annual_report))
        return annual_report_data

    def parse_skeleton_page(self, name, page):
        """解析各个表格的框架页面
        江苏企业公示信息的页面中，各部分（工商公示信息、企业公示信息、其他部门公示信息、
        司法协助信息）在开始通过一个jsp给出该部分所有页面表格的框架
        """
        if name == 'ind_comm_pub_skeleton':
            self.parse_ind_comm_pub_skeleton(page)
        elif name == 'ent_pub_skeleton':
            self.parse_ent_pub_skeleton(page)
        elif name == 'other_dept_pub_skeleton':
            self.parse_other_dept_pub_skeleton(page)
        elif name == 'judical_assist_pub_skeleton':
            self.parse_judical_assist_pub_skeleton(page)
        elif name == 'annual_report_skeleton':
            self.parse_annual_report_skeleton(page)
        else:
            print 'unknown skeleton type %s' % name

    def get_table_data(self, table_name, table_items, json_obj):
        """获取表格数据
        Args:
            table_name: 表名称
            table_items: 表结构
            json_obj: 表数据
        """
        table_dict = {}
        for key in table_items.keys():
            table_dict[table_items.get(key)] = json_obj.get(key)
        if table_name == 'ind_comm_pub_reg_shareholder':
            detail_page_name = 'ind_comm_pub_reg_shareholder_detail'
            post_data = self.crawler.ci_detail_post_data
            post_data['ID'] = json_obj.get('C6')
            post_data['SEQ_ID'] = json_obj.get('C7')
            post_data['specificQuery'] = 'investorInfor'
            detail_page_data = self.crawler.get_page_data(detail_page_name, post_data)
            table_dict[u'详情'] = self.parse_ind_comm_pub_reg_shareholder_detail_page(detail_page_data)
        return table_dict

    def parse_general_page(self, name, page):
        """解析一般的数据页面（非框架页面）
        """
        json_obj = json.loads(page)
        table_items = self.parse_table_items[name]
        if type(json_obj) == dict and json_obj.get('total', None):
            result = []
            for record in json_obj.get('items'):
                result.append(self.get_table_data(name, table_items, record))
        elif type(json_obj) == list and len(json_obj) == 1:
            result = self.get_table_data(name, table_items, json_obj[0])
        return result

    def get_dict_table_items(self, table_tag):
        """获得字典类型的表格的结构
        """
        table_items = {}
        for tr in table_tag.find_all('tr'):
            if tr.find('th') and tr.find('td'):
                ths = tr.find_all('th')
                tds = tr.find_all('td')
                for index, td in enumerate(tds):
                    table_items[CrawlerUtils.get_raw_text_in_bstag(td).strip('{}').replace('PAPERS_', '')]\
                        = CrawlerUtils.get_raw_text_in_bstag(ths[index])
        return table_items

    def get_list_table_items(self, table_tag):
        """获取记录类型的表格的结构
        """
        table_items = {}
        if len(table_tag.find_all('tr')) != 3:
            print 'abnormal list table skeleton, table_tag = ', table_tag
            return table_items
        ths = table_tag.find_all('tr')[1].find_all('th')
        tds = table_tag.find_all('tr')[2].find_all('td')
        if len(ths) != len(tds):
            print 'abnormal list table skeleton, table_tag = ', table_tag
            return table_items
        for index, td in enumerate(tds):
            table_items[CrawlerUtils.get_raw_text_in_bstag(td).strip('{}').replace('PAPERS_', '')] = CrawlerUtils.get_raw_text_in_bstag(ths[index])
        return table_items

    def parse_ind_comm_pub_skeleton(self, page):
        """解析工商公示信息 页面表结构
        """
        if self.ind_comm_pub_skeleton_built:
            return
        soup = BeautifulSoup(page, 'html.parser')
        #注册信息-基本信息
        table = soup.find('table', attrs={'id': 'baseinfo'})
        if not table:
            print 'parse ind comm pub skeleton failed, do not find reg basic table!'
            return
        self.parse_table_items['ind_comm_pub_reg_basic'] = self.get_dict_table_items(table)

        #注册信息-股东信息
        table = soup.find('table', attrs={'id': 'touziren', 'name': 'touzirenTAB'})
        if not table:
            print 'parse ind comm pub skeleton failed, do not find reg shareholder table!'
            return
        self.parse_table_items['ind_comm_pub_reg_shareholder'] = self.get_list_table_items(table)

        #注册信息-变更信息
        table = soup.find('table', attrs={'name': 'biangengxinxiTAB'})
        if not table:
            print 'parse ind comm pub skeleton failed, do not find reg modify table!'
            return
        self.parse_table_items['ind_comm_pub_reg_modify'] = self.get_list_table_items(table)

        #归档信息-主要人员信息
        table = soup.find('table', attrs={'name': 'zhuyaorenyuanxinxiTAB'})
        if not table:
            print 'parse ind comm pub skeleton failed, do not find arch key person table!'
            return
        self.parse_table_items['ind_comm_pub_arch_key_persons'] = self.get_list_table_items(table)

        #归档信息-分支结构
        table = soup.find('table', attrs={'name': 'fengongsixinxiTAB'})
        if not table:
            print 'parse ind comm pub skeleton failed, do not find arch branch table!'
            return
        #分支机构表有些特殊，表结构字段和表数据字段不对应
        arch_branch_table_items = self.get_list_table_items(table)
        changed_value = arch_branch_table_items.get('NO_')
        del arch_branch_table_items['NO_']
        arch_branch_table_items['RN'] = changed_value
        self.parse_table_items['ind_comm_pub_arch_branch'] = arch_branch_table_items


        #归档信息-清算信息
        # table = soup.find('table', attrs={'name': 'qingsuanfuzeren'})
        # if not table:
        #     print 'parse ind comm pub skeleton failed, do not find arch liquidation table!'
        #     return
        # self.parse_table_items['ind_comm_pub_arch_liquidation'] = self.get_list_table_items(table)

        #股权出置登记信息
        # table = soup.find('table', attrs={'name': 'applicationList4TAB'})
        # if not table:
        #     print 'parse ind comm pub skeleton failed, do not find equity ownership reg table!'
        #     return
        # self.parse_table_items['ind_comm_pub_equity_ownership'] = self.get_list_table_items(table)

        #动产抵押信息
        table = soup.find('table', attrs={'name': 'applicationListTAB'})
        if not table:
            print 'parse ind comm pub skeleton failed, do not find movable property reg table!'
            return
        self.parse_table_items['ind_comm_pub_movable_property_reg'] = self.get_list_table_items(table)

        #行政处罚信息
        table = soup.find('table', attrs={'name': 'applicationList1TAB'})
        if not table:
            print 'parse ind comm pub skeleton failed, do not find arch branch table!'
            return
        self.parse_table_items['ind_comm_pub_administration_sanction'] = self.get_list_table_items(table)

        #抽查检查信息
        table = soup.find('table', attrs={'name': 'applicationList5TAB'})
        if not table:
            print 'parse ind comm pub skeleton failed, do not find arch branch table!'
            return
        self.parse_table_items['ind_comm_pub_spot_check'] = self.get_list_table_items(table)

        #经营异常信息
        table = soup.find('table', attrs={'name': 'yichangmingluxinxiTAB'})
        if not table:
            print 'parse ind comm pub skeleton failed, do not find arch branch table!'
            return
        self.parse_table_items['ind_comm_pub_business_exception'] = self.get_list_table_items(table)

        # #严重违法信息
        # tag = soup.find('div', attrs={'id': 'heimingdan'})
        # if tag:
        #     table = tag.find('table', attrs={'class': 'detailsList'})
        #     if table:
        #         self.parse_table_items['ind_comm_pub_serious_violate_law'] = self.get_list_table_items(table)
        self.ind_comm_pub_skeleton_built = True

    def parse_ent_pub_skeleton(self, page):
        """解析企业公示信息 页面表结构
        """
        if self.ent_pub_skeleton_built:
            return
        soup = BeautifulSoup(page, 'html.parser')
        #行政许可信息
        table = soup.find('table', attrs={'name': 'applicationList1TAB'})
        if not table:
            print 'parse ent pub skeleton failed, do not find administrative license table!'
            return
        self.parse_table_items['ent_pub_administrative_license'] = self.get_list_table_items(table)

        #知识产权出质登记信息
        table = soup.find('table', attrs={'name': 'applicationList3TAB'})
        if not table:
            print 'parse ent pub skeleton failed, do not find knowledge property reg table!'
            return
        self.parse_table_items['ent_pub_knowledge_property'] = self.get_list_table_items(table)

        #行政处罚信息
        table = soup.find('table', attrs={'name': 'applicationList5TAB'})
        if not table:
            print 'parse ent pub skeleton failed, do not find administration_sanction table!'
            return
        self.parse_table_items['ent_pub_administrative_sanction'] = self.get_list_table_items(table)

        # #企业投资人出资比例
        # table = soup.find('table', attrs={'name': 'applicationList4TAB'})
        # if not table:
        #     print 'parse ent pub skeleton failed, do not find administration_sanction table!'
        #     return
        # self.parse_table_items['ent_pub_shareholder_capital_contribution'] = self.get_list_table_items(table)

        # #股权变更信息
        # tag = soup.find('div', attrs={'id': 'gudongguquan'})
        # if tag:
        #     table = tag.find('table', attrs={'class': 'detailsList'})
        #     if table:
        #         self.parse_table_items['ent_pub_equity_change'] = self.get_list_table_items(table)
        self.ent_pub_skeleton_built = True

    def parse_other_dept_pub_skeleton(self, page):
        """解析其他部门公示信息 页面表结构
        """
        if self.other_dept_pub_skeleton_built:
            return
        soup = BeautifulSoup(page, 'html.parser')
        #行政许可信息
        table = soup.find('table', attrs={'name': 'xingzhengxukeTAB'})
        if not table:
            print 'parse other dept pub skeleton failed, do not find administration_license table!'
            return
        self.parse_table_items['other_dept_pub_administration_license'] = self.get_list_table_items(table)

        #行政处罚信息
        table = soup.find('table', attrs={'name': 'xingzhengchufaTAB'})
        if not table:
            print 'parse ent pub skeleton failed, do not find administration_sanction table!'
            return
        self.parse_table_items['other_dept_pub_administration_sanction'] = self.get_list_table_items(table)
        self.other_dept_pub_skeleton_built = True

    def parse_judical_assist_pub_skeleton(self, page):
        """解析司法协助信息 页面表结构
        """
        if self.judical_assist_pub_skeleton_built:
            return
        soup = BeautifulSoup(page, 'html.parser')
        #司法股权冻结信息
        table = soup.find('table', attrs={'name': 'gddjTAB'})
        if not table:
            print 'parse judical assist skeleton failed, do not find equity freeze table!'
            return
        self.parse_table_items['judical_assist_pub_equity_freeze'] = self.get_list_table_items(table)

        #司法股东变更登记信息
        table = soup.find('table', attrs={'name': 'gdbgTAB'})
        if not table:
            print 'parse judical assist skeleton failed, do not find shareholder modify table!'
            return
        self.parse_table_items['judical_assist_pub_shareholder_modify'] = self.get_list_table_items(table)
        self.judical_assist_pub_skeleton_built = True

    def parse_annual_report_skeleton(self, page):
        """解析 企业年报页面结构
        """
        #企业基本信息
        soup = BeautifulSoup(page, 'html.parser')
        annual_report_table_items = {}
        tag = soup.find('div', attrs={'id': 'qyjbxx'})
        if not tag:
            print 'parse annual report skeleton failed, do not find qyjbxx table'
            return
        table = tag.find('table', attrs={'class': 'detailsList'})
        if table:
            ent_basic_info_table = {}
            for tr in table.find_all('tr'):
                if tr.find('th') and tr.find('td'):
                    ths = tr.find_all('th')
                    tds = tr.find_all('td')
                    for index, td in enumerate(tds):
                        ent_basic_info_table[td.get('id')] = CrawlerUtils.get_raw_text_in_bstag(ths[index])
            self.parse_table_items['annual_report_ent_basic_info'] = ent_basic_info_table

        #网站或网店信息
        table = soup.find('table', attrs={'id': 'web', 'name': 'applicationList1TAB'})
        if table:
            self.parse_table_items['annual_report_web_info'] = self.get_list_table_items(table)

        #股东及出资信息
        table = soup.find('table', attrs={'id': 'touziren',  'name': 'applicationList4TAB'})
        if table:
            shareholder_info_table = {}

        #对外投资信息
        table = soup.find('table', attrs={'id': 'duiwaitouzi', 'name': 'applicationList3TAB'})
        if table:
            self.parse_table_items['annual_report_investment_abord_info'] = self.get_list_table_items(table)

        #企业资产状况信息
        for table in soup.find_all('table'):
            tr = table.find('tr')
            if tr and tr.find('th') and tr.find('th').text == u'企业资产状况信息':
                ent_property_info_table = {}
                for tr in table.find_all('tr'):
                    if tr.find('th') and tr.find('td'):
                        ths = tr.find_all('th')
                        tds = tr.find_all('td')
                        for index, td in enumerate(tds):
                            ent_property_info_table[td.get('id')] = CrawlerUtils.get_raw_text_in_bstag(ths[index])
                self.parse_table_items['annual_report_ent_property_info'] = ent_property_info_table
                break

        #对外提供担保信息
        table = soup.find('table', attrs={'id': 'duiwaidanbao', 'name': 'applicationList6TAB'})
        if table:
            self.parse_table_items['annual_report_external_guarantee_info'] = self.get_list_table_items(table)

        #股权变更信息
        table = soup.find('table', attrs={'id': 'guquanchange','name':'applicationList5TAB'})
        if table:
            self.parse_table_items['annual_report_equity_modify_info'] = self.get_list_table_items(table)

        #修改记录
        table = soup.find('table', attrs={'id': 'modifyRecord', 'name': 'applicationList2TAB'})
        if table:
            self.parse_table_items['annual_report_modify_record'] = self.get_list_table_items(table)

        self.annual_report_skeleton_built = True

    def parse_ind_comm_pub_reg_shareholder_detail_page(self, page_data):
        """解析工商公示信息-注册信息-投资人信息中的详情页面
        需要单独处理
        """
        json_obj = json.loads(page_data)
        table_data = {}
        table_list = []
        num = len(json_obj.get('listValue', None))
        for i in range(num):
            sub_dict={}
            if json_obj.get('listValue', None):
                table_data[u'投资人名称'] = json_obj.get('listValue')[i].get('STOCK_NAME')
                table_data[u'投资人类型'] = json_obj.get('listValue')[i].get('STOCK_TYPE')
            if json_obj.get('listchuzi', None):
                table_data[u'出资方式'] = json_obj.get('listchuzi')[i].get('INVEST_TYPE_NAME')
                sub_dict[u'认缴出资方式'] = json_obj.get('listchuzi')[i].get('INVEST_TYPE_NAME')
                sub_dict[u'实缴出资方式'] = json_obj.get('listchuzi')[i].get('INVEST_TYPE_NAME')
            if json_obj.get('listrenjiao'):
                table_data[u'认缴额'] = json_obj.get('listrenjiao')[i].get('SHOULD_CAPI')
                sub_dict[u'认缴出资额'] = json_obj.get('listrenjiao')[i].get('SHOULD_CAPI')
                sub_dict[u'认缴出资时间'] = json_obj.get('listrenjiao')[i].get('SHOULD_CAPI_DATE')
            if json_obj.get('listshijiao', None):
                table_data[u'实缴额'] = json_obj.get('listshijiao')[i].get('REAL_CAPI')
                sub_dict[u'实缴出资额'] = json_obj.get('listshijiao')[i].get('REAL_CAPI')
                sub_dict[u'实缴出资时间'] = json_obj.get('listshijiao')[i].get('REAL_CAPI_DATE')
            table_data['list'] = [sub_dict]
            table_list.append(table_data)
        return {u'投资人及出资信息':table_list}

    def parse_annual_report_shareholder_info(self, page):
        """解析年报信息中的投资人信息
        需要单独处理
        """
        shareholder_info = []
        record_columns = [u'股东', u'认缴出资额', u'认缴出资时间', u'认缴出资方式', u'实缴出资额', u'实缴出资时间', u'实缴出资方式']
        json_obj = json.loads(page)
        for record in json_obj.get('items'):
            if not record.get('D1'):
                continue
            result = {}
            soup = BeautifulSoup(record.get('D1'), 'html.parser')
            tds = soup.find_all('td')
            if not tds:
                continue
            for index, column in enumerate(record_columns):
                result[column] = CrawlerUtils.get_raw_text_in_bstag(tds[index])
            shareholder_info.append(result)
        return shareholder_info


# class TestParser(unittest.TestCase):
#     def setUp(self):
#         unittest.TestCase.setUp(self)
#         self.crawler = JiangsuCrawler()
#         self.parser = self.crawler.parser
#
#     def test_parse_ind_comm_pub_skeleton(self):
#         with open('./unittest_data/htmls/ind_comm_pub_skeleton.html') as f:
#             page = f.read()
#             self.parser.parse_ind_comm_pub_skeleton(page)
#
#     def test_parse_ent_pub_skeleton(self):
#         with open('./unittest_data/htmls/ent_pub_skeleton.html') as f:
#             page = f.read()
#             self.parser.parse_ent_pub_skeleton(page)
#
#     def test_parse_other_dept_pub_skeleton(self):
#         with open('./unittest_data/htmls/other_dept_pub_skeleton.html') as f:
#             page = f.read()
#             self.parser.parse_other_dept_pub_skeleton(page)
#
#     def test_parse_judical_assist_pub_skeleton(self):
#         with open('./unittest_data/htmls/judical_assist_pub_skeleton.html') as f:
#             page = f.read()
#             self.parser.parse_judical_assist_pub_skeleton(page)
"""
if __name__ == '__main__':
    from CaptchaRecognition import CaptchaRecognition
    import run
    run.config_logging()
    JiangsuCrawler.code_cracker = CaptchaRecognition('jiangsu')
    crawler = JiangsuCrawler('./enterprise_crawler/Jiangsu.json')
    enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/jiangsu.txt')
    #enterprise_list = ['320000000000192']
    for ent_number in enterprise_list:
        ent_number = ent_number.rstrip('\n')
        logging.info('###################   Start to crawl enterprise with id %s   ###################\n' % ent_number)
        crawler.run(ent_number=ent_number)
"""
