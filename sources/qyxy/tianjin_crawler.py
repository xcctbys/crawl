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

urls = {
    'host': 'http://tjcredit.gov.cn',
    'page_search': 'http://tjcredit.gov.cn/platform/saic/index.ftl',
    'page_Captcha': 'http://tjcredit.gov.cn/verifycode',
    'page_showinfo': 'http://tjcredit.gov.cn/platform/saic/search.ftl',
    'checkcode':'http://tjcredit.gov.cn/platform/saic/search.ftl',
}
CheckDetail = {     #行政处罚
                    'getAdmPen' : "/saicpf/gsxzcf?id=%s&entid=%s&issaic=1&hasInfo=0",
                    #股东信息
                    'getShareHolder' : "/saicpf/gsgdcz?gdczid=%s&entid=%s&issaic=1&hasInfo=0",
                    #动产抵押
                    'getChaMore' : "/saicpf/gsdcdy?id=%s&entid=%s&issaic=1&hasInfo=0",
                    #股权出质
                    'getEquPle' : "/saicpf/gsgqcz?id=%s&entid=%s&issaic=1&hasInfo=0",
            }

headers = { 'Connetion': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36",
            }

class TianjinCrawler(object):
    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()
    def __init__(self, json_restore_path):
        self.html_search = None
        self.html_showInfo = None
        self.Captcha = None
        #self.path_captcha = './Captcha.png'

        self.CR = CR.CaptchaRecognition("tianjin")
        self.requests = requests.Session()
        self.requests.headers.update(headers)
        self.ents = []
        self.json_dict={}
        self.json_restore_path = json_restore_path
        #验证码图片的存储路径
        self.path_captcha = settings.json_restore_path + '/tianjin/ckcode.jpeg'
        #html数据的存储路径
        self.html_restore_path = settings.html_restore_path + '/tianjin/'


    # 破解搜索页面
    def crawl_page_search(self, url):
        r = self.requests.get( url)
        if r.status_code != 200:
            settings.logger.error(u"Something wrong when getting the url:%s , status_code=%d", url, r.status_code)
            return
        r.encoding = "utf-8"
        #settings.logger.debug("searchpage html :\n  %s", r.text)
        self.html_search = r.text

    #分析 展示页面， 获得搜索到的企业列表
    def analyze_showInfo(self, page):
        Ent = []
        soup = BeautifulSoup(page, "html5lib")
        divs = soup.find_all("div", {"class":"result-item"})
        if divs:
            for div in divs:
                a = div.find('a')
                if a and a.has_attr('href'):
                    Ent.append(a['href'])
        self.ents = Ent

    # 破解验证码页面
    def crawl_page_captcha(self, url_Captcha, url_CheckCode,url_showInfo,  textfield= '120000000000165'):

        count = 0
        while True:
            count+= 1
            r = self.requests.get( url_Captcha)
            if r.status_code != 200:
                settings.logger.error(u"Something wrong when getting the Captcha url:%s , status_code=%d", url_Captcha, r.status_code)
                return
            #settings.logger.debug("Captcha page html :\n  %s", self.Captcha)
            if self.save_captcha(r.content):
                result = self.crack_captcha()
                print result
                datas= {
                        'searchContent': textfield,
                        'vcode': result,
                }
                page=  self.crawl_page_by_url_post(url_CheckCode, datas)['page']
                # 如果验证码正确，就返回一种页面，否则返回主页面
                if self.is_search_result_page(page) :
                    self.analyze_showInfo(page)
                    break
                else:
                    settings.logger.debug(u"crack Captcha failed, the %d time(s)", count)
                    if count> 15:
                        break
        return

    # 判断是否成功搜索页面
    def is_search_result_page(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        divs = soup.find('div', {'class':'nav-query'})
        return divs is None

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
        if Captcha is None:
            settings.logger.error(u"Can not store Captcha: None\n")
            return False
        self.write_file_mutex.acquire()
        f = open(self.path_captcha, 'w')
        try:
            f.write(Captcha)
        except IOError:
            settings.logger.debug("%s can not be written", Captcha)
        finally:
            f.close
        self.write_file_mutex.release()
        return True
    def crawl_page_main(self ):
        sub_json_dict= {}
        if not self.ents:
            settings.logger.error(u"Get no search result\n")
        try:
            for ent in self.ents:
                m = re.match('http', ent)
                if m is None:
                    ent = urls['host']+ ent
                settings.logger.debug(u"ent url:%s\n"% ent)
                ent_num = ent[ent.index('entId=')+6 :]
                url_format = "http://tjcredit.gov.cn/platform/saic/baseInfo.json?entId=" + ent_num+"&departmentId=scjgw&infoClassId=%s"
                sub_json_dict.update(self.crawl_ind_comm_pub_pages(url_format))
                url_format = "http://tjcredit.gov.cn/report/%s?entid="+ent_num
                sub_json_dict.update(self.crawl_ent_pub_pages(url_format))
                url_format = "http://tjcredit.gov.cn/report/%s?entid="+ ent_num
                sub_json_dict.update(self.crawl_judical_assist_pub_pages(url_format))
        except Exception as e:
            settings.logger.error(u"An error ocurred when getting the main page, error: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #工商公式信息页面
    def crawl_ind_comm_pub_pages(self, url):
        sub_json_dict={}
        try:
            page = self.crawl_page_by_url(url%'dj')['page']
            dj = self.parse_page(page) # class= result-table

            sub_json_dict['ind_comm_pub_reg_basic'] = dj[u'基本信息'] if dj.has_key(u'基本信息') else {}       # 登记信息-基本信息
            sub_json_dict['ind_comm_pub_reg_shareholder'] = dj[u'股东信息'] if dj.has_key(u'股东信息') else []   # 股东信息
            sub_json_dict['ind_comm_pub_reg_modify'] = dj[u'变更信息'] if dj.has_key(u'变更信息') else []       # 变更信息
            page = self.crawl_page_by_url(url%'ba')['page']

            ba = self.parse_page(page)
            sub_json_dict['ind_comm_pub_arch_key_persons'] = ba[u'主要人员信息'] if ba.has_key(u'主要人员信息') else []   # 备案信息-主要人员信息
            sub_json_dict['ind_comm_pub_arch_branch'] = ba[u'分支机构信息'] if ba.has_key(u'分支机构信息') else []       # 备案信息-分支机构信息
            sub_json_dict['ind_comm_pub_arch_liquidation'] = ba[u'清算信息'] if ba.has_key(u'清算信息') else []   # 备案信息-清算信息
            page = self.crawl_page_by_url(url%'dcdydjxx')['page']
            dcdy = self.parse_page(page)
            sub_json_dict['ind_comm_pub_movable_property_reg'] = dcdy[u'动产抵押登记信息'] if dcdy.has_key(u'动产抵押登记信息') else []
            page = self.crawl_page_by_url(url % 'gqczdjxx')['page']
            gqcz = self.parse_page(page)
            sub_json_dict['ind_comm_pub_equity_ownership_reg'] = gqcz[u'股权出质登记信息'] if gqcz.has_key(u'股权出质登记信息') else []
            page = self.crawl_page_by_url(url % 'xzcf')['page']
            xzcf = self.parse_page(page)
            sub_json_dict['ind_comm_pub_administration_sanction'] = xzcf[u'行政处罚信息'] if xzcf.has_key(u'行政处罚信息') else []
            page = self.crawl_page_by_url(url % 'qyjyycmlxx')['page']
            jyyc = self.parse_page(page)
            sub_json_dict['ind_comm_pub_business_exception'] = jyyc[u'经营异常信息'] if jyyc.has_key(u'经营异常信息') else []
            page = self.crawl_page_by_url(url % 'yzwfqyxx')['page']
            yzwf = self.parse_page(page)
            sub_json_dict['ind_comm_pub_serious_violate_law'] = yzwf[u'严重违法信息'] if yzwf.has_key(u'严重违法信息') else []
            page = self.crawl_page_by_url(url % 'ccjcxx')['page']
            cyjc = self.parse_page(page)
            sub_json_dict['ind_comm_pub_spot_check'] = cyjc[u'抽查检查信息'] if cyjc.has_key(u'抽查检查信息') else []

        except Exception as e:
            logging.debug(u"An error ocurred in crawl_ind_comm_pub_pages: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #爬取 企业公示信息 页面
    def crawl_ent_pub_pages(self, url):
        sub_json_dict = {}
        try:
            settings.logger.info( u"crawl the ent_pub_pages %s."%(url))
            sub_json_dict['ent_pub_administration_license'] = []    #行政许可信息
            sub_json_dict['ent_pub_administration_sanction'] = []   #行政许可信息
            sub_json_dict['ent_pub_reg_modify'] = []   #变更信息
            page = self.crawl_page_by_url(url%'nblist')['page']
            nb = self.parse_page(page)
            sub_json_dict['ent_pub_ent_annual_report'] = nb[u'年报信息'] if nb.has_key(u'年报信息') else []
            page = self.crawl_page_by_url(url%'gdcz')['page']
            p = self.parse_page(page)
            sub_json_dict['ent_pub_shareholder_capital_contribution'] = p[u'股东及出资'] if p.has_key(u'股东及出资') else []
            page = self.crawl_page_by_url(url%'gqbg')['page']
            p = self.parse_page(page)
            sub_json_dict['ent_pub_equity_change'] = p[u'股权变更信息'] if p.has_key(u'股权变更信息') else []
            page = self.crawl_page_by_url(url%'zscq')['page']
            p = self.parse_page(page)
            sub_json_dict['ent_pub_knowledge_property'] = p[u'知识产权出质登记信息'] if p.has_key(u'知识产权出质登记信息') else []

        except Exception as e:
            logging.debug(u"An error ocurred in crawl_ent_pub_pages: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #爬取 司法协助公式 页面
    def crawl_judical_assist_pub_pages(self, url):
        sub_json_dict = {}
        try:
            settings.logger.info( u"crawl the judical_assist_pub page %s."%(url))
            page = self.crawl_page_by_url(url%'gddjlist')['page']
            xz = self.parse_page(page)
            sub_json_dict['judical_assist_pub_equity_freeze'] = xz[u'司法股权冻结信息'] if xz.has_key(u'司法股权冻结信息') else []
            page = self.crawl_page_by_url(url%'gdbglist')['page']
            xz = self.parse_page(page)
            sub_json_dict['judical_assist_pub_shareholder_modify'] = xz[u'司法股东变更登记信息'] if xz.has_key(u'司法股东变更登记信息') else []
        except Exception as e:
            settings.logger.debug(u"An error ocurred in crawl_judical_assist_pub_pages: %s"% (type(e)))
            raise e
        finally:
            return sub_json_dict
        pass

    def get_raw_text_by_tag(self, tag):
        return tag.get_text().strip()

    def get_table_title(self, table_tag):
        """
        # if table_tag.find('tr'):
        #     if table_tag.find('tr').find('th'):
        #         return self.get_raw_text_by_tag(table_tag.find('tr').th)
        #     elif table_tag.find('tr').find('td'):
        #         return self.get_raw_text_by_tag(table_tag.find('tr').td)
        # return ''
        #会出现 class= bg title 的td作为表头
        """
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
            elif table_tag.find('tr').find('td', {'class':'bg title'}):
                # 处理 <th> aa<span> bb</span> </th>
                if table_tag.find('tr').td.stirng == None and len(table_tag.find('tr').td.contents) > 1:
                    # 处理 <th>   <span> bb</span> </th>  包含空格的
                    if (table_tag.find('tr').td.contents[0]).strip()  :
                        return (table_tag.find('tr').td.contents[0]).strip()
                return self.get_raw_text_by_tag(table_tag.find('tr').td)
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

    def get_sub_columns_td_bg_title(self, tr_tag, index, count):
        columns = []
        for i in range(index, index + count):
            th = tr_tag.find_all('td', {'class': 'bg title'})[i]
            if not self.sub_column_count(th):
                columns.append(( self.get_raw_text_by_tag(th), self.get_raw_text_by_tag(th)))
            else:
            #if has sub-sub columns
                columns.append((self.get_raw_text_by_tag(th), self.get_sub_columns_td_bg_title(tr_tag.nextSibling.nextSibling, 0, self.sub_column_count(th))))
        return columns

    def get_sub_columns_td_bg(self, tr_tag, index, count):
        columns = []
        for i in range(index, index + count):
            th = tr_tag.find_all('td', {'class': 'bg'})[i]
            if not self.sub_column_count(th):
                columns.append(( self.get_raw_text_by_tag(th), self.get_raw_text_by_tag(th)))
            else:
            #if has sub-sub columns
                columns.append((self.get_raw_text_by_tag(th), self.get_sub_columns_td_bg(tr_tag.nextSibling.nextSibling, 0, self.sub_column_count(th))))
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
            #print 'href'
            pattern = re.compile(r'http'| r'javascript:void(0);')
            if pattern.search(bs4_tag['href']):
                return bs4_tag['href']
            return urls['prefix_url'] + bs4_tag['href']
        elif bs4_tag.has_attr('onclick'):
            #print 'onclick'
            txt= bs4_tag['onclick']
            if re.compile('CheckDetail').search(txt):

                re1='.*?'   # Non-greedy match on filler
                re2='(?:[a-z][a-z]+)'   # Uninteresting: word
                re3='.*?'   # Non-greedy match on filler
                re4='((?:[a-z][a-z]+))' # Word 1

                rg = re.compile(re1+re2+re3+re4,re.IGNORECASE|re.DOTALL)
                m = rg.search(txt)
                if m:
                    key=m.group(1)
                    re1='.*?'   # Non-greedy match on filler
                    re2='(\\\'.*?\\\')' # Single Quote String 1
                    re3='.*?'   # Non-greedy match on filler
                    re4='(\\\'.*?\\\')' # Single Quote String 2

                    rg = re.compile(re1+re2+re3+re4,re.IGNORECASE|re.DOTALL)
                    m = rg.search(txt)
                    if m:
                        # strip extra \'\' for each side
                        id_str=m.group(1)[1:-1]
                        entid_str=m.group(2)[1:-1]
                    url = urls['host'] + CheckDetail[key]%(id_str, entid_str)

            elif re.compile('nbdetail').search(txt):
                re1='.*?'   # Non-greedy match on filler
                re2='(\\\'.*?\\\')' # Single Quote String 1
                re3='.*?'   # Non-greedy match on filler
                re4='(\\\'.*?\\\')' # Single Quote String 2

                rg = re.compile(re1+re2+re3+re4,re.IGNORECASE|re.DOTALL)
                m = rg.search(txt)
                if m:
                    entid_str=m.group(1)[1:-1]
                    year_str=m.group(2)[1:-1]
                url = urls['host'] + "/report/annals?entid=%s&year=%s&hasInfo=0"%(entid_str, year_str)
            elif re.compile('sfGddjDetail').search(txt):
                re1='.*?'   # Non-greedy match on filler
                re2='(\\\'.*?\\\')' # Single Quote String 1
                re3='.*?'   # Non-greedy match on filler
                re4='(\\\'.*?\\\')' # Single Quote String 2

                rg = re.compile(re1+re2+re3+re4,re.IGNORECASE|re.DOTALL)
                m = rg.search(txt)
                if m:
                    id_str=m.group(1)[1:-1]
                    entid_str=m.group(2)[1:-1]
                url = urls['host'] + "/report/gddjdetail?id=%s&entid=%s&hasInfo=0"%(id_str, entid_str)
            return url
        return None


    def get_columns_of_record_table(self, bs_table, page, table_name):
        tbody = None
        if len(bs_table.find_all('tbody')) > 1:
            tbody= bs_table.find_all('tbody')[1]
        else:
            tbody = bs_table.find('tbody') or BeautifulSoup(page, 'html5lib').find('tbody')

        tr = None
        if tbody:
            if len(tbody.find_all('tr')) <= 1:
                tr = tbody.find('tr')
            else:
                tr = tbody.find_all('tr')[1]
                if not tr.find('th'):
                    if not tr.find('td', {'class': 'bg title'}) and not tr.find('td', {'class': 'bg'}):
                        tr = tbody.find_all('tr')[0]
                    elif len(tr.find_all('td')) == len(tr.find_all('td', attrs={'class':'bg title', 'class': 'bg'})):
                        pass
                    #elif len(tr.find_all('td')) == len(tr.find_all('td', attrs={'class':'bg'})):
                    #    pass
                    else:
                        tr = None
                elif tr.find('td'):
                    tr = None
        else:
            if len(bs_table.find_all('tr')) <= 1:
                return None
            elif bs_table.find_all('tr')[0].find('th') and not bs_table.find_all('tr')[0].find('td') and len(bs_table.find_all('tr')[0].find_all('th')) > 1:
                tr = bs_table.find_all('tr')[0]
            elif bs_table.find_all('tr')[0].find('td', {'class': 'bg title'}) and len(bs_table.find_all('tr')[0].find_all('td', {'class': 'bg title'})) > 1:
                tr = bs_table.find_all('tr')[0]
            elif bs_table.find_all('tr')[1].find('th') and not bs_table.find_all('tr')[1].find('td') and len(bs_table.find_all('tr')[1].find_all('th')) > 1:
                tr = bs_table.find_all('tr')[1]
            elif bs_table.find_all('tr')[1].find('td', {'class': 'bg title'}) and len(bs_table.find_all('tr')[1].find_all('td', {'class': 'bg title'})) > 1:
                tr = bs_table.find_all('tr')[1]
        ret_val=  self.get_record_table_columns_by_tr(tr, table_name)
        return  ret_val

    def get_record_table_columns_by_tr(self, tr_tag, table_name):
        columns = []
        if not tr_tag:
            return columns
        try:
            sub_col_index = 0
            if len(tr_tag.find_all('th'))==0 and ( len(tr_tag.find_all('td', {'class': 'bg title'}))==0 and len(tr_tag.find_all('td', attrs={'class':'bg'}))==0 ):
                logging.error(u"The table %s has no columns"% table_name)
                return columns
            count = 0
            if len(tr_tag.find_all('th'))>0 :
                for th in tr_tag.find_all('th'):
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
            elif len(tr_tag.find_all('td', {'class': 'bg title'}))>0 :
                for td in tr_tag.find_all('td', {'class': 'bg title'}):
                    col_name = self.get_raw_text_by_tag(td)
                    if col_name :
                        if ((col_name, col_name) in columns):
                            col_name = col_name + '_'
                            count+= 1
                        if not self.sub_column_count(td):
                            columns.append((col_name, col_name))
                        else:
                            columns.append((col_name, self.get_sub_columns_td_bg_title(tr_tag.nextSibling.nextSibling, sub_col_index, self.sub_column_count(td))))
                            sub_col_index += self.sub_column_count(td)
                if count == len(tr_tag.find_all('td', {'class': 'bg title'}))/2 :
                    columns = columns[:len(columns)/2]
            elif len(tr_tag.find_all('td', {'class': 'bg'}))>0:
                for td in tr_tag.find_all('td', {'class': 'bg'}):
                    col_name = self.get_raw_text_by_tag(td)
                    if col_name :
                        if ((col_name, col_name) in columns):
                            col_name = col_name + '_'
                            count+= 1
                        if not self.sub_column_count(td):
                            columns.append((col_name, col_name))
                        else:
                            columns.append((col_name, self.get_sub_columns_td_bg(tr_tag.nextSibling.nextSibling, sub_col_index, self.sub_column_count(td))))
                            sub_col_index += self.sub_column_count(td)
                if count == len(tr_tag.find_all('td', {'class': 'bg'}))/2 :
                    columns = columns[:len(columns)/2]
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
                table_data = self.parse_table(table, table_name, page)
                sub_dict[table_name] = table_data
        except Exception as e:
            settings.logger.error(u'annual page: fail to get table data with exception %s' % e)
            raise e
        finally:
            return sub_dict

    # parse main page
    # return params are dicts
    def parse_page(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        page_data = {}
        try:
            table = soup.find('table')
            #print table
            while table:
                if table.name == 'table':
                    table_name = self.get_table_title(table)
                    page_data[table_name] = self.parse_table(table, table_name, page)
                table = table.nextSibling

        except Exception as e:
            logging.error(u'parse failed, with exception %s' % e)
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
            #print columns
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
                sub_list = None
                item = None
                for tr in records_tag.find_all('tr'):
                    if tr.find_all('td', attrs={'class':None,  'class': ""}) and len(tr.find_all('td', recursive=False)) % column_size == 0:
                        col_count = 0
                        item = {}
                        for td in tr.find_all('td',recursive=False):
                            if td.find('a'):
                                #try to retrieve detail link from page
                                next_url = self.get_detail_link(td.find('a'))
                                #print 'next_url: ' + next_url
                                if next_url:
                                    detail_page = self.crawl_page_by_url(next_url)
                                    #html_to_file("next.html", detail_page['page'])
                                    if table_name == u'年报信息':
                                        page_data = self.parse_ent_pub_annual_report_page(detail_page['page'])

                                        item[columns[col_count][0]] = page_data #this may be a detail page data
                                    else:
                                        page_data = self.parse_page(detail_page['page'])
                                        item[columns[col_count][0]] = page_data #this may be a detail page data
                                else:
                                    item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                            else:
                                item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                            col_count += 1
                            if col_count == column_size:
                                item_array.append(item.copy())
                                col_count = 0
                    #this case is for the ind-comm-pub-reg-shareholders----details'table
                    #a fucking dog case!!!!!!
                    elif tr.find_all('td', attrs={'class':None, 'class': ""}) and len(tr.find_all('td', recursive=False)) == col_span and col_span != column_size:
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
                    # 在股东及出资情况当中出现的多行数据, mother-fucker
                    elif tr.find_all('td', attrs={'class':None, 'class': ""}):
                        if len(tr.find_all('td', recursive=False)) == single_col:
                            col_count = 0
                            item = {}
                            sub_list =[]
                            for td in tr.find_all('td',recursive=False):
                                if type(columns[col_count][1]) is not list:
                                    item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                    col_count+= 1
                                else:
                                    pass
                        elif len(tr.find_all('td', recursive=False)) == col_span - single_col:
                            #col_count = single_col
                            sub_col_index = 0
                            #item = {}
                            sub_item = {}
                            t_item={}
                            col_count = single_col
                            for td in tr.find_all('td',recursive=False):
                                if type(columns[col_count][1]) is list:
                                    sub_key = columns[col_count][1][sub_col_index][1]
                                    sub_item[sub_key] = self.get_raw_text_by_tag(td)
                                    sub_col_index += 1
                                    if sub_col_index == len(columns[col_count][1]):
                                        #t_item[columns[col_count][0]] = sub_item.copy()
                                        t_item.update(sub_item.copy())
                                        sub_item = {}
                                        col_count += 1
                                        sub_col_index = 0
                                else:
                                    pass
                            sub_list.append(t_item.copy())

                        if not tr.nextSibling.nextSibling:
                            item['list'] = sub_list
                            item_array.append(item.copy())
                table_dict = item_array
            else:
                table_dict = {}
                if len(bs_table.find_all('th')) == 0:
                    for tr in bs_table.find_all('tr'):
                        if len(tr.find_all('td', {'class': 'bg'}))*2 == len(tr.find_all('td')):
                            ths = tr.find_all('td', {'class': 'bg'})
                            tds = tr.find_all('td', {'class': ''})
                            if len(ths) != len(tds):
                                logging.error(u'th size not equals td size in table %s, what\'s up??' % table_name)
                                return
                            else:
                                for i in range(len(ths)):
                                    if self.get_raw_text_by_tag(ths[i]):
                                        table_dict[self.get_raw_text_by_tag(ths[i])] = self.get_raw_text_by_tag(tds[i])

                else:
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


    def crawl_page_by_url(self, url):
        r = self.requests.get( url)
        if r.status_code != 200:
            settings.logger.error(u"Getting page by url:%s\n, return status %s\n"% (url, r.status_code))
            return False
        # 为了防止页面间接跳转，获取最终目标url
        return {'page' : r.text, 'url': r.url}

    def crawl_page_by_url_post(self, url, data, header={}):
        if header:
            r = self.requests.post(url, data, headers= header)
        else :
            r = self.requests.post(url, data)
        if r.status_code != 200:
            settings.logger.error(u"Getting page by url with post:%s\n, return status %s\n"% (url, r.status_code))
            return False
        return {'page': r.text, 'url': r.url}

    def run(self, ent_num):
        if not os.path.exists(self.html_restore_path):
            os.makedirs(self.html_restore_path)
        self.json_dict = {}
        self.crawl_page_search(urls['page_search'])
        self.crawl_page_captcha(urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        data = self.crawl_page_main()
        self.json_dict[ent_num] = data
        json_dump_to_file(self.json_restore_path , self.json_dict)

    def work(self, ent_num= ""):

        if not os.path.exists(self.html_restore_path):
            os.makedirs(self.html_restore_path)

        self.crawl_page_search(urls['page_search'])
        self.crawl_page_captcha(urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        data = self.crawl_page_main()

        #self.ents= ['/platform/saic/viewBase.ftl?entId=349DDA405D520231E04400306EF52828']
        #data = self.crawl_page_main()

        #txt = html_from_file('tianjin_dj.html')
        #txt = html_from_file('next.html')
        #data = self.parse_page(txt)
        #data = self.parse_ent_pub_annual_report_page(txt)
        #data = self.parse_page(txt)
        json_dump_to_file('tianjin_json.json', data)


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
    tianjin = TianjinCrawler('./enterprise_crawler/tianjin.json')
    #tianjin.work('120000000000165')
    tianjin.work('120000000000165')


if __name__ == "__main__":
    reload (sys)
    sys.setdefaultencoding('utf8')
    import run
    run.config_logging()
    if not os.path.exists("./enterprise_crawler"):
        os.makedirs("./enterprise_crawler")
    tianjin = TianjinCrawler('./enterprise_crawler/tianjin.json')
    ents = read_ent_from_file("./enterprise_list/tianjin.txt")
    tianjin = TianjinCrawler('./enterprise_crawler/tianjin.json')
    for ent_str in ents:
        settings.logger.info(u'###################   Start to crawl enterprise with id %s   ###################\n' % ent_str[2])
        tianjin.run(ent_num = ent_str[2])
        settings.logger.info(u'###################   Enterprise with id  %s Finished!  ###################\n' % ent_str[2])
"""
