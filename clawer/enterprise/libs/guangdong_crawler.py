#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import logging
import os
import sys
import time
import re
from . import settings
import random

import json
import codecs
import threading
from bs4 import BeautifulSoup
from enterprise.libs.CaptchaRecognition import CaptchaRecognition
from .Guangdong0 import Guangdong0
from .Guangdong1 import Guangdong1
from .Guangdong2 import Guangdong2

urls = {
    'host': 'http://gsxt.gdgs.gov.cn/aiccips/',
    'prefix_url_0':'http://www.szcredit.com.cn/web/GSZJGSPT/',
    'prefix_url_1':'http://gsxt.gzaic.gov.cn/search/',
    'page_search': 'http://gsxt.gdgs.gov.cn/aiccips/index',
    'page_Captcha': 'http://gsxt.gdgs.gov.cn/aiccips/verify.html',
    'page_showinfo': 'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/showInfo.html',
    'checkcode':'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/checkCode.html',
}

headers = { 'Connetion': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"}

#HOSTS =["www.szcredit.com.cn", "gsxt.gzaic.gov.cn", "gsxt.gdgs.gov.cn/aiccips"]
HOSTS =["www.szcredit.com.cn", "gsxt.gzaic.gov.cn", "gsxt.gdgs.gov.cn/aiccips"]

class GuangdongClawer(object):

    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()
    def __init__(self, json_restore_path= None):
        self.html_search = None
        self.html_showInfo = None
        self.Captcha = None
        self.CR = CaptchaRecognition("guangdong")
        self.requests = requests.Session()
        self.requests.headers.update(headers)
        self.ents = []
        self.main_host = ""
        self.json_dict={}
        self.json_restore_path = json_restore_path
        self.dir_restore_path = settings.json_restore_path + '/guangdong/'
        #self.json_restore_path = settings.json_restore_path + '/guangdong.json'
        #验证码图片的存储路径
        self.path_captcha = settings.json_restore_path + '/guangdong/ckcode.jpg'

    # 破解搜索页面
    def crawl_page_search(self, url):
        r = self.requests.get( url)
        if r.status_code != 200:
            logging.error(u"Something wrong when getting the url:%s , status_code=%d", url, r.status_code)
            return
        r.encoding = "utf-8"
        #logging.error("searchpage html :\n  %s", r.text)
        self.html_search = r.text
    #获得搜索结果展示页面
    def get_page_showInfo(self, url, datas):
        r = self.requests.post( url, data = datas )
        if r.status_code != 200:
            return False
        r.encoding = "utf-8"
        #logging.error("showInfo page html :\n  %s", r.text)
        self.html_showInfo = r.text

    #分析 展示页面， 获得搜索到的企业列表
    def analyze_showInfo(self):
        if self.html_showInfo is None:
            logging.error(u"Getting Page ShowInfo failed\n")
        # call Object Analyze's method
        Ent = []
        soup = BeautifulSoup(self.html_showInfo, "html5lib")
        divs = soup.find_all("div", {"class":"list"})
        if divs:
            for div in divs:
                logging.error(u"div.ul.li.a['href'] = %s\n", div.ul.li.a['href'])
                Ent.append(div.ul.li.a['href'])
        self.ents = Ent

    # 破解验证码页面
    def crawl_page_captcha(self, url_Captcha, url_CheckCode,url_showInfo,  textfield= '440301102739085'):

        count = 0
        while True:
            count+= 1
            r = self.requests.get( url_Captcha)
            if r.status_code != 200:
                logging.error(u"Something wrong when getting the Captcha url:%s , status_code=%d", url_Captcha, r.status_code)
                return
            self.Captcha = r.content
            if self.save_captcha():
                result = self.crack_captcha()
                #print result
                datas= {
                        'textfield': textfield,
                        'code': result,
                }
                response = self.get_check_response(url_CheckCode, datas)
                # response返回的json结果: {u'flag': u'1', u'textfield': u'H+kiIP4DWBtMJPckUI3U3Q=='}
                if response['flag'] == '1':
                    datas_showInfo = {'textfield': response['textfield'], 'code': result}
                    self.get_page_showInfo(url_showInfo, datas_showInfo)
                    break
                else:
                    logging.error(u"crack ID: %s Captcha failed, the %d time(s)"%(self.ent_num ,count))
                    if count > 15:
                        logging.error(u"ID: %s, crack Captcha failed after the %d times of trial" %( textfield,count))
                        break
            time.sleep(random.uniform(1, 4))
        return
    #获得验证的结果信息
    def get_check_response(self, url, datas):
        r = self.requests.post( url, data = datas )
        if r.status_code != 200:
            return False
        #print r.json()
        return r.json()
    #调用函数，破解验证码图片并返回结果
    def crack_captcha(self):
        if os.path.exists(self.path_captcha) is False:
            logging.error(u"Captcha path is not found\n")
            return
        result = self.CR.predict_result(self.path_captcha)
        return result[1]
        #print result
    # 保存验证码图片
    def save_captcha(self):
        url_Captcha = self.path_captcha
        if self.Captcha is None:
            logging.error(u"Can not store Captcha: None\n")
            return False
        self.write_file_mutex.acquire()
        f = open(url_Captcha, 'w')
        try:
            f.write(self.Captcha)
        except IOError:
            logging.error("%s can not be written", url_Captcha)
        finally:
            f.close
        self.write_file_mutex.release()
        return True
    """
    The following functions are for main page
    """

    """ 1. iterate enterprises in ents
        2. for each ent: decide host so that choose functions by pattern
        3. for each pattern, iterate urls
        4. for each url, iterate item in tabs
    """
    def crawl_page_main(self ):
        sub_json_dict= {}
        if not self.ents:
            logging.error(u"Get no search result\n")
        try:

            for ent in self.ents:
                #http://www.szcredit.com.cn/web/GSZJGSPT/ QyxyDetail.aspx?rid=acc04ef9ac0145ecb8c87dd5710c2f86
                #http://gsxt.gzaic.gov.cn/search/ search!entityShow?entityVo.pripid=440100100012003051400230
                #http://gsxt.gdgs.gov.cn/aiccips /GSpublicity/GSpublicityList.html?service=entInfo_+8/Z3ukM3JcWEfZvXVt+QiLPiIqemiEqqq4l7n9oAh/FI+v6zW/DL40+AV4Hja1y-dA+Hj5oOjXjQTgAhKSP1lA==
                #HOSTS =["www.szcredit.com.cn", "121.8.227.200:7001", "gsxt.gdgs.gov.cn/aiccips"]
                m = re.match('http', ent)
                if m is None:
                    ent = urls['host']+ ent[3:]
                logging.error(u"ent url:%s\n"% ent)
                for i, item in enumerate(HOSTS):
                    if ent.find(item) != -1:

                        #"www.szcredit.com.cn"
                        if i==0:
                            logging.error(u"This %s enterprise is type 0"%(self.ent_num))
                            guangdong = Guangdong0(self.requests, self.ent_num)
                            sub_json_dict =  guangdong.run(ent)
                        elif i==1:
                            logging.error(u"This %s enterprise is type 1"%(self.ent_num))
                            guangdong = Guangdong1(self.requests)
                            sub_json_dict =  guangdong.run(ent)
                        # gsxt.gdgs.gov.cn/aiccips
                        elif i==2:
                            logging.error(u"This %s enterprise is type 2"%(self.ent_num))
                            guangdong = Guangdong2(self.requests)
                            sub_json_dict = guangdong.run(ent)
                        break
                else:
                    logging.error(u"There are no response hosts:%s\n" % self.ent_num)
        except Exception as e:
            logging.error(u"An error ocurred when getting the main page, error: %s"% type(e))
            raise e
        finally:
            return sub_json_dict


    def crawl_page_by_url(self, url):
        r = self.requests.get( url)
        if r.status_code != 200:
            logging.error(u"Getting page by url:%s\n, return status %s\n"% (url, r.status_code))
            return False
        # 为了防止页面间接跳转，获取最终目标url
        return {'page' : r.text, 'url': r.url}

    def crawl_page_by_url_post(self, url, data, header={}):
        if header:
            r = self.requests.post(url, data, headers= header)
        else :
            r = self.requests.post(url, data)
        if r.status_code != 200:
            logging.error(u"Getting page by url with post:%s\n, return status %s\n"% (url, r.status_code))
            return False
        return {'page': r.text, 'url': r.url}

    # main function
    def run(self, ent_num):
        if not os.path.exists( self.dir_restore_path ):
            os.makedirs(self.dir_restore_path)
        json_dict = {}
        self.ent_num = str(ent_num)
        logging.error('crawl ID: %s\n'% ent_num)
        self.crawl_page_search(urls['page_search'])
        self.crawl_page_captcha(urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        self.analyze_showInfo()
        data = self.crawl_page_main()
        json_dict[ent_num] = data
        return json.dumps(json_dict)
        #json_dump_to_file(self.json_restore_path , self.json_dict)

def html_to_file(path, html):
    write_type = 'w'
    if os.path.exists(path):
        write_type = 'a'
    with codecs.open(path, write_type, 'utf-8') as f:
        f.write(html)

def json_dump_to_file(path, json_dict):
    write_type = 'w'
    if os.path.exists(path):
        write_type = 'a'
    with codecs.open(path, write_type, 'utf-8') as f:
        f.write(json.dumps(json_dict, ensure_ascii=False)+'\n')

def read_ent_from_file(path):
    read_type = 'r'
    if not os.path.exists(path):
        logging.error(u"There is no path : %s"% path )
    lines = []
    with codecs.open(path, read_type, 'utf-8') as f:
        lines = f.readlines()
    lines = [ line.split(',') for line in lines ]
    return lines


"""
if __name__ == "__main__":
    reload (sys)
    sys.setdefaultencoding('utf8')
    import run
    run.config_logging()
    ents = read_ent_from_file("./enterprise_list/guangdong.txt")
    if not os.path.exists("./enterprise_crawler"):
        os.makedirs("./enterprise_crawler")
    guangdong = GuangdongClawer('./enterprise_crawler/Guangdong.json')
    for ent_str in ents:
        logging.info(u'###################   Start to crawl enterprise with id %s   ###################\n' % ent_str[2])
        guangdong.run(ent_num = ent_str[2])
        logging.info(u'###################   Enterprise with id Finished : %s   ###################\n' % ent_str[2])
"""
