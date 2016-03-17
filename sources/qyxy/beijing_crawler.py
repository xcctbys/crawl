#!/usr/bin/env python
#encoding=utf-8
import os
import requests
import time
import re
import random
import urllib
import threading
from datetime import datetime, timedelta
import importlib

ENT_CRAWLER_SETTINGS = os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS:
    settings = importlib.import_module(ENT_CRAWLER_SETTINGS)
else:
    import settings

from bs4 import BeautifulSoup
from crawler import Crawler
from crawler import Parser
from crawler import CrawlerUtils



class BeijingCrawler(Crawler):
    """北京工商爬虫
    """
    #html数据的存储路径
    html_restore_path = settings.html_restore_path + '/beijing/'

    #验证码图片的存储路径
    ckcode_image_path = settings.json_restore_path + '/beijing/ckcode.jpg'

    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {'host': 'http://qyxy.baic.gov.cn',
            'official_site': 'http://qyxy.baic.gov.cn/beijing',
            'get_checkcode': 'http://qyxy.baic.gov.cn',
            'post_checkcode': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!checkCode.dhtml',
            'open_info_entry': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!getBjQyList.dhtml',
            'ind_comm_pub_reg_basic': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!openEntInfo.dhtml?',
            'ind_comm_pub_reg_shareholder': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!tzrFrame.dhtml?',
            'ind_comm_pub_reg_modify': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!biangengFrame.dhtml?',
            'ind_comm_pub_arch_key_persons': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!zyryFrame.dhtml?',
            'ind_comm_pub_arch_branch': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!fzjgFrame.dhtml?',
            'ind_comm_pub_arch_liquidation': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!qsxxFrame.dhtml?',
            'ind_comm_pub_movable_property_reg': 'http://qyxy.baic.gov.cn/gjjbjTab/gjjTabQueryCreditAction!dcdyFrame.dhtml?',
            'ind_comm_pub_equity_ownership_reg': 'http://qyxy.baic.gov.cn/gdczdj/gdczdjAction!gdczdjFrame.dhtml?',
            'ind_comm_pub_administration_sanction': 'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list.dhtml?',
            'ind_comm_pub_business_exception': 'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list_jyycxx.dhtml?',
            'ind_comm_pub_serious_violate_law':   'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list_yzwfxx.dhtml?',
            'ind_comm_pub_spot_check':   'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list_ccjcxx.dhtml?',
            'ent_pub_ent_annual_report':   'http://qyxy.baic.gov.cn/qynb/entinfoAction!qyxx.dhtml?',
            'ent_pub_shareholder_capital_contribution':   'http://qyxy.baic.gov.cn/gdcz/gdczAction!list_index.dhtml?',
            'ent_pub_equity_change':   'http://qyxy.baic.gov.cn/gdgq/gdgqAction!gdgqzrxxFrame.dhtml?',
            'ent_pub_administration_license':   'http://qyxy.baic.gov.cn/xzxk/xzxkAction!list_index.dhtml?',
            'ent_pub_knowledge_property':   'http://qyxy.baic.gov.cn/zscqczdj/zscqczdjAction!list_index.dhtml?',
            'ent_pub_administration_sanction':   'http://qyxy.baic.gov.cn/gdgq/gdgqAction!qyxzcfFrame.dhtml?',
            'other_dept_pub_administration_license':   'http://qyxy.baic.gov.cn/qtbm/qtbmAction!list_xzxk.dhtml?',
            'other_dept_pub_administration_sanction':   'http://qyxy.baic.gov.cn/qtbm/qtbmAction!list_xzcf.dhtml?',
            'shareholder_detail': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!touzirenInfo.dhtml?'
            }

    def __init__(self, json_restore_path):
        self.json_restore_path = json_restore_path
        self.parser = BeijingParser(self)
        self.credit_ticket = None

    def run(self, ent_number=0):
        """爬取的主函数
        """
        self.ent_id = ''
        Crawler.run(self, ent_number)

        '''
        self.ent_number = str(ent_number)
        self.html_restore_path = BeijingCrawler.html_restore_path + self.ent_number + '/'

        if settings.save_html and os.path.exists(self.html_restore_path):
            CrawlerUtils.make_dir(self.html_restore_path)

        self.json_dict = {}

        self.reqst = requests.Session()
        self.reqst.headers.update({
                'Accept': 'text/html, application/xhtml+xml, */*',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

        if not self.crawl_check_page():
            settings.logger.error('crack check code failed, stop to crawl enterprise %s' % self.ent_number)
            return

        self.crawl_ind_comm_pub_pages()
        self.crawl_ent_pub_pages()
        self.crawl_other_dept_pub_pages()

        #采用多线程，在写入文件时需要注意加锁
        self.write_file_mutex.acquire()
        CrawlerUtils.json_dump_to_file(self.json_restore_path, {self.ent_number: self.json_dict})
        self.write_file_mutex.release()
        '''

    def crawl_check_page(self):
        """爬取验证码页面，包括获取验证码url，下载验证码图片，破解验证码并提交
        """
        count = 0
        while count < 10:
            cur_time = datetime.now()
            if cur_time >= settings.start_crawl_time + settings.max_crawl_time:
                settings.logger.info('crawl time over, exit!')
                return False


            count += 1
            ckcode = self.crack_checkcode()
            post_data = {'currentTimeMillis': self.time_stamp, 'credit_ticket': self.credit_ticket, 'checkcode': ckcode[1], 'keyword': self.ent_number};
            next_url = self.urls['post_checkcode']
            resp = self.reqst.post(next_url, data=post_data)
            if resp.status_code != 200:
                settings.logger.warn('failed to get crackcode image by url %s, fail count = %d' % (next_url, count))
                continue

            settings.logger.info('crack code = %s, %s, response =  %s' %(ckcode[0], ckcode[1], resp.content))

            if resp.content == 'fail':
                settings.logger.debug('crack checkcode failed, total fail count = %d' % count)
                continue

            next_url = self.urls['open_info_entry']
            resp = self.reqst.post(next_url, data=post_data)
            if resp.status_code != 200:
                settings.logger.warn('failed to open info entry by url %s, fail count = %d' % (next_url, count))
                continue

            crack_result = self.parse_post_check_page(resp.content)
            if crack_result:
                return True
            else:
                settings.logger.debug('crack checkcode failed, total fail count = %d' % count)
        return False

    def crawl_ind_comm_pub_pages(self):
        """爬取工商公示信息页面
        """
        for item in ('ind_comm_pub_reg_basic',          # 登记信息-基本信息
                     'ind_comm_pub_reg_shareholder',   # 股东信息
                     'ind_comm_pub_reg_modify',
                     'ind_comm_pub_arch_key_persons',  # 备案信息-主要人员信息
                     'ind_comm_pub_arch_branch',      # 备案信息-分支机构信息
                     'ind_comm_pub_arch_liquidation',  # 备案信息-清算信息
                     'ind_comm_pub_movable_property_reg',  # 动产抵押登记信息
                     'ind_comm_pub_equity_ownership_reg',  # 股权出置登记信息
                     'ind_comm_pub_administration_sanction',  # 行政处罚信息
                     'ind_comm_pub_business_exception',  # 经营异常信息
                     'ind_comm_pub_serious_violate_law',  # 严重违法信息
                     'ind_comm_pub_spot_check'        # 抽查检查信息
            ):
            self.get_page_json_data(item, 1)

    def crawl_ent_pub_pages(self):
        """爬取企业公示信息页面
        """
        for item in ('ent_pub_ent_annual_report',
                    'ent_pub_shareholder_capital_contribution', #企业投资人出资比例
                    'ent_pub_equity_change', #股权变更信息
                    'ent_pub_administration_license',#行政许可信息
                    'ent_pub_knowledge_property', #知识产权出资登记
                    'ent_pub_administration_sanction' #行政许可信息
                    ):
            self.get_page_json_data(item, 2)

    def crawl_other_dept_pub_pages(self):
        """爬取其他部门公示信息页面
        """
        for item in ('other_dept_pub_administration_license',#行政许可信息
                    'other_dept_pub_administration_sanction'#行政处罚信息
        ):
            self.get_page_json_data(item, 3)

    def crawl_judical_assist_pub_pages(self):
        """爬取司法协助信息页面
        """
        pass

    def get_page_json_data(self, page_name, page_type):
        """获得页面的解析后的json格式数据
        Args:
            page_name: 页面名称
            page_type: 页面类型, 1 工商公示页面， 2 企业公示页面， 3 其他部门公示页面
        """
        page = self.get_page(page_name, page_type)
        pages = self.get_all_pages_of_a_section(page, page_name)
        if len(pages) == 1:
            self.json_dict[page_name] = {}
            json_data = self.parser.parse_page(page, page_name)
            if json_data:
                self.json_dict[page_name] = json_data
        else:
            self.json_dict[page_name] = []
            for p in pages:
                json_data = self.parser.parse_page(p, page_name)
                if json_data:
                    self.json_dict[page_name] += json_data

    def get_checkcode_url(self):
        """获取验证码的url
        """
        while True:
            resp = self.reqst.get(self.urls['official_site'])
            if resp.status_code != 200:
                settings.logger.error('failed to get crackcode url')
                continue
            response = resp.content
            time.sleep(random.uniform(0.2, 1))
            soup = BeautifulSoup(response, 'html.parser')
            ckimg_src = soup.find_all('img', id='MzImgExpPwd')[0].get('src')
            ckimg_src = str(ckimg_src)
            re_checkcode_captcha=re.compile(r'/([\s\S]*)\?currentTimeMillis')
            re_currenttime_millis=re.compile(r'/CheckCodeCaptcha\?currentTimeMillis=([\s\S]*)')
            checkcode_type = re_checkcode_captcha.findall(ckimg_src)[0]

            if checkcode_type == 'CheckCodeCaptcha':
                checkcode_url= self.urls['get_checkcode'] + ckimg_src
                #parse the pre check page, get useful information
                self.parse_pre_check_page(response)
                return checkcode_url
            settings.logger.debug('get crackable checkcode img failed')
        return None

    def parse_post_check_page(self, page):
        """解析提交验证码之后的页面，获取必要的信息
        """
        if page == 'fail':
            settings.logger.error('checkcode error!')
            if settings.sentry_open:
                settings.sentry_client.captureMessage('checkcode error!')
            return False

        soup = BeautifulSoup(page, 'html.parser')
        r = soup.find_all('a', {'href': "#", 'onclick': re.compile(r'openEntInfo')})

        ent = ''
        if r:
            ent = r[0]['onclick']
        else:
            settings.logger.debug('fail to find openEntInfo')
            return False

        m = re.search(r'\'([\w]*)\'[ ,]+\'([\w]*)\'[ ,]+\'([\w]*)\'', ent)
        if m:
            self.ent_id = m.group(1)
            self.credit_ticket = m.group(3)

        r = soup.find_all('input', {'type': "hidden", 'name': "currentTimeMillis", 'id': "currentTimeMillis"})
        if r:
            self.time_stamp = r[0]['value']
        else:
            settings.logger.debug('fail to get time stamp')
        return True

    def parse_pre_check_page(self, page):
        """解析提交验证码之前的页面
        """
        soup = BeautifulSoup(page, 'html.parser')
        ckimg_src = soup.find_all('img', id='MzImgExpPwd')[0].get('src')
        ckimg_src = str(ckimg_src)
        re_currenttime_millis = re.compile(r'/CheckCodeCaptcha\?currentTimeMillis=([\s\S]*)')
        self.credit_ticket = soup.find_all('input',id='credit_ticket')[0].get('value')
        self.time_stamp = re_currenttime_millis.findall(ckimg_src)[0]

    def crawl_page_by_url(self, url):
        """通过url直接获取页面
        """
        resp = self.reqst.get(url)
        if resp.status_code != 200:
            settings.logger.error('failed to crawl page by url' % url)
            return
        page = resp.content
        time.sleep(random.uniform(0.2, 1))
        if settings.save_html:
            CrawlerUtils.save_page_to_file(self.html_restore_path + 'detail.html', page)
        return page

    def get_all_pages_of_a_section(self, page, type, url=None):
        """获取页面上含有 上一页、下一页跳转链接的区域的所有的数据
        Args:
            page: 已经爬取的页面
            type: 页面类型
            url: 该页面的url，默认为None，因为一般可以通过 type 从 BeijingCrawler.urls 中找到
        Returns:
            pages: 所有页面的列表
        """
        if not page:
            return page
        soup = BeautifulSoup(page, 'html.parser')
        page_count = 0
        page_size = 0
        pages_data = []
        pages_data.append(page)
        r1 = soup.find_all('input', {'type': 'hidden', 'id': 'pagescount'})
        r2 = soup.find_all('input', {'type': 'hidden', 'id': 'pageSize', 'name':'pageSize'})
        if r1 and r2:
            page_count = int(r1[0].get('value'))
            page_size = int(r2[0].get('value'))
        else:
            #只有一页
            return pages_data

        if page_count <= 1:
            return pages_data

        if not url:
            next_url = self.urls[type].rstrip('?')
        else:
            next_url = url

        for p in range(1, page_count):
            post_data = {'pageNos': str(p+1), 'clear': '', 'pageNo': str(p), 'pageSize': str(page_size), 'ent_id': self.ent_id}
            try:
                resp = self.reqst.post(next_url, data=post_data)
                if resp.status_code != 200:
                    settings.logger.error('failed to get all page of a section')
                    return pages_data
                page = resp.content
                time.sleep(random.uniform(0.2, 1))
            except Exception as e:
                settings.logger.error('open new tab page failed, url = %s, page_num = %d' % (next_url, p+1))
                page = None
                raise e
            finally:
                if page:
                    pages_data.append(page)
        return pages_data

    def get_page(self, type, tab):
        """获取页面，为了简便，在url后面添加了所有可能用到的数据，即使有多余的参数也不影响
        Args:
            tab: 访问页面时在url后面所用到的数据。1 工商公示信息， 2 企业公示信息， 3 其他部门公示信息
        """
        url = CrawlerUtils.add_params_to_url(self.urls[type],
                                            {'entId':self.ent_id,
                                             'ent_id':self.ent_id,
                                             'entid':self.ent_id,
                                            'credit_ticket':self.credit_ticket,
                                            'entNo':self.ent_number,
                                            'entName':'',
                                            'timeStamp':self.generate_time_stamp(),
                                            'clear':'true',
                                            'str':tab
                                            })
        settings.logger.info('get %s, url:\n%s\n' % (type, url))
        resp = self.reqst.get(url)
        if resp.status_code != 200:
            settings.logger.warn('get page failed by url %s' % url)
            return
        page = resp.content
        time.sleep(random.uniform(0.2, 1))
        if settings.save_html:
            CrawlerUtils.save_page_to_file(self.html_restore_path + type + '.html', page)
        return page

    def crack_checkcode(self):
        """破解验证码"""
        checkcode_url = self.get_checkcode_url()
        resp = self.reqst.get(checkcode_url)
        if resp.status_code != 200:
            settings.logger.warn('failed to get checkcode img')
            return
        page = resp.content

        time.sleep(random.uniform(2, 4))

        self.write_file_mutex.acquire()
        with open(self.ckcode_image_path, 'wb') as f:
            f.write(page)
        if not self.code_cracker:
            print 'invalid code cracker'
            return ''
        try:
            ckcode = self.code_cracker.predict_result(self.ckcode_image_path)
        except Exception as e:
            settings.logger.warn('exception occured when crack checkcode')
            ckcode = ('', '')
        finally:
            pass
        self.write_file_mutex.release()
        return ckcode

    def generate_time_stamp(self):
        """生成时间戳
        """
        return int(time.time())


class BeijingParser(Parser):
    """北京工商页面的解析类
    """
    def __init__(self, crawler):
        self.crawler = crawler

    def parse_page(self, page, type):
        """解析页面
        返回 python 的字典形式数据
        """
        soup = BeautifulSoup(page, 'html.parser')
        page_data = {}
        if soup.body:
            if soup.body.table:
                try:
                    #一个页面中只含有一个表格
                    if len(soup.body.find_all('table')) == 1:
                        if type == 'ind_comm_pub_reg_modify':
                            page_data = self.parse_ind_comm_pub_reg_modify_table(soup.body.table, type, page)
                        else:
                            page_data = self.parse_table(soup.body.table, type, page)

                    #页面中含有多个表格
                    else:
                        table = soup.body.find('table')
                        while table:
                            if table.name == 'table':
                                table_name = self.get_table_title(table)
                                page_data[table_name] = self.parse_table(table, table_name, page)
                            table = table.nextSibling
                except Exception as e:
                    settings.logger.error('parse failed, with exception %s' % e)
                    raise e

                finally:
                    pass
        return page_data

    def parse_list_table_without_sub_list(self, records_tag, table_name, page, columns):
        """提取没有子列的记录形式的表
        Args:
            records_tag: 表的记录标签，用beautiful soup 从html中提取出来的
            table_name: 表名
            page: 原始的html页面
            columns: 表的表头结构
        Returns:
            item_array: 提取出的表数据，列表形式，列表中的元素为一个python字典
        """
        item_array = []
        for tr in records_tag.find_all('tr'):
            col_count = 0
            item = {}
            for td in tr.find_all('td', recursive=False):
                if td.find('a'):
                    #try to retrieve detail link from page
                    next_url = self.get_detail_link(td.find('a'), page)
                    #has detail link
                    if next_url:
                        detail_page = self.crawler.crawl_page_by_url(next_url)
                        if table_name == 'ent_pub_ent_annual_report':
                            page_data = self.parse_ent_pub_annual_report_page(detail_page, table_name + '_detail')
                            item[u'报送年度'] = CrawlerUtils.get_raw_text_in_bstag(td)
                            item[u'详情'] = page_data #this may be a detail page data
                        else:
                            page_data = self.parse_page(detail_page, table_name + '_detail')
                            item[columns[col_count][0]] = page_data #this may be a detail page data
                    else:
                        #item[columns[col_count]] = CrawlerUtils.get_raw_text_in_bstag(td)
                        item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                else:
                    item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                col_count += 1
            if item:
                item_array.append(item)

        return item_array

    def parse_ent_pub_annual_report_page(self, base_page, page_type):
        """解析企业年报页面，该页面需要单独处理
        """
        def get_year_of_annual_report(page):
            soup = BeautifulSoup(page, 'html.parser')
            t = soup.body.find('table')
            return CrawlerUtils.get_raw_text_in_bstag(t.find('tr'))

        if settings.save_html:
            CrawlerUtils.save_page_to_file(self.crawler.html_restore_path + 'annual_report_base_info.html', base_page)

        page_data = {}
        soup = BeautifulSoup(base_page, 'html.parser')
        if soup.body.find('table'):
            base_table = soup.body.find('table')
            table_name = u'企业基本信息'
            page_data[table_name] = self.parse_table(base_table, table_name, base_page)

            if len(soup.find_all('table')) > 1:
                ent_property_table = soup.body.find_all('table')[1]
                table_name = self.get_table_title(ent_property_table)
                page_data[table_name] = self.parse_table(ent_property_table, table_name, base_page)
        else:
            pass

        year = get_year_of_annual_report(base_page)
        report_items = {'wzFrame': 'website_info', 'gdczFrame': 'shareholder_contribute_info',
                        'dwdbFrame': 'external_guarantee_info', 'xgFrame': 'modify_record_info'}
        for item in report_items.items():
            pat = re.compile(r'<iframe +id="%s" +src=\'(/entPub/entPubAction!.+)\'' % item[0])
            m = pat.search(base_page)
            if m:
                next_url = self.crawler.urls['host'] + m.group(1)
                settings.logger.info('get annual report, url:\n%s\n' % next_url)
                page = self.crawler.crawl_page_by_url(next_url)
                pages = self.crawler.get_all_pages_of_a_section(page, page_type, next_url)

                table_name = item[1]
                try:
                    soup = BeautifulSoup(page, 'html.parser')
                    table_name = self.get_table_title(soup.body.table)
                except Exception as e:
                    settings.logger.error('fail to get table name with exception %s' % e)
                    raise e
                try:
                    if len(pages) == 1:
                        table_data = self.parse_page(page, table_name)
                    else:
                        table_data = []
                        for p in pages:
                            table_data += self.parse_page(p, table_name)
                except Exception as e:
                    settings.logger.error('fail to parse page with exception %s'%e)
                    raise e
                finally:
                    page_data[table_name] = table_data
        return page_data

    def parse_ind_comm_pub_reg_modify_table(self, bs_table, table_name, page):
        """解析工商公示信息-注册信息-变更信息表格，由于含有详情页，需要单独处理
        """
        tbody = bs_table.find('tbody')
        if tbody:
            columns = self.get_columns_of_record_table(bs_table, page)
            column_size = len(columns)
            item_array = []

            for tr in tbody.find_all('tr'):
                if tr.find('td'):
                    col_count = 0
                    item = {}
                    for td in tr.find_all('td'):
                        if td.find('a'):
                            #try to retrieve detail link from page
                            next_url = self.get_detail_link(td.find('a'), page)
                            #has detail link
                            if next_url:
                                detail_page = self.crawler.crawl_page_by_url(next_url)
                                detail_soup = BeautifulSoup(detail_page, 'html.parser')
                                before_modify_table = detail_soup.body.find_all('table')[1]
                                table_data = self.parse_table(before_modify_table, 'before_modify', detail_page)
                                item[columns[col_count][0]] = self.parse_table(before_modify_table, 'before_modify', detail_page)
                                col_count += 1
                                after_modify_table = detail_soup.body.find_all('table')[2]
                                item[columns[col_count][0]] = self.parse_table(after_modify_table, 'after_modify', detail_page)
                            else:
                                item[columns[col_count][0]] = CrawlerUtils.get_raw_text_in_bstag(td)
                        else:
                            item[columns[col_count][0]] = CrawlerUtils.get_raw_text_in_bstag(td)

                        col_count += 1
                        if col_count == column_size:
                            item_array.append(item.copy())
                            col_count = 0
            return item_array

    def get_detail_link(self, bs4_tag, page):
        """获取详情链接 url，在bs tag中或者page中提取详情页面
        Args:
            bs4_tag： beautifulsoup 的tag
            page: 页面数据
        """
        detail_op = bs4_tag.get('onclick')
        pat_view_info = re.compile(r'viewInfo\(\'([\w]+)\'\)')
        pat_show_dialog = re.compile(r'showDialog\(\'([^\'\n]+)\'')
        next_url = ''
        if detail_op and pat_view_info.search(detail_op):
            m = pat_view_info.search(detail_op)
            val = m.group(1)
            #detail link type 1, for example : ind_comm_pub info --- registration info -- shareholders info
            pat = re.compile(r'var +url += +rootPath +\+ +\"(.+\?)([\w]+)=\"\+[\w]+\+\"')
            m1 = pat.search(page)
            if m1:
                addition_url = m1.group(1)
                query_key = m1.group(2)

                next_url = CrawlerUtils.add_params_to_url(self.crawler.urls['host'] + addition_url,
                                                          {query_key:val,
                                                          'entId':self.crawler.ent_id,
                                                            'ent_id':self.crawler.ent_id,
                                                            'entid':self.crawler.ent_id,
                                                            'credit_ticket':self.crawler.credit_ticket,
                                                            'entNo':self.crawler.ent_number
                                            })
        elif detail_op and pat_show_dialog.search(detail_op):
            #detail link type 2, for example : ind_comm_pub_info --- registration info ---- modify info
            m = pat_show_dialog.search(detail_op)
            val = m.group(1)
            next_url = self.crawler.urls['host'] + val
        elif 'href' in bs4_tag.attrs.keys():
            #detail link type 3, for example : ent pub info ----- enterprise annual report
            next_url = self.crawler.urls['host'] + bs4_tag['href']

        return next_url

if __name__ == '__main__':
    from CaptchaRecognition import CaptchaRecognition
    import run
    run.config_logging()
    BeijingCrawler.code_cracker = CaptchaRecognition('beijing')
    crawler = BeijingCrawler('./enterprise_crawler/beijing.json')
    #enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/beijing.txt')
    enterprise_list = ['110000005791844'] #'110000005791844', '110000410227029',
    for ent_number in enterprise_list:
        ent_number = ent_number.rstrip('\n')
        settings.logger.info('###################   Start to crawl enterprise with id %s   ###################\n' % ent_number)
        crawler.run(ent_number=ent_number)
