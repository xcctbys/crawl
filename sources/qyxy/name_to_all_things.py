#!/usr/bin/env python
# encoding=utf-8
import os
from os import path
import requests
import time
import thread
import random
import threading
from bs4 import BeautifulSoup
from crawler import Crawler
from crawler import Parser
from crawler import CrawlerUtils
import multiprocessing
import time

ENT_CRAWLER_SETTINGS = os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS and ENT_CRAWLER_SETTINGS.find('settings_pro') >= 0:
    import settings_pro as settings
else:
    import settings


class NameToIDCrawler(Crawler):
    """甘肃工商公示信息网页爬虫
    """
    # html数据的存储路径
    html_restore_path = settings.html_restore_path + '/nametoid/'

    # 验证码文件夹
    ckcode_image_dir_path = settings.json_restore_path + '/nametoid/'
    # 多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    host = 'http://eport.bbdservice.com/show/searchCompany.do'

    def __init__(self, json_restore_path):
        """
        初始化函数
        Args:
            json_restore_path: json文件的存储路径，所有江苏的企业，应该写入同一个文件，因此在多线程爬取时设置相同的路径。同时，
             需要在写入文件的时候加锁
        Returns:
        """
        self.json_restore_path = json_restore_path
        self.parser = NameToIDParser(self)

        self.reqst = requests.Session()
        self.reqst.headers.update({
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Encoding': '"application/json, text/javascript, */*; q=0.01"',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': '"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0"'})
        self.json_dict = {}
        self.ent_name = None
        self.results = None

    def run(self, ent_name=None):
        if ent_name is None:
            return False
        crawler = NameToIDCrawler('./enterprise_crawler/nametoid/name_to_id.json')
        crawler.ent_name = str(ent_name).strip(' ').strip('\n').strip(' ')
        # 对每个企业都指定一个html的存储目录
        self.html_restore_path = self.html_restore_path + crawler.ent_name + '/'
        if settings.save_html and not os.path.exists(self.html_restore_path):
            CrawlerUtils.make_dir(self.html_restore_path)

        page = crawler.crawl_page_by_get_params(crawler.ent_name)
        crawler.results = crawler.parser.parse_search_page(page=page)
        # 采用多线程，在写入文件时需要注意加锁
        self.write_file_mutex.acquire()
        CrawlerUtils.json_dump_to_file(self.json_restore_path, {crawler.ent_name: crawler.results})
        self.write_file_mutex.release()
        return True

    def crawl_page_by_get_params(self, ent_name):
        """
        通过传入不同的参数获得不同的页面
        """
        url = 'http://125.65.43.219:80/show/searchCompany.do?term=' + ent_name
        count = 0
        while count < 30:
            params = {'term': ent_name}
            self.reqst.get('http://report.bbdservice.com/show/index.do')
            self.reqst.post('http://report.bbdservice.com/show/findNoticeInfoCount.do')
            resp = self.reqst.get(url=url)
            if resp.status_code != 200:
                count += 1
                continue
            page = resp.content
            time.sleep(random.uniform(0.001, 0.1))
            return page
        return None


class NameToIDParser(Parser):
    """甘肃工商页面的解析类
    """

    def __init__(self, crawler):
        self.crawler = crawler

    def parse_search_page(self, page):
        soup = BeautifulSoup(page, "html5lib")
        div_table = soup.find_all('div', {'class': 'div-table'})
        if div_table is None:
            return None
        name_table = div_table[0].find('table')
        if name_table is None:
            return None
        name_span = name_table.find('span', {'class': 'spa-size'})
        if name_span is None:
            return None
        name = name_span.get_text()
        name = str(name).strip(' ').strip('\n').strip(' ')
        id_div = div_table[0].find('div', {'class': 'table-content clearfix'})
        if id_div is None:
            return None
        id_li = id_div.find('li')
        if id_li is None:
            return None
        id_span = id_li.find('span', {'class': 'left'})
        if id_span is None:
            return None
        id = id_span.get_text()
        id = str(id).strip(' ').strip('\n').strip(' ')

        results = {}
        results['name'] = name
        results['id'] = id
        return results


def get_enterprise_list(file):
    list = []
    with open(file, 'r') as f:
        for line in f.readlines():
            list.append(line.strip(' \n\r'))
    return list


def process(count):
    import run
    run.config_logging()
    nametoid_to_json_name = 'nametoid' + str(count) + '.json'
    crawler = NameToIDCrawler('./enterprise_crawler/nametoid/'+ str(nametoid_to_json_name))
    nametoid_name = 'nametoid' + str(count) + '.txt'
    enterprise_list = get_enterprise_list('./enterprise_list/' + str(nametoid_name))
    print(len(enterprise_list))
    for ent_name in enterprise_list:
        ent_name = str(ent_name).rstrip('\n')
        print(
            '############   Start to crawl nametoid %d with name %s   ################\n' % (count, ent_name))
        crawler.run(ent_name=ent_name)


if __name__ == '__main__':
    pool = multiprocessing.Pool(processes = 4)
    pool.map(process, (0,1,2,3,))   #维持执行的进程总数为processes，当一个进程执行完毕后会添加新的进程进去
    print "Mark~ Mark~ Mark~~~~~~~~~~~~~~~~~~~~~~"
    pool.close()
    pool.join()   #调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
    print "Sub-process(es) done."
    # thread.start_new_thread(process, (0,))
    # thread.start_new_thread(process, (1,))
    # thread.start_new_thread(process, (2,))
    # thread.start_new_thread(process, (3,))
