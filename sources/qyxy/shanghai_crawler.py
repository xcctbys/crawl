#!/usr/bin/env python
#encoding=utf-8
import os
import threading
import importlib

ENT_CRAWLER_SETTINGS = os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS:
    settings = importlib.import_module(ENT_CRAWLER_SETTINGS)
else:
    import settings

from crawler import CrawlerUtils
from zongju_crawler import ZongjuCrawler
from zongju_crawler import ZongjuParser
class ShanghaiCrawler(ZongjuCrawler):
    """上海爬虫
    """
    #html数据的存储路径
    html_restore_path = settings.html_restore_path + '/shanghai/'

    #验证码图片的存储路径
    ckcode_image_path = settings.json_restore_path + '/shanghai/ckcode.jpg'

    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {'host': 'https://qyxy.baic.gov.cn',
            'official_site': 'https://www.sgs.gov.cn/notice/home',
            'get_checkcode': 'https://www.sgs.gov.cn/notice/captcha?preset=',
            'post_checkcode': 'https://www.sgs.gov.cn/notice/security/verify_captcha',
            'get_info_entry': 'https://www.sgs.gov.cn/notice/search/ent_info_list',
            'open_info_entry': 'https://www.sgs.gov.cn/notice/notice/view?',
            'open_detail_info_entry': ''
            }

    def __init__(self, json_restore_path):
        ZongjuCrawler.__init__(self, json_restore_path)
        self.json_restore_path = json_restore_path
        self.parser = ShanghaiParser(self)


class ShanghaiParser(ZongjuParser):
    def __init__(self, crawler):
        self.crawler = crawler


if __name__ == '__main__':
    from CaptchaRecognition import CaptchaRecognition
    import run
    run.config_logging()
    ShanghaiCrawler.code_cracker = CaptchaRecognition('shanghai')

    crawler = ShanghaiCrawler('./enterprise_crawler/shanghai.json')
    enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/shanghai.txt')
    # enterprise_list = ['310000000007622']
    for ent_number in enterprise_list:
        ent_number = ent_number.rstrip('\n')
        settings.logger.info('###################   Start to crawl enterprise with id %s   ###################\n' % ent_number)
        crawler.run(ent_number=ent_number)

