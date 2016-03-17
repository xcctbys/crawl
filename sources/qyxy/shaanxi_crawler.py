#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import logging
import os
import sys
import time
import re
import importlib
ENT_CRAWLER_SETTINGS = os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS:
    settings = importlib.import_module(ENT_CRAWLER_SETTINGS)
else:
    import settings

import json
import codecs
import unittest
import threading
from bs4 import BeautifulSoup
import CaptchaRecognition as CR
import random

urls = {
    'host': 'http://xygs.snaic.gov.cn/',
    'webroot' : 'http://xygs.snaic.gov.cn/',
    'page_search': 'http://xygs.snaic.gov.cn/ztxy.do?method=index&random=%d',
    'page_Captcha': 'http://xygs.snaic.gov.cn/ztxy.do?method=createYzm&dt=%d&random=%d',
    'page_showinfo': 'http://xygs.snaic.gov.cn/ztxy.do?method=list&djjg=&random=%d',
    'checkcode': 'http://xygs.snaic.gov.cn/ztxy.do?method=list&djjg=&random=%d',
}

headers = { 'Connetion': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36",
            }

class ShaanxiCrawler(object):
    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    def __init__(self, json_restore_path):
        self.CR = CR.CaptchaRecognition("shaanxi")
        self.requests = requests.Session()
        self.requests.headers.update(headers)
        self.ents = []
        self.json_restore_path = json_restore_path
        self.pripid = ""
        #验证码图片的存储路径
        self.path_captcha = settings.json_restore_path + '/shaanxi/ckcode.jpeg'
        #html数据的存储路径
        self.html_restore_path = settings.html_restore_path + '/shaanxi/'


    # 破解搜索页面
    def crawl_page_search(self, url):
        r = self.requests.get( url)
        if r.status_code != 200:
            settings.logger.error(u"Something wrong when getting the url:%s , status_code=%d", url, r.status_code)
            return
        r.encoding = "utf-8"
        #settings.logger.debug("searchpage html :\n  %s", r.text)
        return r.text

    def analyze_showInfo(self, page):
        """ 判断是否成功搜索页面
            分析 展示页面， 获得搜索到的企业列表
        """
        Ent = []
        soup = BeautifulSoup(page, "html5lib")
        divs = soup.find_all("div", {"style":"width:950px; padding:25px 20px 0px; overflow: hidden;float: left;"})
        if divs:
            for div in divs:
                if div and div.ul and div.ul.li and div.ul.li.a and div.ul.li.a.has_attr('onclick'):
                    a= div.ul.li.a
                    Ent.append(a['onclick'])
        if not Ent:
            return False
        self.ents = Ent
        return True

    #
    def crawl_page_captcha(self, url_search, url_Captcha, url_CheckCode,url_showInfo,  textfield= '610000100026931'):
        """破解验证码页面"""
        randoms = int(time.time())
        html_search = self.crawl_page_search(url_search%randoms)
        if not html_search:
            settings.logger.error(u"There is no search page")
        soup = BeautifulSoup(html_search, 'html5lib')
        form = soup.find_all('input', {'name': True})
        datas = {}
        datas['maent.entname'] = textfield
        count = 0
        while True:
            count+= 1
            r = self.requests.get( url_Captcha%(randoms, randoms))
            if r.status_code != 200:
                settings.logger.error(u"Something wrong when getting the Captcha url:%s , status_code=%d", url_Captcha%randoms, r.status_code)
                return
            #settings.logger.debug("Captcha page html :\n  %s", self.Captcha)
            if self.save_captcha(r.content):
                settings.logger.info("Captcha is saved successfully \n" )
                result = self.crack_captcha()
                print result
                datas['yzm'] = result
                page=  self.crawl_page_by_url_post(url_CheckCode%randoms, datas)['page']
                # 如果验证码正确，就返回一种页面，否则返回主页面
                if self.analyze_showInfo(page):
                    break
                else:
                    settings.logger.debug(u"crack Captcha failed, the %d time(s)", count)
                    if count>15:
                        break
        return



    #调用函数，破解验证码图片并返回结果
    def crack_captcha(self):
        if os.path.exists(self.path_captcha) is False:
            settings.logger.error(u"Captcha path is not found\n")
            return
        result = self.CR.predict_result(self.path_captcha)
        return result[1]
        #print result
    # 保存验证码图片
    def save_captcha(self, Captcha):
        url_Captcha = self.path_captcha
        if Captcha is None:
            settings.logger.error(u"Can not store Captcha: None\n")
            return False
        self.write_file_mutex.acquire()
        f = open(url_Captcha, 'w')
        try:
            f.write(Captcha)
        except IOError:
            settings.logger.debug("%s can not be written", url_Captcha)
        finally:
            f.close
        self.write_file_mutex.release()
        return True
    """
        The following enterprises in ents
        2. for each ent: decide host so that choose e urls
        4. for eah url, iterate item in tabs
    """
    def crawl_page_main(self ):
        sub_json_dict= {}
        if not self.ents:
            settings.logger.error(u"Get no search result\n")
        try:
            for ent in self.ents:
                #settings.logger.info(u"crawl main url:%s"% ent)
                params = re.findall(r'\'(.*?)\'', ent)
                url = "http://xygs.snaic.gov.cn/ztxy.do"
                pripid, enttype, others= params
                self.pripid = pripid
                sub_json_dict.update(self.crawl_ind_comm_pub_pages(url, {
                    'maent.pripid': pripid,
                    'maent.entbigtype' : enttype,
                    'random' : int(time.time()),
                    'djjg' : "",
                }))
                sub_json_dict.update(self.crawl_ent_pub_pages(url, {'maent.pripid': pripid,'random' : int(time.time())}))
                sub_json_dict.update(self.crawl_other_dept_pub_pages(url, {'maent.pripid': pripid,'random' : int(time.time())}))
                sub_json_dict.update(self.crawl_judical_assist_pub_pages(url, {'maent.pripid': pripid,'random' : int(time.time())}))

        except Exception as e:
            settings.logger.error(u"An error ocurred when getting the main page, error: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #工商公式信息页面
    def crawl_ind_comm_pub_pages(self, url="", post_data={}):
        sub_json_dict={}
        try:
            #settings.logger.info( u"crawl the crawl_ind_comm_pub_pages page %s."%(url))
            post_data['method'] = 'qyInfo'
            post_data['czmk'] = 'czmk1'
            post_data['from'] = ''
            page = self.crawl_page_by_url_post(url, post_data)['page']
            #page = html_from_file('next.html')
            #html_to_file('next.html', page)
            page = page.replace('</br', '')
            dj = self.parse_page(page, 'jibenxinxi') #
            sub_json_dict['ind_comm_pub_reg_basic'] = dj[u'基本信息'] if dj.has_key(u'基本信息') else []        # 登记信息-基本信息
            sub_json_dict['ind_comm_pub_reg_shareholder'] =dj[u'股东信息'] if dj.has_key(u'股东信息') else []   # 股东信息
            dj = self.parse_page(page, 'biangeng')
            sub_json_dict['ind_comm_pub_reg_modify'] =  dj[u'变更信息'] if dj.has_key(u'变更信息') else []      # 变更信息
            post_data['czmk'] = 'czmk2'
            post_data['method'] = 'baInfo'
            page = self.crawl_page_by_url_post(url, post_data)['page']
            page = page.replace('</br', '')
            ba = self.parse_page(page, 'beian')
            sub_json_dict['ind_comm_pub_arch_key_persons'] = ba[u'主要人员信息'] if ba.has_key(u'主要人员信息') else []   # 备案信息-主要人员信息
            sub_json_dict['ind_comm_pub_arch_branch'] = ba[u'分支机构信息'] if ba.has_key(u'分支机构信息') else []       # 备案信息-分支机构信息
            sub_json_dict['ind_comm_pub_arch_liquidation'] = ba[u'清算信息'] if ba.has_key(u'清算信息') else []   # 备案信息-清算信息
            post_data['czmk'] = 'czmk4'
            post_data['method'] = 'dcdyInfo'
            page = self.crawl_page_by_url_post(url, post_data)['page']
            dcdy = self.parse_page(page, 'dongchandiya')
            sub_json_dict['ind_comm_pub_movable_property_reg'] = dcdy[u'动产抵押登记信息'] if dcdy.has_key(u'动产抵押登记信息') else []
            post_data['czmk'] = 'czmk4'
            post_data['method'] = 'gqczxxInfo'
            page = self.crawl_page_by_url_post(url, post_data)['page']
            gqcz = self.parse_page(page, 'guquanchuzhi')
            sub_json_dict['ind_comm_pub_equity_ownership_reg'] = gqcz[u'股权出质登记信息'] if gqcz.has_key(u'股权出质登记信息') else []
            post_data['czmk'] = 'czmk3'
            post_data['method'] = 'cfInfo'
            page = self.crawl_page_by_url_post(url, post_data)['page']
            xzcf = self.parse_page(page, 'gsgsxx_xzcf')
            sub_json_dict['ind_comm_pub_administration_sanction'] = xzcf[u'行政处罚信息'] if xzcf.has_key(u'行政处罚信息') else []
            post_data['czmk'] = 'czmk6'
            post_data['method'] = 'jyycInfo'
            page = self.crawl_page_by_url_post(url, post_data)['page']
            jyyc= self.parse_page(page, 'yichangminglu')
            sub_json_dict['ind_comm_pub_business_exception'] = jyyc[u'经营异常信息'] if jyyc.has_key(u'经营异常信息') else []
            post_data['czmk'] = 'czmk14'
            post_data['method'] = 'yzwfInfo'
            page = self.crawl_page_by_url_post(url, post_data)['page']
            yzwf = self.parse_page(page, 'yanzhongweifa')
            sub_json_dict['ind_comm_pub_serious_violate_law'] = yzwf[u'严重违法信息'] if yzwf.has_key(u'严重违法信息') else []
            post_data['czmk'] = 'czmk7'
            post_data['method'] = 'ccjcInfo'
            page = self.crawl_page_by_url_post(url, post_data)['page']
            cyjc= self.parse_page(page, 'chouchaxinxi')
            sub_json_dict['ind_comm_pub_spot_check'] = cyjc[u'抽查检查信息'] if cyjc.has_key(u'抽查检查信息') else []
        except Exception as e:
            settings.logger.debug(u"An error ocurred in crawl_ind_comm_pub_pages: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #爬取 企业公示信息 页面
    def crawl_ent_pub_pages(self, url= "", post_data={}):
        sub_json_dict = {}
        try:
            #settings.logger.info( u"crawl the crawl_ent_pub_pages page %s."%(url))
            post_data['method'] = 'qygsInfo'
            post_data['czmk'] = 'czmk8'
            page = self.crawl_page_by_url_post(url, post_data)['page']
            nb = self.parse_page(page, 'qynb')
            sub_json_dict['ent_pub_ent_annual_report'] = nb[u'企业年报'] if nb.has_key(u'企业年报') else []
            post_data['method'] = 'qygsForXzxkInfo'
            post_data['czmk'] = 'czmk10'
            page = self.crawl_page_by_url_post(url, post_data)['page']
            xk = self.parse_page(page, 'xzxk')
            sub_json_dict['ent_pub_administration_license'] = xk[u'行政许可信息'] if xk.has_key(u'行政许可信息') else []
            post_data['method'] = 'qygsForXzcfInfo'
            post_data['czmk'] = 'czmk13'
            page = self.crawl_page_by_url_post(url, post_data)['page']
            cf = self.parse_page(page, 'xzcf')
            sub_json_dict['ent_pub_administration_sanction'] = cf[u'行政处罚信息'] if cf.has_key(u'行政处罚信息') else []
            post_data['method'] = 'qygsForTzrxxInfo'
            post_data['czmk'] = 'czmk12'
            page = self.crawl_page_by_url_post(url, post_data)['page']
            tzr= self.parse_page(page, 'tzrxx')
            sub_json_dict['ent_pub_shareholder_capital_contribution'] = tzr[u'股东及出资信息'] if tzr.has_key(u'股东及出资信息') else []
            sub_json_dict['ent_pub_reg_modify'] = tzr[u'变更信息'] if tzr.has_key(u'变更信息') else []
            post_data['method'] = 'qygsForTzrbgxxInfo'
            post_data['czmk'] = 'czmk15'
            page = self.crawl_page_by_url_post(url, post_data)['page']
            gq = self.parse_page(page, 'tzrbgxx')
            sub_json_dict['ent_pub_equity_change'] = gq[u'股权变更信息'] if gq.has_key(u'股权变更信息') else []
            post_data['method'] = 'qygsForZzcqInfo'
            post_data['czmk'] = 'czmk11'
            page = self.crawl_page_by_url_post(url, post_data)['page']
            zscq = self.parse_page(page, 'zzcq')
            sub_json_dict['ent_pub_knowledge_property'] = zscq[u'知识产权出质登记信息'] if zscq.has_key(u'知识产权出质登记信息') else []
        except Exception as e:
            settings.logger.debug(u"An error ocurred in crawl_ent_pub_pages: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #爬取 其他部门公示 页面
    def crawl_other_dept_pub_pages(self, url="", post_data={}):
        """爬取 其他部门公示 页面"""
        sub_json_dict = {}
        try:
            #settings.logger.info( u"crawl the crawl_other_dept_pub_pages page %s."%(url))
            post_data['method'] = 'qtgsInfo'
            post_data['czmk'] = 'czmk9'
            page = self.crawl_page_by_url_post(url, post_data)['page']
            xk = self.parse_page(page, "xingzhengxuke")#行政许可信息
            sub_json_dict["other_dept_pub_administration_license"] =  xk[u'行政许可信息'] if xk.has_key(u'行政许可信息') else []
            post_data['method'] = 'qtgsForCfInfo'
            post_data['czmk'] = 'czmk16'
            page = self.crawl_page_by_url_post(url, post_data)['page']
            cf = self.parse_page(page, "xingzhengchufa")  # 行政处罚信息
            sub_json_dict["other_dept_pub_administration_sanction"] = cf[u'行政处罚信息'] if cf.has_key(u'行政处罚信息') else []
        except Exception as e:
            settings.logger.debug(u"An error ocurred in crawl_other_dept_pub_pages: %s"% (type(e)))
            raise e
        finally:
            return sub_json_dict
    # 爬取司法协助信息页面
    def crawl_judical_assist_pub_pages(self, url="", post_data={}):
        """爬取司法协助信息页面 """
        sub_json_dict = {}
        try:
            #settings.logger.info( u"crawl the crawl_judical_assist_pub_pages page %s."%(url))
            post_data['method'] = 'sfgsInfo'
            post_data['czmk'] = 'czmk17'
            page = self.crawl_page_by_url_post(url, post_data)['page']
            xz = self.parse_page(page, 'guquandongjie')
            sub_json_dict['judical_assist_pub_equity_freeze'] = xz[u'司法股权冻结信息'] if xz.has_key(u'司法股权冻结信息') else []
            post_data['method'] = 'sfgsbgInfo'
            post_data['czmk'] = 'czmk18'
            page = self.crawl_page_by_url_post(url, post_data)['page']
            gd = self.parse_page(page, 'gudongbiangeng')
            sub_json_dict['judical_assist_pub_shareholder_modify'] = gd[u'司法股东变更登记信息'] if gd.has_key(u'司法股东变更登记信息') else []
        except Exception as e:
            settings.logger.debug(u"An error ocurred in crawl_judical_assist_pub_pages: %s"% (type(e)))
            raise e
        finally:
            return sub_json_dict


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
                settings.logger.error('invalid multi_col_tag, multi_col_tag = %s', multi_col_tag)
                return data

            if len(columns) != len(multi_col_tag.find_all('td', recursive=False)):
                settings.logger.error('column head size != column data size, columns head = %s, columns data = %s' % (columns, multi_col_tag.contents))
                return data

            for id, col in enumerate(columns):
                data[col[0]] = self.get_column_data(col[1], multi_col_tag.find_all('td', recursive=False)[id])
            return data
        else:
            td_text = self.get_raw_text_by_tag(td_tag)
            if td_text.find('\n\t\t\t        \t\t\t\t\t\t'):
                return td_text.split('\n\t\t\t        \t\t\t\t\t\t')[0].strip()
            return td_text


    def get_detail_link(self, bs4_tag):
        if bs4_tag.has_attr('href') and (bs4_tag['href'] != '###' and bs4_tag['href'] != '#' and bs4_tag['href'] != 'javascript:void(0);'):
            pattern = re.compile(r'http')
            if pattern.search(bs4_tag['href']):
                return bs4_tag['href']
            return urls['webroot'] + bs4_tag['href']
        elif bs4_tag.has_attr('onclick'):
            #print 'onclick'
            astr = bs4_tag['onclick']
            if re.compile(r'showRyxx').search(astr):
                m = re.findall("(\'.*?\')", astr)
                if m:
                    ryId, nbxh = [s.strip("'") for s in m]
                    return urls['host']+ "ztxy.do?method=tzrCzxxDetial&maent.xh="+ryId+"&maent.pripid="+nbxh+"&random=" + str(int(time.time()))
            elif re.compile(r'doNdbg').search(astr):
                m = re.compile(r'\d+').search(astr)
                if m:
                    year = eval(m.group())
                    return urls['host'] + "ztxy.do?method=ndbgDetail&maent.pripid="+self.pripid+"&maent.nd="+str(year)+"&random="+ str(int(time.time()))
            elif re.compile(r'doXkxkDetail').search(astr):
                m = re.findall(r'(\'.*?\')', astr)
                if m:
                    nbxh, xh, lx = [s.strip("'") for s in m]
                    return urls['host'] + "ztxy.do?method=doXkxkDetail&maent.pripid="+nbxh+"&maent.xh="+xh+"&maent.lx="+lx+"&random="+ str(int(time.time()))
            elif re.compile(r'doZscqDetail').search(astr):
                m = re.findall(r'(\'.*?\')', astr)
                if m:
                    xh, lx = [s.strip("'") for s in m]
                    return urls['host']+"ztxy.do?method=zscqDetail&maent.pripid="+self.pripid+"&maent.xh="+xh+"&maent.lx="+lx+"&random="+ str(int(time.time()))
            elif re.compile(r'doGqZxDetail').search(astr):
                m = re.findall(r'(\'.*?\')', astr)
                if m:
                    licid= [s.strip("'") for s in m]
                    return urls['host']+"ztxy.do?method=gqczxxZxDetail&maent.pripid="+self.pripid+"&maent.lx=X&maent.xh="+licid+"&random="+str(int(time.time()))
            elif re.compile(r'doGqCxDetail').search(astr):
                m = re.findall(r'(\'.*?\')', astr)
                if m:
                    licid= [s.strip("'") for s in m]
                    return urls['host']+"ztxy.do?method=gqczxxZxDetail&maent.pripid="+self.pripid+"&maent.lx=C&maent.xh="+licid+"&random="+str(int(time.time()))
            elif re.compile(r'doGqcx').search(astr):
                m = re.findall(r'(\'.*?\')', astr)
                if m:
                    licid= [s.strip("'") for s in m]
                    return urls['host']+ "ztxy.do?method=gqczxxDetail&maent.pripid="+self.pripid+"&maent.xh="+licid+"&random="+ str(int(time.time()))
            elif re.compile(r'doXzfyDetail').search(astr):
                m = re.findall(r'(\'.*?\')', astr)
                if m:
                    nbxh,ajbh= [s.strip("'") for s in m]
                    return urls['host'] + "ztxy.do?method=doXzfyDetail&maent.pripid="+nbxh+"&maent.xh="+ajbh+"&random=" + str(int(time.time()))
            elif re.compile(r'_doSfgqbgDetail').search(astr):
                m = re.findall(r'(\'.*?\')', astr)
                if m:
                    ids= [s.strip("'") for s in m]
                    return urls['host']+"ztxy.do?method=doGqdjbgDetail&maent.pripid="+ self.pripid+"&maent.xh="+ids+"&random=" + str(int(time.time()))
            elif re.compile(r'_doSfgqdjDetail').search(astr):
                m = re.findall(r'(\'.*?\')', astr)
                if m:
                    ids= [s.strip("'") for s in m]
                    return urls['host']+ "ztxy.do?method=doGqdjDetail&maent.pripid="+self.pripid+"&maent.xh="+ids+"&random=" + str(int(time.time()))
            elif re.compile(r'_doXzxkDetail').search(astr):
                m = re.findall(r'(\'.*?\')', astr)
                if m:
                    xh = [s.strip("'") for s in m]
                    return urls['host']+ "ztxy.do?method=doXzxkDetail&maent.pripid="+self.pripid+"&maent.xh="+xh+"&random="+ str(int(time.time()))
            elif re.compile(r'_doXzcfDetail').search(astr):
                m = re.findall(r'(\'.*?\')', astr)
                if m:
                    xh = [s.strip("'") for s in m]
                    return urls['host'] + "ztxy.do?method=doXzcfDetail&maent.pripid="+self.pripid+"&maent.xh="+xh+"&random=" + str(int(time.time()))
            elif re.compile(r'qtgsxxDetail').search(astr):
                m = re.findall(r'(\'.*?\')', astr)
                if m:
                    newsid,flag = [s.strip("'") for s in m]
                    return urls['host']+"ztxy.do?method=qtgsxxDetail&newsid="+newsid+"&flag="+flag+"&random=" + str(int(time.time()))
            else:
                pass
            settings.logger.error(u"onclick attr was found in detail link")
        return None


    def get_columns_of_record_table(self, bs_table, page, table_name):
        tbody = None
        if len(bs_table.find_all('tbody')) > 1:
            tbody= bs_table.find_all('tbody')[0]
        else:
            tbody = bs_table.find('tbody') or BeautifulSoup(page, 'html5lib').find('tbody')
        tr = None
        # print tbody
        if tbody:
            if len(tbody.find_all('tr')) <= 1:
                tr = tbody.find_all('tr')[1]
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
            # 主要人员信息 表，列名称没有<tr> </tr>
            elif bs_table.find_all('th', recursive = False):
                trstr = "<tr>\n"
                for th in bs_table.find_all('th', recursive = False):
                    # 这里的th 类型为<class 'bs4.element.Tag'>， 需要转换
                    trstr += str(th)+"\n"
                trstr += "</tr>"
                tr = BeautifulSoup(trstr, 'html.parser')
        ret_val=  self.get_record_table_columns_by_tr(tr, table_name)
        return  ret_val

    def get_record_table_columns_by_tr(self, tr_tag, table_name):
        columns = []
        if not tr_tag:
            return columns
        try:
            sub_col_index = 0
            if len(tr_tag.find_all('th'))==0 :
                settings.logger.error(u"The table %s has no columns"% table_name)
                return columns
            count = 0
            if len(tr_tag.find_all('th'))>0 :
                for th in tr_tag.find_all('th'):
                    #settings.logger.debug(u"th in get_record_table_columns_by_tr =\n %s", th)
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
            settings.logger.error(u'exception occured in get_table_columns, except_type = %s, table_name = %s' % (type(e), table_name))
        finally:
            return columns

    def parse_ent_pub_annual_report_page(self, page):
        """分析企业年报详细页面"""
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

            content_table = soup.find_all('table')[1:]
            for table in content_table:
                table_name = self.get_table_title(table)
                if table_name:
                    sub_dict[table_name] = self.parse_table(table, table_name, page)
        except Exception as e:
            settings.logger.error(u'annual page: fail to get table data with exception %s' % e)
            raise e
        finally:
            return sub_dict

    def parse_page(self, page, div_id='sifapanding', post_data= {}):
        soup = BeautifulSoup(page, 'html5lib')
        page_data = {}
        try:
            div = soup.find('div', {'id' : div_id})
            # print div
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
            settings.logger.error(u'parse page failed, with exception %s' % e)
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
            # print columns
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
                            if td.find('a', recursive = False):
                                #try to retrieve detail link from page
                                next_url = self.get_detail_link(td.find('a'))
                                # print next_url
                                settings.logger.info(u'crawl detail url: %s'% next_url)
                                if next_url:
                                    detail_page = self.crawl_page_by_url(next_url)
                                    #html_to_file("test.html", detail_page['page'])
                                    #print "table_name : "+ table_name
                                    if table_name == u'企业年报':
                                        #settings.logger.debug(u"next_url = %s, table_name= %s\n", detail_page['url'], table_name)
                                        page_data = self.parse_ent_pub_annual_report_page(detail_page['page'])

                                        item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                        item[u'详情'] = page_data #this may be a detail page data
                                    else:
                                        page_data = self.parse_page(detail_page['page'])
                                        item[columns[col_count][0]] = page_data #this may be a detail page data
                                else:
                                    #item[columns[col_count]] = CrawlerUtils.get_raw_text_in_bstag(td)
                                    item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                            else:
                                # 更多和 收起更多的按钮
                                if len(td.find_all('span')) == 2:
                                    span = td.find_all('span')[1]
                                    span.a.clear()# 删除a标签的内容
                                    item[columns[col_count][0]] = self.get_raw_text_by_tag(span)
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
                            settings.logger.error(u'th size not equals td size in table %s, what\'s up??' % table_name)
                            return
                        else:
                            for i in range(len(ths)):
                                if self.get_raw_text_by_tag(ths[i]):
                                    table_dict[self.get_raw_text_by_tag(ths[i])] = self.get_raw_text_by_tag(tds[i])
        except Exception as e:
            settings.logger.error(u'parse table %s failed with exception %s' % (table_name, type(e)))
            raise e
        finally:
            return table_dict


    def crawl_page_by_url(self, url):
        try:
            r = self.requests.get( url)
            if r.status_code != 200:
                settings.logger.error(u"Getting page by url:%s, return status %s\n"% (url, r.status_code))
            text = r.text
            urls = r.url
            # 为了防止页面间接跳转，获取最终目标url
        except Exception as e:
            settings.logger.error(u"Cann't get page by url:%s, exception is %s"%(url, type(e)))
        finally:
            return {'page' : text, 'url': urls}

    def crawl_page_by_url_post(self, url, data, headers={}):
        try:
            if headers:
                self.requests.headers.update(headers)
                r = self.requests.post(url, data)
            else :
                r = self.requests.post(url, data)
            if r.status_code != 200:
                settings.logger.error(u"Getting page by url with post:%s, return status %s\n"% (url, r.status_code))
            text = r.text
            urls = r.url
        except Exception as e:
            settings.logger.error(u"Cann't post page by url:%s, exception is %s"%(url, type(e)))
        finally:
            return {'page': text, 'url': urls}

    def run(self, ent_num):
        if not os.path.exists(self.html_restore_path):
            os.makedirs(self.html_restore_path)
        json_dict = {}
        self.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        data = self.crawl_page_main()
        json_dict[ent_num] = data
        json_dump_to_file(self.json_restore_path , json_dict)

    def work(self, ent_num= ""):

        if not os.path.exists(self.html_restore_path):
            os.makedirs(self.html_restore_path)
        self.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        data = self.crawl_page_main()
        #json_dump_to_file('shaanxi_json.json', data)
        #data = self.crawl_ind_comm_pub_pages(url = "http://xygs.snaic.gov.cn/ztxy.do", post_data={'maent.pripid':'610000100026931', "random": int(time.time())})
        # data = self.crawl_ent_pub_pages(url = "http://xygs.snaic.gov.cn/ztxy.do", post_data={'maent.pripid':'610000100026931', "random": int(time.time())})
        # data = self.crawl_judical_assist_pub_pages(url = "http://xygs.snaic.gov.cn/ztxy.do", post_data={'maent.pripid':'610000100026931', "random": int(time.time())})
        json_dump_to_file('shaanxi.json', data)

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
        settings.logger.error(u"There is no path : %s"% path )
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
    shaanxi = ShaanxiCrawler('./enterprise_crawler/shaanxi.json')
    shaanxi.work('610100100012377')


if __name__ == "__main__":
    reload (sys)
    sys.setdefaultencoding('utf8')
    import run
    run.config_logging()
    if not os.path.exists("./enterprise_crawler"):
        os.makedirs("./enterprise_crawler")
    shaanxi = shaanxiCrawler('./enterprise_crawler/shaanxi.json')
    ents = read_ent_from_file("./enterprise_list/shaanxi.txt")
    shaanxi = shaanxiCrawler('./enterprise_crawler/shaanxi.json')
    for ent_str in ents:
        settings.logger.info(u'###################   Start to crawl enterprise with id %s   ###################\n' % ent_str[2])
        shaanxi.run(ent_num = ent_str[2])
        settings.logger.info(u'###################   Enterprise with id  %s Finished!  ###################\n' % ent_str[2])

"""
