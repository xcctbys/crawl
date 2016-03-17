#!/usr/bin/env python
#!encoding=utf-8
import os
import sys
import raven
import gzip
import random
import time
import datetime
import stat
import unittest

import logging
import Queue
import threading
import multiprocessing
import socket
import raven
from encodings import zlib_codec
import zlib
import jinja2
import importlib


from mail import SendMail

from CaptchaRecognition import CaptchaRecognition
from crawler import CrawlerUtils
from beijing_crawler import BeijingCrawler
from jiangsu_crawler import JiangsuCrawler
from zongju_crawler import ZongjuCrawler
from shanghai_crawler import ShanghaiCrawler
from guangdong_crawler import GuangdongClawer
from heilongjiang_crawler import HeilongjiangClawer
from anhui_crawler import AnhuiCrawler
from yunnan_crawler import YunnanCrawler
from tianjin_crawler import TianjinCrawler
from hunan_crawler import HunanCrawler
from fujian_crawler import FujianCrawler
from sichuan_crawler import SichuanCrawler
from shandong_crawler import ShandongCrawler
from hebei_crawler import HebeiCrawler
from shaanxi_crawler import ShaanxiCrawler
from henan_crawler import HenanCrawler
from neimenggu_crawler import NeimengguClawer
from chongqing_crawler import ChongqingClawer
from xinjiang_crawler import XinjiangClawer
from zhejiang_crawler import ZhejiangCrawler
from liaoning_crawler import LiaoningCrawler
from guangxi_crawler import GuangxiCrawler
from gansu_crawler import GansuClawer
from shanxi_crawler import ShanxiCrawler
from qinghai_crawler import QinghaiCrawler
from hubei_crawler import HubeiCrawler
from guizhou_crawler import GuizhouCrawler
from jilin_crawler import JilinCrawler
from hainan_crawler import HainanCrawler
from xizang_crawler import XizangCrawler
import traceback


ENT_CRAWLER_SETTINGS = os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS:
    settings = importlib.import_module(ENT_CRAWLER_SETTINGS)
else:
    import settings


TEST = False


province_crawler = {
    'beijing': BeijingCrawler,
    'jiangsu': JiangsuCrawler,
    'zongju': ZongjuCrawler,
    'shanghai': ShanghaiCrawler,
    'guangdong': GuangdongClawer,
    'heilongjiang': HeilongjiangClawer,
    'anhui': AnhuiCrawler,
    'yunnan':YunnanCrawler,
    'tianjin' : TianjinCrawler,
    'hunan' : HunanCrawler,
    'fujian' : FujianCrawler,
    'sichuan': SichuanCrawler,
    'shandong' : ShandongCrawler,
    'hebei' : HebeiCrawler,
    'neimenggu':NeimengguClawer,
    'shaanxi': ShaanxiCrawler,
    'henan' : HenanCrawler,
    'xinjiang':XinjiangClawer,
    'chongqing':ChongqingClawer,
    'zhejiang' : ZhejiangCrawler,
    'liaoning': LiaoningCrawler,
    'gansu':GansuClawer,
    'guangxi': GuangxiCrawler,
    'shanxi':ShanxiCrawler,
    'qinghai':QinghaiCrawler,
    'hubei':HubeiCrawler,
    'guizhou' : GuizhouCrawler,
    'jilin' : JilinCrawler,
    'hainan' : HainanCrawler,
    'xizang' : XizangCrawler,
}

process_pool = None
cur_date = CrawlerUtils.get_cur_y_m_d()


def set_codecracker():
    for province in sorted(province_crawler.keys()):
        try:
            province_crawler.get(province).code_cracker = CaptchaRecognition(province)
        except Exception, e:
            settings.logger.warn("init captcha recognition of %s", province)


def config_logging():
    settings.logger = logging.getLogger('enterprise-crawler')
    settings.logger.setLevel(settings.log_level)
    fh = logging.FileHandler(settings.log_file)
    fh.setLevel(settings.log_level)
    ch = logging.StreamHandler()
    ch.setLevel(settings.log_level)

    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(pathname)s:%(lineno)d:: %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    settings.logger.addHandler(fh)
    settings.logger.addHandler(ch)


def crawl_work(province, json_restore_path, enterprise_no):
    settings.logger.info('crawler start to crawler enterprise(ent_id = %s)' % (enterprise_no))

    try:
        crawler = province_crawler[province](json_restore_path)
        crawler.run(enterprise_no)
    except Exception as e:
        settings.logger.error('crawler %s failed to get enterprise(%s), with exception %s' % (province, enterprise_no, e))
        send_sentry_report()
    finally:
        os._exit(0)


def crawl_province(province):
    settings.logger.info('ready to clawer %s' % province)
    #创建存储路径
    json_restore_dir = '%s/%s/%s/%s' % (settings.json_restore_path, province, cur_date[0], cur_date[1])
    if not os.path.exists(json_restore_dir):
        CrawlerUtils.make_dir(json_restore_dir)

    #获取企业名单
    enterprise_list_path = settings.enterprise_list_path + province + '.txt'

    #json存储文件名
    json_restore_path = '%s/%s.json' % (json_restore_dir, cur_date[2])

    with open(enterprise_list_path) as f:
        for line in f:
            fields = line.strip().split(",")
            if len(fields) < 3:
                continue
            no = fields[2]
            process = multiprocessing.Process(target=crawl_work, args=(province, json_restore_path, no))
            process.daemon = True
            process.start()
            process.join(300)

    settings.logger.info('All %s crawlers work over' % province)

    #压缩保存
    if not os.path.exists(json_restore_path):
        settings.logger.warn('json restore path %s does not exist!' % json_restore_path)
        os._exit(1)
        return

    with open(json_restore_path, 'r') as f:
        data = f.read()
        compressed_json_restore_path = json_restore_path + '.gz'
        with gzip.open(compressed_json_restore_path, 'wb') as cf:
            cf.write(data)

    #删除json文件，只保留  .gz 文件
    os.remove(json_restore_path)
    os._exit(0)


def force_exit():
    pgid = os.getpgid(0)

    settings.logger.error("PID %d run timeout", pgid)

    if process_pool != None:
        process_pool.terminate()

    os.killpg(pgid, 9)
    os._exit(1)


class Checker(object):
    """ Is obtain data from province enterprise site today ?
    """
    def __init__(self, dt=None):
        self.yesterday = datetime.datetime.now() - datetime.timedelta(1)
        if dt:
            self.yesterday = dt
        self.parent = settings.json_restore_path
        self.success = [] # {'name':'', "size':0, "rows":0}
        self.failed = [] # string list
        self.enterprise_count = 0
        self.done = 0
        self.html_template = os.path.join(os.path.dirname(__file__), "mail.html")
        self.send_mail = SendMail(settings.EMAIL_HOST, settings.EMAIL_PORT, settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD, ssl=True)

    def run(self):
        for province in sorted(province_crawler.keys()):
            enterprise_count = self._get_enterprise_count(province)
            data = {"name": province, "size": 0, "done": 0, "enterprise_count": enterprise_count, "done_ratio": 0}

            self.enterprise_count += enterprise_count
            path = self._json_path(province)
            if os.path.exists(path) is False:
                self.failed.append(data)
                continue

            st = os.stat(path)
            data["done"] = self._get_rows(path)
            data["size"] = st[stat.ST_SIZE]
            data['done_ratio'] = float(data["done"]) / data["enterprise_count"]
            self.success.append(data)

            self.done += data["done"]

        #output
        settings.logger.error("success %d, failed %d, enterprise count %d, done %d", len(self.success), len(self.failed), self.enterprise_count, self.done)
        for item in self.success:
            settings.logger.error("\t%s: %d bytes, done %d, enterprise count %d", item['name'], item['size'], item["done"], item["enterprise_count"])

        settings.logger.error("Failed province")
        for item in self.failed:
            settings.logger.error("\t%s", item['name'])

        self._report()

    def _json_path(self, province):
        path = os.path.join(self.parent, province, self.yesterday.strftime("%Y/%m/%d.json.gz"))
        return path

    def _get_rows(self, path):
        rows = 0

        with gzip.open(path) as f:
            for line in f:
                if len(line.strip()) == 0:
                    continue
                rows += 1

        return rows

    def _get_enterprise_count(self, province):
        path = os.path.join(settings.enterprise_list_path, "%s.txt" % province)
        count = 0
        with open(path) as f:
            for line in f:
                if line.split(",") < 3:
                    continue
                count += 1

        return count

    def _report(self):
        title = u"%s 企业信用爬取情况" % (self.yesterday.strftime("%Y-%m-%d"))
        content = self._render_html()
        to_admins = [x[1] for x in settings.ADMINS]

        self.send_mail.send_html(settings.EMAIL_HOST_USER, to_admins, title, content)

    def _render_html(self):
        html = ""
        with open(self.html_template) as f:
            html = f.read()

        template = jinja2.Template(html)
        return template.render(yesterday=self.yesterday.date(), success=self.success, failed=self.failed, host=socket.gethostname(), \
                               enterprise_count=self.enterprise_count, done=self.done)



class NoDaemonProcess(multiprocessing.Process):
    # make 'daemon' attribute always return False
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)

# We sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.
class MyPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess


def main():
    config_logging()

    if not os.path.exists(settings.json_restore_path):
        CrawlerUtils.make_dir(settings.json_restore_path)

    cur_date = CrawlerUtils.get_cur_y_m_d()
    set_codecracker()

    if len(sys.argv) >= 2 and sys.argv[1] == "check":
        dt = None
        if len(sys.argv) == 3:
            dt = datetime.datetime.strptime(sys.argv[2], "%Y-%m-%d")
        checker = Checker(dt)
        checker.run()
        return

    if len(sys.argv) < 3:
        print 'usage: run.py [check] [max_crawl_time(minutes) province...] \n\tmax_crawl_time 最大爬取秒数，以秒计;\n\tprovince 是所要爬取的省份列表 用空格分开, all表示爬取全部)'
        return

    try:
        max_crawl_time = int(sys.argv[1])
        settings.max_crawl_time = datetime.timedelta(minutes=max_crawl_time)
    except ValueError as e:
        settings.logger.error('invalid max_crawl_time, should be a integer')
        os._exit(1)

    timer = threading.Timer(max_crawl_time, force_exit)
    timer.start()

    settings.logger.info(u'即将开始爬取，最长爬取时间为 %s 秒' % settings.max_crawl_time)
    settings.start_crawl_time = datetime.datetime.now()

    if sys.argv[2] == 'all':
        args = [p for p in sorted(province_crawler.keys())]
        process_pool = MyPool()
        process_pool.map(crawl_province, args)
        process_pool.close()
        settings.logger.info("wait processes....")
        process_pool.join()
    else:
        provinces = sys.argv[2:]
        for p in provinces:
            if not p in province_crawler.keys():
                settings.logger.warn('province %s is not supported currently' % p)
                continue

            crawl_province(p)



def send_sentry_report():
    if settings.sentry_client:
        settings.sentry_client.captureException()


class TestChecker(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.checker = Checker()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test_render_html(self):
        html = self.checker._render_html()
        self.assertGreater(len(html), 0)

    def test_report(self):
        #self.checker.run()
        self.checker._report()


if __name__ == '__main__':
    if TEST:
        unittest.main()

    try:
        main()
    except:
        send_sentry_report()
        print traceback.format_exc(10)

