#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from shaanxi_crawler import ShaanxiCrawler
from common_func import get_proxy


class XinjiangCrawler(ShaanxiCrawler):
    urls = {
        'host': 'http://gsxt.xjaic.gov.cn:7001/',
        'webroot': 'http://gsxt.xjaic.gov.cn:7001/',
        'page_search': 'http://gsxt.xjaic.gov.cn:7001/ztxy.do?method=index&random=%d',
        'page_Captcha': 'http://gsxt.xjaic.gov.cn:7001/ztxy.do?method=createYzm&dt=%d&random=%d',
        'page_showinfo': 'http://gsxt.xjaic.gov.cn:7001/ztxy.do?method=list&djjg=&random=%d',
        'checkcode': 'http://gsxt.xjaic.gov.cn:7001/ztxy.do?method=list&djjg=&random=%d',
    }

    def __init__(self, json_restore_path=None):
        super(XinjiangCrawler, self).__init__(json_restore_path)
        self.json_restore_path = json_restore_path
        #验证码图片的存储路径
        self.path_captcha = self.json_restore_path + '/xinjiang/ckcode.jpeg'
        #html数据的存储路径
        self.html_restore_path = self.json_restore_path + '/xinjiang/'
        self.proxies = get_proxy('xinjiang')
