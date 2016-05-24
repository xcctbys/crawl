#!/usr/bin/env python
#encoding=utf-8
import os
import threading
from zongju_crawler import ZongjuCrawler
from zongju_crawler import ZongjuParser
from common_func import get_proxy
# from enterprise.libs.CaptchaRecognition import CaptchaRecognition

class FujianCrawler(ZongjuCrawler):
    """福建爬虫
    """
    # code_cracker = CaptchaRecognition('fujian')
    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {'host': 'http://wsgs.fjaic.gov.cn/',
            'official_site': 'http://wsgs.fjaic.gov.cn/creditpub/home',
            'get_checkcode': 'http://wsgs.fjaic.gov.cn/creditpub/captcha?preset=math-01',
            'post_checkcode': 'http://wsgs.fjaic.gov.cn/creditpub/security/verify_captcha',
            'get_info_entry': 'http://wsgs.fjaic.gov.cn/creditpub/search/ent_info_list',
            'open_info_entry': 'http://wsgs.fjaic.gov.cn/creditpub/notice/view?',  #获得企业信息页面的url，通过指定不同的tab=1-4来选择不同的内容（工商公示，企业公示...）
        }

    def __init__(self, json_restore_path=None):
        super(FujianCrawler, self).__init__(json_restore_path)
        self.json_restore_path = json_restore_path
        #html数据的存储路径
        self.html_restore_path = self.json_restore_path + '/fujian/'
        #验证码图片的存储路径
        self.ckcode_image_path = self.json_restore_path + '/fujian/ckcode.jpg'
        self.parser = FujianParser(self)
        self.proxies = get_proxy('fujian')

class FujianParser(ZongjuParser):
    def __init__(self, crawler):
        self.crawler = crawler

