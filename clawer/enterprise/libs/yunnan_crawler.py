#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from hebei_crawler import HebeiCrawler
from common_func import get_proxy


class YunnanCrawler(HebeiCrawler):

    urls = {
        'host': 'http://gsxt.ynaic.gov.cn/notice/',
        'webroot': 'http://gsxt.ynaic.gov.cn/',
        'page_search': 'http://gsxt.ynaic.gov.cn/notice/',
        'page_Captcha': 'http://gsxt.ynaic.gov.cn/notice/captcha?preset=&ra=',    # preset 有数字的话，验证码会是字母+数字的组合
        'page_showinfo': 'http://gsxt.ynaic.gov.cn/notice/search/ent_info_list',
        'checkcode': 'http://gsxt.ynaic.gov.cn/notice/security/verify_captcha',
    }

    def __init__(self, json_restore_path=None):
        super(YunnanCrawler, self).__init__(json_restore_path)
        self.json_restore_path = json_restore_path
        #验证码图片的存储路径
        self.path_captcha = self.json_restore_path + '/yunnan/ckcode.jpeg'
        #html数据的存储路径
        self.html_restore_path = self.json_restore_path + '/yunnan/'

        self.proxies = get_proxy('yunnan')
