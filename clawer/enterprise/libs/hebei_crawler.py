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

urls = {
    'host': 'http://www.hebscztxyxx.gov.cn/notice/',
    'webroot' : 'http://www.hebscztxyxx.gov.cn/',
    'page_search': 'http://www.hebscztxyxx.gov.cn/notice/',
    'page_Captcha': 'http://www.hebscztxyxx.gov.cn/notice/captcha?preset=&ra=', # preset 有数字的话，验证码会是字母+数字的组合
    'page_showinfo': 'http://www.hebscztxyxx.gov.cn/notice/search/ent_info_list',
    'checkcode':'http://www.hebscztxyxx.gov.cn/notice/security/verify_captcha',
}

headers = { #'Connetion': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36",
            }

class HebeiCrawler(object):
    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    def __init__(self, json_restore_path):
        self.CR = CaptchaRecognition("hebei")
        self.requests = requests.Session()
        self.requests.headers.update(headers)
        self.ents = []
        self.json_restore_path = json_restore_path
        self.csrf = ""
        #验证码图片的存储路径
        self.path_captcha = settings.json_restore_path + '/hebei/ckcode.jpeg'
        #html数据的存储路径
        self.html_restore_path = settings.json_restore_path + '/hebei/'

    # 破解搜索页面
    def crawl_page_search(self, url):
        r = self.requests.get( url)
        if r.status_code != 200:
            logging.error(u"Something wrong when getting the url:%s , status_code=%d", url, r.status_code)
            return
        r.encoding = "utf-8"
        #logging.debug("searchpage html :\n  %s", r.text)
        return r.text

    #分析 展示页面， 获得搜索到的企业列表
    def analyze_showInfo(self, page):
        Ent = []
        soup = BeautifulSoup(page, "html5lib")
        divs = soup.find_all("div", {"class":"list-item"})
        for div in divs:
            Ent.append(div.find('a')['href'])
        self.ents = Ent

    def crawl_page_captcha(self, url_search, url_Captcha, url_CheckCode,url_showInfo,  textfield= '130000000021709'):
        """破解验证码页面"""
        html_search = self.crawl_page_search(url_search)
        if not html_search:
            logging.error(u"There is no search page")
            return
        soup = BeautifulSoup(html_search, 'html5lib')
        form = soup.find('form', {'id':'formInfo'})
        datas= {
                #'searchType' : 1,
                'captcha': None,
                'session.token': form.find('input',{'name': 'session.token'})['value'],
                #'condition.keyword': textfield,
        }
        count = 0
        while True:
            count+= 1
            r = self.requests.get( url_Captcha+ str(random.random()))
            if r.status_code != 200:
                logging.error(u"Something wrong when getting the Captcha url:%s , status_code=%d", url_Captcha+ str(random.random()), r.status_code)
                return
            #logging.debug("Captcha page html :\n  %s", self.Captcha)
            if self.save_captcha(r.content):
                logging.info("Captcha is saved successfully \n" )
                datas['captcha'] = self.crack_captcha()
                logging.info("cracked captcha is %d"%(datas['captcha']) )
                res=  self.crawl_page_by_url_post(url_CheckCode, datas)['page']
                # 如果验证码正确，就返回一种页面，否则返回主页面
                if str(res) is not '0' :
                    datas['searchType'] = 1
                    datas['condition.keyword'] = textfield
                    page =  self.crawl_page_by_url_post(url_showInfo, datas)['page']
                    self.analyze_showInfo(page)
                    break
                else:
                    logging.debug(u"crack Captcha failed, the %d time(s)", count)
                    if count > 15:
                        break
        return
    def crack_captcha(self):
        """调用函数，破解验证码图片并返回结果"""
        if os.path.exists(self.path_captcha) is False:
            logging.error(u"Captcha path is not found\n")
            return
        result = self.CR.predict_result(self.path_captcha)
        return result[1]
        #print result
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
    """
        The following enterprises in ents
        1. for each ent: decide host so that choose e urls
        2. for eah url, iterate item in tabs
    """
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
                #工商公示信息
                url = ent
                sub_json_dict.update(self.crawl_ind_comm_pub_pages(url))
                url = url[:-2]+"02"
                sub_json_dict.update(self.crawl_ent_pub_pages(url))
                url = url[:-2] + "03"
                sub_json_dict.update(self.crawl_other_dept_pub_pages(url))
                url = url[:-2] + "06"
                sub_json_dict.update(self.crawl_judical_assist_pub_pages(url))

        except Exception as e:
            logging.error(u"An error ocurred when getting the main page, error: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #工商公式信息页面
    def crawl_ind_comm_pub_pages(self, url):
        """  爬取 工商公式 信息页面        """
        sub_json_dict={}
        try:
            #page = html_from_file('next.html')
            logging.info( u"crawl the crawl_ind_comm_pub_pages page %s."%(url))
            page = self.crawl_page_by_url(url)['page']
            #html_to_file('next.html', page)
            dj = self.parse_page(page ) # class= result-table
            sub_json_dict['ind_comm_pub_reg_basic'] = dj[u'基本信息'] if dj.has_key(u'基本信息') else []        # 登记信息-基本信息
            sub_json_dict['ind_comm_pub_reg_shareholder'] =dj[u'股东信息'] if dj.has_key(u'股东信息') else []   # 股东信息
            sub_json_dict['ind_comm_pub_reg_modify'] =  dj[u'变更信息'] if dj.has_key(u'变更信息') else []      # 变更信息
            sub_json_dict['ind_comm_pub_arch_key_persons'] = dj[u'主要人员信息'] if dj.has_key(u'主要人员信息') else []   # 备案信息-主要人员信息
            sub_json_dict['ind_comm_pub_arch_branch'] = dj[u'分支机构信息'] if dj.has_key(u'分支机构信息') else []       # 备案信息-分支机构信息
            sub_json_dict['ind_comm_pub_arch_liquidation'] = dj[u'清算信息'] if dj.has_key(u'清算信息') else []   # 备案信息-清算信息
            sub_json_dict['ind_comm_pub_movable_property_reg'] = dj[u'动产抵押登记信息'] if dj.has_key(u'动产抵押登记信息') else []
            sub_json_dict['ind_comm_pub_equity_ownership_reg'] = dj[u'股权出质登记信息'] if dj.has_key(u'股权出质登记信息') else []
            sub_json_dict['ind_comm_pub_administration_sanction'] = dj[u'行政处罚信息'] if dj.has_key(u'行政处罚信息') else []
            sub_json_dict['ind_comm_pub_business_exception'] = dj[u'经营异常信息'] if dj.has_key(u'经营异常信息') else []
            sub_json_dict['ind_comm_pub_serious_violate_law'] = dj[u'严重违法信息'] if dj.has_key(u'严重违法信息') else []
            sub_json_dict['ind_comm_pub_spot_check'] = dj[u'抽查检查信息'] if dj.has_key(u'抽查检查信息') else []
        except Exception as e:
            logging.debug(u"An error ocurred in crawl_ind_comm_pub_pages: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #爬取 企业公示信息 页面
    def crawl_ent_pub_pages(self, url):
        """  爬取 企业公示信息 信息页面        """
        sub_json_dict = {}
        try:
            logging.info( u"crawl the crawl_ent_pub_pages page %s"%(url))
            page = self.crawl_page_by_url(url)['page']
            #html_to_file('next.html', page)
            #page = html_from_file('next.html')
            p = self.parse_page(page)
            sub_json_dict['ent_pub_ent_annual_report'] = p[u'企业年报'] if p.has_key(u'企业年报') else []
            sub_json_dict['ent_pub_administration_license'] = p[u'行政许可信息'] if p.has_key(u'行政许可信息') else []
            sub_json_dict['ent_pub_administration_sanction'] = p[u'行政处罚信息'] if p.has_key(u'行政处罚信息') else []
            sub_json_dict['ent_pub_shareholder_capital_contribution'] = p[u'股东及出资信息（币种与注册资本一致）'] if p.has_key(u'股东及出资信息（币种与注册资本一致）') else []
            sub_json_dict['ent_pub_reg_modify'] = p[u'变更信息'] if p.has_key(u'变更信息') else []
            sub_json_dict['ent_pub_equity_change'] = p[u'股权变更信息'] if p.has_key(u'股权变更信息') else []
            sub_json_dict['ent_pub_knowledge_property'] = p[u'知识产权出质登记信息'] if p.has_key(u'知识产权出质登记信息') else []
        except Exception as e:
            logging.debug(u"An error ocurred in crawl_ent_pub_pages: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #爬取 其他部门公示 页面
    def crawl_other_dept_pub_pages(self, url):
        """  爬取其他部门信息页面        """
        sub_json_dict = {}
        try:
            logging.info( u"crawl the crawl_other_dept_pub_pages page %s."%(url))
            page = self.crawl_page_by_url(url)['page']
            #html_to_file('next.html', page)
            #page = html_from_file('next.html')
            xk = self.parse_page(page)#行政许可信息
            sub_json_dict["other_dept_pub_administration_license"] =  xk[u'行政许可信息'] if xk.has_key(u'行政许可信息') else []
            sub_json_dict["other_dept_pub_administration_sanction"] = xk[u'行政处罚信息'] if xk.has_key(u'行政处罚信息') else []  # 行政处罚信息
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
            xz = self.parse_page(page)
            sub_json_dict['judical_assist_pub_equity_freeze'] = xz[u'司法股权冻结信息'] if xz.has_key(u'司法股权冻结信息') else []
            sub_json_dict['judical_assist_pub_shareholder_modify'] = xz[u'司法股东变更登记信息'] if xz.has_key(u'司法股东变更登记信息') else []
        except Exception as e:
            logging.debug(u"An error ocurred in crawl_judical_assist_pub_pages: %s"% (type(e)))
            raise e
        finally:
            return sub_json_dict

    # 出资方式字典
    def dicInvtType(self, types):
        if types == "1":
            return  "货币"
        if types == "2":
            return  "实物"
        if types == "3":
            return  "知识产权"
        if types == "4":
            return  "债权"
        if types == "5":
            return  "高新技术成果"
        if types == "6":
            return  "土地使用权"
        if types == "7":
            return  "股权"
        if types == "8":
            return  "劳务"
        if types == "9":
            return  "其他"

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
            return urls['webroot'] + bs4_tag['href']
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
            logging.error(u'annual page: fail to get table data with exception %s' % e)
            raise e
        finally:
            return sub_dict
    #股东及出资信息（币种与注册资本一致）
    def parse_table_qygs_gudongchuzi(self, page):
        coms = re.findall(r'var investor.*?list.push\(investor\);', page, flags=re.DOTALL+re.MULTILINE)
        sub_item={}
        item = {}
        Item = []
        for comstr in coms:
            m_invstr = re.compile(r'investor.inv.*?;').search(comstr)
            if m_invstr:
                invstr = m_invstr.group()
                inv = re.compile(r'\".*?\"').search(invstr).group().strip('\"')
                #认缴
                rjSubConAmlist=[]
                count_rj = 0
                for itemstr in re.findall(r'invt.subConAm.*?;', comstr, flags = re.DOTALL+ re.MULTILINE):
                    subConAm = eval(re.compile(r"\".*?\"").search(itemstr).group().strip('\"'))
                    count_rj += subConAm

                    rjSubConAmlist.append(subConAm)
                rjconDateList=[]
                for itemstr in  re.findall(r'invt.conDate.*?;', comstr, flags = re.DOTALL+ re.MULTILINE):
                    conDate = (re.compile(r"\'.*?\'").search(itemstr).group().strip("\'"))
                    rjconDateList.append(conDate)
                rjconFormList=[]
                for itemstr in re.findall(r'invt.conForm.*?;', comstr, flags = re.DOTALL+ re.MULTILINE):
                    conForm = (re.compile(r"\".*?\"").search(itemstr).group().strip('\"'))
                    rjconFormList.append(conForm)
                #实缴
                sjAcConAm=[]
                count_sj = 0
                for itemstr in re.findall(r'invtActl.acConAm.*?;', comstr, flags = re.DOTALL+ re.MULTILINE):
                    acConAm = eval(re.compile(r"\".*?\"").search(itemstr).group().strip('\"'))
                    count_sj += acConAm
                    sjAcConAm.append(acConAm)
                sjconDateList = []
                for itemstr in re.findall(r'invtActl.conDate.*?;', comstr, flags = re.DOTALL+ re.MULTILINE):
                    conDate = (re.compile(r"\'.*?\'").search(itemstr).group().strip("\'"))
                    sjconDateList.append(conDate)
                sjconFormList = []
                for itemstr in re.findall(r'invtActl.conForm.*?;', comstr, flags = re.DOTALL+ re.MULTILINE):
                    conForm = (re.compile(r"\".*?\"").search(itemstr).group().strip('\"'))
                    sjconFormList.append(conForm)
                len_rj = len(rjSubConAmlist)
                len_sj = len(sjAcConAm)
                item = {}
                item_list = []
                item[u'股东'] = inv
                item[u'认缴额（万元）'] = count_rj
                item[u'实缴额（万元）'] = count_sj
                try:
                    maxRow = max( len_sj,  len_rj)
                    for i in xrange(maxRow):
                        sub_item={}
                        if i < len_rj:
                            sub_item[u'认缴出资方式'] = self.dicInvtType(rjconFormList[i])
                            sub_item[u'认缴出资额（万元）'] = rjSubConAmlist[i]
                            sub_item[u'认缴出资日期'] =  rjconDateList[i]
                        else:
                            sub_item[u'认缴出资方式'] =""
                            sub_item[u'认缴出资额（万元）'] =""
                            sub_item[u'认缴出资日期'] = ""
                        #item[u'认缴明细'] = sub_item
                        if i< len_sj:
                            sub_item[u'实缴出资方式'] = self.dicInvtType(sjconFormList[i])
                            sub_item[u'实缴出资额（万元'] = sjAcConAm[i]
                            sub_item[u'实缴出资日期'] =  sjconDateList[i]
                        else:
                            sub_item[u'实缴出资方式'] =""
                            sub_item[u'实缴出资额（万元'] =""
                            sub_item[u'实缴出资日期'] = ""
                        #item[u'实缴明细'] = sub_item
                        item_list.append(sub_item)
                except Exception as e:
                    logging.error(u"exception : %s"%(type(e)))
                item[u'详情'] = item_list
                Item.append(item)
            else:
                logging.error(u"There is no company, continue!")
        return Item

    def parse_page(self, page, div_id='cont-r-b'):
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
                    if table_name == u"股东及出资信息（币种与注册资本一致）":
                        page_data[table_name ] =self.parse_table_qygs_gudongchuzi(page)
                    else:
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

                                        item[columns[col_count][0]] = page_data #this may be a detail page data
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


    def crawl_page_by_url(self, url):
        try:
            r = self.requests.get( url)
            if r.status_code != 200:
                logging.error(u"Getting page by url:%s, return status %s\n"% (url, r.status_code))
            text = r.text
            urls = r.url
            # 为了防止页面间接跳转，获取最终目标url
        except Exception as e:
            logging.error(u"Cann't get page by url:%s, exception is %s"%(url, type(e)))
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
        self.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        data = self.crawl_page_main()
        json_dict[ent_num] = data
        #json_dump_to_file(self.json_restore_path , json_dict)
        #2016-2-16
        return json.dumps(json_dict)

    def work(self, ent_num= ""):

        # if not os.path.exists(self.html_restore_path):
        #     os.makedirs(self.html_restore_path)
        self.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        data = self.crawl_page_main()
        json_dump_to_file('hebei_json.json', data)
        # 测试
        # url = "http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=u9Abs75MdJjl94Li4fXsN.dDmlDUrpmY&tab=06"
        # data = self.crawl_judical_assist_pub_pages(url)
        # json_dump_to_file('hebei_json.json', data)

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
    hebei = HebeiCrawler('./enterprise_crawler/hebei.json')
    hebei.work('130000000021709')


if __name__ == "__main__":
    reload (sys)
    sys.setdefaultencoding('utf-8')
    import run
    run.config_logging()
    if not os.path.exists("./enterprise_crawler"):
        os.makedirs("./enterprise_crawler")
    hebei = HebeiCrawler('./enterprise_crawler/hebei.json')
    ents = read_ent_from_file("./enterprise_list/hebei.txt")
    hebei = HebeiCrawler('./enterprise_crawler/hebei.json')
    for ent_str in ents:
        logging.info(u'###################   Start to crawl enterprise with id %s   ###################\n' % ent_str[2])
        hebei.run(ent_num = ent_str[2])
        logging.info(u'###################   Enterprise with id  %s Finished!  ###################\n' % ent_str[2])

"""
