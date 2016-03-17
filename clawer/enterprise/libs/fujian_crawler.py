#!/usr/bin/env python
#encoding=utf-8
import os
import threading
from . import settings

from crawler import CrawlerUtils
from zongju_crawler import ZongjuCrawler
from zongju_crawler import ZongjuParser
from enterprise.libs.CaptchaRecognition import CaptchaRecognition

class FujianCrawler(ZongjuCrawler):
    """福建爬虫
    """
    #html数据的存储路径
    html_restore_path = settings.json_restore_path + '/fujian/'

    #验证码图片的存储路径
    ckcode_image_path = settings.json_restore_path + '/fujian/ckcode.jpg'
    code_cracker = CaptchaRecognition('fujian')
    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {'host': 'http://www.fjaic.gov.cn/',
            'official_site': 'http://wsgs.fjaic.gov.cn/creditpub/home',
            'get_checkcode': 'http://wsgs.fjaic.gov.cn/creditpub/captcha?preset=math-01',
            'post_checkcode': 'http://wsgs.fjaic.gov.cn/creditpub/security/verify_captcha',
            'get_info_entry': 'http://wsgs.fjaic.gov.cn/creditpub/search/ent_info_list',

            'open_info_entry': 'http://wsgs.fjaic.gov.cn/creditpub/notice/view?',  #获得企业信息页面的url，通过指定不同的tab=1-4来选择不同的内容（工商公示，企业公示...）
            'open_detail_info_entry': '',
        }

    def __init__(self, json_restore_path):
        ZongjuCrawler.__init__(self, json_restore_path)
        self.json_restore_path = json_restore_path
        self.parser = FujianParser(self)


class FujianParser(ZongjuParser):
    def __init__(self, crawler):
        self.crawler = crawler

"""
if __name__ == '__main__':
    from CaptchaRecognition import CaptchaRecognition
    import run
    run.config_logging()
    FujianCrawler.code_cracker = CaptchaRecognition('fujian')

    crawler = FujianCrawler('./enterprise_crawler/fujian.json')
    enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/fujian.txt')
    # enterprise_list = ['100000000018305']
    for ent_number in enterprise_list:
        ent_number = ent_number.rstrip('\n')
        settings.logger.info('###################   Start to crawl enterprise with id %s   ###################\n' % ent_number)
        crawler.run(ent_number=ent_number)

"""
