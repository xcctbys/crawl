#coding:utf8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import logging
import unittest
import re
import time
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool

DEBUG = True
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")

choices = dict([
(u'安徽', 'ANHUI'),
(u'北京', 'BEIJING'),
(u'重庆', 'CHONGQING'),
(u'福建', 'FUJIAN'),
(u'甘肃', 'GANSU'),
(u'广东', 'GUANGDONG'),
(u'广西', 'GUANGXI'),
(u'贵州', 'GUIZHOU'),
(u'海南', 'HAINAN'),
(u'河北', 'HEBEI'),
(u'黑龙', 'HEILONGJIANG'),
(u'河南', 'HENAN'),
(u'湖北', 'HUBEI'),
(u'湖南', 'HUNAN'),
(u'江苏', 'JIANGSU'),
(u'江西', 'JIANGXI'),
(u'吉林', 'JILIN'),
(u'辽宁', 'LIAONING'),
(u'内蒙', 'NEIMENGGU'),
(u'宁夏', 'NINGXIA'),
(u'青海', 'QINGHAI'),
(u'陕西', 'SHAANXI'),
(u'山东', 'SHANDONG'),
(u'上海', 'SHANGHAI'),
(u'山西', 'SHANXI'),
(u'四川', 'SICHUAN'),
(u'天津', 'TIANJIN'),
(u'新疆', 'XINJIANG'),
(u'云南', 'YUNNAN'),
(u'浙江', 'ZHEJIANG'),
(u'总局', 'ZONGJU'),
(u'西藏', 'XIZANG')])

class BaseProxy(object):
    def __init__(self):
        self.url = 'http://qsrdk.daili666api.com/ip/?tid=557067352008097&num=30&delay=5&area=北京&category=2&sortby=time&foreign=none&exclude_ports=8090,8123&filter=on'
        self.timeout = 15
        self.reqst = requests.Session()
        self.reqst.headers.update(
            {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

    def run(self):
        pass

class PaidProxy(BaseProxy):


    def __init__(self):
        BaseProxy.__init__(self)
        #self.url = 'http://www.xicidaili.com/nn'          #西刺代理
        #self.url
        self.a_list=[]

    def get_ipproxy(self,):
        print 111

        resp = self.reqst.get(self.url, timeout=self.timeout)
        # trs = BeautifulSoup(resp.content, 'html.parser').find_all('tr')[:60]
        print resp
        print 2222
        #trs = BeautifulSoup(resp.content, 'html.parser').find_all('tr')
        trs = BeautifulSoup(resp.content, 'html.parser').find_all()
        print trs

        # for tr in trs:
        #     tds = [td.get_text().strip() for td in tr.find_all('td', class_='line-content')]
        #     print tds
        #     print '-------tds--------'
        #     try:
        #         pass
        #     except KeyError:
        #         print 'error'
        #     province = 'OTHER'
        #     http =  "%s:%s" % (tds[1],tds[2])
        #     http = (http, province)
        #     print http
        #     self.a_list.append(http)
        print 4444
        return self.a_list


    # def run(self):
    #     pool = Pool()
    #     # for i in range(1, total_count):
    #     #     pool.apply_async(change_valid, i)
    #     pool.map(self.get_ipproxy, self.url_list)
    #     pool.close()
    #     pool.join()
    #
    #     return self.a_list




if __name__ == '__main__':

    #if DEBUG:
        #unittest.main()
    test =PaidProxy()
    test.get_ipproxy()

