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
import urlparse
import codecs
from bs4 import BeautifulSoup
import common_func as common_func
import datetime

urls = {
    'host': 'http://gsxt.gdgs.gov.cn/aiccips/',
    'prefix_url':'http://www.szcredit.com.cn/web/GSZJGSPT/',
    'page_search': 'http://gsxt.gdgs.gov.cn/aiccips/index',
    'page_showinfo': 'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/showInfo.html',
    'checkcode':'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/checkCode.html',
}

headers = { 'Connetion': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"}
class Crawler(object):
    def __init__(self, analysis, req= None):
        self.analysis = analysis
        if req:
            self.requests = req
        else:
            self.requests = requests.Session()
            self.requests.headers.update(headers)
        self.ents = []
        self.json_dict={}


    def crawl_xingzhengchufa_page(self, url, text):
        data = self.analysis.analyze_xingzhengchufa(text)
        r = self.requests.post( url, data)
        if r.status_code != 200:
            return False
        #html_to_file("xingzhengchufa.html",r.text)
        return r.text
    def crawl_biangengxinxi_page(self, url, text):
        datas = self.analysis.analyze_biangengxinxi(text)
        r2 = self.requests.post( url, datas, headers = {'X-Requested-With': 'XMLHttpRequest', 'X-MicrosoftAjax': 'Delta=true', 'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',})
        if r2.status_code != 200:
            return False
        return r2.text
    # 爬取 工商公示信息 页面
    def crawl_ind_comm_pub_pages(self, url):
        sub_json_dict={}
        try:
            page = self.crawl_page_by_url(url)['page']
            common_func.save_to_html(self.path, 'ind_comm_pub.html', page)
            #html_to_file("pub.html", page)
            page_xingzhengchufa = self.crawl_xingzhengchufa_page(url, page)
            common_func.save_to_html(self.path, 'xingzhengchufa.html', page_xingzhengchufa)
            page_biangengxinxi = self.crawl_biangengxinxi_page(url, page_xingzhengchufa)
            common_func.save_to_html(self.path, 'biangengxinxi.html', page_biangengxinxi)

            dict_jiben = self.analysis.parse_page(page, 'jibenxinxi')  #   基本信息, 投资人信息
            sub_json_dict['ind_comm_pub_reg_shareholder'] = dict_jiben[u'投资人信息'] if dict_jiben.has_key(u'投资人信息') else []
            sub_json_dict['ind_comm_pub_reg_basic']=  dict_jiben[u'基本信息'] if dict_jiben.has_key(u'基本信息') else []

            dict_beian =  self.analysis.parse_page(page, 'beian')#分支机构信息,经营范围信息,   清算信息, 主要人员信息,
            sub_json_dict['ind_comm_pub_arch_branch'] = dict_beian[u'分支机构信息'] if dict_beian.has_key(u'分支机构信息') else []
            sub_json_dict['ind_comm_pub_arch_liquidation'] = dict_beian[u"清算信息"] if dict_beian.has_key(u'清算信息') else []
            sub_json_dict['ind_comm_pub_arch_key_persons'] =  dict_beian[u'主要人员信息'] if dict_beian.has_key(u"主要人员信息") else []
            bg = self.analysis.parse_page(page_biangengxinxi, 'biangengxinxi')
            sub_json_dict['ind_comm_pub_reg_modify'] = bg[u'变更信息'] if bg.has_key(u'变更信息') else []
            dcdy = self.analysis.parse_page(page, 'dongchandiya')
            sub_json_dict['ind_comm_pub_movable_property_reg'] = dcdy[u'动产抵押登记信息'] if dcdy.has_key(u'动产抵押登记信息') else []
            gqcz = self.analysis.parse_page(page, 'guquanchuzi')
            sub_json_dict['ind_comm_pub_equity_ownership_reg'] = gqcz[u'股权出质登记信息'] if gqcz.has_key(u'股权出质登记信息') else []
            jyyc = self.analysis.parse_page(page, 'jingyingyichang')
            sub_json_dict['ind_comm_pub_business_exception'] = jyyc[u'异常名录信息'] if jyyc.has_key(u'异常名录信息') else []
            yzwf = self.analysis.parse_page(page, 'yanzhongweifa')
            sub_json_dict['ind_comm_pub_serious_violate_law'] = yzwf[u'严重违法信息'] if yzwf.has_key(u'严重违法信息') else []
            cyjc = self.analysis.parse_page(page, 'chouchajiancha')
            sub_json_dict['ind_comm_pub_spot_check'] = cyjc[u'抽查检查信息'] if cyjc.has_key(u'抽查检查信息') else []
            xzcf = self.analysis.parse_page(page_xingzhengchufa, 'xingzhengchufa')
            sub_json_dict['ind_comm_pub_administration_sanction'] = xzcf[u'行政处罚信息'] if xzcf.has_key(u'行政处罚信息') else []
        except Exception as e:
            logging.error(u"An error ocurred in crawl_ind_comm_pub_pages: %s, ID= %s"% (type(e), self.ent_num))
            raise e
        finally:
            return sub_json_dict
        #json_dump_to_file("json_dict.json", self.json_dict)


    #爬取 企业公示信息 页面
    def crawl_ent_pub_pages(self, url):
        sub_json_dict = {}
        try:
            page = self.crawl_page_by_url(url)['page']
            common_func.save_to_html(self.path, 'ent_pub_pages.html', page)
            p = self.analysis.parse_page(page, 'qiyenianbao')
            sub_json_dict['ent_pub_ent_annual_report'] = p[u'企业年报'] if p.has_key(u'企业年报') else []
            p = self.analysis.parse_page(page, 'touziren')
            sub_json_dict['ent_pub_shareholder_capital_contribution'] = p[u'股东及出资信息'] if p.has_key(u'股东及出资信息') else []
            sub_json_dict['ent_pub_reg_modify'] = p[u'变更信息'] if p.has_key(u'变更信息') else []
            p = self.analysis.parse_page(page, 'xingzhengxuke')
            sub_json_dict['ent_pub_administration_license'] = p[u'行政许可信息'] if p.has_key(u'行政许可信息') else []
            p = self.analysis.parse_page(page, 'xingzhengchufa')
            sub_json_dict['ent_pub_administration_sanction'] = p[u'行政处罚信息'] if p.has_key(u'行政处罚信息') else []
            p = self.analysis.parse_page(page, 'gudongguquan')
            sub_json_dict['ent_pub_equity_change'] = p[u'股权变更信息'] if p.has_key(u'股权变更信息') else []
            p = self.analysis.parse_page(page, 'zhishichanquan')
            sub_json_dict['ent_pub_knowledge_property'] = p[u'知识产权出质登记信息'] if p.has_key(u'知识产权出质登记信息') else []
        except Exception as e:
            logging.error(u"An error ocurred in crawl_ent_pub_pages: %s, ID= %s"% (type(e), self.ent_num))
            raise e
        finally:
            return sub_json_dict

    #爬取 其他部门公示信息 页面
    def crawl_other_dept_pub_pages(self, url):
        sub_json_dict={}
        try:
            page = self.crawl_page_by_url(url)['page']
            common_func.save_to_html(self.path, 'other_dept_pub_pages.html', page)
            xk = self.analysis.parse_page(page, 'xingzhengxuke')
            sub_json_dict["other_dept_pub_administration_license"] =  xk[u'行政许可信息'] if xk.has_key(u'行政许可信息') else []  #行政许可信息
            xk = self.analysis.parse_page(page, 'xingzhengchufa')
            sub_json_dict["other_dept_pub_administration_sanction"] = xk[u'行政处罚信息'] if xk.has_key(u'行政处罚信息') else []  # 行政处罚信息

        except Exception as e:
            logging.error(u"An error ocurred in crawl_other_dept_pub_pages: %s, ID= %s " %( type(e), self.ent_num))
            raise e
        finally:
            return sub_json_dict

    #judical assist pub informations
    def crawl_judical_assist_pub_pages(self):
        pass

    def crawl_page_by_url(self, url):
        r = self.requests.get( url)
        if r.status_code != 200:
            logging.error(u"Getting page by url:%s\n, return status %s\n"% (url, r.status_code))
            return False
        return {'page' : r.text, 'url': r.url}

    def run(self, ent):

        todaystr = datetime.datetime.now()
        self.path = os.path.join(common_func.PATH, todaystr.strftime("%Y/%m/%d") , str(self.ent_num))
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        sub_json_dict= {}
        rid = ent[ent.index("rid")+4: len(ent)]
        url = "http://www.szcredit.com.cn/web/GSZJGSPT/QyxyDetail.aspx?rid=" + rid
        sub_json_dict.update(self.crawl_ind_comm_pub_pages(url))
        url = "http://www.szcredit.com.cn/web/GSZJGSPT/QynbDetail.aspx?rid=" + rid
        sub_json_dict.update(self.crawl_ent_pub_pages(url))
        url = "http://www.szcredit.com.cn/web/GSZJGSPT/QtbmDetail.aspx?rid=" + rid
        sub_json_dict.update(self.crawl_other_dept_pub_pages(url))

        return sub_json_dict

class Analyze(object):

    crawler = None
    def __init__(self):
        self.Ent = []
        self.json_dict = {}

    def analyze_xingzhengchufa(self, text):
        soup = BeautifulSoup(text, "html5lib")
        generator = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})['value']
        state = soup.find("input", {"id": "__VIEWSTATE"})['value']

        data = {
                '__VIEWSTATEGENERATOR':generator,
                '__VIEWSTATE': state,
                '__EVENTTARGET':'Timer1',
                'ScriptManager1':"xingzhengchufa|Timer1",
                '__EVENTARGUMENT':'',
                '__ASYNCPOST':'true',
        }
        return data
    def analyze_biangengxinxi(self, text):
        #soup = BeautifulSoup(text, "html5lib")
        pattern = re.compile(r'__VIEWSTATE\|(.*?)\|')
        viewstate_object = pattern.search(text)
        state = ""
        generator = ""
        if viewstate_object :
            state = viewstate_object.group().split('|')[1]
        else:
            print 'None'
        pattern = re.compile(r'__VIEWSTATEGENERATOR\|(.*?)\|')
        viewgenerator_object = pattern.search(text)
        if viewgenerator_object:
            generator = viewgenerator_object.group().split('|')[1]
        else:
            print "None"

        data = {
                '__VIEWSTATEGENERATOR':generator,
                '__VIEWSTATE': state,
                '__EVENTTARGET':'Timer2',
                'ScriptManager1':"biangengxinxi|Timer2",
                '__EVENTARGUMENT':'',
                '__ASYNCPOST':'true',
        }
        return data
    #
    def analyze_biangengxinxi_page(self, text):
        soup = BeautifulSoup(text, "html5lib")
        biangengxinxi_div = soup.find("table")
        trs = biangengxinxi_div.find_all("tr", {"width" : "95%"})
        biangengxinxi_name = ""
        titles = []
        results = []
        #print(biangengxinxi_div.prettify())
        for line, tr in enumerate(trs):
            if line==0:
                biangengxinxi_name =  tr.get_text().strip()
            elif line == 1:
                ths = tr.find_all("th")
                titles = [ th.get_text().strip() for th in ths]
            else:
                tds_tag = tr.find_all("td")
                tds = [td.get_text().strip() for td in tds_tag]
                results.append(dict(zip(titles, tds)))
        self.json_dict[biangengxinxi_name] = results
        #json_dump_to_file("json_dict.json", self.json_dict)



    def get_raw_text_by_tag(self, tag):
        return tag.get_text().strip()

    def get_table_title(self, table_tag):
        if table_tag.find('tr'):
            if table_tag.find('tr').find('th'):
                return self.get_raw_text_by_tag(table_tag.find('tr').th)
            elif table_tag.find('tr').find('td'):
                return self.get_raw_text_by_tag(table_tag.find('tr').td)
        return ''

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
                logging.error('invalid multi_col_tag, multi_col_tag = %s, ID= %s '%(multi_col_tag, self.ent_num))
                return data
            #数据表中会出现多出一空列的情况，fuck it。 要判断最后一列内容是否为空。
            tds = multi_col_tag.find_all('td', recursive = False)
            len_tds = len(tds)
            if not tds[len_tds-1].get_text().strip() :
                len_tds= len_tds - 1

            if len(columns) != len_tds:
                logging.error('column head size != column data size, columns head = %s, columns data = %s, ID= %s' % (columns, multi_col_tag.contents, self.ent_num))
                return data

            for id, col in enumerate(columns):
                data[col[0]] = self.get_column_data(col[1], multi_col_tag.find_all('td', recursive=False)[id])
            return data
        else:
            return self.get_raw_text_by_tag(td_tag)

    def get_detail_link(self, bs4_tag):
        pattern = re.compile(r'http')
        if pattern.search(bs4_tag['href']):
            return bs4_tag['href']
        return urls['prefix_url'] + bs4_tag['href']

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
        #logging.error(u"get_columns_of_record_table->tr:%s\n", tr)
        ret_val=  self.get_record_table_columns_by_tr(tr, table_name)
        # logging.error(u"ret_val->%s\n, ID = %s"%( ret_val, self.ent_num))
        return  ret_val

    def get_record_table_columns_by_tr(self, tr_tag, table_name):
        columns = []
        if not tr_tag:
            return columns
        try:
            sub_col_index = 0
            if len(tr_tag.find_all('th'))==0:
                logging.error(u"The table %s has no columns , ID = %s "%(table_name, self.ent_num))
                return columns
            count = 0
            for i, th in enumerate(tr_tag.find_all('th')):
                #logging.error(u"th in get_record_table_columns_by_tr =\n %s", th)
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
            logging.error(u'exception occured in get_table_columns, except_type = %s, table_name = %s, ID = %s' % (type(e), table_name, self.ent_num))
        finally:
            return columns


    # parse main page
    # return params are dicts
    def parse_page(self, page, types):
        soup = BeautifulSoup(page, 'html5lib')
        page_data = {}
        if soup.body:
            if soup.body.table:
                try:

                    divs = soup.body.find('div', {"id": types})
                    table = None
                    if not divs:
                        table = soup.body.find('table')
                    else :
                        table = divs.find('table')
                    #print table
                    while table:
                        if table.name == 'table':
                            table_name = self.get_table_title(table)
                            page_data[table_name] = self.parse_table(table, table_name, page)
                        table = table.nextSibling

                except Exception as e:
                    logging.error(u'parse failed, with exception %s, ID= %s' % (e, self.ent_num))
                    raise e

                finally:
                    pass
        return page_data

    def parse_table(self, bs_table, table_name, page):
        table_dict = None
        try:
            # tb_title = self.get_table_title(bs_table)
            #this is a fucking dog case, we can't find tbody-tag in table-tag, but we can see tbody-tag in table-tag
            #in case of that, we use the whole html page to locate the tbody

            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            tbody = None
            if len(bs_table.find_all('tbody'))>1:
                tbody = bs_table.find_all('tbody')[1]
            else:
                tbody = bs_table.find('tbody') or BeautifulSoup(page, 'html5lib').find('tbody')
            if columns:
                col_span = 0
                for col in columns:
                    if type(col[1]) == list:
                        col_span += len(col[1])
                    else:
                        col_span += 1

                column_size = len(columns)
                item_array = []
                if not tbody:
                    records_tag = bs_table
                else:
                    records_tag = tbody
                for tr in records_tag.find_all('tr'):

                    if tr.find('td') and col_span == column_size and len(tr.find_all('td', recursive=False)) % column_size == 0:
                        col_count = 0
                        item = {}
                        for td in tr.find_all('td',recursive=False):
                            if td.find('a'):
                                #try to retrieve detail link from page
                                next_url = self.get_detail_link(td.find('a'))
                                #has detail link
                                if next_url:
                                    detail_page = self.crawler.crawl_page_by_url(next_url)
                                    #html_to_file("next.html", detail_page['page'])
                                    if table_name == u'企业年报':
                                        #logging.error(u"next_url = %s, table_name= %s\n", detail_page['url'], table_name)
                                        page_data = self.parse_ent_pub_annual_report_page(detail_page, table_name + '_detail')
                                        item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                        item[u'详情'] = page_data
                                    else:
                                        page_data = self.parse_page(detail_page['page'], table_name + '_detail')
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
                    elif tr.find('td') and len(tr.find_all('td', recursive=False)) == col_span and col_span != column_size:

                        col_count = 0
                        sub_col_index = 0
                        item = {}
                        sub_item = {}
                        tds = tr.find_all('td',recursive=False)
                        for i, td in enumerate(tds):
                            if td.find('a'):
                                #try to retrieve detail link from page
                                next_url = self.get_detail_link(td.find('a'), page)
                                #has detail link
                                if next_url:
                                    detail_page = self.crawler.crawl_page_by_url(next_url)['page']
                                    #html_to_file("next.html", detail_page['page'])

                                    if table_name == u'企业年报':
                                        #logging.error(u"2next_url = %s, table_name= %s\n", next_url, table_name)

                                        page_data = self.parse_ent_pub_annual_report_page(detail_page, table_name + '_detail')
                                        item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                        item[u'详情'] = page_data
                                    else:
                                        page_data = self.parse_page(detail_page['page'], table_name + '_detail')
                                        item[columns[col_count][0]] = page_data #this may be a detail page data
                                else:
                                    #item[columns[col_count]] = CrawlerUtils.get_raw_text_in_bstag(td)
                                    item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                            else :

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
                    # 我给跪了，数据表无缘无故最后的多出一空列
                    elif tr.find('td') and len(tr.find_all('td', recursive=False)) == col_span+1 and col_span != column_size:
                        col_count = 0
                        sub_col_index = 0
                        item = {}
                        sub_item = {}
                        tds = tr.find_all('td',recursive=False)[:-1]
                        for i, td in enumerate(tds):
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
                            logging.error(u'th size not equals td size in table %s, what\'s up??, ID= %s' % (table_name, self.ent_num))
                            return
                        else:
                            for i in range(len(ths)):
                                if self.get_raw_text_by_tag(ths[i]):
                                    table_dict[self.get_raw_text_by_tag(ths[i])] = self.get_raw_text_by_tag(tds[i])
        except Exception as e:
            logging.error(u'parse table %s failed with exception %s, ID = %s' % (table_name, type(e), self.ent_num))
            raise e
        finally:
            return table_dict

    def parse_report_table(self, table, table_name):
        table_dict = {}

        try:
            if table_name == u'基本信息':
                rowspan_name = ""
                item={}
                sub_item= {}
                trs = table.find_all("tr")[1:]
                i =0
                while i < len(trs):
                    tr  = trs[i]
                    titles = tr.find_all("td", {"align": True})
                    datas = tr.find_all("td", {"align": False})
                    if len(titles) != len(datas):
                        if len(titles) - len(datas) == 1:
                            row_num = int(titles[0]['rowspan'])
                            rowspan_name = titles[0].get_text().strip()
                            sub_item = {}
                            sub_item.update(dict(zip([ t.get_text().strip() for t in titles[1:]], [d.get_text().strip() for d in datas])))
                            j=1
                            while j < row_num:
                                tr= trs[i + j]
                                titles = tr.find_all("td", {"align": True})
                                datas = tr.find_all("td", {"align": False})
                                sub_item.update(dict(zip([t.get_text().strip() for t in titles], [ d.get_text().strip() for d in datas])))
                                j= j+1
                            i = i+ row_num-1
                            item[rowspan_name] = sub_item
                            #json_dump_to_file("sub_item.json", item)

                    else:
                        item.update(dict(zip([t.get_text().strip() for t in titles], [ d.get_text().strip() for d in datas])))
                    i+=1
                #json_dump_to_file("sub_item.json", item)

                table_dict[table_name] = item
            else:
                item={}
                sub_item= []
                tables = table.find_all("tr")[1:]

                while tables:
                    tds =  tables[0].find_all("td")
                    flag = False
                    for td in tds:
                        if not td.has_attr('align'):
                            flag = True
                            break
                    #如果第一排有横向的数据
                    if flag:
                        first_line = tables[0].find_all("td")
                        item[first_line[0].get_text().strip()] = first_line[1].get_text().strip()
                        tables = tables[1:]
                        continue
                    columns = [ td.get_text().strip() for td in tables[0].find_all("td")]
                    for tr in tables[1:]:
                        data = [td.get_text().strip() for td in tr.find_all("td")]
                        sub_item.append( dict( zip(columns, data)) )
                    item['list'] = sub_item
                    break

                table_dict[table_name] = item

        except Exception as e:
            logging.error(u"parse report table %s failed with exception %s, ID= %s\n"%(table_name, type(e), self.ent_num))
            raise e

        return table_dict

    def parse_ent_pub_annual_report_page(self, page_dict, table_name):
        page_data = {}
        soup = BeautifulSoup(page_dict['page'], 'html5lib')
        if soup.body.find('table'):
            try:
                #忽略第一行tr
                detail_base_table = soup.body.find('table').find_all('tr')[1:]
                table_name = self.get_raw_text_by_tag(detail_base_table[0])
                sub_dict = {}
                for tr in detail_base_table[1:]:
                    if tr.find('th') and tr.find('td'):
                        ths = tr.find_all('th')
                        tds = tr.find_all('td')
                        if len(ths) != len(tds):
                            settings.logger.error(u'th size not equals td size in table %s, what\'s up??' % table_name)
                            return
                        else:
                            for i in range(len(ths)):
                                if self.get_raw_text_by_tag(ths[i]):
                                    sub_dict[self.get_raw_text_by_tag(ths[i])] = self.get_raw_text_by_tag(tds[i])

                page_data[table_name] = sub_dict
            except Exception as e:
                settings.logger.error(u"fail to get table name with exception %s" % (type(e)))
            try:
                tables = soup.body.find_all('table')[1:]
                for table in tables:
                        table_name = self.get_table_title(table)
                        page_data[table_name] =self.parse_table(table, table_name, page_dict['page'])
                        # print page_data[table_name]
            except Exception as e:
                logging.error(u"fail to parse the rest tables with exception %s, ID= %s" %(type(e), self.ent_num))
        else:
            pass
        return page_data

    """
    def parse_ent_pub_annual_report_page(self, page_dict, table_name):
        url = page_dict['url']
        page = page_dict['page']
        page_data= {}
        soup = BeautifulSoup(page, "html5lib")
        number = len(soup.find('ul', {'id': 'ContentPlaceHolder1_ulTag'}).find_all('li'))
        if number == 0 :
            logging.error(u"Could not find tab in annual report page")
            return
        generator = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})['value']
        validation = soup.find("input", {"id": "__EVENTVALIDATION"})['value']
        state = soup.find("input", {"id": "__VIEWSTATE"})['value']
        ContentPlaceHolder = "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$lbtnTag0"
        target = "ctl00$ContentPlaceHolder1$lbtnTag0"
        data= {
            'ctl00$ContentPlaceHolder1$smObj':ContentPlaceHolder, #ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$lbtnTag1
            '__EVENTTARGET': target,   #ctl00$ContentPlaceHolder1$lbtnTag0
            '__EVENTARGUMENT': '',
            '__VIEWSTATE':state,
            '__VIEWSTATEGENERATOR':generator,
            '__EVENTVALIDATION':validation,
            '__ASYNCPOST':'true',
        }
        r = self.crawler.requests.post(url, data, headers = {'X-Requested-With': 'XMLHttpRequest', 'X-MicrosoftAjax': 'Delta=true', 'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'} )
        if r.status_code != 200:
            logging.error(u'Could not get response page')
            return False
        page = r.text
        #html_to_file("annual.html", page)
        table_name = ""
        try:
            soup = BeautifulSoup(page, 'html5lib')
            content_table = soup.find_all('table')[1:]
            for table in content_table:
                table_name = self.get_table_title(table)
                #logging.error(u"annual report table_name= %s\n", table_name)
                table_data = self.parse_report_table(table, table_name)
                page_data[table_name] = table_data
        except Exception as e:
            logging.error(u'annual page: fail to get table data with exception %s' % e)
            raise e

        #html_to_file("annual.html", page)
        for i in range(number-1):
            state = re.compile(r"__VIEWSTATE\|(.*?)\|").search(page).group().split('|')[1]
            generator = re.compile(r"__VIEWSTATEGENERATOR\|(.*?)\|").search(page).group().split('|')[1]
            validation = re.compile(r"__EVENTVALIDATION\|(.*?)\|").search(page).group().split('|')[1]
            ContentPlaceHolder = "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$lbtnTag%d"%(i+1)
            target = "ctl00$ContentPlaceHolder1$lbtnTag%d"%(i+1)
            data= {
                'ctl00$ContentPlaceHolder1$smObj':ContentPlaceHolder, #ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$lbtnTag1
                '__EVENTTARGET': target,   #ctl00$ContentPlaceHolder1$lbtnTag0
                '__EVENTARGUMENT': '',
                '__VIEWSTATE':state,
                '__VIEWSTATEGENERATOR':generator,
                '__EVENTVALIDATION':validation,
                '__ASYNCPOST':'true',
            }
            r = self.crawler.requests.post(url, data, headers = {'X-Requested-With': 'XMLHttpRequest', 'X-MicrosoftAjax': 'Delta=true', 'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',} )
            if r.status_code != 200:
                logging.error(u'Could not get response page')
                return False
            page = r.text
            #html_to_file("annual.html", page)
            table_name = ""
            try:
                soup = BeautifulSoup(page, 'html5lib')
                content_table = soup.find_all('table')[1:]
                for table in content_table:
                    table_name = self.get_table_title(table)
                    #logging.error(u"annual report table_name= %s\n", table_name)
                    table_data = self.parse_report_table(table, table_name)
                    #json_dump_to_file('report_json.json', table_data)
                    page_data[table_name] = table_data

            except Exception as e:
                logging.error(u'annual page: fail to parse page with exception %s'%e)
                raise e
        #json_dump_to_file('report_json.json', page_data)
        return page_data
    """

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

def html_from_file(path):
    read_type = 'r'
    if not os.path.exists(path):
        return None
    datas = None
    with codecs.open(path, read_type, 'utf8') as f:
        datas = f.read()
        f.close()
    return datas



class Guangdong0(object):
    def __init__(self, req= None, ent_number= None):
        self.analysis = Analyze()
        self.crawler = Crawler(self.analysis, req)
        self.analysis.crawler = self.crawler
        self.analysis.ent_num = ent_number
        self.crawler.ent_num = ent_number

    def run(self, url):
        return self.crawler.run(url)
