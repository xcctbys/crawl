#!/usr/local/bin/python
# encoding=utf-8

import requests
import logging
import os
import sys
import time
import re
import json
import urlparse
import urllib
import codecs
from bs4 import BeautifulSoup
import datetime
import gevent
from gevent import Greenlet

import gevent.monkey

import unittest


def exe_time(func):
    """
        装饰器，在调试协程时候用到；用于查看调用顺序
    """

    def fnc(*args, **kwargs):
        start = datetime.datetime.now()
        print "call " + func.__name__ + "()..."
        print func.__name__ + " start :" + str(start)
        func(*args, **kwargs)
        end = datetime.datetime.now()
        print func.__name__ + " end :" + str(end)

    return fnc


def get_cookie(url):
    """
        获取浏览的cookie信息
    """
    g = ghost.Ghost()
    cookiedict = []
    cookiestr = ""
    with g.start() as se:
        se.wait_timeout = 999
        mycookielist = []
        page, extra_resources = se.open(url)
        for element in se.cookies:
            mycookielist.append(element.toRawForm().split(";"))
        # for item in mycookielist:
        #     cookiedict.update( reduce(lambda x,y: {x: y},  item[0].split("=")) )
        cookiestr = reduce(lambda x, y: x[0] + ";" + y[0], mycookielist)
    return cookiestr


class Crawler(object):
    analysis = None

    def __init__(self, req=None):
        headers = {
            'Connetion': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language':
            'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            "User-Agent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:46.0) Gecko/20100101 Firefox/46.0",
    # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"
        }
        if req:
            self.request = req

        else:
            self.request = requests.Session()
            self.request.headers.update(headers)
            adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
            self.request.mount('http://', adapter)
        self.ents = []
        self.json_dict = {}
        self.timeout = (30, 20)

    # 爬取 工商公示信息 页面
    @exe_time
    def crawl_ind_comm_pub_pages(self, url, types, post_data={}):
        sub_json_dict = {}
        prefix_GSpublicity = 'aiccips/GSpublicity/GSpublicityList.html'
        try:

            @exe_time
            def entInfo():
                div_name = 'jibenxinxi'
                url = "%s/%s?service=%s" % (self.urls['host'], prefix_GSpublicity, 'entInfo')    # 登记信息
                page = self.request_by_method('POST', url, data=post_data)
                dict_jiben = self.analysis.parse_page_2(page, div_name, post_data)
                sub_json_dict['ind_comm_pub_reg_modify'] = dict_jiben[u'变更信息'] if dict_jiben.has_key(u"变更信息") else {}
                sub_json_dict['ind_comm_pub_reg_basic'] = dict_jiben[u'基本信息'] if dict_jiben.has_key(u"基本信息") else []
                sub_json_dict['ind_comm_pub_reg_shareholder'] = dict_jiben[u'股东信息'] if dict_jiben.has_key(
                    u"股东信息") else []

            @exe_time
            def entCheckInfo():
                div_name = 'beian'
                url = "%s/%s?service=%s" % (self.urls['host'], prefix_GSpublicity, 'entCheckInfo')    #备案信息
                page = self.request_by_method('POST', url, data=post_data)
                # print page.encode('utf8')
                dict_beian = self.analysis.parse_page_2(page, div_name, post_data)
                sub_json_dict['ind_comm_pub_arch_key_persons'] = dict_beian[u'主要人员信息'] if dict_beian.has_key(
                    u"主要人员信息") else []
                sub_json_dict['ind_comm_pub_arch_branch'] = dict_beian[u'分支机构信息'] if dict_beian.has_key(
                    u"分支机构信息") else []
                sub_json_dict['ind_comm_pub_arch_liquidation'] = dict_beian[u"清算信息"] if dict_beian.has_key(
                    u'清算信息') else []

            @exe_time
            def stockInfo():
                div_name = 'guquanchuzhi'
                url = "%s/%s?service=%s" % (self.urls['host'], prefix_GSpublicity, 'curStoPleInfo')    #股权出质
                page = self.request_by_method('POST', url, data=post_data)
                dj = self.analysis.parse_page_2(page, div_name, post_data)
                sub_json_dict['ind_comm_pub_equity_ownership_reg'] = dj[u'股权出质登记信息'] if dj.has_key(u'股权出质登记信息') else []

            @exe_time
            def pleInfo():
                div_name = 'dongchandiya'
                url = "%s/%s?service=%s" % (self.urls['host'], prefix_GSpublicity, 'pleInfo')    #动产抵押登记信息
                page = self.request_by_method('POST', url, data=post_data)
                dj = self.analysis.parse_page_2(page, div_name, post_data)
                sub_json_dict['ind_comm_pub_movable_property_reg'] = dj[u'动产抵押信息'] if dj.has_key(u'动产抵押信息') else []

            @exe_time
            def penaltyInfo():
                div_name = 'xingzhengchufa'
                url = "%s/%s?service=%s" % (self.urls['host'], prefix_GSpublicity, 'cipPenaltyInfo')    #行政处罚
                page = self.request_by_method('POST', url, data=post_data)
                dj = self.analysis.parse_page_2(page, div_name, post_data)
                sub_json_dict['ind_comm_pub_administration_sanction'] = dj[u'行政处罚信息'] if dj.has_key(u'行政处罚信息') else []

            @exe_time
            def exceptionInfo():
                div_name = 'jingyingyichang'
                url = "%s/%s?service=%s" % (self.urls['host'], prefix_GSpublicity, 'cipUnuDirInfo')    #经营异常
                page = self.request_by_method('POST', url, data=post_data)
                dj = self.analysis.parse_page_2(page, div_name, post_data)
                sub_json_dict['ind_comm_pub_business_exception'] = dj[u'经营异常信息'] if dj.has_key(u'经营异常信息') else []

            @exe_time
            def blackInfo():
                div_name = 'yanzhongweifa'
                url = "%s/%s?service=%s" % (self.urls['host'], prefix_GSpublicity, 'cipBlackInfo')    #严重违法
                page = self.request_by_method('POST', url, data=post_data)
                dj = self.analysis.parse_page_2(page, div_name, post_data)
                sub_json_dict['ind_comm_pub_serious_violate_law'] = dj[u'严重违法信息'] if dj.has_key(u'严重违法信息') else []

            @exe_time
            def spotCheckInfo():
                div_name = 'chouchajiancha'
                url = "%s/%s?service=%s" % (self.urls['host'], prefix_GSpublicity, 'cipSpotCheInfo')    #抽查检查
                page = self.request_by_method('POST', url, data=post_data)
                dj = self.analysis.parse_page_2(page, div_name, post_data)
                sub_json_dict['ind_comm_pub_spot_check'] = dj[u'抽查检查信息'] if dj.has_key(u'抽查检查信息') else []

            threads = []
            threads.append(gevent.spawn(entInfo))
            threads.append(gevent.spawn(entCheckInfo))
            threads.append(gevent.spawn(stockInfo))
            threads.append(gevent.spawn(pleInfo))
            threads.append(gevent.spawn(penaltyInfo))
            threads.append(gevent.spawn(exceptionInfo))
            threads.append(gevent.spawn(blackInfo))
            threads.append(gevent.spawn(spotCheckInfo))

            gevent.joinall(threads)
        except Exception as e:
            logging.error(u"An error ocurred in crawl_ind_comm_pub_pages: %s, type is %d" % (type(e), types))
            raise e
        finally:
            self.json_dict.update(sub_json_dict)
    #爬取 企业公示信息 页面
    @exe_time
    def crawl_ent_pub_pages(self, url, types, post_data={}):
        sub_json_dict = {}
        try:

            @exe_time
            def report():
                url = "%s/%s" % (self.urls['host'], "aiccips/BusinessAnnals/BusinessAnnalsList.html")
                page = self.request_by_method('POST', url, data=post_data)
                # print page.encode('utf8')
                p = self.analysis.parse_page_2(page, 'qiyenianbao', post_data)
                sub_json_dict['ent_pub_ent_annual_report'] = p[u'企业年报'] if p.has_key(u'企业年报') else []

            @exe_time
            def permission():
                url = "%s/%s" % (self.urls['host'], "aiccips/AppPerInformation.html")
                page = self.request_by_method('POST', url, data=post_data)
                p = self.analysis.parse_page_2(page, 'appPer', post_data)
                sub_json_dict['ent_pub_administration_license'] = p[u'行政许可情况'] if p.has_key(u'行政许可情况') else []

            @exe_time
            def sanction():
                url = "%s/%s" % (self.urls['host'], "aiccips/XZPunishmentMsg.html")
                page = self.request_by_method('POST', url, data=post_data)
                p = self.analysis.parse_page_2(page, 'xzpun', post_data)
                sub_json_dict['ent_pub_administration_sanction'] = p[u'行政处罚情况'] if p.has_key(u'行政处罚情况') else []

            @exe_time
            def shareholder():
                url = "%s/%s" % (self.urls['host'], "aiccips/ContributionCapitalMsg.html")
                page = self.request_by_method('POST', url, data=post_data)
                p = self.analysis.parse_page(page, 'sifapanding', post_data)
                sub_json_dict['ent_pub_shareholder_capital_contribution'] = p[u'股东及出资信息'] if p.has_key(
                    u'股东及出资信息') else []
                sub_json_dict['ent_pub_reg_modify'] = p[u'变更信息'] if p.has_key(u'变更信息') else []

            @exe_time
            def change():
                url = "%s/%s" % (self.urls['host'], "aiccips/GDGQTransferMsg/shareholderTransferMsg.html")
                page = self.request_by_method('POST', url, data=post_data)
                p = self.analysis.parse_page_2(page, 'guquanbiangeng', post_data)
                sub_json_dict['ent_pub_equity_change'] = p[u'股权变更信息'] if p.has_key(u'股权变更信息') else []

            @exe_time
            def properties():
                url = "%s/%s" % (self.urls['host'], "aiccips/intPropertyMsg.html")
                page = self.request_by_method('POST', url, data=post_data)
                p = self.analysis.parse_page_2(page, 'inproper', post_data)
                sub_json_dict['ent_pub_knowledge_property'] = p[u'知识产权出质登记信息'] if p.has_key(u'知识产权出质登记信息') else []

            threads = []
            threads.append(gevent.spawn(report))
            threads.append(gevent.spawn(permission))
            threads.append(gevent.spawn(sanction))
            threads.append(gevent.spawn(shareholder))
            threads.append(gevent.spawn(change))
            threads.append(gevent.spawn(properties))
            gevent.joinall(threads)
        except Exception as e:
            logging.error(u"An error ocurred in crawl_ent_pub_pages: %s, types = %d" % (type(e), types))
            raise e
        finally:
            self.json_dict.update(sub_json_dict)

    #爬取 其他部门公示信息 页面
    @exe_time
    def crawl_other_dept_pub_pages(self, url, types, post_data={}):
        sub_json_dict = {}
        try:

            def permission():
                url = "%s/%s" % (self.urls['host'], "aiccips/OtherPublicity/environmentalProtection.html")
                page = self.request_by_method('POST', url, data=post_data)
                xk = self.analysis.parse_page_2(page, "xzxk", post_data)
                sub_json_dict["other_dept_pub_administration_license"] = xk[u'行政许可信息'] if xk.has_key(u'行政许可信息') else []

            def sanction():
                url = "%s/%s" % (self.urls['host'], "aiccips/OtherPublicity/environmentalProtection.html")
                page = self.request_by_method('POST', url, data=post_data)
                xk = self.analysis.parse_page_2(page, "czcf", post_data)
                sub_json_dict["other_dept_pub_administration_sanction"] = xk[u'行政处罚信息'] if xk.has_key(u'行政处罚信息') else [
                ]    # 行政处罚信息

            threads = []
            threads.append(gevent.spawn(permission))
            threads.append(gevent.spawn(sanction))
            gevent.joinall(threads)
        except Exception as e:
            logging.error(u"An error ocurred in crawl_other_dept_pub_pages: %s, types = %d" % (type(e), types))
            raise e
        finally:
            self.json_dict.update(sub_json_dict)

    #judical assist pub informations
    @exe_time
    def crawl_judical_assist_pub_pages(self, url, types, post_data={}):
        sub_json_dict = {}
        try:

            def freezeInfo():
                url = "%s/%s" % (self.urls['host'], "aiccips/judiciaryAssist/judiciaryAssistInit.html")
                page = self.request_by_method('POST', url, data=post_data)
                xz = self.analysis.parse_page_2(page, 'guquandongjie', post_data)
                sub_json_dict['judical_assist_pub_equity_freeze'] = xz[u'司法股权冻结信息'] if xz.has_key(u'司法股权冻结信息') else []

            def modifyInfo():
                url = "%s/%s" % (self.urls['host'], "aiccips/sfGuQuanChange/guQuanChange.html")
                page = self.request_by_method('POST', url, data=post_data)
                xz = self.analysis.parse_page_2(page, 'gudongbiangeng', post_data)
                sub_json_dict['judical_assist_pub_shareholder_modify'] = xz[u'司法股东变更登记信息'] if xz.has_key(
                    u'司法股东变更登记信息') else []

            threads = []
            threads.append(gevent.spawn(freezeInfo))
            threads.append(gevent.spawn(modifyInfo))
            gevent.joinall(threads)
        except Exception as e:
            logging.error(u"An error ocurred in crawl_other_dept_pub_pages: %s, types = %d" % (type(e), types))
            raise e
        finally:
            self.json_dict.update(sub_json_dict)

    def request_by_method(self, method, url, *args, **kwargs):
        r = None
        try:
            r = self.request.request(method, url, *args, **kwargs)
        except requests.Timeout as err:
            logging.error(u'Getting url: %s timeout. %s .' % (url, err.message))
            return False
        except Exception as err:
            logging.error(u'Getting url: %s exception:%s . %s .' % (url, type(err), err.message))
            return False
        if r.status_code != 200:
            logging.error(u"Something wrong when getting url:%s , status_code=%d", url, r.status_code)
            return False
        return r.text

    def run(self, ent):
        url = ent
        page_entInfo = self.request_by_method('GET', url)    #self.crawl_page_by_url(url)['page']
        post_data = self.analysis.parse_page_data_2(page_entInfo)
        self.crawl_ind_comm_pub_pages(url, 2, post_data)
        # url = "http://gsxt.gdgs.gov.cn/aiccips/BusinessAnnals/BusinessAnnalsList.html"
        self.crawl_ent_pub_pages(url, 2, post_data)
        # url = "http://gsxt.gdgs.gov.cn/aiccips/OtherPublicity/environmentalProtection.html"
        self.crawl_other_dept_pub_pages(url, 2, post_data)
        # url = "http://gsxt.gdgs.gov.cn/aiccips/judiciaryAssist/judiciaryAssistInit.html"
        self.crawl_judical_assist_pub_pages(url, 2, post_data)
        return self.json_dict

    def run_asyn(self, url):
        gevent.monkey.patch_socket()
        threads = []
        # cookies = get_cookie(url)
        # print cookies
        # cookies = {"__jsluid":"0310175ec8b141ee15613e2c0ad95dfe" , "__jsl_clearance":"1463469056.082|0|I2ZEEWsFDuyXH0KYg1GV1Xe9JkE%3D"}
        # for key, value in cookies.items():
        #     self.request.cookies[str(key)] = str(value)
        # heads={}
        # cookies="__jsluid=0310175ec8b141ee15613e2c0ad95dfe;__jsl_clearance=1463469056.082|0|I2ZEEWsFDuyXH0KYg1GV1Xe9JkE%3D"
        # self.request.headers["Cookie"] = str(cookies)

        # heads['Cookie'] = str(cookies)
        page_entInfo = self.request_by_method('GET', url)
        # print page_entInfo
        # print self.request.cookies.keys()
        if not page_entInfo:
            logging.error("Can't get page %s ." % (url))
            return {}
        post_data = self.analysis.parse_page_data_2(page_entInfo)

        threads.append(gevent.spawn(self.crawl_ind_comm_pub_pages, url, 2, post_data))
        threads.append(gevent.spawn(self.crawl_ent_pub_pages, url, 2, post_data))
        threads.append(gevent.spawn(self.crawl_other_dept_pub_pages, url, 2, post_data))
        threads.append(gevent.spawn(self.crawl_judical_assist_pub_pages, url, 2, post_data))
        gevent.joinall(threads)

        return self.json_dict


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
            if table_tag.find('tr').find_all('th'):

                if len(table_tag.find('tr').find_all('th')) > 1:
                    return None
                # 处理 <th> aa<span> bb</span> </th>
                if table_tag.find('tr').th.stirng == None and len(table_tag.find('tr').th.contents) > 1:
                    # 处理 <th>   <span> bb</span> </th>  包含空格的
                    if (table_tag.find('tr').th.contents[0]).strip():
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
                columns.append((self.get_raw_text_by_tag(th), self.get_raw_text_by_tag(th)))
            else:
                #if has sub-sub columns
                columns.append((self.get_raw_text_by_tag(th), self.get_sub_columns(tr_tag.nextSibling.nextSibling, 0,
                                                                                   self.sub_column_count(th))))
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
                logging.error('column head size != column data size, columns head = %s, columns data = %s' %
                              (columns, multi_col_tag.contents))
                return data

            for id, col in enumerate(columns):
                data[col[0]] = self.get_column_data(col[1], multi_col_tag.find_all('td', recursive=False)[id])
            return data
        else:
            return self.get_raw_text_by_tag(td_tag)

    def get_detail_link(self, bs4_tag):
        if bs4_tag.has_attr('onclick'):
            url = self.get_detail_link_onclick(bs4_tag['onclick'])
            return url

        elif bs4_tag.has_attr('href') and bs4_tag['href'] != '#':
            pattern = re.compile(r'http')
            if pattern.search(bs4_tag['href']):

                return bs4_tag['href']
            return None

    def get_detail_link_onclick(self, bs4_tag):
        var_re = '((?:[a-z][a-z0-9_]*))'    # Variable Name 1
        m = re.compile(var_re, re.IGNORECASE | re.DOTALL).search(bs4_tag)
        if m:
            var_str = m.group(1)
            var = var_str.strip("'")
            if var == "toDetail":
                # toDetail('a94afb64-ce89-4158-88a9-dd1eb32797bf','有效')
                # "http://gsxt.gdgs.gov.cn/aiccips/detailedness?id="+id+"&status="+encodeURI(status));
                m2 = re.compile('.*?(\'.*?\').*?(\'.*?\')', re.IGNORECASE | re.DOTALL).search(bs4_tag)
                if m2:
                    id_str = m2.group(1).strip("\'")
                    status_str = m2.group(2).strip("\'")
                    query_param = urllib.urlencode({'id': id_str, 'status': status_str.encode('utf8')})
                    url = "%s/%s" % (self.urls['host'], "aiccips/detailedness?" + query_param)
                    return url

        re1 = '.*?'    # Non-greedy match on filler
        re2 = '(\\\'.*?\\\')'    # Single Quote String 1

        rg = re.compile(re1 + re2, re.IGNORECASE | re.DOTALL)
        m = rg.search(bs4_tag)
        url = ""
        if m:
            strng1 = m.group(1)
            url = strng1.strip("\'")
        return url

    def get_columns_of_record_table(self, bs_table, page, table_name):
        tbody = None
        if len(bs_table.find_all('tbody')) > 1:
            tbody = bs_table.find_all('tbody')[1]
        else:
            tbody = bs_table.find('tbody') or BeautifulSoup(page, 'html5lib').find('tbody')

        tr = None
        if tbody:
            if len(tbody.find_all('tr')) <= 1:
                #tr = tbody.find('tr')
                tr = None
            else:
                tr = tbody.find_all('tr')[1]
                if not tr.find('th'):
                    tr = tbody.find_all('tr')[0]
                elif tr.find('td'):
                    tr = None
        else:
            if len(bs_table.find_all('tr')) <= 1:
                return None
            elif bs_table.find_all('tr')[0].find('th') and not bs_table.find_all('tr')[0].find('td') and len(
                    bs_table.find_all('tr')[0].find_all('th')) > 1:
                tr = bs_table.find_all('tr')[0]
            elif bs_table.find_all('tr')[1].find('th') and not bs_table.find_all('tr')[1].find('td') and len(
                    bs_table.find_all('tr')[1].find_all('th')) > 1:
                tr = bs_table.find_all('tr')[1]
        ret_val = self.get_record_table_columns_by_tr(tr, table_name)
        return ret_val

    def get_record_table_columns_by_tr(self, tr_tag, table_name):
        columns = []
        if not tr_tag:
            return columns
        try:
            sub_col_index = 0
            if len(tr_tag.find_all('th')) == 0:
                logging.error(u"The table %s has no columns" % table_name)
                return columns
            #排除仅仅出现一列重复的名字
            count = 0
            for i, th in enumerate(tr_tag.find_all('th')):
                col_name = self.get_raw_text_by_tag(th)
                if col_name:
                    if ((col_name, col_name) in columns):
                        col_name = col_name + '_'
                        count += 1
                    if not self.sub_column_count(th):
                        columns.append((col_name, col_name))
                    else:    #has sub_columns
                        if not len(tr_tag.nextSibling.nextSibling.find_all('th')):
                            columns.append((col_name, col_name))
                            continue
                        columns.append((col_name, self.get_sub_columns(tr_tag.nextSibling.nextSibling, sub_col_index,
                                                                       self.sub_column_count(th))))
                        sub_col_index += self.sub_column_count(th)

            if count == len(tr_tag.find_all('th')) / 2:
                columns = columns[:len(columns) / 2]

        except Exception as e:
            logging.error(u'exception occured in get_table_columns, except_type = %s, table_name = %s' %
                          (type(e), table_name))
        finally:
            return columns

    def parse_ent_pub_annual_report_page_2(self, base_page, page_type):

        page_data = {}
        soup = BeautifulSoup(base_page, 'html5lib')
        if soup.body.find('table'):
            try:
                base_table = soup.body.find('table')
                table_name = u'企业基本信息'    #self.get_table_title(base_table)
                #这里需要连续两个nextSibling，一个nextSibling会返回空
                detail_base_table = base_table.nextSibling.nextSibling
                if detail_base_table.name == 'table':
                    page_data[table_name] = self.parse_table_2(detail_base_table)
                    pass
                else:
                    logging.error(u"Can't find details of base informations for annual report")
            except Exception as e:
                logging.error(u"fail to get table name with exception %s" % (type(e)))
            try:
                table = detail_base_table.nextSibling.nextSibling
                while table:
                    if table.name == 'table':
                        table_name = self.get_table_title(table)
                        page_data[table_name] = []
                        columns = self.get_columns_of_record_table(table, base_page, table_name)
                        page_data[table_name] = self.parse_table_2(table, columns, {}, table_name)
                    table = table.nextSibling
            except Exception as e:
                logging.error(u"fail to parse the rest tables with exception %s" % (type(e)))

        return page_data

    def parse_page_data_2(self, page):
        data = {"aiccipsUrl": "", "entNo": "", "entType": "", "regOrg": "", }
        try:
            soup = BeautifulSoup(page, "html5lib")
            data['aiccipsUrl'] = soup.find("input", {"id": "aiccipsUrl"})['value']
            data['entNo'] = soup.find("input", {"id": "entNo"})['value']
            data['entType'] = soup.find("input", {"id": "entType"})['value'].strip() + "++"
            data['regOrg'] = soup.find("input", {"id": "regOrg"})['value']

        except Exception as e:
            logging.error(u"parse page failed in function parse_page_data_2\n")
            raise e
        finally:
            return data

    def get_particular_table(self, table, page):
        """ 获取 股东及出资信息的表格，按照指定格式输出
        """
        table_dict = {}
        sub_dict = {}
        table_list = []
        try:
            trs = table.find_all('tr')
            for tr in trs:
                if tr.find('td'):
                    tds = tr.find_all('td')
                    table_dict[u'股东'] = self.get_raw_text_by_tag(tds[0])
                    table_dict[u'股东类型'] = self.get_raw_text_by_tag(tds[1])
                    sub_dict = {}
                    sub_dict[u'认缴出资额（万元）'] = self.get_raw_text_by_tag(tds[2])
                    sub_dict[u'认缴出资方式'] = self.get_raw_text_by_tag(tds[3])
                    sub_dict[u'认缴出资日期'] = self.get_raw_text_by_tag(tds[4])
                    table_dict['认缴明细'] = sub_dict
                    sub_dict = {}
                    sub_dict[u'实缴出资额（万元）'] = self.get_raw_text_by_tag(tds[5])
                    sub_dict[u'实缴出资方式'] = self.get_raw_text_by_tag(tds[6])
                    sub_dict[u'实缴出资时间'] = self.get_raw_text_by_tag(tds[7])
                    table_dict['实缴明细'] = sub_dict

                    table_dict['实缴额（万元）'] = self.get_raw_text_by_tag(tds[5])
                    table_dict['认缴额（万元）'] = self.get_raw_text_by_tag(tds[2])
                    table_list.append(table_dict)
        except Exception as e:
            logging.error(u'parse 股东及出资信息 table failed! : %s' % e)
        return table_list

    def parse_page_2(self, page, div_id, post_data={}):
        soup = BeautifulSoup(page, 'html5lib')
        page_data = {}
        if soup.body:
            if soup.body.table:
                try:
                    divs = soup.body.find('div', {"id": div_id})
                    table = None
                    if not divs:
                        table = soup.body.find('table')
                    else:
                        table = divs.find('table')
                    table_name = ""
                    columns = []
                    while table:
                        if table.name == 'table':
                            table_name = self.get_table_title(table)
                            if table_name is None:
                                table_name = div_id
                            if table_name == u'股东及出资信息':
                                page_data[table_name] = self.get_particular_table(table, page)
                                table = table.nextSibling
                                continue
                            page_data[table_name] = []
                            columns = self.get_columns_of_record_table(table, page, table_name)
                            result = self.parse_table_2(table, columns, post_data, table_name)
                            if not columns and not result:
                                del page_data[table_name]
                            else:
                                page_data[table_name] = result

                        elif table.name == 'div':
                            if not columns:
                                logging.error(u"Can not find columns when parsing page 2, table :%s" % div_id)
                                break
                            page_data[table_name] = self.parse_table_2(table, columns, post_data, table_name)
                            columns = []
                        table = table.nextSibling

                except Exception as e:
                    logging.error(u'parse failed, with exception %s' % e)
                    raise e

                finally:
                    pass
        return page_data

    def parse_page(self, page, div_id, post_data={}):
        soup = BeautifulSoup(page, 'html5lib')
        page_data = {}
        if soup.body:
            if soup.body.table:
                try:
                    divs = soup.body.find('div', {"id": div_id})
                    table = None
                    if not divs:
                        table = soup.body.find('table')
                    else:
                        table = divs.find('table')
                    table_name = ""
                    columns = []
                    while table:
                        if table.name == 'table':
                            table_name = self.get_table_title(table)
                            if table_name is None:
                                table_name = div_id

                            page_data[table_name] = []
                            columns = self.get_columns_of_record_table(table, page, table_name)
                            result = self.parse_table_2(table, columns, post_data, table_name)
                            if not columns and not result:
                                del page_data[table_name]
                            else:
                                page_data[table_name] = result

                        elif table.name == 'div':
                            if not columns:
                                logging.error(u"Can not find columns when parsing page, table :%s" % div_id)
                                break
                            page_data[table_name] = self.parse_table_2(table, columns, post_data, table_name)
                            columns = []
                        table = table.nextSibling

                except Exception as e:
                    logging.error(u'parse failed, with exception %s' % e)
                    raise e

                finally:
                    pass
        return page_data

    def parse_table_2(self, bs_table, columns=[], post_data={}, table_name=""):
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
                # <div> <table>数据</table><table>下一页</table> </div>
                tables = bs_table.find_all('table')
                if len(tables) == 2 and tables[1].find('a'):
                    # 获取下一页的url
                    clickstr = tables[1].find('a')['onclick']

                    re1 = '.*?'    # Non-greedy match on filler
                    re2 = '\\\'.*?\\\''    # Uninteresting: strng
                    re3 = '.*?'    # Non-greedy match on filler
                    re4 = '(\\\'.*?\\\')'    # Single Quote String 1
                    re5 = '.*?'    # Non-greedy match on filler
                    re6 = '(\\\'.*?\\\')'    # Single Quote String 2

                    rg = re.compile(re1 + re2 + re3 + re4 + re5 + re6, re.IGNORECASE | re.DOTALL)
                    m = rg.search(clickstr)
                    url = ""
                    if m:
                        string1 = m.group(1)
                        string2 = m.group(2)
                        url = string1.strip('\'') + string2.strip('\'')
                        logging.error(u"url = %s\n" % url)
                    data = {
                        "pageNo": 2,
                        "entNo": post_data["entNo"].encode('utf-8'),
                        "regOrg": post_data["regOrg"],
                        "entType": post_data["entType"].encode('utf-8'),
                    }
                    res = self.crawler.request_by_method('POST',
                                                         url,
                                                         data=data,
                                                         headers={
                                                             'Content-Type':
                                                             'application/x-www-form-urlencoded; charset=UTF-8',
                                                         })
                    if table_name == u"变更信息":
                        # chaToPage
                        d = json.loads(res)
                        titles = [column[0] for column in columns]
                        for i, model in enumerate(d['list']):
                            data = [model['altFiledName'], model['altBe'], model['altAf'], model['altDate']]
                            item_array.append(dict(zip(titles, data)))
                    elif table_name == u"主要人员信息":
                        # vipToPage
                        d = json.loads(res, encoding="utf-8")
                        titles = [column[0] for column in columns]
                        for i, model in enumerate(d['list']):
                            data = [i + 1, model['name'], model['position']]
                            item_array.append(dict(zip(titles, data)))

                    elif table_name == u"分支机构信息":
                        #braToPage
                        d = json.loads(res)
                        titles = [column[0] for column in columns]
                        for i, model in enumerate(d['list']):
                            data = [i + 1, model['regNO'], model['brName'], model['regOrg']]
                            item_array.append(dict(zip(titles, data)))

                    elif table_name == u"股东信息":
                        d = json.loads(res)
                        titles = [column[0] for column in columns]
                        surl = self.urls['host'] + "/aiccips/GSpublicity/invInfoDetails.html?" + "entNo=" + str(
                            post_data['entNo']) + "&regOrg=" + str(post_data['regOrg'])
                        for model in (d['list']):
                            # 详情
                            nurl = surl + "&invNo=" + str(model['invNo'])
                            nres = self.crawler.request_by_method('GET', nurl)
                            detail_page = self.parse_page_2(nres, table_name + '_detail')
                            data = [model['invType'], model['inv'], model['certName'], model['certNo'], detail_page]
                            item_array.append(dict(zip(titles, data)))

                    table_dict = item_array

                else:

                    if not tbody:
                        records_tag = tables[0]
                    else:
                        records_tag = tbody
                    for tr in records_tag.find_all('tr'):
                        if tr.find('td') and len(tr.find_all('td', recursive=False)) % column_size == 0:
                            col_count = 0
                            item = {}
                            # print "table_name=%s"%table_name.encode('utf8')
                            for td in tr.find_all('td', recursive=False):
                                if td.find('a'):
                                    next_url = self.get_detail_link(td.find('a'))
                                    # print next_url
                                    if re.match(r"http", next_url):
                                        detail_page = self.crawler.request_by_method('GET', next_url)
                                        if table_name == u'企业年报':
                                            #logging.error(u"next_url = %s, table_name= %s\n", detail_page['url'], table_name)
                                            page_data = self.parse_ent_pub_annual_report_page_2(detail_page,
                                                                                                table_name + '_detail')
                                            item[columns[col_count][0]] = self.get_column_data(columns[col_count][1],
                                                                                               td)

                                            item[u'详情'] = page_data

                                        else:
                                            page_data = self.parse_page_2(detail_page, table_name + '_detail')
                                            item[columns[col_count][0]] = page_data    #this may be a detail page data
                                    else:
                                        item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                else:
                                    item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                col_count += 1
                                if col_count == column_size:
                                    item_array.append(item.copy())
                                    col_count = 0
                        #this case is for the ind-comm-pub-reg-shareholders----details'table
                        elif tr.find('td') and len(tr.find_all(
                                'td', recursive=False)) == col_span and col_span != column_size:
                            col_count = 0
                            sub_col_index = 0
                            item = {}
                            sub_item = {}
                            for td in tr.find_all('td', recursive=False):
                                if td.find('a'):
                                    #try to retrieve detail link from page
                                    next_url = self.get_detail_link(td.find('a'))
                                    if next_url:
                                        detail_page = self.crawler.request_by_method('GET', next_url)

                                        if table_name == u'企业年报':
                                            #logging.error(u"2next_url = %s, table_name= %s\n", next_url, table_name)

                                            page_data = self.parse_ent_pub_annual_report_page_2(detail_page,
                                                                                                table_name + '_detail')

                                            item[columns[col_count][0]] = self.get_column_data(columns[col_count][1],
                                                                                               td)
                                            item[u'详情'] = page_data

                                        else:
                                            page_data = self.parse_page_2(detail_page, table_name + '_detail')
                                            item[columns[col_count][0]] = page_data    #this may be a detail page data
                                    else:
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


class Guangdong2(object):
    urls = {'host': 'http://gsxt.gdgs.gov.cn', }

    def __init__(self, req=None, ent_number=None):
        self.analysis = Analyze()
        self.crawler = Crawler(req)
        self.crawler.analysis = self.analysis
        self.analysis.crawler = self.crawler
        self.analysis.ent_num = ent_number
        self.crawler.ent_num = ent_number
        self.crawler.urls = self.urls
        self.analysis.urls = self.urls

    def run(self, url):
        return self.crawler.run(url)

    def run_asyn(self, url):
        return self.crawler.run_asyn(url)

# class Guangdong2Test(unittest.TestCase):

#     def setUp(self):
#         unittest.TestCase.setUp(self)

#     # @unittest.skip("skipping")
#     def test_crawl_ind_comm_pub_pages(self):
#         ent_str = "http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo_GmjYOaEEX9Xx3eeM0JcrtOywZcfQzs3Ry0M6NPS1/iCr+cQwm+oHVoPBzdIqEiYb-7vusEl1hPU+qjV70QwcUXQ=="
#         guangdong = Guangdong2()
#         result = guangdong.run_asyn(ent_str)
#         self.assertTrue(result)
#         print result

# if __name__ == "__main__":
#     unittest.main()
