#!/usr/bin/env python
#encoding=utf-8

from hebei_crawler import HebeiCrawler
from common_func import get_proxy


class ShanghaiCrawler(HebeiCrawler):

    urls = {
        'host': 'http://www.sgs.gov.cn/notice/',
        'webroot': 'http://www.sgs.gov.cn/',
        'page_search': 'http://www.sgs.gov.cn/notice/',
        'page_Captcha': 'http://www.sgs.gov.cn/notice/captcha?preset=&ra=',    # preset 有数字的话，验证码会是字母+数字的组合
        'page_showinfo': 'http://www.sgs.gov.cn/notice/search/ent_info_list',
        'checkcode': 'http://www.sgs.gov.cn/notice/security/verify_captcha',
    }

    def __init__(self, json_restore_path=None):
        super(ShanghaiCrawler, self).__init__(json_restore_path)
        self.json_restore_path = json_restore_path
        #验证码图片的存储路径
        self.path_captcha = self.json_restore_path + '/Shanghai/ckcode.jpeg'
        #html数据的存储路径
        self.html_restore_path = self.json_restore_path + '/Shanghai/'

        self.proxies = get_proxy('shanghai')
