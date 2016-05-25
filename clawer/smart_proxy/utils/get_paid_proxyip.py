#coding:utf8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import logging
import unittest
import re
import urllib
import time
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool

DEBUG = True
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


"""

tid	 订单号	123456768123121
num	 提取数量	1到50000任意数字
operator 运营商	电信(1) / 联通(2) / 移动(3)
area	地区
ports	端口号
foreign	是否提取大陆以外IP	全部(all) / 仅非大陆(only) / 仅大陆(none)
exclude_ports	排除端口号 eg:8090,8123
filter	过滤24小时内提取过的	默认不过滤，加上 on 参数就过滤
protocol	支持的协议	默认为http和https, 可传入 https
category	类别(匿名度)	默认为普匿 + 高匿, 可传入参数 普匿(1) / 高匿(2)
delay	延迟，单位是秒 判断条件为通过代理打开百度首页的时间。可传入任意数字，数字越小速度越快
sortby  IP排序	默认最快优先， 传入 speed表示最快优先， time 表示最新优先

举例: http://qsrdk.daili666api.com/ip/?tid=557067352008097&num=10&operator=1&delay=1&area=北京&category=2&foreign=none&exclude_ports=8090,8123&filter=on

"""

"""
 上海使用 protocol='https'
"""



class BaseProxy(object):
    def __init__(self):
        self.url = 'http://qsrdk.daili666api.com/ip/?'
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


    def __init__(self, tid='557067352008097',num='10',area='北京',filter= 'off',protocol='http',category='2',delay='1',sortby='speed',foreign='none'):
        BaseProxy.__init__(self)
        #self.url = 'http://www.xicidaili.com/nn'          #西刺代理
        self.a_list=[]
        self.tid= tid
        self.num = num
        self.filter=filter
        self.prot= protocol
        self.category=category
        self.delay=delay
        self.sortby=sortby
        self.foreign=foreign
        self.parameter = {'num':self.num, 'filter':self.filter,  'category':self.category, 'delay':self.delay,  'tid':self.tid,'protocol':self.prot,'sortby':self.sortby}

        para_url = urllib.urlencode(self.parameter)
        self.urlget= self.url+para_url+'&area='+area

        #parameter_list=[tid,num,operator,area,ports,exclude_ports,filter,protocol,category,delay,sortby]
        #'protocol':self.protocol,'sortby':self.sortby,



    def get_ipproxy(self,):
        resp = self.reqst.get(self.urlget, timeout=self.timeout)
        # trs = BeautifulSoup(resp.content, 'html.parser').find_all('tr')[:60]
        ip_content= re.split('\r\n',resp.content)
        proxy_list = ip_content


        print proxy_list
        return proxy_list







if __name__ == '__main__':

    #if DEBUG:
        #unittest.main()
    test =PaidProxy(num=2,sortby= 'time',protocol= 'https')
    test.get_ipproxy()

