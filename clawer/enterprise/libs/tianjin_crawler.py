#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import logging
import os
import sys
import time
import re
import datetime
import json
import codecs
import threading
from bs4 import BeautifulSoup
from . import settings

from enterprise.libs.CaptchaRecognition import CaptchaRecognition
from common_func import get_proxy, exe_time, json_dump_to_file, get_user_agent
import gevent
from gevent import Greenlet
import gevent.monkey
import random

urls = {
    'host': 'http://tjcredit.gov.cn',
    'page_search': 'http://tjcredit.gov.cn/platform/saic/index.ftl',
    'page_Captcha': 'http://tjcredit.gov.cn/verifycode',
    'page_showinfo': 'http://tjcredit.gov.cn/platform/saic/search.ftl',
    'checkcode': 'http://tjcredit.gov.cn/platform/saic/search.ftl',
}
CheckDetail = {    #行政处罚
    'getAdmPen': "/saicpf/gsxzcf?id=%s&entid=%s&issaic=1&hasInfo=0",
    #股东信息
    'getShareHolder': "/saicpf/gsgdcz?gdczid=%s&entid=%s&issaic=1&hasInfo=0",
    #动产抵押
    'getChaMore': "/saicpf/gsdcdy?id=%s&entid=%s&issaic=1&hasInfo=0",
    #股权出质
    'getEquPle': "/saicpf/gsgqcz?id=%s&entid=%s&issaic=1&hasInfo=0",
}


class TianjinCrawler(object):
    """ 天津爬虫， 继承object基类。 """
    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    def __init__(self, json_restore_path=None):
        headers = {
            'Connetion': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language':
            'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            "User-Agent": get_user_agent(),
        }
        self.CR = CaptchaRecognition("tianjin")
        self.requests = requests.Session()
        self.requests.headers.update(headers)
        adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self.requests.mount('http://', adapter)

        self.ents = {}
        self.json_dict = {}
        self.json_restore_path = json_restore_path
        #验证码图片的存储路径
        self.path_captcha = self.json_restore_path + '/tianjin/ckcode.jpeg'
        #数据的存储路径
        self.html_restore_path = self.json_restore_path + '/tianjin/'
        proxies = get_proxy('tianjin')
        if proxies:
            print proxies
            self.requests.proxies = proxies
        self.timeout = (30, 20)

    #分析 展示页面， 获得搜索到的企业列表
    def analyze_showInfo(self, page):
        Ent = {}
        soup = BeautifulSoup(page, "html5lib")
        divs = soup.find_all("div", {"class": "result-item"})
        if divs:
            count = 0
            for div in divs:
                count += 1
                url = ""
                ent = ""
                link = div.find('a')
                if link and link.has_attr('href'):
                    url = link['href']
                profile = div.find('div', {'class': 'result-detail'})
                ent_id = profile.span.find_next_sibling()
                if ent_id:
                    ent = self.get_raw_text_by_tag(ent_id)
                name = link.get_text().strip()
                if name == self.ent_num:
                    Ent.clear()
                    Ent[ent] = url
                    break
                if count == 3:
                    break
                Ent[ent] = url
        self.ents = Ent

    # 破解验证码页面
    def crawl_page_captcha(self, url_search, url_Captcha, url_CheckCode, url_showInfo, textfield='120000000000165'):
        if not self.request_by_method('GET', url_search, timeout=self.timeout):
            return
        count = 0
        while count < 15:
            count += 1
            r = self.requests.get(url_Captcha)
            if r.status_code != 200:
                logging.error(u"Something wrong when getting the Captcha url:%s , status_code=%d", url_Captcha,
                              r.status_code)
                return
            if self.save_captcha(r.content):
                result = self.crack_captcha()
                print result
                datas = {'searchContent': textfield, 'vcode': result, }
                page = self.request_by_method('POST', url_CheckCode, data=datas, timeout=self.timeout)
                if not page: continue
                # 如果验证码正确，就返回一种页面，否则返回主页面
                if self.is_search_result_page(page):
                    self.analyze_showInfo(page)
                    break
                else:
                    logging.error(u"crack Captcha failed, the %d time(s)", count)
            time.sleep(random.uniform(1, 4))

    # 判断是否成功搜索页面
    def is_search_result_page(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        divs = soup.find('div', {'class': 'nav-query'})
        return divs is None

    #调用函数，破解验证码图片并返回结果
    def crack_captcha(self):
        if os.path.exists(self.path_captcha) is False:
            logging.error(u"Captcha path is not found\n")
            return
        result = self.CR.predict_result(self.path_captcha)
        return result[1]

    # 保存验证码图片
    def save_captcha(self, Captcha):
        if Captcha is None:
            logging.error(u"Can not store Captcha: None\n")
            return False
        self.write_file_mutex.acquire()
        f = open(self.path_captcha, 'w')
        try:
            f.write(Captcha)
        except IOError:
            logging.error("%s can not be written", Captcha)
        finally:
            f.close
        self.write_file_mutex.release()
        return True

    def crawl_page_main(self):
        gevent.monkey.patch_socket()
        sub_json_list = []
        if not self.ents:
            logging.error(u"Get no search result\n")
        try:
            for ent, url in self.ents.items():
                m = re.match('http', url)
                if m is None:
                    url = urls['host'] + url
                logging.error(u"ent url:%s\n" % url)
                self.json_dict = {}
                threads = []
                ent_num = url[url.index('entId=') + 6:]
                url_format = "http://tjcredit.gov.cn/platform/saic/baseInfo.json?entId=" + ent_num + "&departmentId=scjgw&infoClassId=%s"
                threads.append(gevent.spawn(self.crawl_ind_comm_pub_pages, url_format))
                url_format = "http://tjcredit.gov.cn/report/%s?entid=" + ent_num
                threads.append(gevent.spawn(self.crawl_ent_pub_pages, url_format))
                url_format = "http://tjcredit.gov.cn/report/%s?entid=" + ent_num
                threads.append(gevent.spawn(self.crawl_judical_assist_pub_pages, url_format))
                gevent.joinall(threads)
                sub_json_list.append({ent: self.json_dict})
        except Exception as e:
            logging.error(u"An error ocurred when getting the main page, error: %s" % type(e))
            raise e
        finally:
            return sub_json_list
    #工商公式信息页面
    @exe_time
    def crawl_ind_comm_pub_pages(self, url):
        sub_json_dict = {}
        try:

            def dj():
                page = self.request_by_method('GET', url % 'dj', timeout=self.timeout)
                if not page: return
                dj = self.parse_page(page)    # class= result-table

                sub_json_dict['ind_comm_pub_reg_basic'] = dj[u'基本信息'] if dj.has_key(u'基本信息') else {}    # 登记信息-基本信息
                sub_json_dict['ind_comm_pub_reg_shareholder'] = dj[u'股东信息'] if dj.has_key(u'股东信息') else []    # 股东信息
                sub_json_dict['ind_comm_pub_reg_modify'] = dj[u'变更信息'] if dj.has_key(u'变更信息') else []    # 变更信息

            def ba():
                page = self.request_by_method('GET', url % 'ba', timeout=self.timeout)
                if not page: return
                ba = self.parse_page(page)
                sub_json_dict['ind_comm_pub_arch_key_persons'] = ba[u'主要人员信息'] if ba.has_key(u'主要人员信息') else [
                ]    # 备案信息-主要人员信息
                sub_json_dict['ind_comm_pub_arch_branch'] = ba[u'分支机构信息'] if ba.has_key(u'分支机构信息') else [
                ]    # 备案信息-分支机构信息
                sub_json_dict['ind_comm_pub_arch_liquidation'] = ba[u'清算信息'] if ba.has_key(u'清算信息') else [
                ]    # 备案信息-清算信息

            def dcdydjxx():
                page = self.request_by_method('GET', url % 'dcdydjxx', timeout=self.timeout)
                if not page: return
                dcdy = self.parse_page(page)
                sub_json_dict['ind_comm_pub_movable_property_reg'] = dcdy[u'动产抵押登记信息'] if dcdy.has_key(
                    u'动产抵押登记信息') else []

            def gqczdjxx():
                page = self.request_by_method('GET', url % 'gqczdjxx', timeout=self.timeout)
                if not page: return
                gqcz = self.parse_page(page)
                sub_json_dict['ind_comm_pub_equity_ownership_reg'] = gqcz[u'股权出质登记信息'] if gqcz.has_key(
                    u'股权出质登记信息') else []

            def xzcf():
                page = self.request_by_method('GET', url % 'xzcf', timeout=self.timeout)
                if not page: return
                xzcf = self.parse_page(page)
                sub_json_dict['ind_comm_pub_administration_sanction'] = xzcf[u'行政处罚信息'] if xzcf.has_key(
                    u'行政处罚信息') else []

            def qyjyycmlxx():
                page = self.request_by_method('GET', url % 'qyjyycmlxx', timeout=self.timeout)
                if not page: return
                jyyc = self.parse_page(page)
                sub_json_dict['ind_comm_pub_business_exception'] = jyyc[u'经营异常信息'] if jyyc.has_key(u'经营异常信息') else []

            def yzwfqyxx():
                page = self.request_by_method('GET', url % 'yzwfqyxx', timeout=self.timeout)
                if not page: return
                yzwf = self.parse_page(page)
                sub_json_dict['ind_comm_pub_serious_violate_law'] = yzwf[u'严重违法信息'] if yzwf.has_key(u'严重违法信息') else []

            def ccjcxx():
                page = self.request_by_method('GET', url % 'ccjcxx', timeout=self.timeout)
                if not page: return
                cyjc = self.parse_page(page)
                sub_json_dict['ind_comm_pub_spot_check'] = cyjc[u'抽查检查信息'] if cyjc.has_key(u'抽查检查信息') else []

            threads = []
            threads.append(gevent.spawn(dj))
            threads.append(gevent.spawn(ba))
            threads.append(gevent.spawn(dcdydjxx))
            threads.append(gevent.spawn(gqczdjxx))
            threads.append(gevent.spawn(xzcf))
            threads.append(gevent.spawn(qyjyycmlxx))
            threads.append(gevent.spawn(yzwfqyxx))
            threads.append(gevent.spawn(ccjcxx))
            gevent.joinall(threads)

        except Exception as e:
            logging.error(u"An error ocurred in crawl_ind_comm_pub_pages: %s" % type(e))
            raise e
        finally:
            self.json_dict.update(sub_json_dict)
    #爬取 企业公示信息 页面
    @exe_time
    def crawl_ent_pub_pages(self, url):
        sub_json_dict = {}
        try:
            # logging.info( u"crawl the ent_pub_pages %s."%(url))
            sub_json_dict['ent_pub_administration_license'] = []    #行政许可信息
            sub_json_dict['ent_pub_administration_sanction'] = []    #行政许可信息
            sub_json_dict['ent_pub_reg_modify'] = []    #变更信息

            def nblist():
                page = self.request_by_method('GET', url % 'nblist', timeout=self.timeout)
                if not page: return
                nb = self.parse_page(page)
                sub_json_dict['ent_pub_ent_annual_report'] = nb[u'年报信息'] if nb.has_key(u'年报信息') else []

            def gdcz():
                page = self.request_by_method('GET', url % 'gdcz', timeout=self.timeout)
                if not page: return
                p = self.parse_page(page)
                sub_json_dict['ent_pub_shareholder_capital_contribution'] = p[u'股东及出资'] if p.has_key(u'股东及出资') else []

            def gqbg():
                page = self.request_by_method('GET', url % 'gqbg', timeout=self.timeout)
                if not page: return
                p = self.parse_page(page)
                sub_json_dict['ent_pub_equity_change'] = p[u'股权变更信息'] if p.has_key(u'股权变更信息') else []

            def zscq():
                page = self.request_by_method('GET', url % 'zscq', timeout=self.timeout)
                if not page: return
                p = self.parse_page(page)
                sub_json_dict['ent_pub_knowledge_property'] = p[u'知识产权出质登记信息'] if p.has_key(u'知识产权出质登记信息') else []

            threads = []
            threads.append(gevent.spawn(nblist))
            threads.append(gevent.spawn(gdcz))
            threads.append(gevent.spawn(gqbg))
            threads.append(gevent.spawn(zscq))
            gevent.joinall(threads)
        except Exception as e:
            logging.error(u"An error ocurred in crawl_ent_pub_pages: %s" % type(e))
            raise e
        finally:
            self.json_dict.update(sub_json_dict)
    #爬取 司法协助公式 页面
    @exe_time
    def crawl_judical_assist_pub_pages(self, url):
        sub_json_dict = {}
        try:
            # logging.info( u"crawl the judical_assist_pub page %s."%(url))
            def gddjlist():
                page = self.request_by_method('GET', url % 'gddjlist', timeout=self.timeout)
                if not page: return
                xz = self.parse_page(page)
                sub_json_dict['judical_assist_pub_equity_freeze'] = xz[u'司法股权冻结信息'] if xz.has_key(u'司法股权冻结信息') else []

            def gdbglist():
                page = self.request_by_method('GET', url % 'gdbglist', timeout=self.timeout)
                if not page: return
                xz = self.parse_page(page)
                sub_json_dict['judical_assist_pub_shareholder_modify'] = xz[u'司法股东变更登记信息'] if xz.has_key(
                    u'司法股东变更登记信息') else []

            threads = []
            threads.append(gevent.spawn(gddjlist))
            threads.append(gevent.spawn(gdbglist))
            gevent.joinall(threads)
        except Exception as e:
            logging.error(u"An error ocurred in crawl_judical_assist_pub_pages: %s" % (type(e)))
            raise e
        finally:
            self.json_dict.update(sub_json_dict)
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
            if table_tag.find('tr').find_all('th'):
                if len(table_tag.find('tr').find_all('th')) > 1:
                    return None
                # 处理 <th> aa<span> bb</span> </th>
                if table_tag.find('tr').th.stirng == None and len(table_tag.find('tr').th.contents) > 1:
                    # 处理 <th>   <span> bb</span> </th>  包含空格的
                    if (table_tag.find('tr').th.contents[0]).strip():
                        return (table_tag.find('tr').th.contents[0]).strip()
                # <th><span> bb</span> </th>
                return self.get_raw_text_by_tag(table_tag.find('tr').th)
            elif table_tag.find('tr').find('td', {'class': 'bg title'}):
                # 处理 <th> aa<span> bb</span> </th>
                if table_tag.find('tr').td.stirng == None and len(table_tag.find('tr').td.contents) > 1:
                    # 处理 <th>   <span> bb</span> </th>  包含空格的
                    if (table_tag.find('tr').td.contents[0]).strip():
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
                columns.append((self.get_raw_text_by_tag(th), self.get_raw_text_by_tag(th)))
            else:
                #if has sub-sub columns
                columns.append((self.get_raw_text_by_tag(th), self.get_sub_columns(tr_tag.nextSibling.nextSibling, 0,
                                                                                   self.sub_column_count(th))))
        return columns

    def get_sub_columns_td_bg_title(self, tr_tag, index, count):
        columns = []
        for i in range(index, index + count):
            th = tr_tag.find_all('td', {'class': 'bg title'})[i]
            if not self.sub_column_count(th):
                columns.append((self.get_raw_text_by_tag(th), self.get_raw_text_by_tag(th)))
            else:
                #if has sub-sub columns
                columns.append((self.get_raw_text_by_tag(th), self.get_sub_columns_td_bg_title(
                    tr_tag.nextSibling.nextSibling, 0, self.sub_column_count(th))))
        return columns

    def get_sub_columns_td_bg(self, tr_tag, index, count):
        columns = []
        for i in range(index, index + count):
            th = tr_tag.find_all('td', {'class': 'bg'})[i]
            if not self.sub_column_count(th):
                columns.append((self.get_raw_text_by_tag(th), self.get_raw_text_by_tag(th)))
            else:
                #if has sub-sub columns
                columns.append((self.get_raw_text_by_tag(th), self.get_sub_columns_td_bg(tr_tag.nextSibling.nextSibling,
                                                                                         0, self.sub_column_count(th))))
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
        if bs4_tag.has_attr('href') and (bs4_tag['href'] != '#' and bs4_tag['href'] != 'javascript:void(0);'):
            #print 'href'
            pattern = re.compile(r'http' | r'javascript:void(0);')
            if pattern.search(bs4_tag['href']):
                return bs4_tag['href']
            return urls['prefix_url'] + bs4_tag['href']
        elif bs4_tag.has_attr('onclick'):
            #print 'onclick'
            txt = bs4_tag['onclick']
            if re.compile('CheckDetail').search(txt):

                re1 = '.*?'    # Non-greedy match on filler
                re2 = '(?:[a-z][a-z]+)'    # Uninteresting: word
                re3 = '.*?'    # Non-greedy match on filler
                re4 = '((?:[a-z][a-z]+))'    # Word 1

                rg = re.compile(re1 + re2 + re3 + re4, re.IGNORECASE | re.DOTALL)
                m = rg.search(txt)
                if m:
                    key = m.group(1)
                    re1 = '.*?'    # Non-greedy match on filler
                    re2 = '(\\\'.*?\\\')'    # Single Quote String 1
                    re3 = '.*?'    # Non-greedy match on filler
                    re4 = '(\\\'.*?\\\')'    # Single Quote String 2

                    rg = re.compile(re1 + re2 + re3 + re4, re.IGNORECASE | re.DOTALL)
                    m = rg.search(txt)
                    if m:
                        # strip extra \'\' for each side
                        id_str = m.group(1)[1:-1]
                        entid_str = m.group(2)[1:-1]
                    url = urls['host'] + CheckDetail[key] % (id_str, entid_str)

            elif re.compile('nbdetail').search(txt):
                re1 = '.*?'    # Non-greedy match on filler
                re2 = '(\\\'.*?\\\')'    # Single Quote String 1
                re3 = '.*?'    # Non-greedy match on filler
                re4 = '(\\\'.*?\\\')'    # Single Quote String 2

                rg = re.compile(re1 + re2 + re3 + re4, re.IGNORECASE | re.DOTALL)
                m = rg.search(txt)
                if m:
                    entid_str = m.group(1)[1:-1]
                    year_str = m.group(2)[1:-1]
                url = urls['host'] + "/report/annals?entid=%s&year=%s&hasInfo=0" % (entid_str, year_str)
            elif re.compile('sfGddjDetail').search(txt):
                re1 = '.*?'    # Non-greedy match on filler
                re2 = '(\\\'.*?\\\')'    # Single Quote String 1
                re3 = '.*?'    # Non-greedy match on filler
                re4 = '(\\\'.*?\\\')'    # Single Quote String 2

                rg = re.compile(re1 + re2 + re3 + re4, re.IGNORECASE | re.DOTALL)
                m = rg.search(txt)
                if m:
                    id_str = m.group(1)[1:-1]
                    entid_str = m.group(2)[1:-1]
                url = urls['host'] + "/report/gddjdetail?id=%s&entid=%s&hasInfo=0" % (id_str, entid_str)
            return url
        return None

    def get_columns_of_record_table(self, bs_table, page, table_name):
        tbody = None
        if len(bs_table.find_all('tbody')) > 1:
            tbody = bs_table.find_all('tbody')[1]
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
                    elif len(tr.find_all('td')) == len(tr.find_all('td', attrs={'class': 'bg title', 'class': 'bg'})):
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
            elif bs_table.find_all('tr')[0].find('th') and not bs_table.find_all('tr')[0].find('td') and len(
                    bs_table.find_all('tr')[0].find_all('th')) > 1:
                tr = bs_table.find_all('tr')[0]
            elif bs_table.find_all('tr')[0].find(
                    'td', {'class':
                           'bg title'}) and len(bs_table.find_all('tr')[0].find_all('td', {'class': 'bg title'})) > 1:
                tr = bs_table.find_all('tr')[0]
            elif bs_table.find_all('tr')[1].find('th') and not bs_table.find_all('tr')[1].find('td') and len(
                    bs_table.find_all('tr')[1].find_all('th')) > 1:
                tr = bs_table.find_all('tr')[1]
            elif bs_table.find_all('tr')[1].find(
                    'td', {'class':
                           'bg title'}) and len(bs_table.find_all('tr')[1].find_all('td', {'class': 'bg title'})) > 1:
                tr = bs_table.find_all('tr')[1]
        ret_val = self.get_record_table_columns_by_tr(tr, table_name)
        return ret_val

    def get_record_table_columns_by_tr(self, tr_tag, table_name):
        columns = []
        if not tr_tag:
            return columns
        try:
            sub_col_index = 0
            if len(tr_tag.find_all('th')) == 0 and (len(tr_tag.find_all('td', {'class': 'bg title'})) == 0
                                                    and len(tr_tag.find_all('td', attrs={'class': 'bg'})) == 0):
                logging.error(u"The table %s has no columns" % table_name)
                return columns
            count = 0
            if len(tr_tag.find_all('th')) > 0:
                for th in tr_tag.find_all('th'):
                    col_name = self.get_raw_text_by_tag(th)
                    if col_name:
                        if ((col_name, col_name) in columns):
                            col_name = col_name + '_'
                            count += 1
                        if not self.sub_column_count(th):
                            columns.append((col_name, col_name))
                        else:    #has sub_columns
                            columns.append((col_name, self.get_sub_columns(tr_tag.nextSibling.nextSibling,
                                                                           sub_col_index, self.sub_column_count(th))))
                            sub_col_index += self.sub_column_count(th)
                if count == len(tr_tag.find_all('th')) / 2:
                    columns = columns[:len(columns) / 2]
            elif len(tr_tag.find_all('td', {'class': 'bg title'})) > 0:
                for td in tr_tag.find_all('td', {'class': 'bg title'}):
                    col_name = self.get_raw_text_by_tag(td)
                    if col_name:
                        if ((col_name, col_name) in columns):
                            col_name = col_name + '_'
                            count += 1
                        if not self.sub_column_count(td):
                            columns.append((col_name, col_name))
                        else:
                            columns.append((col_name, self.get_sub_columns_td_bg_title(
                                tr_tag.nextSibling.nextSibling, sub_col_index, self.sub_column_count(td))))
                            sub_col_index += self.sub_column_count(td)
                if count == len(tr_tag.find_all('td', {'class': 'bg title'})) / 2:
                    columns = columns[:len(columns) / 2]
            elif len(tr_tag.find_all('td', {'class': 'bg'})) > 0:
                for td in tr_tag.find_all('td', {'class': 'bg'}):
                    col_name = self.get_raw_text_by_tag(td)
                    if col_name:
                        if ((col_name, col_name) in columns):
                            col_name = col_name + '_'
                            count += 1
                        if not self.sub_column_count(td):
                            columns.append((col_name, col_name))
                        else:
                            columns.append((col_name, self.get_sub_columns_td_bg(
                                tr_tag.nextSibling.nextSibling, sub_col_index, self.sub_column_count(td))))
                            sub_col_index += self.sub_column_count(td)
                if count == len(tr_tag.find_all('td', {'class': 'bg'})) / 2:
                    columns = columns[:len(columns) / 2]
        except Exception as e:
            logging.error(u'exception occured in get_table_columns, except_type = %s, table_name = %s' %
                          (type(e), table_name))
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
            logging.error(u'annual page: fail to get table data with exception %s' % e)
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
            if len(bs_table.find_all('tbody')) > 1:
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
                        single_col += 1
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
                    if tr.find_all('td', attrs={
                            'class': None,
                            'class': ""
                    }) and len(tr.find_all('td', recursive=False)) % column_size == 0:
                        col_count = 0
                        item = {}
                        for td in tr.find_all('td', recursive=False):
                            if td.find('a'):
                                #try to retrieve detail link from page
                                next_url = self.get_detail_link(td.find('a'))
                                #print 'next_url: ' + next_url
                                if next_url:
                                    detail_page = self.request_by_method('GET', next_url, timeout=self.timeout)
                                    if table_name == u'年报信息':
                                        page_data = self.parse_ent_pub_annual_report_page(detail_page)

                                        item[columns[col_count][0]] = page_data    #this may be a detail page data
                                    else:
                                        page_data = self.parse_page(detail_page)
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
                    #a fucking dog case!!!!!!
                    elif tr.find_all('td', attrs={
                            'class': None,
                            'class': ""
                    }) and len(tr.find_all('td', recursive=False)) == col_span and col_span != column_size:
                        col_count = 0
                        sub_col_index = 0
                        item = {}
                        sub_item = {}
                        for td in tr.find_all('td', recursive=False):
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
                    elif tr.find_all('td', attrs={'class': None, 'class': ""}):
                        if len(tr.find_all('td', recursive=False)) == single_col:
                            col_count = 0
                            item = {}
                            sub_list = []
                            for td in tr.find_all('td', recursive=False):
                                if type(columns[col_count][1]) is not list:
                                    item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                    col_count += 1
                                else:
                                    pass
                        elif len(tr.find_all('td', recursive=False)) == col_span - single_col:
                            #col_count = single_col
                            sub_col_index = 0
                            #item = {}
                            sub_item = {}
                            t_item = {}
                            col_count = single_col
                            for td in tr.find_all('td', recursive=False):
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
                        if len(tr.find_all('td', {'class': 'bg'})) * 2 == len(tr.find_all('td')):
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

    def request_by_method(self, method, url, *args, **kwargs):
        r = None
        try:
            r = self.requests.request(method, url, *args, **kwargs)
        except requests.exceptions.Timeout as err:
            logging.error(u'Getting url: %s timeout. %s .' % (url, err.message))
            return False
        except requests.exceptions.ConnectionError:
            logging.error(u"Getting url:%s connection error ." % (url))
            return False
        except Exception as err:
            logging.error(u'Getting url: %s exception:%s . %s .' % (url, type(err), err.message))
            return False
        if r.status_code != 200:
            logging.error(u"Something wrong when getting url:%s , status_code=%d", url, r.status_code)
            return False
        return r.content

    def run(self, ent_num):
        print self.__class__.__name__
        logging.error('crawl %s .', self.__class__.__name__)
        if not os.path.exists(self.html_restore_path):
            os.makedirs(self.html_restore_path)
        self.ent_num = str(ent_num)
        self.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'],
                                self.ent_num)
        if not self.ents:
            return json.dumps([{self.ent_num: None}])
        data = self.crawl_page_main()
        # path = os.path.join(os.getcwd(), 'tianjin.json')
        # json_dump_to_file(path, data)
        return json.dumps(data)
