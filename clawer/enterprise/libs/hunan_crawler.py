#!/usr/bin/env python
#encoding=utf-8
import threading
from zongju_crawler import ZongjuCrawler
from zongju_crawler import ZongjuParser
from common_func import get_proxy
# from enterprise.libs.CaptchaRecognition import CaptchaRecognition

class HunanCrawler(ZongjuCrawler):
    """湖南爬虫
    """
    # code_cracker = CaptchaRecognition('hunan')
    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {'host': 'http://www.hnaic.net.cn/visit/category/a/hnaicalllist',
            'official_site': 'http://gsxt.hnaic.gov.cn/notice/search/ent_info_list',
            'get_checkcode': 'http://gsxt.hnaic.gov.cn/notice/captcha?preset=',
            'post_checkcode': 'http://gsxt.hnaic.gov.cn/notice/search/popup_captcha',

            'get_info_entry': 'http://gsxt.hnaic.gov.cn/notice/search/ent_info_list',  # 获得企业入口
            'open_info_entry': 'http://gsxt.hnaic.gov.cn/notice/notice/view?',
            # 获得企业信息页面的url，通过指定不同的tab=1-4来选择不同的内容（工商公示，企业公示...）
            'open_detail_info_entry': '',
            }
    def __init__(self, json_restore_path=None):
        super(HunanCrawler, self).__init__(json_restore_path)
        self.json_restore_path = json_restore_path
        #html数据的存储路径
        self.html_restore_path = self.json_restore_path + '/hunan/'
        #验证码图片的存储路径
        self.ckcode_image_path = self.json_restore_path + '/hunan/ckcode.jpg'
        self.parser = HunanParser(self)
        self.proxies = get_proxy('hunan')


class HunanParser(ZongjuParser):
    def __init__(self, crawler):
        self.crawler = crawler


