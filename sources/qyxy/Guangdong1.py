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
import urlparse
import codecs

#import traceback
import unittest
from bs4 import BeautifulSoup
import CaptchaRecognition as CR
urls = {
    'host': 'http://gsxt.gdgs.gov.cn/aiccips/',
    'prefix_url_0':'http://www.szcredit.com.cn/web/GSZJGSPT/',
    'prefix_url_1':'http://gsxt.gzaic.gov.cn:7001/search/',
    'page_search': 'http://gsxt.gdgs.gov.cn/aiccips/index',
    'page_Captcha': 'http://gsxt.gdgs.gov.cn/aiccips/verify.html',
    'page_showinfo': 'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/showInfo.html',
    'checkcode':'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/checkCode.html',
    'ind_comm_pub_reg_basic': 'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo',
    'prefix_GSpublicity':'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=',
}


headers = { 'Connetion': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"}
class Crawler(object):
    def __init__(self, analysis):
        self.analysis = analysis
        self.html_search = None
        self.html_showInfo = None
        self.Captcha = None
        #self.opener = self.make_opener()
        self.requests = requests.Session()
        self.requests.headers.update(headers)
        self.ents = []
        self.main_host = ""
        self.json_dict={}

    # 爬取 工商公示信息 页面
    def crawl_ind_comm_pub_pages(self, url, post_data= {}):
        sub_json_dict={}
        try:
            page = self.crawl_page_by_url(url)['page']
            dict_jiben = self.analysis.parse_page_1(page, 'jibenxinxi', post_data)
            sub_json_dict['ind_comm_pub_reg_basic'] = dict_jiben[u'企业基本信息'] if dict_jiben.has_key(u'企业基本信息') else {}
            sub_json_dict['ind_comm_pub_reg_shareholder'] = dict_jiben[u'出资人及出资信息'] if dict_jiben.has_key(u'出资人及出资信息') else []
            sub_json_dict['ind_comm_pub_reg_modify'] =   dict_jiben[u'变更信息'] if dict_jiben.has_key(u'变更信息') else []
            dict_beian = self.analysis.parse_page_1(page, 'beian', post_data)
            sub_json_dict['ind_comm_pub_arch_key_persons'] =  dict_beian[u'主要人员信息'] if dict_beian.has_key(u'主要人员信息') else []
            sub_json_dict['ind_comm_pub_arch_branch'] =  dict_beian[u'分支机构信息'] if dict_beian.has_key(u'分支机构信息') else []
            sub_json_dict['ind_comm_pub_arch_liquidation'] =   dict_beian[u'清算信息'] if dict_beian.has_key(u'清算信息') else []

            gqcz =  self.analysis.parse_page_1(page, 'guquanchuzi', post_data)
            sub_json_dict['ind_comm_pub_equity_ownership_reg'] = gqcz[u'股权出质登记信息'] if gqcz.has_key(u'股权出质登记信息') else []
            dj = self.analysis.parse_page_1(page, 'dongchandiya', post_data)
            sub_json_dict['ind_comm_pub_movable_property_reg'] = dj[u'动产抵押登记信息'] if dj.has_key(u'动产抵押登记信息') else []
            dj = self.analysis.parse_page_1(page, 'jingyingyichang', post_data)
            sub_json_dict['ind_comm_pub_business_exception'] = dj[u'经营异常信息'] if dj.has_key(u'经营异常信息') else []
            dj = self.analysis.parse_page_1(page, 'yanzhongweifa', post_data)
            sub_json_dict['ind_comm_pub_serious_violate_law'] = dj[u'严重违法信息'] if dj.has_key(u'严重违法信息') else []
            dj = self.analysis.parse_page_1(page, 'chouchajiancha', post_data)
            sub_json_dict['ind_comm_pub_spot_check'] = dj[u'抽查检查信息'] if dj.has_key(u'抽查检查信息') else []
            dj = self.analysis.parse_page_1(page, 'xingzhengchufa', post_data)
            sub_json_dict['ind_comm_pub_administration_sanction'] = dj[u'行政处罚信息'] if dj.has_key(u'行政处罚信息') else []
        except Exception as e:
            settings.logger.debug(u"An error ocurred in crawl_ind_comm_pub_pages: %s, type is %d"% (type(e), types))
            raise e
        finally:
            return sub_json_dict
    #爬取 企业公示信息 页面
    def crawl_ent_pub_pages(self, url, post_data={}):
        sub_json_dict = {}
        try:
            page = self.crawl_page_by_url(url)['page']
            p = self.analysis.parse_page_1(page, 'nianbao')
            sub_json_dict['ent_pub_ent_annual_report'] = p[u'基本信息'] if p.has_key(u'基本信息') else []
            p = self.analysis.parse_page_1(page, 'zizhizigexuke')
            sub_json_dict['ent_pub_administration_license'] = p[u'行政许可信息'] if p.has_key(u'行政许可信息') else []
            p = self.analysis.parse_page_1(page, 'xingzhengchufa')
            sub_json_dict['ent_pub_administration_sanction'] = p[u'行政处罚信息'] if p.has_key(u'行政处罚信息') else []
            p = self.analysis.parse_page_1(page, 'touzirenjichuzi')
            sub_json_dict['ent_pub_shareholder_capital_contribution'] = p[u'股东及出资信息'] if p.has_key(u'股东及出资信息') else []
            sub_json_dict['ent_pub_reg_modify'] = []
            p = self.analysis.parse_page_1(page, 'guquanbiangeng')
            sub_json_dict['ent_pub_equity_change'] = p[u'股权变更信息'] if p.has_key(u'股权变更信息') else []
            p = self.analysis.parse_page_1(page, 'zhishichanquanchuzidengji')
            sub_json_dict['ent_pub_knowledge_property'] = p[u'知识产权出质登记信息'] if p.has_key(u'知识产权出质登记信息') else []
        except Exception as e:
            settings.logger.debug(u"An error ocurred in crawl_ent_pub_pages: %s, types = %d"% (type(e), types))
            raise e
        finally:
            return sub_json_dict

    #爬取 其他部门公示信息 页面
    def crawl_other_dept_pub_pages(self, url):
        sub_json_dict={}
        try:

            page = self.crawl_page_by_url(url)['page']
            xk = self.analysis.parse_page_1(page, 'zizhizigexuke')
            sub_json_dict["other_dept_pub_administration_license"] =  xk[u'设立信息'] if xk.has_key(u'设立信息') else []
            xk =self.analysis.parse_page_1(page, 'xingzhengchufa')
            sub_json_dict["other_dept_pub_administration_sanction"] = xk[u'行政处罚结果信息'] if xk.has_key(u'行政处罚结果信息') else []  # 行政处罚信息
        except Exception as e:
            settings.logger.debug(u"An error ocurred in crawl_other_dept_pub_pages: %s, types = %d"% (type(e), types))
            raise e
        finally:
            return sub_json_dict

    #judical assist pub informations
    def crawl_judical_assist_pub_pages(self, url):
        sub_json_dict={}
        try:
            page = self.crawl_page_by_url(url)['page']
            xz = self.analysis.parse_page_1(page, 'guquandongjie')
            sub_json_dict['judical_assist_pub_equity_freeze'] = xz[u'司法股权冻结信息'] if xz.has_key(u'司法股权冻结信息') else []
            xz = self.analysis.parse_page_1(page, 'gudongbiangeng')
            sub_json_dict['judical_assist_pub_shareholder_modify'] = xz[u'司法股东变更登记信息'] if xz.has_key(u'司法股东变更登记信息') else []
        except Exception as e:
            settings.logger.debug(u"An error ocurred in crawl_other_dept_pub_pages: %s, types = %d"% (type(e), types))
            raise e
        finally:
            return sub_json_dict
        pass

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

    # main function
    def work(self):
        """
        ens = read_ent_from_file("./enterprise_list/guangdong1.txt")
        #os.makedirs("./Guangdong")
        for i, ent in enumerate(ens):
            self.crawl_page_search(urls['page_search'])
            self.crawl_page_captcha(urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent[2])
            self.analyze_showInfo()
            data = self.crawl_page_main()
            self.json_dict[ent[0]] = data
            json_dump_to_file("./guangdong/final_json_%s.json" % ent[0], self.json_dict)
            settings.logger.debug(u"Now %s was finished\n"% ent[0])
        """
        #url = "http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo_06CAc+ibgylJZ6y3lp3JBNsJrQ1qA5gDU7qYIU/VOow9Am1tz4CcjiZg6BZzhZQU-QuOaBlqqlUykdKokb5yijg=="
        #东莞证券
        #url = "http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo_06CAc+ibgylJZ6y3lp3JBNsJrQ1qA5gDU7qYIU/VOow9Am1tz4CcjiZg6BZzhZQU-QuOaBlqqlUykdKokb5yijg=="
        #self.crawl_ind_comm_pub_pages(url, 2)
        #self.crawl_ent_pub_pages(url, 2)
        #self.crawl_other_dept_pub_pages(url, 2)
        #self.crawl_judical_assist_pub_pages(url, 2)

#        datas = html_from_file('next.html')
        #self.analysis.parse_ent_pub_annual_report_page_2(datas, "_detail")
        url = "http://gsxt.gzaic.gov.cn:7001/search/search!entityShow?entityVo.pripid=440100100012003051400230"
        sub_json = self.crawl_ind_comm_pub_pages(url, 1, {'pripid': '440100100012003051400230'})
        #url = "http://gsxt.gzaic.gov.cn:7001/search/search!enterpriseShow?entityVo.pripid=440100100012003051400230#"
        #sub_json = self.crawl_ent_pub_pages(url, 1)
        #url = "http://gsxt.gzaic.gov.cn:7001/search/search!otherDepartShow?entityVo.pripid=440100100012003051400230"
        #sub_json = self.crawl_other_dept_pub_pages(url, 1)
        #url = "http://gsxt.gzaic.gov.cn:7001/search/search!judicialShow?entityVo.pripid=440100100012003051400230"
        #sub_json = self.crawl_judical_assist_pub_pages(url, 1)
        #json_dump_to_file("json_dict.json", sub_json)
        """
        sub_json_dict = {}
        datas = html_from_file('next.html')
        sub_json_dict['guquanbiangeng'] = self.analysis.parse_page_2(datas, 'guquanbiangeng', {})
        json_dump_to_file("crawl_ent_pub_pages.json", sub_json_dict)
        """

    def run(self, ent):
        print "guangdong1"
        sub_json_dict = {}

        pripid = ent[ent.index("pripid")+7: len(ent)]
        url = "http://gsxt.gzaic.gov.cn:7001/search/search!entityShow?entityVo.pripid=" + pripid
        sub_json_dict.update(self.crawl_ind_comm_pub_pages(url, {'pripid': pripid}))
        url = "http://gsxt.gzaic.gov.cn:7001/search/search!enterpriseShow?entityVo.pripid="+ pripid
        sub_json_dict.update(self.crawl_ent_pub_pages(url))
        url = "http://gsxt.gzaic.gov.cn:7001/search/search!otherDepartShow?entityVo.pripid=" + pripid
        sub_json_dict.update(self.crawl_other_dept_pub_pages(url))
        url = "http://gsxt.gzaic.gov.cn:7001/search/search!judicialShow?entityVo.pripid=" + pripid
        sub_json_dict.update(self.crawl_judical_assist_pub_pages(url))
        return sub_json_dict

class Analyze(object):

    crawler = None
    def __init__(self):
        self.Ent = []
        self.json_dict = {}

    def get_raw_text_by_tag(self, tag):
        return tag.get_text().strip()
    #获得表头
    def get_table_title(self, table_tag):
        if table_tag.find('tr'):
            if table_tag.find('tr').find_all('th') :
                if len(table_tag.find('tr').find_all('th')) > 1:
                    return None
                # 处理 <th> aa<span> bb</span> </th>
                if table_tag.find('tr').th.stirng == None and len(table_tag.find('tr').th.contents) > 1:
                    # 处理 <th>   <span> bb</span> </th>  包含空格的
                    if (table_tag.find('tr').th.contents[0]).strip()  :
                        return (table_tag.find('tr').th.contents[0])
                # <th><span> bb</span> </th>
                return self.get_raw_text_by_tag(table_tag.find('tr').th)
            elif table_tag.find('tr').find('td'):
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
            return self.get_raw_text_by_tag(td_tag)

    def get_detail_link(self, bs4_tag, prefix_url = ""):
        if bs4_tag['href'] and bs4_tag['href'] != '#':
            pattern = re.compile(r'http')
            if pattern.search(bs4_tag['href']):
                return bs4_tag['href']
            return prefix_url + bs4_tag['href']
        elif bs4_tag['onclick']:
            pattern = re.compile(r'http')
            if pattern.search(bs4_tag['onclick']):
                return self.get_detail_link_onclick(bs4_tag)
            return prefix_url + self.get_detail_link_onclick(bs4_tag)

    # type = 2 的详细报告的url
    def get_detail_link_onclick(self, bs4_tag):
        re1='.*?'   # Non-greedy match on filler
        re2='(\\\'.*?\\\')' # Single Quote String 1

        rg = re.compile(re1+re2,re.IGNORECASE|re.DOTALL)
        m = rg.search(bs4_tag['onclick'])
        url= ""
        if m:
            strng1=m.group(1)
            url = strng1.strip("\'")
        return url

    def get_columns_of_record_table(self, bs_table, page, table_name):
        tbody = None
        if len(bs_table.find_all('tbody')) > 1:
            if len(bs_table.find_all('tbody')[0].find_all('tr')) >1:
                tbody = bs_table.find_all('tbody')[0]
            else :
                tbody= bs_table.find_all('tbody')[1]
        else:
            tbody = bs_table.find('tbody') or BeautifulSoup(page, 'html5lib').find('tbody')
        tr = None
        if tbody:
            if len(tbody.find_all('tr')) <= 1:
                tr = tbody.find('tr')
                #return None
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
        #settings.logger.debug(u"get_columns_of_record_table->tr:%s\n", tr)
        ret_val=  self.get_record_table_columns_by_tr(tr, table_name)
        #settings.logger.debug(u"table columns:%s\n"% table_name)
        #settings.logger.debug(u"ret_val->%s\n", ret_val)
        return  ret_val

    def get_record_table_columns_by_tr(self, tr_tag, table_name):
        columns = []
        if not tr_tag:
            return columns
        try:
            sub_col_index = 0
            if len(tr_tag.find_all('th'))==0:
                settings.logger.error(u"The table %s has no columns"% table_name)
                return columns
            #排除仅仅出现一列重复的名字
            count = 0
            for i, th in enumerate(tr_tag.find_all('th')):
                col_name = self.get_raw_text_by_tag(th)
                #if col_name and ((col_name, col_name) not in columns) :

                if col_name:
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
            settings.logger.error(u'exception occured in get_table_columns_by_tr, except_type = %s, table_name = %s' % (type(e), table_name))
        finally:
            return columns


    # 如果是第一种： http://gsxt.gzaic.gov.cn:7001/search/search!annalShow?annalVo.id=30307309
    def parse_ent_pub_annual_report_page_1(self, base_page, page_type):
        page_data = {}
        soup = BeautifulSoup(base_page, 'html5lib')
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
                        page_data[table_name] = []
                        columns = self.get_columns_of_record_table(table, base_page, table_name)
                        page_data[table_name] =self.parse_table_1(table, columns, {}, table_name)
            except Exception as e:
                settings.logger.error(u"fail to parse the rest tables with exception %s" %(type(e)))
        else:
            pass
        return page_data

    def parse_page_1(self, page, div_id, post_data={}):
        soup = BeautifulSoup(page, 'html5lib')
        page_data = {}
        if soup.body:
            if soup.body.table:
                try:
                    divs = soup.body.find('div', {"id": div_id})

                    table = None
                    if not divs:
                        table = soup.body.find('table')
                    else :
                        if div_id == 'jibenxinxi':
                            table = divs.find('div').find('table')
                            table_name = self.get_table_title(table)
                            if table_name== None :
                                table_name = div_id
                            page_data[table_name] = []
                            columns = self.get_columns_of_record_table(table, page, table_name)
                            page_data[table_name] =self.parse_table_1(table, columns, post_data, table_name)
                            table = divs.find('table', recursive = False)
                        else:
                            table = divs.find('table')
                    #print table
                    table_name = ""
                    columns = []
                    while table:
                        if table.name == 'table':
                            table_name = self.get_table_title(table)
                            if table_name== None :
                                table_name = div_id
                            #page_data[table_name] = []
                            columns = self.get_columns_of_record_table(table, page, table_name)
                            if columns is not  None:
                                page_data[table_name] =self.parse_table_1(table, columns, post_data, table_name)
                        table = table.nextSibling

                except Exception as e:
                    settings.logger.error(u'parse failed, with exception %s' % e)
                    raise e

                finally:
                    pass
        return page_data

    def parse_table_1(self, bs_table, columns=[] , post_data= {}, table_name= ""):
        table_dict = None
        try:
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
                # 这里注意unicode编码
                next_dicts = {
                    u"主要人员信息" : "http://gsxt.gzaic.gov.cn:7001/search/search!staffListShow?entityVo.pageSize=10&entityVo.curPage=%d&entityVo.pripid=%s",
                    u"分支机构信息":  "http://gsxt.gzaic.gov.cn:7001/search/search!branchListShow?_=1451527284000&entityVo.curPage=%d&entityVo.pripid=%s",
                    u"出资人及出资信息": "http://gsxt.gzaic.gov.cn:7001/search/search!investorListShow?_=1451527307501&entityVo.curPage=%d&entityVo.pripid=%s",
                    u"变更信息" : "http://gsxt.gzaic.gov.cn:7001/search/search!changeListShow?_=1451527321304&entityVo.curPage=%d&entityVo.pripid=%s",
                }
                if next_dicts.has_key(table_name) and post_data :
                    url = next_dicts[table_name]%(1,  post_data['pripid'])
                    res = self.crawler.crawl_page_by_url(url)['page']
                    d = json.loads(res)
                    totalPage = int(d['baseVo']['totalPage'])
                    data_list = []

                    titles = [column[0] for column in columns]
                    if table_name == u"主要人员信息":
                        for i in xrange(totalPage):
                            url = next_dicts[table_name]%(i + 1,  post_data['pripid'])
                            res = self.crawler.crawl_page_by_url(url)['page']
                            d = json.loads(res)
                            data_list.extend([item for item in d['staffList']])
                        for i, model in enumerate(data_list):
                            data = [i+1, model['name'], model['sdutyname']]
                            item_array.append(dict(zip(titles, data)))
                    elif table_name == u"分支机构信息":
                        for i in xrange(totalPage):
                            url = next_dicts[table_name]%(i + 1,  post_data['pripid'])
                            res = self.crawler.crawl_page_by_url(url)['page']
                            d = json.loads(res)
                            data_list.extend([item for item in d['branchList']])
                        for i, model in enumerate(data_list):
                            data = [i+1, model['branchregno'], model['branchentname'], model['sregorgname']]
                            item_array.append(dict(zip(titles, data)))
                    elif table_name == u"出资人及出资信息":
                        for i in xrange(totalPage):
                            url = next_dicts[table_name]%(i + 1,  post_data['pripid'])
                            res = self.crawler.crawl_page_by_url(url)['page']
                            d = json.loads(res)
                            data_list.extend([item for item in d['investorList']])
                        for i, model in enumerate(data_list):
                            data = [ model['sinvenstorname'], model['inv'], model['cardname'], model['cerno']]
                            item_array.append(dict(zip(titles, data)))
                    elif table_name == u"变更信息":
                        for i in xrange(totalPage):
                            url = next_dicts[table_name]%(i + 1,  post_data['pripid'])
                            res = self.crawler.crawl_page_by_url(url)['page']
                            d = json.loads(res)
                            data_list.extend([item for item in d['changeList']])
                        for i, model in enumerate(data_list):
                            data = [ model['sname'], model['altbe'], model['altaf'], model['altdate']]
                            item_array.append(dict(zip(titles, data)))
                    table_dict = item_array
                else:
                    if not tbody:
                        #records_tag = bs_table
                        records_tag = bs_table
                    else:
                        records_tag = tbody
                    for tr in records_tag.find_all('tr'):
                        if tr.find('td') and len(tr.find_all('td', recursive=False)) % column_size == 0:
                            col_count = 0
                            item = {}
                            print "table_name=%s"%table_name
                            for td in tr.find_all('td',recursive=False):
                                if td.find('a'):
                                    next_url = self.get_detail_link(td.find('a'), urls['prefix_url_1'])
                                    #has detail link
                                    if next_url:
                                        detail_page = self.crawler.crawl_page_by_url(next_url)
                                        #html_to_file("next.html", detail_page['page'])
                                        if table_name == u'基本信息':
                                            page_data = self.parse_ent_pub_annual_report_page_1(detail_page['page'], table_name+ '_detail')
                                            item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                            item[u'详情'] = page_data
                                        else:
                                            page_data = self.parse_page_2(detail_page['page'], table_name + '_detail')
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
                        elif tr.find('td') and len(tr.find_all('td', recursive=False)) == col_span and col_span != column_size:
                            col_count = 0
                            sub_col_index = 0
                            item = {}
                            sub_item = {}
                            for td in tr.find_all('td',recursive=False):
                                if td.find('a'):
                                    #try to retrieve detail link from page
                                    next_url = self.get_detail_link(td.find('a'), urls['prefix_url_1'])
                                    #has detail link
                                    if next_url:
                                        detail_page = self.crawler.crawl_page_by_url(next_url)['page']
                                        #html_to_file("next.html", detail_page['page'])

                                        if table_name == u'基本信息':
                                            page_data = self.parse_ent_pub_annual_report_page_1(detail_page['page'], table_name+ '_detail')
                                            item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                            item[u'详情'] = page_data
                                        else:
                                            page_data = self.parse_page_2(detail_page['page'], table_name + '_detail')
                                            item[columns[col_count][0]] = page_data #this may be a detail page data
                                    else:
                                        #item[columns[col_count]] = CrawlerUtils.get_raw_text_in_bstag(td)
                                        item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                else:
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
        settings.logger.error(u"There is no path : %s"% path )
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


class Guangdong1(object):
    def __init__(self):
        self.analysis = Analyze()
        self.crawler = Crawler(self.analysis)
        self.analysis.crawler = self.crawler

    def run(self, url):
        return self.crawler.run(url)
    def work(self):
        self.crawler.work()

"""
if __name__ == "__main__":
    reload (sys)
    sys.setdefaultencoding('utf8')
    guangdong = Guangdong1()
    guangdong.work()
"""
