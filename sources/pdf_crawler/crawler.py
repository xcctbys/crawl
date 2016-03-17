#!/usr/bin/env python
#encoding=utf-8
import os
import time
import random
import requests
from datetime import datetime, timedelta
import json
import errno
import urllib
import urllib2
import cookielib
import logging
import codecs
import copy
import bs4
from bs4 import BeautifulSoup

ENT_CRAWLER_SETTINGS=os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS and ENT_CRAWLER_SETTINGS.find('settings_pro') >= 0:
    import settings_pro as settings
else:
    import settings

class CrawlerUtils(object):
    """爬虫工具类，封装了一些常用函数
    """
    @staticmethod
    def make_dir(path):
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5 (except OSError, exc: for Python <2.5)
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise exc

    @staticmethod
    def set_logging(level):
        logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")

    @staticmethod
    def set_opener_header(opener, header):
        tmp_header = []
        opener.addheaders = []
        for key, value in header.items():
            elem = (key, value)
            tmp_header.append(elem)
        opener.addheaders = tmp_header

    @staticmethod
    def add_opener_header(opener, header):
        for key, value in header.items():
            elem = (key, value)
            opener.addheaders.append(elem)

    @staticmethod
    def make_opener(head = {
                'Connetion': 'Keep-Alive',
                'Accept': 'text/html, application/xhtml+xml, */*',
                'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'}):

        cj = cookielib.CookieJar()
        pro = urllib2.HTTPCookieProcessor(cj) #Python自动处理cookie
        opener = urllib2.build_opener(pro)    #用于打开url的opener
        urllib2.install_opener(opener)
        CrawlerUtils.set_opener_header(opener, head)
        return opener

    #在给定的url基础上，添加额外的信息
    @staticmethod
    def add_params_to_url(url, args):
        return url + urllib.urlencode(args)

    @staticmethod
    def save_page_to_file(path, page):
        with open(path, 'w') as f:
            f.write(page)

    @staticmethod
    def get_enterprise_list(file):
        list = []
        with open(file, 'r') as f:
            for line in f.readlines():
                sp = line.split(',')
                if len(sp) >= 3:
                    list.append(sp[2].strip(' \n\r'))
        return list

    @staticmethod
    def display_item(item):
        if type(item) == list or type(item) == tuple:
            for i in item:
                CrawlerUtils.display_item(i)
        elif type(item) == dict:
            for k in item:
                CrawlerUtils.display_item(k)
                CrawlerUtils.display_item(item[k])
        elif type(item) in (int, str, float, bool, bs4.element.NavigableString):
            print item
        elif type(item) == unicode:
            print item.encode('utf-8')
        else:
            print 'unknown type in CrawlerUtils.display_item, type = %s' % type(item)

    @staticmethod
    def json_dump_to_file(path, json_dict):
        write_type = 'wb'
        if os.path.exists(path):
            write_type = 'a'
        with codecs.open(path, write_type, 'utf-8') as f:
            f.write(json.dumps(json_dict, ensure_ascii=False)+'\n')

    @staticmethod
    def get_raw_text_in_bstag(tag):
        text = tag.string
        if not text:
            text = tag.get_text()
        if not text:
            return ''
        return text.strip()

    @staticmethod
    def get_cur_time():
        return time.strftime("%Y-%m-%d_%H:%M:%S",time.localtime(time.time()))

    @staticmethod
    def get_cur_date():
        return time.strftime("%Y-%m-%d",time.localtime(time.time()))

    @staticmethod
    def get_random_ms():
        return random.uniform(0.2, 1)

    @staticmethod
    def get_cur_y_m_d():
        cur_date = time.strftime("%Y-%m-%d")
        return cur_date.split('-')


class Crawler(object):
    """爬虫的基类
    """
    code_cracker = None

    def __init__(self):
        pass

    def run(self, ent_number=0):
        self.ent_number = str(ent_number)
        self.html_restore_path = self.html_restore_path + self.ent_number + '/'

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
        
        cur_time = datetime.now()
        if cur_time >= settings.start_crawl_time + settings.max_crawl_time:
            settings.logger.info('crawl time over, exit!')
            return False

        self.crawl_ind_comm_pub_pages()

        cur_time = datetime.now()
        if cur_time >= settings.start_crawl_time + settings.max_crawl_time:
            settings.logger.info('crawl time over, exit!')
            return False

        self.crawl_ent_pub_pages()

        cur_time = datetime.now()
        if cur_time >= settings.start_crawl_time + settings.max_crawl_time:
            settings.logger.info('crawl time over, exit!')
            return False
        self.crawl_other_dept_pub_pages()

        cur_time = datetime.now()
        if cur_time >= settings.start_crawl_time + settings.max_crawl_time:
            settings.logger.info('crawl time over, exit!')
            return False
        self.crawl_judical_assist_pub_pages()

        #采用多线程，在写入文件时需要注意加锁
        self.write_file_mutex.acquire()
        CrawlerUtils.json_dump_to_file(self.json_restore_path, {self.ent_number: self.json_dict})
        self.write_file_mutex.release()

    def crack_checkcode(self):
        pass

    def crawl_check_page(self):
        pass

    def crawl_ind_comm_pub_pages(self):
        pass

    def crawl_ent_pub_pages(self):
        pass

    def crawl_other_dept_pub_pages(self):
        pass

    def crawl_judical_assist_pub_pages(self):
        pass


class Parser(object):
    """网页解析的基类
    注意：对记录类型的表列含有子列的情形，暂时只支持处理含有一级子列, 网页中还没有见到过含有二级子列的情形
    """
    def __init__(self, crawler):
        self.crawler = crawler

    def parse_page(self, page):
        pass

    def get_columns_of_record_table(self, bs_table, page):
        """获得纪录性质的表的 列名
        Args:
            bs_table: html 的 table tag
            page: html 数据
        Returns:
            表的列名，形式为列表，列表中的元素 item 形式为 (column_name, sub_column_list or column_name)
            如果列中含有子列，item[1] 为 该列的包含的所有子列的 列名结构，和本结构相同
            如果列中没有子列，item[1] 和 item[0]相同，都为该列的名称
        """
        tbody = bs_table.find('tbody') or BeautifulSoup(page, 'html.parser').find('tbody')
        tr = None
        if tbody:
            if len(tbody.find_all('tr')) <= 1:
                tr = tbody.find('tr')
            else:
                tr = tbody.find_all('tr')[1]
                if not tr.find('th'):
                    tr = tbody.find_all('tr')[0]
        else:
            if len(bs_table.find_all('tr')) <= 1:
                return None
            elif bs_table.find_all('tr')[0].find('th') and not bs_table.find_all('tr')[0].find('td') and len(bs_table.find_all('tr')[0].find_all('th')) > 1:
                tr = bs_table.find_all('tr')[0]
            elif bs_table.find_all('tr')[1].find('th') and not bs_table.find_all('tr')[1].find('td') and len(bs_table.find_all('tr')[1].find_all('th')) > 1:
                tr = bs_table.find_all('tr')[1]
        return self.get_record_table_columns_by_tr(tr)

    def sub_column_count(self, th_tag):
        """得到子列的个数
        Args:
            th_tag: 父列在表头中的 th 标签
        Returns:
            th_tag代表的父列所含有的子列的个数
        """
        if th_tag.has_attr('colspan') and th_tag.get('colspan') > 1:
            return int(th_tag.get('colspan'))
        return 0

    def get_sub_columns(self, tr_tag, index, count):
        """得到子列的列名
        """
        columns = []
        for i in range(index, index + count):
            th = tr_tag.find_all('th')[i]
            if not self.sub_column_count(th):
                columns.append((CrawlerUtils.get_raw_text_in_bstag(th), CrawlerUtils.get_raw_text_in_bstag(th)))
            else:
            #if has sub-sub columns
                columns.append((CrawlerUtils.get_raw_text_in_bstag(th), self.get_sub_columns(tr_tag.nextSibling.nextSibling, 0, self.sub_column_count(th))))
        return columns

    def get_table_title(self, table_tag, redundent_title=False):
        """获取表名
        """
        if table_tag.find('tr'):
            if not redundent_title:
                return CrawlerUtils.get_raw_text_in_bstag(table_tag.find('tr').th)
            elif len(table_tag.find_all('table', recursive=False)) > 1:
                return CrawlerUtils.get_raw_text_in_bstag(table_tag.find_all('table', recursive=False)[1])
        return ''

    def get_record_table_columns_by_tr(self, tr_tag):
        """通过tr tag获取记录类型的表的表头
        """
        columns = []
        if not tr_tag:
            return columns
        try:
            sub_col_index = 0
            for th in tr_tag:
                col_name = CrawlerUtils.get_raw_text_in_bstag(th)
                if col_name:
                    if not self.sub_column_count(th):
                        columns.append((col_name, col_name))
                    else: #has sub_columns
                        columns.append((col_name, self.get_sub_columns(tr_tag.nextSibling.nextSibling, sub_col_index, self.sub_column_count(th))))
                        sub_col_index += self.sub_column_count(th)
        except Exception as e:
            settings.logger.error('exception occured in get_table_columns, except_type = %s' % type(e))
        finally:
            return columns

    def get_column_data(self, columns, td_tag):
        """获得列的数据
        Args:
            columns: 表头结构
            td_tag: 含有列数据的 td
        """
        #含有子列
        if type(columns) == list:
            data = {}
            multi_col_tag = td_tag
            if td_tag.find('table'):
                multi_col_tag = td_tag.find('table').find('tr')
            if not multi_col_tag:
                settings.logger.deubg('invalid multi_col_tag, multi_col_tag = %s', multi_col_tag)
                if settings.sentry_open:
                    settings.sentry_client.captureMessage('invalid multi_col_tag, multi_col_tag = %s', multi_col_tag)
                return data

            if len(columns) != len(multi_col_tag.find_all('td', recursive=False)):
                settings.logger.debug('column head size != column data size, columns head = %s, columns data = %s' % (columns, multi_col_tag.contents))
                if settings.sentry_open:
                    settings.sentry_client.captureMessage('column head size != column data size, columns head = %s, columns data = %s' % (columns, multi_col_tag.contents))
                return data

            for id, col in enumerate(columns):
                data[col[0]] = self.get_column_data(col[1], multi_col_tag.find_all('td', recursive=False)[id])
            return data
        #不含有子列
        else:
            return CrawlerUtils.get_raw_text_in_bstag(td_tag)

    def parse_dict_table(self, bs_table, table_name):
        """解析字典类型的表结构
        Args:
            bs_table: 在html中要解析的table tag，用beautifulsoup提取过的
            table_name: 表名称
        Returns:
            table_dict: 返回的内容数据，为字典形式
        """
        table_dict = {}
        for tr in bs_table.find_all('tr'):
            if tr.find('th') and tr.find('td'):
                ths = tr.find_all('th')
                tds = tr.find_all('td')
                if len(ths) != len(tds):
                    settings.logger.debug('th size not equals td size in table %s, what\'s up??' % table_name)
                    if settings.sentry_open:
                        settings.sentry_client.captureMessage('th size not equals td size in table %s, what\'s up??' % table_name)
                    return
                else:
                    for i in range(len(ths)):
                        if CrawlerUtils.get_raw_text_in_bstag(ths[i]):
                            table_dict[CrawlerUtils.get_raw_text_in_bstag(ths[i])] = CrawlerUtils.get_raw_text_in_bstag(tds[i])
        return table_dict

    def parse_list_table_with_sub_list(self, records_tag, table_name, page, columns):
        """提取含有子列的表
        Args:
            records_tag: beautiful soup从html中提取出的record的tag
            table_name: 表名
            page: html 页面数据
            columns: 表头数据
        """

        column_size = len(columns)
        column_index = 0
        item = {}
        item_array = []
        for tr in records_tag.find_all('tr', recursive=False):
            for td in tr.find_all('td', recursive=False):
                if td.find('a'):
                    #try to retrieve detail link from page
                    next_url = self.get_detail_link(td.find('a'), page)
                    #has detail link
                    if next_url:
                        detail_page = self.crawler.crawl_page_by_url(next_url)
                        page_data = self.parse_page(detail_page, table_name + '_detail')
                        item[columns[column_index][0]] = page_data
                    else:
                        item[columns[column_index][0]] = self.get_column_data(columns[column_index][1], td)
                else:
                    record_data = self.parse_list_record(td, columns[column_index][1])
                    if record_data:
                        item[columns[column_index][0]] = record_data
                        column_index += 1
                    if column_index == column_size:
                        item_array.append(item.copy())
                        column_index = 0

        return item_array

    def parse_list_record(self, record_tag, column):
        """获取一个记录的数据
        """
        record_dict = {}
        if type(column) == list:
            if record_tag.find('tr'):
                for index, td in enumerate(record_tag.find('tr').find_all('td', recursive=False)):
                    record_dict[column[index][0]] = self.parse_list_record(td, column[index][1])
            return record_dict
        else:
            record_dict = CrawlerUtils.get_raw_text_in_bstag(record_tag)
        return record_dict

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
                        page_data = self.parse_page(detail_page, table_name + '_detail')
                        item[columns[col_count][0]] = page_data #this may be a detail page data
                    else:
                        #item[columns[col_count]] = CrawlerUtils.get_raw_text_in_bstag(td)
                        item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                else:
                    item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                col_count += 1
            item_array.append(item.copy())

        return item_array

    def parse_list_table(self, bs_table, table_name, page, columns):
        """解析记录类型的表结构
        Args:
            bs_table: beautiful soup提取过的 html 中的table tag
            table_name: 表名
            page: 原始的html页面
            columns: 记录的表头结构
        Returns:
            提取出来的记录列表，形式为python 列表，列表中的元素为python 字典，保存每一条记录的数据
        """
        tbody = bs_table.find('tbody') or BeautifulSoup(page, 'html.parser').find('tbody')
        col_span = 0
        for col in columns:
            if type(col[1]) == list:
                col_span += len(col[1])
            else:
                col_span += 1

        column_size = len(columns)
        if not tbody:
            records_tag = bs_table
        else:
            records_tag = tbody

        #没有子列的表
        if col_span == column_size:
            return self.parse_list_table_without_sub_list(records_tag, table_name, page, columns)
        else:
        #含有子列的表
            return self.parse_list_table_with_sub_list(records_tag, table_name, page, columns)

    def parse_table(self, bs_table, table_name, page):
        """解析表结构，表中的数据可能为字典形式，或者为列表形式
        """
        table_dict = {}
        try:
            columns = self.get_columns_of_record_table(bs_table, page)
            if columns:
                table_dict = self.parse_list_table(bs_table, table_name, page, columns)
            else:
                table_dict = self.parse_dict_table(bs_table, table_name)
        except Exception as e:
            settings.logger.error('parse table %s failed with exception %s' % (table_name, type(e)))
            raise e
        finally:
            return table_dict

    def get_detail_link(self, bs4_tag, page):
        """提取页面的链接
        """
        pass

    def wipe_off_newline_and_blank_for_fe(self,data):
        """
        去除字符串首尾中的换行,空格,还有制表符
        """
        return str(data).strip('\n').strip(' ').strip('\t').strip('\n').encode(encoding='utf-8')

    def wipe_off_newline_and_blank(self, data):
        """
        去除字符串中所有的换行,空格,制表符
        """
        data = str(data)
        data.replace('\n','')
        data.replace('\t','')
        data.replace(' ','')
        return data.encode(encoding='utf-8')

