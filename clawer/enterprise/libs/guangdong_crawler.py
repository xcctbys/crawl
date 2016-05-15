#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import logging
import os
import re
from . import settings
import random
import time

import json
import threading
from bs4 import BeautifulSoup
from enterprise.libs.CaptchaRecognition import CaptchaRecognition
from .Guangdong0 import Guangdong0
from .Guangdong1 import Guangdong1
from .Guangdong2 import Guangdong2
from common_func import get_proxy

urls = {
    'host': 'http://gsxt.gdgs.gov.cn/aiccips/',
    'page_search': 'http://gsxt.gdgs.gov.cn/aiccips/index',
    'page_captcha': 'http://gsxt.gdgs.gov.cn/aiccips/verify.html',
    'page_showinfo': 'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/showInfo.html',
    'checkcode':'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/checkCode.html',
}

headers = { 'Connetion': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"}

HOSTS =["www.szcredit.com.cn", "gsxt.gzaic.gov.cn", "gsxt.gdgs.gov.cn/aiccips"]

class GuangdongClawer(object):

    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()
    def __init__(self, json_restore_path= None):
        self.html_showInfo = None
        self.Captcha = None
        self.CR = CaptchaRecognition("guangdong")
        self.requests = requests.Session()
        self.requests.headers.update(headers)
        self.ents = []
        self.json_restore_path = json_restore_path
        self.dir_restore_path = settings.json_restore_path + '/guangdong/'
        #验证码图片的存储路径
        self.path_captcha = settings.json_restore_path + '/guangdong/ckcode.jpg'
        self.timeout = (10, 10)
        self.requests.proxies = get_proxy('guangdong')
        print self.requests.proxies


    # 破解搜索页面
    def crawl_page_search(self, url):
        r = self.request_by_method('GET', url, timeout=self.timeout)
        if not r:
            logging.error(u"Something wrong when getting the url:%s , status_code=%d", url, r.status_code)
            return None
        # r.encoding = "utf-8"
        return r.text
    #获得搜索结果展示页面
    def get_page_showInfo(self, url, datas):
        r = self.request_by_method('POST', url, data = datas)
        if not r:
            logging.error(u"Something wrong when posting the url:%s , status_code=%d", url, r.status_code)
            return False
        self.html_showInfo = r.text

    #分析 展示页面， 获得搜索到的企业列表
    def analyze_showInfo(self):
        if self.html_showInfo is None:
            logging.error(u"Getting Page ShowInfo failed\n")
            return
        Ent = []
        soup = BeautifulSoup(self.html_showInfo, "html5lib")
        divs = soup.find_all("div", {"class":"list"})
        if divs:
            for div in divs:
                logging.error(u"div.ul.li.a['href'] = %s\n", div.ul.li.a['href'])
                Ent.append(div.ul.li.a['href'])
        self.ents = Ent

    # 破解验证码页面
    def crawl_page_captcha(self, url_page_search ,url_captcha, url_CheckCode,url_showInfo,  textfield= '440301102739085'):
        html = self.crawl_page_search(url_page_search)
        count = 0
        while count < 15:
            count+= 1
            r = self.request_by_method('GET', url_captcha, timeout= self.timeout)
            if not r:
                logging.error(u"Something wrong when getting the Captcha url:%s , status_code=%d", url_captcha, r.status_code)
                continue
            if self.save_captcha(r.content):
                result = self.crack_captcha()
                #print result
                datas= {
                        'textfield': textfield,
                        'code': result,
                }
                response = self.request_by_method('POST', url_CheckCode, data = datas).json()
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

    #调用函数，破解验证码图片并返回结果
    def crack_captcha(self):
        if os.path.exists(self.path_captcha) is False:
            logging.error(u"Captcha path is not found\n")
            return
        result = self.CR.predict_result(self.path_captcha)
        return result[1]

    # 保存验证码图片
    def save_captcha(self, captcha):
        url_Captcha = self.path_captcha
        if captcha is None:
            logging.error(u"Can not store Captcha: None\n")
            return False
        self.write_file_mutex.acquire()
        f = open(url_Captcha, 'w')
        try:
            f.write(captcha)
        except IOError:
            logging.error("%s can not be written", url_Captcha)
        finally:
            f.close
        self.write_file_mutex.release()
        return True

    def request_by_method(self,method, url, *args, **kwargs):
        r = None
        try:
            r = self.requests.request(method, url, *args, **kwargs)
        except requests.Timeout as err:
            logging.error(u'Getting url: %s timeout. %s .'%(url, err.message))
            return False
        except Exception as err:
            logging.error(u'Getting url: %s exception:%s . %s .'%(url, type(err), err.message))
            return False
        if r.status_code != 200:
            logging.error(u"Something wrong when getting url:%s , status_code=%d", url, r.status_code)
            return False
        return r
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
                # http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo_cPlFMHz7UORGuPsot6Ab+gyFHBRDGmiqdLAvpr4C7UU=-7PUW92vxF0RgKhiSE63aCw==
                #http://gsxt.gdgs.gov.cn/aiccips /GSpublicity/GSpublicityList.html?service=entInfo_+8/Z3ukM3JcWEfZvXVt+QiLPiIqemiEqqq4l7n9oAh/FI+v6zW/DL40+AV4Hja1y-dA+Hj5oOjXjQTgAhKSP1lA==

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
                            # sub_json_dict =  guangdong.run(ent)
                            sub_json_dict = guangdong.run_asyn(ent)
                        # gsxt.gzaic.gov.cn
                        elif i==1:
                            logging.error(u"This %s enterprise is type 1"%(self.ent_num))
                            guangdong = Guangdong1(self.requests)
                            sub_json_dict =  guangdong.run(ent)
                        # gsxt.gdgs.gov.cn/aiccips
                        elif i==2:
                            logging.error(u"This %s enterprise is type 2"%(self.ent_num))
                            guangdong = Guangdong2(self.requests)
                            sub_json_dict = guangdong.run(ent)
                        else:
                            logging.error(u"This %s enterprise is no type!"%(self.ent_num))
                        break
                else:
                    logging.error(u"There are no response hosts:%s\n" % self.ent_num)
        except Exception as e:
            logging.error(u"An error ocurred when getting the main page, error: %s"% type(e))
            raise e
        finally:
            return sub_json_dict

    def run(self, ent_num):
        if not os.path.exists( self.dir_restore_path ):
            os.makedirs(self.dir_restore_path)
        json_dict = {}
        self.ent_num = str(ent_num)
        logging.error('crawl ID: %s\n'% ent_num)
        self.crawl_page_captcha(urls['page_search'], urls['page_captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        self.analyze_showInfo()
        data = self.crawl_page_main()
        json_dict[ent_num] = data
        return json.dumps(json_dict)
