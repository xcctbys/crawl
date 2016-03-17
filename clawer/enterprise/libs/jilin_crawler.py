#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import logging
import os
import sys
import time
import re
from . import settings
import json
import codecs
import threading
from bs4 import BeautifulSoup
from enterprise.libs.CaptchaRecognition import CaptchaRecognition
import random
import hashlib # MD5 encrypt

urls = {
    'host': 'http://211.141.74.198:8081/aiccips/pub/',
    'webroot' : 'http://211.141.74.198:8081/aiccips/',
    'root' : 'http://211.141.74.198:8081/',
    'page_search': 'http://211.141.74.198:8081/aiccips/',
    'page_Captcha': 'http://211.141.74.198:8081/aiccips/securitycode',
    'checkcode':'http://211.141.74.198:8081/aiccips/pub/indsearch',
}

headers = { #'Connetion': 'Keep-Alive',
            'Host' : '211.141.74.198:8081',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:43.0) Gecko/20100101 Firefox/43.0",
            'Referer': "http://211.141.74.198:8081/aiccips/",
            }

class JilinCrawler(object):
    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    def __init__(self, json_restore_path):
        self.CR = CaptchaRecognition("jilin")
        self.requests = requests.Session()
        self.requests.headers.update(headers)
        self.ents = []
        self.json_restore_path = json_restore_path
        self.csrf = ""
        self.ROBOTCOOKIEID = ""
        self.encrpripid = ""
        self.enttype = ""
        #验证码图片的存储路径
        self.path_captcha = settings.json_restore_path + '/jilin/ckcode.jpg'
        #html数据的存储路径
        self.html_restore_path = settings.json_restore_path + '/jilin/'

    #分析 展示页面， 获得搜索到的企业列表
    def analyze_showInfo(self, page):
        Ent = []
        soup = BeautifulSoup(page, "html5lib")
        divs = soup.find_all("div", {"class":"list"})
        if divs:
            for div in divs:
                a = div.find('a')
                if a.has_attr('href'):
                    Ent.append(a['href'])
        self.ents = Ent

    def is_search_result_page(self, page):
        """判断是否成功搜索页面"""
        soup = BeautifulSoup(page, 'html5lib')
        divs = soup.find('div', {'class':'list'})
        return divs is not None

    def crawl_page_captcha(self, url_search, url_Captcha, url_CheckCode,  textfield= ''):
        """破解验证码页面"""
        page = self.crawl_page_by_url(url_search)['page']
        robotcookieid =  re.findall(r'\|([0-9a-z]{40})\|', page)
        forms = None
        if robotcookieid:
            for cookie in robotcookieid:
                self.ROBOTCOOKIEID = cookie
                page = self.crawl_page_by_url(url_search)['page']
                soup = BeautifulSoup(page, 'html5lib')
                forms = soup.find('form', {'id':'searchform'})
                if forms:
                    self.ROBOTCOOKIEID = cookie
                    self.csrf = forms.find('input',{'name': '_csrf'})['value']
                    break
        else:
            soup = BeautifulSoup(page, 'html5lib')
            self.csrf = soup.find('meta', {'name': '_csrf'})['content']
        if not self.csrf :
            return
        datas= {
                'kw' : textfield,
                '_csrf': self.csrf,
                'secode': None,
        }
        count = 0
        while True:
            count+= 1
            r = self.requests.get( url_Captcha, cookies={'ROBOTCOOKIEID': self.ROBOTCOOKIEID}, headers={'Referer': "http://211.141.74.198:8081/aiccips/"})
            if r.status_code != 200:
                logging.error(u"Something wrong when getting the Captcha url:%s , status_code=%d", url_Captcha, r.status_code)
                return
            if self.save_captcha(r.content):
                result = self.crack_captcha()
                print result
                datas['secode'] = hashlib.md5(str(result)).hexdigest()
                res=  self.crawl_page_by_url_post(url_CheckCode, datas)['page']
                # 如果验证码正确，就返回一种页面，否则返回主页面
                if self.is_search_result_page(res) :
                    self.analyze_showInfo(res)
                    break
                else:
                    logging.debug(u"crack Captcha failed, the %d time(s)", count)
                    if count >15:
                        break;
        return
    def crack_captcha(self):
        """调用函数，破解验证码图片并返回结果"""
        if os.path.exists(self.path_captcha) is False:
            logging.error(u"Captcha path is not found\n")
            return
        result = self.CR.predict_result(self.path_captcha)
        # print result
        return result[1]

    def save_captcha(self, Captcha):
        """保存验证码图片"""
        url_Captcha = self.path_captcha
        if Captcha is None:
            logging.error(u"Can not store Captcha: None\n")
            return False
        self.write_file_mutex.acquire()
        f = open(url_Captcha, 'w')
        try:
            f.write(Captcha)
        except IOError:
            logging.debug("%s can not be written", url_Captcha)
        finally:
            f.close
        self.write_file_mutex.release()
        return True
    def crawl_page_main(self ):
        """  爬取页面信息总函数        """
        sub_json_dict= {}
        if not self.ents:
            logging.error(u"Get no search result\n")
        try:
            for ent in self.ents:
                m = re.match('http', ent)
                if m is None:
                    ent = urls['host']+ ent
                logging.info(u"crawl main url:%s"% ent)
                self.encrpripid = ent[ent.rfind('/')+1:]
                temp = ent[:ent.rfind('/')]
                self.enttype =  temp[temp.rfind('/')+1 :]
                #工商公示信息
                url = ent
                sub_json_dict.update(self.crawl_ind_comm_pub_pages(url))
                url = urls['host'] + "qygsdetail/"+ self.enttype+"/" + self.encrpripid
                sub_json_dict.update(self.crawl_ent_pub_pages(url))
                url = urls['host'] + "qtgsdetail/"+ self.enttype+"/" + self.encrpripid
                sub_json_dict.update(self.crawl_other_dept_pub_pages(url))
                url = urls['host'] + "sfgsdetail/"+ self.enttype+"/" + self.encrpripid
                sub_json_dict.update(self.crawl_judical_assist_pub_pages(url))

        except Exception as e:
            logging.error(u"An error ocurred when getting the main page, error: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #工商公式信息页面
    def crawl_ind_comm_pub_pages(self, url, post_data={}):
        """  爬取 工商公式 信息页面        """
        sub_json_dict={}
        try:
            #page = html_from_file('next.html')
            logging.info( u"crawl the crawl_ind_comm_pub_pages page %s."%(url))
            page = self.crawl_page_by_url(url)['page']
            #html_to_file('next.html', page)
            # page = html_from_file('next.html')
            post_data = {'encrpripid': self.encrpripid}
            dj = self.parse_page_gsgs(page , 'jibenxinxi')
            sub_json_dict['ind_comm_pub_reg_basic'] = dj[u'基本信息'] if dj.has_key(u'基本信息') else []        # 登记信息-基本信息
            sub_json_dict['ind_comm_pub_reg_shareholder'] =dj[u'股东信息'] if dj.has_key(u'股东信息') else []   # 股东信息
            sub_json_dict['ind_comm_pub_reg_modify'] =  dj[u'变更信息'] if dj.has_key(u'变更信息') else []      # 变更信息
            dj = self.parse_page_gsgs(page , 'beian', post_data)
            sub_json_dict['ind_comm_pub_arch_key_persons'] = dj[u'主要人员信息'] if dj.has_key(u'主要人员信息') else []   # 备案信息-主要人员信息
            sub_json_dict['ind_comm_pub_arch_branch'] = dj[u'分支机构信息'] if dj.has_key(u'分支机构信息') else []       # 备案信息-分支机构信息
            sub_json_dict['ind_comm_pub_arch_liquidation'] = dj[u'清算信息'] if dj.has_key(u'清算信息') else []   # 备案信息-清算信息
            dj = self.parse_page_gsgs(page , 'dongchandiya', post_data)
            sub_json_dict['ind_comm_pub_movable_property_reg'] = dj[u'动产抵押登记信息'] if dj.has_key(u'动产抵押登记信息') else []
            dj = self.parse_page_gsgs(page , 'guquanchuzhi', post_data)
            sub_json_dict['ind_comm_pub_equity_ownership_reg'] = dj[u'股权出质登记信息'] if dj.has_key(u'股权出质登记信息') else []
            dj = self.parse_page_gsgs(page , 'xingzhengchufa', post_data)
            sub_json_dict['ind_comm_pub_administration_sanction'] = dj[u'行政处罚信息'] if dj.has_key(u'行政处罚信息') else []
            dj = self.parse_page_gsgs(page , 'jingyingyichangminglu', post_data)
            sub_json_dict['ind_comm_pub_business_exception'] = dj[u'经营异常信息'] if dj.has_key(u'经营异常信息') else []
            dj = self.parse_page_gsgs(page , 'yanzhongweifaqiye', post_data)
            sub_json_dict['ind_comm_pub_serious_violate_law'] = dj[u'严重违法信息'] if dj.has_key(u'严重违法信息') else []
            dj = self.parse_page_gsgs(page , 'chouchaxinxi', post_data)
            sub_json_dict['ind_comm_pub_spot_check'] = dj[u'抽查检查信息'] if dj.has_key(u'抽查检查信息') else []
        except Exception as e:
            logging.debug(u"An error ocurred in crawl_ind_comm_pub_pages: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    # 工商公式信息页面
    def parse_page_gsgs(self, page, div_id='sifapanding', post_data= {}):
        soup = BeautifulSoup(page, 'html5lib')
        page_data = {}

        try:
            div = soup.find('div', attrs = {'id':div_id})
            if div:
                table = div.find('table')
            else:
                table = soup.find('table')
            #print table
            while table:
                if table.name == 'table':
                    table_name = self.get_table_title(table)
                    if table_name:
                        if table_name == u"股东信息":
                            page_data[table_name] =  self.parse_table_gudong(table, table_name, page)
                        elif table_name == u"变更信息":
                            page_data[table_name] = self.parse_table_biangeng(table, table_name, page)
                        elif table_name == u"股东及出资信息":
                            page_data[table_name] = self.parse_table_gdczxx(table, table_name, page)
                        elif table_name == u"主要人员信息":
                            page_data[table_name] = self.parse_table_people(table, table_name, page, post_data)
                        elif table_name == u"分支机构信息":
                            page_data[table_name] = self.parse_table_branch(table, table_name, page, post_data)
                        elif table_name == u"动产抵押登记信息":
                            page_data[table_name] = self.parse_table_dongchandiya(table, table_name, page, post_data)
                        elif table_name == u"股权出质登记信息":
                            page_data[table_name] = self.parse_table_guquanchuzhi(table, table_name, page, post_data)
                        elif table_name == u"严重违法信息":
                            page_data[table_name] = self.parse_table_yanzhongweifa(table, table_name, page, post_data)
                        elif table_name == u"抽查检查信息":
                            page_data[table_name] = self.parse_table_chouyangjiancha(table, table_name, page, post_data)
                        elif table_name == u"行政处罚信息":
                            page_data[table_name] = self.parse_table_xingzhengchufa(table, table_name, page, post_data)
                        elif table_name == u"经营异常信息":
                            page_data[table_name] = self.parse_table_jingyingyichang(table, table_name, page, post_data)
                        # elif table_name == u"变更":
                        #     page_data[table_name] = self.parse_table_guquanchuzhi_biangeng(table, table_name, page, post_data)
                        else:
                            page_data[table_name] = self.parse_table(table, table_name, page)
                table = table.nextSibling

        except Exception as e:
            logging.error(u'parse failed, with exception %s' % e)
            raise e
        finally:
            return page_data
    # 工商公示信息 - 经营异常信息
    def parse_table_jingyingyichang(self, bs_table, table_name, page, post_data):
        """     工商公示信息 - 经营异常信息 """
        sub_json_list=[]
        try:
            logging.info(u"parse table 经营异常信息 ")
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = urls['host']+ "/jyyc/1219"
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_abn = l['abntime']
                date_rem = l['remdate']
                # 这里注意type
                datas = [i+1, l['specause'], self.SetJsonTime(date_abn), l['remexcpres'], self.SetJsonTime(date_rem), l['decorg']]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse table 经营异常信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 工商公示信息 - 行政处罚信息
    def parse_table_xingzhengchufa(self, bs_table, table_name, page, post_data):
        """     工商公示信息 - 行政处罚信息     """
        sub_json_list=[]
        try:
            logging.info(u"parse table 行政处罚信息 ")
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = urls['host'] + "/gsxzcfxx"
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_abn = l['pendecissdate']
                #logging.info( u"crawl the link %s, table_name is %s"%(link, table_name))
                link = urls['webroot']+"pub/gsxzcfdetail/"+post_data['encrpripid']+"/"+l['caseno']
                logging.info( u"crawl the link %s, table_name is %s"%(link, table_name))
                link_page = self.crawl_page_by_url(link)['page']
                ########!!!!!!!!!!!!!!这里的link_page没有做
                link_data = self.parse_page(link_page)
                # 这里注意type
                datas = [i+1, l['pendecno'], l['illegacttype'], self.getCfType(l['pentype'])+" 罚款金额:"+str(l['penam'])+"万元 没收金额:"+ str(l['forfam'])+"万元", l['penauth'],self.SetJsonTime(date_abn), l['insres']]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse table 行政处罚信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 工商公示信息 - 抽样检查信息
    def parse_table_chouyangjiancha(self, bs_table, table_name, page, post_data):
        """     工商公示信息 - 抽样检查信息     """
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = urls['host'] + "/ccjcxx"
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_abn = l['insdate']
                datas = [i+1, l['insauth'], l['instype'],self.SetJsonTime(date_abn), l['insres']]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse table 抽样检查信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 工商公示信息 - 严重违法信息
    def parse_table_yanzhongweifa(self, bs_table, table_name, page, post_data):
        """     工商公示信息 - 严重违法信息     """
        sub_json_list=[]
        try:
            logging.info(u"parse table 严重违法信息" )
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = urls['host'] +"/yzwfqy"
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_abn = l['abntime']
                date_rem = l['remdate']
                #logging.info( u"crawl the link %s, table_name is %s"%(link, table_name))
                # 这里注意type
                datas = [i+1, l['serillrea'],self.SetJsonTime(date_abn), l['remexcpres'],self.SetJsonTime(date_rem), l['decorg']]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse table 严重违法信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 工商公示信息 - 股权出质登记信息
    def parse_table_guquanchuzhi(self, bs_table, table_name, page, post_data):
        """     工商公示信息 - 股权出质登记信息   """
        sub_json_list=[]
        try:
            logging.info(u"parse table 股权出质 ")
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = urls['host'] +"/gsgqcz"
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_dict = l['equpledate']
                link = urls['webroot']+"pub/gsgqczdetail/"+post_data['encrpripid']+"/"+str(l['equityno'])+"/"+str(l['type'])
                logging.info( u"crawl the link %s, table_name is %s"%(link, table_name))
                link_page = self.crawl_page_by_url(link)['page']
                ########!!!!!!!!!!!!!!这里的link_page没有做
                link_data = self.parse_page(link_page)
                # 这里注意type
                datas = [i+1, l['equityno'], l['pledgor'], l['blicno'], str(l['impam'])+l['pledamunit'], l['imporg'], l['impmorblicno'],self.SetJsonTime(date_dict) ,'有效' if int(l['type'])==1 else '无效', link_data]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse table 股权出质 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 工商公示信息 - 动产抵押登记信息
    def parse_table_dongchandiya(self, bs_table, table_name, page, post_data):
        """     工商公示信息 - 动产抵押登记信息 """
        sub_json_list=[]
        try:
            logging.info(u"parse table 动产抵押登记信息")
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = urls['host'] + "/gsdcdy"
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_dict = l['regidate']
                # 详情处没有处理，还没有见到有数据的表格
                datas = [i+1, l['morregcno'], self.SetJsonTime(date_dict) ,l['regorg'], str(l['priclasecam'])+"万元", '有效' if l['type']==1 else '无效', '详情']
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse table 动产抵押登记信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 工商公示信息 - 分支机构信息
    def parse_table_branch(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = urls['host'] + "/gsfzjg/1219"
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            ls = json.loads(res)
            for i, l in enumerate(ls):
                datas = [i+1, l['regno'], l['brname'], l['regorg']]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse table 分支机构信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 工商公示信息 - 主要人员信息
    def parse_table_people(self, bs_table, table_name, page, post_data):
        """ 工商公示信息 - 主要人员信息 """
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = "http://211.141.74.198:8081/aiccips/pub/gsryxx/1219"
            #print post_data
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            ls = json.loads(res)
            for i, l in enumerate(ls):
                datas = [i+1, l['name'], l['position']]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse table 主要人员信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 工商公示信息 - 股东信息表
    def parse_table_gudong(self, bs_table, table_name, page):
        """工商公示信息 - 股东信息表 """
        sub_json_list = []
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            m = re.compile(r"czxxliststr\s*=\s*(\'.*?\');").search(page)
            if m:
                czxxliststr = m.group()
                strs = re.compile(r"(\'.*?\')").search(czxxliststr).group()
                if strs.strip("'"):
                    czxxlist = json.loads(strs.strip("'"))  # 将字符串转换成list
                    m1  = re.compile(r"encrpripid\s*=\s*(\'.*?\');").search(page)
                    if m1:
                        pripidstr = m1.group()

                        encrpripid = re.compile(r"(\'.*?\')").search(pripidstr).group().strip("'")

                        for item in czxxlist:
                            if item['xzqh'] == "1":
                                link = urls['webroot'] + 'pub/gsnzczxxdetail/'+ encrpripid+'/'+ item['recid']
                                link_page = self.crawl_page_by_url(link)['page']
                                link_data = self.parse_page_gsgs(link_page, table_name+'_detail')
                                datas = [ item['invtype'], item['inv'], item['blictype'], item['blicno'], link_data]
                            else:
                                datas = [ item['invtype'], item['inv'], item['blictype'], item['blicno'], '']
                            sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse table 股东信息表 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 工商公示信息 - 变更信息表
    def parse_table_biangeng(self, bs_table, table_name, page):
        """ 工商公示信息 - 变更信息表 """
        sub_json_list = []
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]

            m = re.compile(r"bgsxliststr\s*=\s*(\'.*?\');").search(page)
            if m:
                bgsxliststr = m.group()
                m1 = re.compile(r"(\'.*?\')").search(bgsxliststr)
                if m1:
                    strs = m1.group().strip("'")
                    bgsxlist = json.loads(strs) if strs else []  # 将字符串转换成list
                    # print type(bgsxlist)
                    for item in bgsxlist:
                        date_dict = item['altdate']
                        datas = [ item['altitem'], item['altbe'], item['altaf'], self.SetJsonTime(date_dict) ]
                        sub_json_list.append(dict(zip(titles, datas)))
                else:
                    logging.error(u"can't find bgsxliststr in table 变更信息表" )
        except Exception as e:
            logging.error(u"parse table 变更信息表 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list

    def SetJsonTime(self, item):
        if type(item)== dict:
            return str(item['year']+1900)+'年'+ str(item['month']%12+1)+'月'+ str(item['date'])+'日'
        return ""
    def currency(self, cur):
        strcur=u"元"
        if cur == "156":
            strcur=u"元"
        elif cur=="840":
            strcur=u"美元"
        elif cur=="392":
            strcur=u"日元"
        elif cur=="954":
            strcur=u"欧元"
        elif cur=="344":
            strcur=u"港元"
        elif cur=="826":
            strcur=u"英镑"
        elif cur=="280":
            strcur=u"德国马克"
        elif cur=="124":
            strcur=u"加拿大元"
        elif cur=="250":
            strcur=u"法国法郎"
        elif cur=="528":
            strcur=u"荷兰"
        elif cur=="756":
            strcur=u"瑞士法郎"
        elif cur=="702":
            strcur=u"新加坡元"
        elif cur=="036":
            strcur=u"澳大利亚元"
        elif cur=="208":
            strcur=u"丹麦克郎"
        return strcur
    def getRange(self, ranges):
        rtn=""
        ras=ranges.split(",");
        for l in ras:
            if l ==  "1":
                rtn+="主债权 "
            elif l ==  "2":
                rtn+="利息 "
            elif l ==  "3":
                rtn+="违约金 "
            elif l ==  "4":
                rtn+="损害赔偿金 "
            elif l ==  "5":
                rtn+="实现债权的费用 "
            elif l ==  "6":
                rtn+="其他约定 "
        return rtn

    #爬取 企业公示信息 页面
    def crawl_ent_pub_pages(self, url):
        """  爬取 企业公示信息 信息页面        """
        sub_json_dict = {}
        try:
            logging.info( u"crawl the crawl_ent_pub_pages page %s"%(url))
            page = self.crawl_page_by_url(url)['page']
            #html_to_file('next2.html', page)
            #page = html_from_file('next.html')
            post_data = {'encrpripid': self.encrpripid}
            p = self.parse_page_qygs(page, 'qiyenianbao', post_data)
            sub_json_dict['ent_pub_ent_annual_report'] = p[u'企业年报'] if p.has_key(u'企业年报') else []
            p = self.parse_page_qygs(page, 'zhishichanquan', post_data)
            sub_json_dict['ent_pub_knowledge_property'] = p[u'知识产权出质登记信息'] if p.has_key(u'知识产权出质登记信息') else []
            p = self.parse_page_qygs(page, 'xingzhengxuke', post_data)
            sub_json_dict['ent_pub_administration_license'] = p[u'行政许可信息'] if p.has_key(u'行政许可信息') else []
            p = self.parse_page_qygs(page, 'xingzhengchufa', post_data)
            sub_json_dict['ent_pub_administration_sanction'] = p[u'行政处罚信息'] if p.has_key(u'行政处罚信息') else []
            p = self.parse_page_qygs(page, 'touziren', post_data)
            sub_json_dict['ent_pub_shareholder_capital_contribution'] = p[u'股东及出资信息'] if p.has_key(u'股东及出资信息') else []
            sub_json_dict['ent_pub_reg_modify'] = p[u'变更信息'] if p.has_key(u'变更信息') else []
            p = self.parse_page_qygs(page, 'gudongguquan', post_data)
            sub_json_dict['ent_pub_equity_change'] = p[u'股权变更信息'] if p.has_key(u'股权变更信息') else []
        except Exception as e:
            logging.debug(u"An error ocurred in crawl_ent_pub_pages: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    # 企业公示信息页面
    def parse_page_qygs(self, page, div_id='sifapanding', post_data= {}):
        soup = BeautifulSoup(page, 'html5lib')
        page_data = {}
        try:
            div = soup.find('div', attrs = {'id':div_id})
            if div:
                table = div.find('table')
            else:
                table = soup.find('table')
            #print table
            while table:
                if table.name == 'table':
                    table_name = self.get_table_title(table)
                    if table_name:
                        if table_name == u"股东及出资信息":
                            page_data[table_name] = self.parse_table_qygs_gudongchuzi(table, table_name, page, post_data)
                        elif table_name == u"变更信息":
                            page_data[table_name] = self.parse_table_qygs_biangengxinxi(table, table_name, page, post_data)
                        elif table_name == u"股权变更信息":
                            page_data[table_name] = self.parse_table_qygs_guquan(table, table_name, page, post_data)
                        elif table_name == u"行政许可信息":
                            page_data[table_name] = self.parse_table_qygs_xinzhengxuke(table, table_name, page, post_data)
                        elif table_name == u"知识产权出质登记信息":
                            page_data[table_name] = self.parse_table_qygs_zhishichanquan(table, table_name, page, post_data)
                        elif table_name == u"行政处罚信息":
                            page_data[table_name] = self.parse_table_qygs_xinzhengchufa(table, table_name, page, post_data)
                        else:
                            page_data[table_name] = self.parse_table(table, table_name, page)
                table = table.nextSibling

        except Exception as e:
            logging.error(u'parse qygs page failed, with exception %s' % e)
            raise e
        finally:
            return page_data
    # 企业公示信息 - 行政处罚信息
    def parse_table_qygs_xinzhengchufa(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            logging.info(u"parse qygs table 行政处罚信息")
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = urls['host'] + "qygsjsxxxzcfxx"
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf, 'X-Requested-With': 'XMLHttpRequest','Referer': "http://211.141.74.198:8081/aiccips/pub/qygsdetail/1219/"+self.encrpripid})['page']
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_from = l['pendecissdate']
                # 这里注意type
                datas = [i+1, l['pendecno'], self.getCfType(l['pentype']),l['penauth'] , self.SetJsonTime(date_from), l['remark']]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse qygs table 行政处罚信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 企业公示信息 - 知识产权出质登记信息
    def parse_table_qygs_zhishichanquan(self, bs_table, table_name, page, post_data):
        """ 企业公示信息 - 知识产权出质登记信息 """
        sub_json_list=[]
        try:
            logging.info(u"parse qygs table 知识产权出质登记信息")
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = urls['host']+ "qygsjsxxzscqcz"
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf, 'X-Requested-With': 'XMLHttpRequest','Referer': "http://211.141.74.198:8081/aiccips/pub/qygsdetail/1219/"+self.encrpripid})['page']
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_from = l['pleregperfrom']
                date_to = l['pleregperto']
                link = urls['webroot']+"pub/jszscqdetail/"+post_data['encrpripid']+"/"+l['pid']+"/"+l['type']
                link_page = self.crawl_page_by_url(link)['page']
                link_data = self.parse_page_qygs(link_page)
                # 这里注意type
                datas = [i+1, l['tmregno'], l['tmname'], l['kinds'], l['pledgor'], l['imporg'],  self.SetJsonTime(date_from) +" - " + self.SetJsonTime(date_to) , '有效' if int(l['type'])==1 else '无效', link_data]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse qygs table 知识产权出质登记信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 企业公示信息 - 行政许可信息
    def parse_table_qygs_xinzhengxuke(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            logging.info(u"parse qygs table 行政许可信息")
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = urls['host'] + "qygsjsxxxzxk"
            #print post_data
            #print self.csrf
            #print page
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf, 'X-Requested-With': 'XMLHttpRequest','Referer': "http://211.141.74.198:8081/aiccips/pub/qygsdetail/1219/"+self.encrpripid,})['page']
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_from = l['valfrom']
                date_to   = l['valto']
                link = urls['webroot']+"pub/jsxzxkdetail/"+post_data['encrpripid']+"/"+l['pid']+"/"+l['type']
                #link_page = self.crawl_page_by_url(link)['page']
                #logging.info( u"crawl the link %s, table_name is %s"%(link, table_name))
                #link_data = self.parse_page_qygs(link_page)
                link_data = u"无"
                # 这里注意type
                datas = [i+1, l['licno'], l['licname'], self.SetJsonTime(date_from), self.SetJsonTime(date_to) ,\
                            l['licanth'], l['licitem'], '有效' if int(l['type'])==1 else '无效', link_data]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse qygs table 行政许可信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 企业公示信息 - 股权变更信息
    def parse_table_qygs_guquan(self, bs_table, table_name, page, post_data):
        """ 企业公示信息 - 股权变更信息"""
        sub_json_list=[]
        try:
            logging.info(u"parse qygs table 股权变更信息")
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = urls['host']+ "/qygsJsxxgqbg"
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf, 'X-Requested-With': 'XMLHttpRequest','Referer': "http://211.141.74.198:8081/aiccips/pub/qygsdetail/1219/"+self.encrpripid})['page']
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_from = l['altdate']
                # 这里注意type
                datas = [i+1, l['inv'], l['transamprpre'], l['transampraft'] , self.SetJsonTime(date_from)]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse qygs table 股权变更信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 企业公示信息 - 变更信息
    def parse_table_qygs_biangengxinxi(self, bs_table, table_name, page, post_data):
        """ 企业公示信息 - 变更信息 """
        sub_json_list=[]
        try:
            logging.info(u"parse qygs table 股东及出资- 变更信息 ")
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = urls['host'] + "/qygsjsxxczxxbgsx"
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf, 'X-Requested-With': 'XMLHttpRequest','Referer': "http://211.141.74.198:8081/aiccips/pub/qygsdetail/1219/"+self.encrpripid})['page']
            ls = json.loads(res)
            for rows in ls:
                for i, l in enumerate(rows['bgxx']):
                    date_from = l['altdate']
                    # 这里注意type
                    datas = [i+1, l['altitem'], self.SetJsonTime(date_from), l['altbe'], l['altaf'] ]
                    sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse qygs table 股东及出资信息- 变更信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list

    # 企业公示信息 - 股东及出资信息
    def parse_table_qygs_gudongchuzi(self, bs_table, table_name, page, post_data):
        """ 企业公示信息 - 股东及出资信息 """
        sub_json_list=[]
        try:
            logging.info(u"parse qygs table 股东及出资信息 ")
            url = urls['host']+ "/qygsjsxxxzczxx"
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf, 'X-Requested-With': 'XMLHttpRequest','Referer': "http://211.141.74.198:8081/aiccips/pub/qygsdetail/1219/"+self.encrpripid})['page']
            ls = json.loads(res)
            for i, l in enumerate(ls):
                czxx = l['czxx']
                rjxxs= l['rjxx']
                sjxxs= l['sjxx']
                item = {}
                sub_item = {}
                item[u'股东'] = czxx['inv']
                item[u'认缴额（万元）'] = czxx['lisubconam']
                item[u'实缴额（万元）'] = czxx['liacconam']
                if len(rjxxs) >0 and rjxxs[0]:
                    sub_item[u'认缴出资方式'] =  rjxxs[0]['conform']
                    sub_item[u'认缴出资额（万元）'] =rjxxs[0]['subconam']
                    date_dict = rjxxs[0]['condate']
                    #print type(date_dict['date'])   全是int型
                    sub_item[u'认缴出资日期'] =self.SetJsonTime(date_dict)
                else:
                    sub_item[u'认缴出资方式'] =""
                    sub_item[u'认缴出资额（万元）'] =""
                    sub_item[u'认缴出资日期'] = ""
                item[u'认缴明细'] = sub_item

                if len(sjxxs) > 0 and sjxxs[0]:
                    sub_item = {}
                    sub_item[u'实缴出资方式'] =sjxxs[0]['conform']
                    sub_item[u'实缴出资额（万元）'] =sjxxs[0]['acconam']
                    date_dict = sjxxs[0]['condate']
                    sub_item[u'实缴出资日期'] = self.SetJsonTime(date_dict)
                else:
                    sub_item[u'实缴出资方式'] =""
                    sub_item[u'实缴出资额（万元'] =""
                    sub_item[u'实缴出资日期'] = ""
                item[u'实缴明细'] = sub_item
                sub_json_list.append(item.copy())
        except Exception as e:
            logging.error(u"parse qygs table 股东及出资信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list

    #爬取 其他部门公示 页面
    def crawl_other_dept_pub_pages(self, url):
        """  爬取其他部门信息页面        """
        sub_json_dict = {}
        try:
            logging.info( u"crawl the crawl_other_dept_pub_pages page %s."%(url))
            page = self.crawl_page_by_url(url)['page']
            # html_to_file('next.html', page)
            #page = html_from_file('next.html')
            xk = self.parse_page(page, 'xingzhengxuke') #行政许可信息
            sub_json_dict["other_dept_pub_administration_license"] =  xk[u'行政许可信息'] if xk.has_key(u'行政许可信息') else []
            cf = self.parse_page(page, 'xingzhengchufa') #行政处罚信息
            sub_json_dict["other_dept_pub_administration_sanction"] = cf[u'行政处罚信息'] if cf.has_key(u'行政处罚信息') else []  # 行政处罚信息
        except Exception as e:
            logging.debug(u"An error ocurred in crawl_other_dept_pub_pages: %s"% (type(e)))
            raise e
        finally:
            return sub_json_dict

    def crawl_judical_assist_pub_pages(self, url):
        """爬取司法协助信息页面 """
        sub_json_dict = {}
        try:
            logging.info( u"crawl the crawl_judical_assist_pub_pages page %s."%(url))
            page = self.crawl_page_by_url(url)['page']
            #page = html_from_file('next.html')
            #html_to_file('next.html', page)
            xz = self.parse_table_share_freeze(page, 'sifaxiezhu')
            sub_json_dict['judical_assist_pub_equity_freeze'] = xz #xz[u'司法股权冻结信息'] if xz.has_key(u'司法股权冻结信息') else []
            xz = self.parse_page(page, 'sifagudong')
            sub_json_dict['judical_assist_pub_shareholder_modify'] = xz[u'司法股东变更登记信息'] if xz.has_key(u'司法股东变更登记信息') else []
        except Exception as e:
            logging.debug(u"An error ocurred in crawl_judical_assist_pub_pages: %s"% (type(e)))
            raise e
        finally:
            return sub_json_dict
    # 司法协助公示信息 - 司法股权冻结信息 table
    def parse_table_share_freeze(self, page, div_id =""):
        """工商公示信息 - 股东信息表 """
        sub_json_list = []
        try:
            logging.info(u"parse table 股东信息表")
            titles = [u"序号", u"被执行人", u"股权数额", u"执行法院", u"协助公示通知书文号", u"状态", u"详情"]
            m = re.compile(r"gqxxliststr\s*=\s*(\'.*?\');").search(page)
            if m:
                gqxxliststr = m.group()
                strs = re.compile(r"(\'.*?\')").search(gqxxliststr).group()
                if strs.strip("'"):
                    gqxxlist = json.loads(strs.strip("'"))  # 将字符串转换成list
                    for i, item in enumerate(gqxxlist):
                        link = urls['webroot'] + 'pub/sfgsgqxxdetail/'+ self.encrpripid+'/'+ self.enttype+'/' + str(item['pid']) + '/' + str(item['frozstate'])
                        link_page = self.crawl_page_by_url(link)['page']
                        link_data = self.parse_page(link_page, table_name+'_detail')
                        if item['enttype'].find('12')!= -1 or item['enttype'].find('52')!= -1 or item['enttype'].find('62')!= -1:
                            num = item['froam'] + u"万股"
                        else:
                            num = item['froam'] + u"万元"
                        state = u'冻结' if int(item['frozstate'])== 1 else u"解除冻结" if int(item['frozstate'])==2 else u'失效' if int(item['frozstate'])==3 else u""
                        datas = [i+1,  item['inv'], num,  item['froauth'], item['executeno'],state,  link_data]
                        sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse table 股东信息表 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    def get_raw_text_by_tag(self, tag):
        return tag.get_text().strip()
    def get_table_title(self, table_tag):
        if table_tag.find('tr'):
            if table_tag.find('tr').find_all('th')  :
                if len(table_tag.find('tr').find_all('th')) > 1 :
                    return None
                # 处理 <th> aa<span> bb</span> </th>
                if table_tag.find('tr').th.stirng == None and len(table_tag.find('tr').th.contents) > 1:
                    # 处理 <th>   <span> bb</span> </th>  包含空格的
                    if (table_tag.find('tr').th.contents[0]).strip()  :
                        return (table_tag.find('tr').th.contents[0]).strip()
                # <th><span> bb</span> </th>
                return self.get_raw_text_by_tag(table_tag.find('tr').th)
        return None
    def sub_column_count(self, th_tag):
        if th_tag.has_attr('colspan') and th_tag.get('colspan') > 1:
            return int(th_tag.get('colspan'))
        return 0
    def get_sub_columns(self, tr_tag, index, count):
        columns = []
        for i in range(index, index + count):
            th = tr_tag.find_all('th')[i]
            if not self.sub_column_count(th):
                columns.append(( self.get_raw_text_by_tag(th), self.get_raw_text_by_tag(th)))
            else:
            #if has sub-sub columns
                columns.append((self.get_raw_text_by_tag(th), self.get_sub_columns(tr_tag.nextSibling.nextSibling, 0, self.sub_column_count(th))))
        return columns
    #get column data recursively, use recursive because there may be table in table
    def get_column_data(self, columns, td_tag):
        if type(columns) == list:
            data = {}
            multi_col_tag = td_tag
            if td_tag.find('table'):
                multi_col_tag = td_tag.find('table').find('tr')
            if not multi_col_tag:
                logging.error('invalid multi_col_tag, multi_col_tag = %s', multi_col_tag)
                return data

            if len(columns) != len(multi_col_tag.find_all('td', recursive=False)):
                logging.error('column head size != column data size, columns head = %s, columns data = %s' % (columns, multi_col_tag.contents))
                return data

            for id, col in enumerate(columns):
                data[col[0]] = self.get_column_data(col[1], multi_col_tag.find_all('td', recursive=False)[id])
            return data
        else:
            return self.get_raw_text_by_tag(td_tag)
    def get_detail_link(self, bs4_tag):
        if bs4_tag.has_attr('href') and (bs4_tag['href'] != '#' and bs4_tag['href'] != 'javascript:void(0);'):
            pattern = re.compile(r'http')
            if pattern.search(bs4_tag['href']):
                return bs4_tag['href']
            return urls['root'] + bs4_tag['href']
        elif bs4_tag.has_attr('onclick'):
            #print 'onclick'
            logging.error(u"onclick attr was found in detail link")
        return None
    def get_columns_of_record_table(self, bs_table, page, table_name):
        tbody = None
        if len(bs_table.find_all('tbody')) > 1:
            tbody= bs_table.find_all('tbody')[0]
        else:
            tbody = bs_table.find('tbody') or BeautifulSoup(page, 'html5lib').find('tbody')

        tr = None
        if tbody:
            if len(tbody.find_all('tr')) <= 1:
                tr = tbody.find('tr')
            else:
                tr = tbody.find_all('tr')[1]
                if not tr.find('th'):
                    tr = tbody.find_all('tr')[0]
                elif tr.find('td'):
                    tr = None
        else:
            if len(bs_table.find_all('tr')) <= 1:
                return None
            elif bs_table.find_all('tr')[0].find('th') and not bs_table.find_all('tr')[0].find('td') and len(bs_table.find_all('tr')[0].find_all('th')) > 1:
                tr = bs_table.find_all('tr')[0]
            elif bs_table.find_all('tr')[1].find('th') and not bs_table.find_all('tr')[1].find('td') and len(bs_table.find_all('tr')[1].find_all('th')) > 1:
                tr = bs_table.find_all('tr')[1]
        ret_val=  self.get_record_table_columns_by_tr(tr, table_name)
        #logging.debug(u"ret_val->%s\n", ret_val)
        return  ret_val
    def get_record_table_columns_by_tr(self, tr_tag, table_name):
        columns = []
        if not tr_tag:
            return columns
        try:
            sub_col_index = 0
            if len(tr_tag.find_all('th'))==0 :
                logging.error(u"The table %s has no columns"% table_name)
                return columns
            count = 0
            if len(tr_tag.find_all('th'))>0 :
                for th in tr_tag.find_all('th'):
                    #logging.debug(u"th in get_record_table_columns_by_tr =\n %s", th)
                    col_name = self.get_raw_text_by_tag(th)
                    if col_name :
                        if ((col_name, col_name) in columns) :
                            col_name= col_name+'_'
                            count+=1
                        if not self.sub_column_count(th):
                            columns.append((col_name, col_name))
                        else: #has sub_columns
                            columns.append((col_name, self.get_sub_columns(tr_tag.nextSibling.nextSibling, sub_col_index, self.sub_column_count(th))))
                            sub_col_index += self.sub_column_count(th)
                if count == len(tr_tag.find_all('th'))/2:
                    columns= columns[: len(columns)/2]
        except Exception as e:
            logging.error(u'exception occured in get_table_columns, except_type = %s, table_name = %s' % (type(e), table_name))
        finally:
            return columns

    # 分析企业年报详细页面
    def parse_ent_pub_annual_report_page(self, page):
        sub_dict = {}
        try:
            soup = BeautifulSoup(page, 'html5lib')
            # 基本信息表包含两个表头, 需要单独处理
            basic_table = soup.find('table')
            trs = basic_table.find_all('tr')
            title = self.get_raw_text_by_tag(trs[1].th)
            print title
            table_dict = {}
            for tr in trs[2:]:
                if tr.find('th') and tr.find('td'):
                    ths = tr.find_all('th')
                    tds = tr.find_all('td')
                    if len(ths) != len(tds):
                        logging.error(u'th size not equals td size in table %s, what\'s up??' % table_name)
                        return
                    else:
                        for i in range(len(ths)):
                            if self.get_raw_text_by_tag(ths[i]):
                                table_dict[self.get_raw_text_by_tag(ths[i])] = self.get_raw_text_by_tag(tds[i])
            sub_dict[title] = table_dict

            #网站或网店信息
            titles = [u'类型', u'名称', u'网址']
            m = re.compile(r"wdxxliststr\s*=.*?;").search(page)

            if m:
                wdxxliststr = m.group()
                strs = re.compile(r"(\'.*?\')").search(wdxxliststr).group().strip("'")
                wdxxlist = json.loads(strs) if strs else []  # 将字符串转换成list
                sub_item = []
                for item in wdxxlist:
                    datas = [ u'网站' if str(item['webtype'])== '1' else u'网店', item['websitname'], item['domain'] ]
                    sub_item.append(dict(zip(titles, datas)))
                sub_dict[u"网站或网店信息"] = sub_item
            else:
                logging.error(u"cann't find 网站或网店信息 str in html")

            #股东及出资信息
            titles = [u'股东（发起人）', u'认缴出资额（万元）', u'认缴出资时间', u'认缴出资方式', u'实缴出资额（万元）', u'出资时间', u'出资方式']
            m = re.compile(r"czxxliststr\s*=\s*(\'.*?\')").search(page)
            if m:
                czxxliststr = m.group()
                strs = re.compile(r"(\'.*?\')").search(czxxliststr).group().strip("'")
                sub_item = []
                czxxlist = json.loads(strs) if strs else []  # 将字符串转换成list
                for item in czxxlist:
                    date_sub = item['subcondate']
                    date_acc = item['accondate']
                    datas = [ item['inv'], str(item['lisubconam'])+"万"+ self.currency(item['subconcurrency']), self.SetJsonTime(date_sub), item['subconform'].split('|')[1], \
                                 str(item['liacconam'])+"万" +self.currency(item['acconcurrency']), self.SetJsonTime(date_acc), item['acconform'].split('|')[1] ]
                    sub_item.append(dict(zip(titles, datas)))
                sub_dict[u"股东及出资信息"] = sub_item
            else:
                logging.error(u"cann't find 股东及出资信息 str in html")
            #对外投资信息
            titles = [u'投资设立企业或购买股权企业名称', u'注册号']
            m = re.compile(r"dwtzliststr\s*=\s*(\'.*?\');").search(page)
            if m:
                dwtzliststr = m.group()
                sub_item = []
                strs = re.compile(r"(\'.*?\')").search(dwtzliststr).group().strip("'")
                dwtzlist = json.loads(strs) if strs else []  # 将字符串转换成list
                for item in dwtzlist:
                    datas = [ item['entname'], item['regno']]
                    sub_item.append(dict(zip(titles, datas)))
                sub_dict[u"对外投资信息"] = sub_item
            else:
                logging.error(u"cann't find 对外投资信息 str in html")

            #对外提供保证担保信息
            titles = [u'债权人', u'债务人' ,u'主债权种类', u'主债权数额', u'履行债务的期限', u'保证的期间', u'保证的方式', u'保证担保的范围']
            m = re.compile(r"nbdwdbstr\s*=\s*(\'.*?\');").search(page)
            if m:
                nbdwdbstr = m.group()
                m1 = re.compile(r"(\'.*?\')").search(nbdwdbstr)
                sub_item = []
                if m1:
                    if m1.group().strip("'"):
                        dwdblist = json.loads(m1.group().strip("'"))  # 将字符串转换成list
                        for item in dwdblist:
                            datas = [ item['more'], item['mortgagor'],'合同' if int(item['priclaseckind'])==1 else '其他', item['priclasecam']+"万元", self.SetJsonTime(item['pefperfrom']) +" - "+ self.SetJsonTime(item['pefperto']),\
                                     "期限" if int(item['guaranperiod'])==1 else "未约定", "一般保证" if int(item['gatype'])==1 else "连带保证" if int(item['gatype'])==2 else "未约定", self.getRange(item['rage'])]
                            sub_item.append(dict(zip(titles, datas)))
                sub_dict[u"对外提供保证担保信息"] = sub_item
            else:
                logging.error(u"cann't find 对外提供保证担保信息 str in html")

            #股权变更信息
            titles = [u'股东（发起人）', u'变更前股权比例' ,u'变更后股权比例', u'股权变更日期']
            m = re.compile(r"nbgqbgsstr\s*=\s*(\'.*?\');").search(page)
            if m:
                nbgqbgsstr = m.group()
                m1 = re.compile(r"(\'.*?\')").search(nbgqbgsstr)
                sub_item = []
                if m1:
                    if m1.group().strip("'"):
                        gqbglist = json.loads(m1.group().strip("'"))  # 将字符串转换成list
                        for item in gqbglist:
                            datas = [ item['inv'], item['transamprpre'], item['transampraf'] ,self.SetJsonTime(item['altdate'])]
                            sub_item.append(dict(zip(titles, datas)))
                sub_dict[u"股权变更信息"] = sub_item
            else:
                logging.error(u"cann't find 股权变更信息 str in html")
            #修改记录
            titles = [u'序号', u'修改事项' ,u'修改前', u'修改后', u'修改日期']
            m = re.compile(r"nbalthisstr\s*=\s*(\'.*?\');").search(page)
            if m:
                nbalthisstr = m.group()
                m1 = re.compile(r"(\'.*?\')").search(nbalthisstr)
                sub_item = []
                if m1:
                    if m1.group().strip("'"):
                        althistlist = json.loads(m1.group().strip("'"))  # 将字符串转换成list
                        for item in althistlist:
                            datas = [i+1,  item['altfield'], item['altbefore'], item['altafter'], self.SetJsonTime(item['altdate']) ]
                            sub_item.append(dict(zip(titles, datas)))
                sub_dict[u"修改记录"] = sub_item
            else:
                logging.error(u"cann't find 修改记录 str in html")


            content_table = soup.find_all('table')[1:]
            for table in content_table:
                table_name = self.get_table_title(table)
                if table_name:
                    if table_name == u"企业资产状况信息":
                        table_data = self.parse_table(table, table_name, page)
                        sub_dict[table_name] = table_data
        except Exception as e:
            logging.error(u'annual page: fail to get table data with exception %s' % e)
            raise e
        finally:
            return sub_dict

    def parse_page(self, page, div_id='sifapanding'):
        soup = BeautifulSoup(page, 'html5lib')
        page_data = {}

        try:
            div = soup.find('div', attrs = {'id':div_id})
            if div:
                tables = div.find_all('table')
            else:
                tables = soup.find_all('table')
            #print table
            for table in tables:
                table_name = self.get_table_title(table)
                if table_name:
                    page_data[table_name] = self.parse_table(table, table_name, page)
        except Exception as e:
            logging.error(u'parse page failed, with exception %s' % e)
            raise e
        finally:
            return page_data

    def parse_table(self, bs_table, table_name, page):
        table_dict = None
        try:
            # tb_title = self.get_table_title(bs_table)
            #this is a fucking dog case, we can't find tbody-tag in table-tag, but we can see tbody-tag in table-tag
            #in case of that, we use the whole html page to locate the tbody
            print table_name
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            tbody = None
            if len(bs_table.find_all('tbody'))>1:
                tbody = bs_table.find_all('tbody')[1]
            else:
                tbody = bs_table.find('tbody') or BeautifulSoup(page, 'html5lib').find('tbody')
            if columns:
                col_span = 0
                single_col = 0
                for col in columns:
                    if type(col[1]) == list:
                        col_span += len(col[1])
                    else:
                        single_col+=1
                        col_span += 1

                column_size = len(columns)
                item_array = []
                if not tbody:
                    records_tag = bs_table
                else:
                    records_tag = tbody
                item = None
                for tr in records_tag.find_all('tr'):
                    if tr.find_all('td') and len(tr.find_all('td', recursive=False)) % column_size == 0:
                        col_count = 0
                        item = {}
                        for td in tr.find_all('td',recursive=False):
                            if td.find('a'):
                                #try to retrieve detail link from page
                                next_url = self.get_detail_link(td.find('a'))
                                logging.info(u'crawl detail url: %s'% next_url)
                                if next_url:
                                    detail_page = self.crawl_page_by_url(next_url)
                                    #html_to_file("test.html", detail_page['page'])
                                    #print "table_name : "+ table_name
                                    if table_name == u'企业年报':
                                        #logging.debug(u"next_url = %s, table_name= %s\n", detail_page['url'], table_name)
                                        page_data = self.parse_ent_pub_annual_report_page(detail_page['page'])

                                        item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                        item[u'详情'] =  page_data #this may be a detail page data
                                    else:
                                        page_data = self.parse_page(detail_page['page'])
                                        item[columns[col_count][0]] = page_data #this may be a detail page data
                                else:
                                    #item[columns[col_count]] = CrawlerUtils.get_raw_text_in_bstag(td)
                                    item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                            else:
                                item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                            col_count += 1
                            if col_count == column_size:
                                item_array.append(item.copy())
                                col_count = 0
                    #this case is for the ind-comm-pub-reg-shareholders----details'table
                    #a fucking dog case!!!!!!
                    elif tr.find_all('td') and len(tr.find_all('td', recursive=False)) == col_span and col_span != column_size:
                        col_count = 0
                        sub_col_index = 0
                        item = {}
                        sub_item = {}
                        for td in tr.find_all('td',recursive=False):
                            if type(columns[col_count][1]) == list:
                                sub_key = columns[col_count][1][sub_col_index][1]
                                sub_item[sub_key] = self.get_raw_text_by_tag(td)
                                sub_col_index += 1
                                if sub_col_index == len(columns[col_count][1]):
                                    item[columns[col_count][0]] = sub_item.copy()
                                    sub_item = {}
                                    col_count += 1
                                    sub_col_index = 0
                            else:
                                item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                col_count += 1
                            if col_count == column_size:
                                item_array.append(item.copy())
                                col_count = 0
                table_dict = item_array
            else:
                table_dict = {}

                for tr in bs_table.find_all('tr'):
                    if tr.find('th') and tr.find('td'):
                        ths = tr.find_all('th')
                        tds = tr.find_all('td')
                        if len(ths) != len(tds):
                            logging.error(u'th size not equals td size in table %s, what\'s up??' % table_name)
                            return
                        else:
                            for i in range(len(ths)):
                                if self.get_raw_text_by_tag(ths[i]):
                                    table_dict[self.get_raw_text_by_tag(ths[i])] = self.get_raw_text_by_tag(tds[i])
        except Exception as e:
            logging.error(u'parse table %s failed with exception %s' % (table_name, type(e)))
            raise e
        finally:
            return table_dict

    def crawl_page_by_url(self, url , cookie={}, header={}):
        try:
            r = self.requests.get( url, cookies= {'ROBOTCOOKIEID': self.ROBOTCOOKIEID}, headers= header)
            if r.status_code != 200:
                logging.error(u"Getting page by url:%s, return status %s\n"% (url, r.status_code))
            text = r.text
            urls = r.url
            # 为了防止页面间接跳转，获取最终目标url
        except Exception as e:
            logging.error(u"Cann't get page by url:%s, exception is %s"%(url, type(e)))
        finally:
            return {'page' : text, 'url': urls}

    def crawl_page_by_url_post(self, url, data, header={}):
        try:
            self.requests.headers.update(header)
            r = self.requests.post(url, data =data, cookies= {'ROBOTCOOKIEID': self.ROBOTCOOKIEID})
            if r.status_code != 200:
                logging.error(u"Getting page by url with post:%s, return status %s\n"% (url, r.status_code))
            text = r.text
            urls = r.url
        except Exception as e:
            logging.error(u"Cann't post page by url:%s, exception is %s"%(url, type(e)))
        finally:
            return {'page': text, 'url': urls}

    def run(self, ent_num):
        if not os.path.exists(self.html_restore_path):
            os.makedirs(self.html_restore_path)
        json_dict = {}
        self.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], ent_num)
        data = self.crawl_page_main()
        json_dict[ent_num] = data
        return json.dumps(json_dict)
        # json_dump_to_file(self.json_restore_path , json_dict)

    def work(self, ent_num= ""):

        # if not os.path.exists(self.html_restore_path):
        #     os.makedirs(self.html_restore_path)
        self.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], ent_num)
        data = self.crawl_page_main()
        json_dump_to_file('jilin_json.json', data)
        # 测试
        # url = "http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=u9Abs75MdJjl94Li4fXsN.dDmlDUrpmY&tab=06"
        # data = self.crawl_judical_assist_pub_pages(url)
        # json_dump_to_file('jilin_json.json', data)

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

def html_from_file(path):
    if not os.path.exists(path):
        return
    a = ""
    with codecs.open(path, 'r') as f:
        a = f.read()
    return a

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
    if not os.path.exists("./enterprise_crawler"):
        os.makedirs("./enterprise_crawler")
    jilin = JilinCrawler('./enterprise_crawler/jilin.json')
    jilin.work('220214000015448')


if __name__ == "__main__":
    reload (sys)
    sys.setdefaultencoding('utf-8')
    import run
    run.config_logging()
    if not os.path.exists("./enterprise_crawler"):
        os.makedirs("./enterprise_crawler")
    jilin = JilinCrawler('./enterprise_crawler/jilin.json')
    ents = read_ent_from_file("./enterprise_list/jilin.txt")
    jilin = JilinCrawler('./enterprise_crawler/jilin.json')
    for ent_str in ents:
        logging.info(u'###################   Start to crawl enterprise with id %s   ###################\n' % ent_str[2])
        jilin.run(ent_num = ent_str[2])
        logging.info(u'###################   Enterprise with id  %s Finished!  ###################\n' % ent_str[2])
"""
