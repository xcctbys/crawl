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
import hashlib #验证码是MD5加密的，调用此包
#import simplejson
from enterprise.libs.proxies import Proxies


urls = {
    'host': 'http://218.57.139.24/pub/',
    'webroot' : 'http://218.57.139.24/',
    'page_search': 'http://218.57.139.24/',
    'page_Captcha': 'http://218.57.139.24/securitycode',
    'page_showinfo': 'http://218.57.139.24/pub/indsearch',
    'checkcode':'http://218.57.139.24/pub/indsearch',
}

headers = { #'Connetion': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36",
            }

class ShandongCrawler(object):
    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    def __init__(self, json_restore_path):
        self.CR = CaptchaRecognition("shandong")
        self.requests = requests.Session()
        self.requests.headers.update(headers)
        self.ents = []
        self.json_restore_path = json_restore_path
        self.csrf = ""
        #验证码图片的存储路径
        self.path_captcha = settings.json_restore_path + '/shandong/ckcode.jpeg'
        #html数据的存储路径
        self.html_restore_path = settings.json_restore_path + '/shandong/'
        p = Proxies()
        self.proxies = p.get_proxies()
        self.timeout = 15


    #分析 展示页面， 获得搜索到的企业列表
    def analyze_showInfo(self, page):
        Ent = []
        soup = BeautifulSoup(page, "html5lib")
        divs = soup.find_all("div", {"class":"list"})
        if divs:
            for div in divs:
                if div and div.ul and div.ul.li and div.ul.li.a and div.ul.li.a.has_attr('href'):
                    Ent.append(div.ul.li.a['href'])
        self.ents = Ent

    # 破解验证码页面
    def crawl_page_captcha(self, url_search, url_Captcha, url_CheckCode,url_showInfo,  textfield= '370000018067809'):
        # get 搜索页面
        html_search = self.crawl_page_by_url(url_search)['page']
        count = 0
        while count < 15:
            count+= 1
            r = self.requests.get( url_Captcha, proxies = self.proxies, timeout = self.timeout )
            if r.status_code != 200:
                logging.error(u"Something wrong when getting the Captcha url:%s , status_code=%d, ID= %s\n" %( url_Captcha, r.status_code, textfield))
                return
            #logging.error("Captcha page html :\n  %s", self.Captcha)
            if self.save_captcha(r.content):

                result = self.crack_captcha()
                secode = hashlib.md5(str(result)).hexdigest() # MD5 encode
                if not html_search:
                    logging.error(u"There is no search page")
                soup = BeautifulSoup(html_search, 'html5lib')
                csrf = soup.find('input', {'name':'_csrf'})['value']
                self.csrf = csrf
                datas= {
                        'kw' : textfield,
                        '_csrf': csrf,
                        'secode': secode,
                }
                logging.error(u"check code post datas = %s, ID= %s" %( datas, textfield) )
                page=  self.crawl_page_by_url_post(url_CheckCode, datas)['page']
                # 如果验证码正确，就返回一种页面，否则返回主页面

                if self.is_search_result_page(page) :
                    self.analyze_showInfo(page)
                    break
                else:
                    logging.error(u"crack Captcha failed, the %d time(s), ID= %s" %( count, textfield) )
            else:
                logging.error("Captcha is not saved successfully \n" )

        return

    # 判断是否成功搜索页面
    def is_search_result_page(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        divs = soup.find('div', {'class':'list'})
        return divs is not None

    #调用函数，破解验证码图片并返回结果
    def crack_captcha(self):
        if os.path.exists(self.path_captcha) is False:
            logging.error(u"Captcha path is not found\n")
            return
        result = self.CR.predict_result(self.path_captcha)
        return result[1]
        #print result
    # 保存验证码图片
    def save_captcha(self, Captcha):
        url_Captcha = self.path_captcha
        if Captcha is None:
            logging.error(u"Can not store Captcha: None\n")
            return False
        self.write_file_mutex.acquire()
        f = open(url_Captcha, 'w')
        try:
            f.write(Captcha)
        except IOError:
            logging.error("%s can not be written", url_Captcha)
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
            logging.error(u"Get no search result\n")
        try:
            for ent in self.ents:
                m = re.match('http', ent)
                if m is None:
                    ent = urls['host']+ ent
                #logging.error(u"ent url:%s\n"% ent)
                logging.error(u"crawl main url:%s"% ent)
                #ent_num = ent[ent.index('entId=')+6 :]
                #工商公示信息
                url = ent
                #html_to_file('next.html', page)
                entpripid = ent[ent.rfind('/')+1:]
                temp = ent[:ent.rfind('/')]
                enttype =  temp[temp.rfind('/')+1 :]

                sub_json_dict.update(self.crawl_ind_comm_pub_pages(url))
                url = urls['host'] + 'qygsdetail/'+ enttype+'/'+entpripid
                sub_json_dict.update(self.crawl_ent_pub_pages(url))
                #其他部门http://218.57.139.24/pub/qtgsdetail/
                url = urls['host']+'qtgsdetail/' + enttype+'/' + entpripid
                sub_json_dict.update(self.crawl_other_dept_pub_pages(url))
                # 司法协助公示信息 sfgsdetail
                url = urls['host']+ 'sfgsdetail/' + enttype +'/' + entpripid
                sub_json_dict.update(self.crawl_judical_assist_pub_pages(url))

        except Exception as e:
            logging.error(u"An error ocurred when getting the main page, error: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #工商公式信息页面
    def crawl_ind_comm_pub_pages(self, url):
        sub_json_dict={}
        try:
            #url = "http://218.57.139.24/pub/gsgsdetail/1223/6e0948678bfeed4ac8115d5cafef819ad6951a24f0c0188cd6c047570329c9b6"
            #page = html_from_file('next.html')
            logging.error( u"crawl the crawl_ind_comm_pub_pages page %s."%(url))
            page = self.crawl_page_by_url(url)['page']
            entpripid = url[url.rfind('/')+1:]
            post_data = {'encrpripid' : entpripid}
            dj = self.parse_page(page, 'jibenxinxi') # class= result-table
            sub_json_dict['ind_comm_pub_reg_basic'] = dj[u'基本信息'] if dj.has_key(u'基本信息') else []        # 登记信息-基本信息
            sub_json_dict['ind_comm_pub_reg_shareholder'] =dj[u'股东信息'] if dj.has_key(u'股东信息') else []   # 股东信息
            sub_json_dict['ind_comm_pub_reg_modify'] =  dj[u'变更信息'] if dj.has_key(u'变更信息') else []      # 变更信息

            ba = self.parse_page(page, 'beian', post_data)
            sub_json_dict['ind_comm_pub_arch_key_persons'] = ba[u'主要人员信息'] if ba.has_key(u'主要人员信息') else []   # 备案信息-主要人员信息
            sub_json_dict['ind_comm_pub_arch_branch'] = ba[u'分支机构信息'] if ba.has_key(u'分支机构信息') else []       # 备案信息-分支机构信息
            sub_json_dict['ind_comm_pub_arch_liquidation'] = ba[u'清算信息'] if ba.has_key(u'清算信息') else []   # 备案信息-清算信息
            dcdy = self.parse_page(page, 'dongchandiya', post_data)
            sub_json_dict['ind_comm_pub_movable_property_reg'] = dcdy[u'动产抵押登记信息'] if dcdy.has_key(u'动产抵押登记信息') else []
            gqcz = self.parse_page(page, 'guquanchuzhi', post_data)
            sub_json_dict['ind_comm_pub_equity_ownership_reg'] = gqcz[u'股权出质登记信息'] if gqcz.has_key(u'股权出质登记信息') else []
            xzcf = self.parse_page(page, 'xingzhengchufa', post_data)
            sub_json_dict['ind_comm_pub_administration_sanction'] = xzcf[u'行政处罚信息'] if xzcf.has_key(u'行政处罚信息') else []
            jyyc= self.parse_page(page, 'jingyingyichangminglu', post_data)
            sub_json_dict['ind_comm_pub_business_exception'] = jyyc[u'经营异常信息'] if jyyc.has_key(u'经营异常信息') else []
            yzwf = self.parse_page(page, 'yanzhongweifaqiye', post_data)
            sub_json_dict['ind_comm_pub_serious_violate_law'] = yzwf[u'严重违法信息'] if yzwf.has_key(u'严重违法信息') else []
            cyjc= self.parse_page(page, 'chouchaxinxi', post_data)
            sub_json_dict['ind_comm_pub_spot_check'] = cyjc[u'抽查检查信息'] if cyjc.has_key(u'抽查检查信息') else []
        except Exception as e:
            logging.error(u"An error ocurred in crawl_ind_comm_pub_pages: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #爬取 企业公示信息 页面
    def crawl_ent_pub_pages(self, url):
        sub_json_dict = {}
        try:
            logging.error( u"crawl the crawl_ent_pub_pages page %s."%(url))
            page = self.crawl_page_by_url(url)['page']
            #html_to_file('next.html', page)
            entpripid = url[url.rfind('/')+1:]
            post_data = {'encrpripid' : entpripid}
            nb = self.parse_page_qygs(page, 'qiyenianbao', post_data)
            sub_json_dict['ent_pub_ent_annual_report'] = nb[u'企业年报'] if nb.has_key(u'企业年报') else []
            xk = self.parse_page_qygs(page, 'xingzhengxuke', post_data)
            sub_json_dict['ent_pub_administration_license'] = xk[u'行政许可信息'] if xk.has_key(u'行政许可信息') else []
            cf = self.parse_page_qygs(page, 'xingzhengchufa', post_data)
            sub_json_dict['ent_pub_administration_sanction'] = cf[u'行政处罚信息'] if cf.has_key(u'行政处罚信息') else []
            tzr= self.parse_page_qygs(page, 'touziren', post_data)
            sub_json_dict['ent_pub_shareholder_capital_contribution'] = tzr[u'股东及出资信息'] if tzr.has_key(u'股东及出资信息') else []

            sub_json_dict['ent_pub_reg_modify'] = tzr[u'变更信息'] if tzr.has_key(u'变更信息') else []
            gq = self.parse_page_qygs(page, 'gudongguquan', post_data)
            sub_json_dict['ent_pub_equity_change'] = gq[u'股权变更信息'] if gq.has_key(u'股权变更信息') else []
            zscq = self.parse_page_qygs(page, 'zhishichanquan', post_data)
            sub_json_dict['ent_pub_knowledge_property'] = zscq[u'知识产权出质登记信息'] if zscq.has_key(u'知识产权出质登记信息') else []
        except Exception as e:
            logging.error(u"An error ocurred in crawl_ent_pub_pages: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #爬取 其他部门公示 页面
    def crawl_other_dept_pub_pages(self, url):
        sub_json_dict = {}
        try:
            logging.error( u"crawl the crawl_other_dept_pub_pages page %s."%(url))
            page = self.crawl_page_by_url(url)['page']
            #html_to_file('next.html', page)
            # entpripid = url[url.rfind('/')+1:]
            # post_data = {'encrpripid' : entpripid}
            xk = self.parse_page_qtbm(page, "xingzhengxuke")#行政许可信息
            sub_json_dict["other_dept_pub_administration_license"] =  xk[u'行政许可信息'] if xk.has_key(u'行政许可信息') else []
            cf = self.parse_page_qtbm(page, "xingzhengchufa")  # 行政处罚信息
            sub_json_dict["other_dept_pub_administration_sanction"] = cf[u'行政处罚信息'] if cf.has_key(u'行政处罚信息') else []
        except Exception as e:
            logging.error(u"An error ocurred in crawl_other_dept_pub_pages: %s"% (type(e)))
            raise e
        finally:
            return sub_json_dict

    def crawl_judical_assist_pub_pages(self, url):
        """爬取司法协助信息页面
        """
        sub_json_dict = {}
        try:
            logging.error( u"crawl the crawl_judical_assist_pub_pages page %s."%(url))
            page = self.crawl_page_by_url(url)['page']
            #html_to_file('next.html', page)
            xz = self.parse_page_sfxz(page, 'sifaxiezhu')
            sub_json_dict['judical_assist_pub_equity_freeze'] = xz[u'司法股权冻结信息'] if xz.has_key(u'司法股权冻结信息') else []
            gd = self.parse_page_sfxz(page, 'sifagudong')
            sub_json_dict['judical_assist_pub_shareholder_modify'] = gd[u'司法股东变更登记信息'] if gd.has_key(u'司法股东变更登记信息') else []
        except Exception as e:
            logging.error(u"An error ocurred in crawl_judical_assist_pub_pages: %s"% (type(e)))
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

    # 司法协助信息页面
    def parse_page_sfxz(self, page, div_id='sifapanding', post_data= {}):
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
                    if table_name== u"司法股权冻结信息":
                        page_data[table_name] = (self.parse_table_sfxz_sfgq(table, table_name, page))
                    else:
                        page_data[table_name] = (self.parse_table(table, table_name, page))
        except Exception as e:
            logging.error(u'parse sifaxiezhu pagefailed, with exception %s' % e)
            raise e
        finally:
            return page_data

    # 司法协助 - 股权冻结信息
    def parse_table_sfxz_sfgq(self, bs_table, table_name, page, post_data={}):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            m_enttype = re.compile(r'enttype.*?;').search(page)
            if m_enttype:
                enttypestr = m_enttype.group()
                enttype = str(re.compile(r"\d+").search(enttypestr).group())
                m_encrpripidstr = re.compile(r'encrpripid.*?;').search(page)
                if m_encrpripidstr:
                    encrpripidstr = m_encrpripidstr.group()
                    encrpripid = str(re.compile(r"(\'.*?\')").search(encrpripidstr).group()[1:-1]) # convert to list
                    m = re.compile(r"gqxxliststr.*?;").search(page)
                    if m:
                        gqxxliststr = m.group()
                        #print gqxxliststr
                        try:
                            # 不知道啥情况，strs自动添加了连个引号
                            strs = re.compile(r"(\'.*?\')").search(gqxxliststr).group().strip("'")
                            if strs:
                                gqxxlist = json.JSONDecoder().decode(strs)
                        except Exception as e:
                            raise e
                        sub_item = []
                        for i, item in enumerate(gqxxlist):

                            link = urls['webroot']+'pub/sfgsgqxxdetail/'+encrpripid+'/'+enttype+'/'+str(item['pid'])+'/'+ str(item['frozstate'])
                            logging.error( u"crawl the link %s, table_name is %s"%(link, table_name))
                            link_page = self.crawl_page_by_url(link)['page']
                            link_data = self.parse_page_sfxz(link_page)
                            datas = [i+1, item['inv'], str(item['froam'])+ (u"万股" if enttype.find('12') != -1 and enttype.find('52')!=-1 and enttype.find('62')!= -1 else u"万元"), \
                                    item['froauth'], item['executeno'],  u'冻结' if int(item['frozstate'])== 1 else u'解除冻结' if int(item['frozstate'])==2 else u'失效' , link_data ]
                            sub_item.append(dict(zip(titles, datas)))
                        #sub_json_list[u"司法股权冻结信息"] = sub_item
                        sub_json_list = sub_item
                else:
                    logging.error(u"Can not find encrpripid in html")
                    return sub_json_list
            else:
                logging.error(u"Can not find enttype in html")
                return sub_json_list
        except Exception as e:
            logging.error(u"parse 司法协助 table 司法协助- 司法股权冻结信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list

    # 其他部门信息页面
    def parse_page_qtbm(self, page, div_id='sifapanding', post_data= {}):
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
                        page_data[table_name] = self.parse_table(table, table_name, page)
                table = table.nextSibling
        except Exception as e:
            logging.error(u'parse qitabumen failed, with exception %s' % e)
            raise e
        finally:
            return page_data

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

    def SetJsonTime(self, item):
        if type(item)== dict:
            return str(item['year']+1900)+'年'+ str(item['month']%12+1)+'月'+ str(item['date'])+'日'
        return ""
    #企业公示页面分析
    dicts_qygs={
        u"股东及出资信息":"http://218.57.139.24/pub/qygsjsxxxzczxx",
        u"变更信息":"http://218.57.139.24/pub/qygsjsxxczxxbgsx",
        u"股权变更信息":"http://218.57.139.24/pub/qygsJsxxgqbg",
        u"行政许可信息":"http://218.57.139.24/pub/qygsjsxxxzxk",
        u"知识产权出质登记信息":"http://218.57.139.24/pub/qygsjsxxzscqcz",
        u"行政处罚信息":"http://218.57.139.24/pub/qygsjsxxxzcfxx",
    }
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
    # 股东及出资信息
    def parse_table_qygs_gudongchuzi(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            #columns = self.get_columns_of_record_table(bs_table, page, table_name)
            #titles = [column[0] for column in columns]
            url = self.dicts_qygs[table_name]
            #print post_data
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            #print type(res)
            ls = json.loads(res)
            for i, l in enumerate(ls):
                #logging.error( u"crawl the link %s, table_name is %s"%(link, table_name))
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

    # 股东及出资 - 变更信息
    def parse_table_qygs_biangengxinxi(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = self.dicts_qygs[table_name]
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            #print type(res)
            ls = json.loads(res)
            for rows in ls:
                for i, l in enumerate(rows['bgxx']):
                    date_from = l['altdate']
                    #logging.error( u"crawl the link %s, table_name is %s"%(link, table_name))
                    # 这里注意type
                    datas = [i+1, l['altitem'], self.SetJsonTime(date_from), l['altbe'], l['altaf'] ]
                    sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse qygs table 股东及出资- 变更信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list

    # 知识产权出质登记信息
    def parse_table_qygs_zhishichanquan(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = self.dicts_qygs[table_name]
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            #print type(res)
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_from = l['pleregperfrom']
                date_to = l['pleregperto']
                link = urls['webroot']+"pub/jszscqdetail/"+post_data['encrpripid']+"/"+l['pid']+"/"+l['type']
                link_page = self.crawl_page_by_url(link)['page']
                logging.error( u"crawl the link %s, table_name is %s"%(link, table_name))
                link_data = self.parse_page_qygs(link_page)
                # 这里注意type
                datas = [i+1, l['tmregno'], l['tmname'], l['kinds'], l['pledgor'], l['imporg'],  self.SetJsonTime(date_from) +" - " + self.SetJsonTime(date_to) , '有效' if int(l['type'])==1 else '无效', link_data]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse qygs table 知识产权出质登记信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list

    # 股权变更信息
    def parse_table_qygs_guquan(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = self.dicts_qygs[table_name]
            #print post_data
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            #print type(res)
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_from = l['altdate']
                #logging.error( u"crawl the link %s, table_name is %s"%(link, table_name))
                # 这里注意type
                datas = [i+1, l['inv'], l['transamprpre'], l['transampraft'] , self.SetJsonTime(date_from)]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse qygs table 股权变更信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list

    # 行政处罚信息
    def parse_table_qygs_xinzhengchufa(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = self.dicts_qygs[table_name]
            #print post_data
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            #print type(res)
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_from = l['pendecissdate']
                #logging.error( u"crawl the link %s, table_name is %s"%(link, table_name))
                # 这里注意type
                datas = [i+1, l['pendecno'], self.getCfType(l['pentype']),l['penauth'] , self.SetJsonTime(date_from), l['remark']]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse qygs table 行政处罚信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list

    # 行政许可信息
    def parse_table_qygs_xinzhengxuke(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = self.dicts_qygs[table_name]
            #print post_data
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            #print type(res)
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_from = l['valfrom']
                date_to   = l['valto']
                link = urls['webroot']+"pub/jsxzxkdetail/"+post_data['encrpripid']+"/"+l['pid']+"/"+l['type']
                #link_page = self.crawl_page_by_url(link)['page']
                #logging.error( u"crawl the link %s, table_name is %s"%(link, table_name))
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
    #工商公示信息表连接
    dicts={
        u"主要人员信息" : "http://218.57.139.24/pub/gsryxx/1223",
        u"分支机构信息" : "http://218.57.139.24/pub/gsfzjg/1223",
        u"动产抵押登记信息": "http://218.57.139.24/pub/gsdcdy",
        u"股权出质登记信息":"http://218.57.139.24/pub/gsgqcz",
        u"严重违法信息":"http://218.57.139.24/pub/yzwfqy",
        u"抽查检查信息":"http://218.57.139.24/pub/ccjcxx",
        u"经营异常信息":"http://218.57.139.24/pub/jyyc/1223",
        u"行政处罚信息":"http://218.57.139.24/pub/gsxzcfxx",
    }
    # 工商公式信息页面
    def parse_page(self, page, div_id='sifapanding', post_data= {}):
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
                        elif table_name == u"变更":
                            page_data[table_name] = self.parse_table_guquanchuzhi_biangeng(table, table_name, page, post_data)
                        else:
                            page_data[table_name] = self.parse_table(table, table_name, page)
                table = table.nextSibling

        except Exception as e:
            logging.error(u'parse failed, with exception %s' % e)
            raise e
        finally:
            return page_data
    #经营异常信息
    def parse_table_jingyingyichang(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = self.dicts[table_name]
            #print post_data
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            #print type(res)
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
    # 行政处罚信息
    def parse_table_xingzhengchufa(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = self.dicts[table_name]
            #print post_data
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            #print type(res)
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_abn = l['pendecissdate']
                #logging.error( u"crawl the link %s, table_name is %s"%(link, table_name))
                link = urls['webroot']+"pub/gsxzcfdetail/"+post_data['encrpripid']+"/"+l['caseno']
                logging.error( u"crawl the link %s, table_name is %s"%(link, table_name))
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

    #行政处罚信息初始化展示
    def getCfType(cftype):
        if(cftype =='01'): return '警告'
        if(cftype =='02'): return '罚款'
        if(cftype =='03'): return '没收违法所得和非法财物'
        if(cftype =='04'): return '责令停产停业'
        if(cftype =='05'): return '暂扣许可证'
        if(cftype =='06'): return '暂扣执照(登记证)'
        if(cftype =='07'): return '吊销许可证'
        if(cftype =='08'): return '吊销执照(登记证)'
        if(cftype =='09'): return '法律、法规规定的其他行政处罚方式'
        if(cftype =='1') :return '警告'
        if(cftype =='2') :return '罚款'
        if(cftype =='3') :return '没收违法所得和非法财物'
        if(cftype =='4') :return '责令停产停业'
        if(cftype =='5') :return '暂扣许可证'
        if(cftype =='6') :return '暂扣执照(登记证)'
        if(cftype =='7') :return '吊销许可证'
        if(cftype =='8') :return '吊销执照(登记证)'
        if(cftype =='9') :return '法律、法规规定的其他行政处罚方式'
    # 抽样检查信息
    def parse_table_chouyangjiancha(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = self.dicts[table_name]
            #print post_data
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            #print type(res)
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_abn = l['insdate']
                #logging.error( u"crawl the link %s, table_name is %s"%(link, table_name))

                # 这里注意type
                datas = [i+1, l['insauth'], l['instype'],self.SetJsonTime(date_abn), l['insres']]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse table 抽样检查信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 严重违法信息
    def parse_table_yanzhongweifa(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = self.dicts[table_name]
            #print post_data
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            #print type(res)
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_abn = l['abntime']
                date_rem = l['remdate']
                #logging.error( u"crawl the link %s, table_name is %s"%(link, table_name))
                # 这里注意type
                datas = [i+1, l['serillrea'],self.SetJsonTime(date_abn), l['remexcpres'],self.SetJsonTime(date_rem), l['decorg']]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse table 严重违法信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 股权出质---变更
    def parse_table_guquanchuzhi_biangeng(self, bs_table, table_name, page, post_data={}):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            m1  = re.compile(r"_gqczBgxxlist\s*=\s*eval\((\'.*?\')\)").search(page)
            if m1:
                pripidstr = m1.group()
                # turn into list
                strs = re.compile(r"(\'.*?\')").search(pripidstr).group()
                if strs.strip("'"):
                    bglist = json.loads(strs.strip("'"))
                    for i, item in enumerate(bglist):
                        altdate = item['altdate']
                        datas= [i+1,self.SetJsonTime(altdate), item['alt']]
                        sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse table 股权出质--变更 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 股权出质
    def parse_table_guquanchuzhi(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = self.dicts[table_name]
            #print post_data
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            #print type(res)
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_dict = l['equpledate']
                link = urls['webroot']+"pub/gsgqczdetail/"+post_data['encrpripid']+"/"+str(l['equityno'])+"/"+str(l['type'])
                logging.error( u"crawl the link %s, table_name is %s"%(link, table_name))
                link_page = self.crawl_page_by_url(link)['page']
                #print link_page
                ########!!!!!!!!!!!!!!这里的link_page没有做
                link_data = self.parse_page(link_page)
                # 这里注意type
                datas = [i+1, l['equityno'], l['pledgor'], l['blicno'], str(l['impam'])+l['pledamunit'], l['imporg'], l['impmorblicno'],self.SetJsonTime(date_dict) ,'有效' if int(l['type'])==1 else '无效', link_data]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse table 股权出质 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 动产抵押登记信息
    def parse_table_dongchandiya(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = self.dicts[table_name] #"http://218.57.139.24/pub/gsfzjg/1223"
            #print post_data
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            #print type(res)
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
    # 分支机构信息
    def parse_table_branch(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = self.dicts[table_name] #"http://218.57.139.24/pub/gsfzjg/1223"
            #print post_data
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            #print type(res)
            ls = json.loads(res)
            for i, l in enumerate(ls):
                datas = [i+1, l['regno'], l['brname'], l['regorg']]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse table 分支机构信息 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 主要人员信息
    def parse_table_people(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = self.dicts[table_name] #"http://218.57.139.24/pub/gsryxx/1223"
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
    # 股东信息表
    def parse_table_gudong(self, bs_table, table_name, page):
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
                    #print type(czxxlist)
                    #var encrpripid = '6e0948678bfeed4ac8115d5cafef819ad6951a24f0c0188cd6c047570329c9b6';
                    m1  = re.compile(r"encrpripid\s*=\s*(\'.*?\');").search(page)
                    if m1:
                        pripidstr = m1.group()

                        encrpripid = re.compile(r"(\'.*?\')").search(pripidstr).group().strip("'")

                        for item in czxxlist:
                            if item['xzqh'] == "1":
                                link = urls['webroot'] + 'pub/gsnzczxxdetail/'+ encrpripid+'/'+ item['recid']
                                link_page = self.crawl_page_by_url(link)['page']
                                link_data = self.parse_page(link_page, table_name+'_detail')
                                datas = [ item['invtype'], item['inv'], item['blictype'], item['blicno'], link_data]
                            else:
                                datas = [ item['invtype'], item['inv'], item['blictype'], item['blicno'], '']
                            sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            logging.error(u"parse table 股东信息表 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 股东及出资信息
    def parse_table_gdczxx(self, bs_table, table_name, page):
        sub_json_dict= {}
        try:
            #columns = self.get_columns_of_record_table(bs_table, page, table_name)
            #czxxlist
            m = re.compile(r"czxxstr\s*=\s*(\'.*?\');").search(page)
            if m:
                czxxliststr = m.group()
                czxxliststr = re.compile(r"(\'.*?\')").search(czxxliststr).group()
                czxxlist = json.loads(czxxliststr.strip("'")) if czxxliststr.strip("'") else [] # 将字符串转换成list
                m1  = re.compile(r"czxxrjstr\s*=\s*(\'.*?\');").search(page)      # 认缴
                if m1:
                    czxxrjstr = m1.group()
                    czxxrjstr = re.compile(r"(\'.*?\')").search(czxxrjstr).group().strip("'")
                    czxxrjlist = json.loads(czxxrjstr) if czxxrjstr else []
                    m2  = re.compile(r"czxxsjstr\s*=\s*(\'.*?\');").search(page)      # 实缴
                    if m2:
                        czxxsjstr = m2.group()
                        czxxsjstr = re.compile(r"(\'.*?\')").search(czxxsjstr).group().strip("'")
                        czxxsjlist = json.loads(czxxsjstr) if czxxsjstr else []
                        ######################
                        item = {}
                        sub_item = {}
                        if len(czxxlist) > 0 and czxxlist[0]:
                            item[u'股东（发起人）'] = czxxlist[0]['inv']
                            item[u'认缴额（万元）'] = czxxlist[0]['lisubconam']
                            item[u'实缴额（万元）'] = czxxlist[0]['liacconam']
                        if len(czxxrjlist) >0 and czxxrjlist[0]:
                            sub_item[u'认缴出资方式'] =  czxxrjlist[0]['conform']
                            sub_item[u'认缴出资额（万元）'] =czxxrjlist[0]['subconam']
                            date_dict = czxxrjlist[0]['condate']
                            #print type(date_dict['date'])   全是int型
                            sub_item[u'认缴出资日期'] =self.SetJsonTime(date_dict)
                        else:
                            sub_item[u'认缴出资方式'] =""
                            sub_item[u'认缴出资额（万元）'] =""
                            sub_item[u'认缴出资日期'] = ""
                        item[u'认缴明细'] = sub_item
                        sub_item = {}
                        if len(czxxsjlist) > 0 and czxxsjlist[0]:
                            sub_item[u'实缴出资方式'] =czxxsjlist[0]['conform']
                            sub_item[u'实缴出资额（万元）'] =czxxsjlist[0]['acconam']
                            date_dict = czxxsjlist[0]['condate']

                            sub_item[u'实缴出资日期'] = self.SetJsonTime(date_dict)
                        else:
                            sub_item[u'实缴出资方式'] =""
                            sub_item[u'实缴出资额（万元'] =""
                            sub_item[u'实缴出资日期'] = ""
                        item[u'实缴明细'] = sub_item
                        sub_json_dict = (item.copy())
        except Exception as e:
            logging.error(u"parse table 股东及出资信息 failed with exception:%s" % (type(e)))
        finally:
            return [sub_json_dict]
        pass
    # 变更信息表
    def parse_table_biangeng(self, bs_table, table_name, page):
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
                                logging.error(u'crawl detail url: %s'% next_url)
                                if next_url:
                                    detail_page = self.crawl_page_by_url(next_url)
                                    #html_to_file("test.html", detail_page['page'])
                                    #print "table_name : "+ table_name
                                    if table_name == u'企业年报':
                                        #logging.error(u"next_url = %s, table_name= %s\n", detail_page['url'], table_name)
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
        text = ""
        urls = ""
        try:
            r = self.requests.get( url, proxies = self.proxies, timeout= self.timeout)
            if r.status_code != 200:
                logging.error(u"Getting page by url:%s, return status %s\n"% (url, r.status_code))
            text = r.text
            urls = r.url
            # 为了防止页面间接跳转，获取最终目标url
        except requests.exceptions.ConnectionError :
            self.proxies = Proxies().get_proxies()
            logging.error("get method self.proxies changed proxies = %s\n"%(self.proxies))
            return self.crawl_page_by_url( url)
        except requests.exceptions.Timeout:
            self.timeout += 5
            logging.error("get method self.timeout plus timeout = %d, proxies= %s\n"%(self.timeout, self.proxies) )
            if self.timeout >25:
                logging.error("post method self.timeout plus timeout > 100 , proxies= %s\n"%(self.proxies) )
                self.proxies = Proxies().get_proxies()
            return self.crawl_page_by_url( url)
        except Exception as e:
            logging.error(u"Cann't get page by url:%s, exception is %s"%(url, type(e)))
        return {'page' : text, 'url': urls}

    def crawl_page_by_url_post(self, url, data, header={}):
        text = ""
        urls = ""
        try:
            self.requests.headers.update(header)
            r = self.requests.post(url, data, proxies = self.proxies, timeout= self.timeout)
            if r.status_code != 200:
                logging.error(u"Getting page by url with post:%s, return status %s\n"% (url, r.status_code))
            text = r.text
            urls = r.url
        except requests.exceptions.ConnectionError :
            self.proxies = Proxies().get_proxies()
            logging.error("post method self.proxies changed proxies = %s\n"%(self.proxies))
            return self.crawl_page_by_url_post( url, data, header)
        except requests.exceptions.Timeout:
            self.timeout += 5
            logging.error("post method self.timeout plus timeout = %d, proxies= %s\n"%(self.timeout, self.proxies) )
            if self.timeout >25:
                self.proxies = Proxies().get_proxies()
                logging.error("post method self.timeout plus timeout > 100 , proxies= %s\n"%(self.proxies) )
            return self.crawl_page_by_url_post( url, data, header)
        except Exception as e:
            logging.error(u"Cann't post page by url:%s, exception is %s"%(url, type(e)))
        return {'page': text, 'url': urls}

    def run(self, ent_num):
        if not os.path.exists(self.html_restore_path):
            os.makedirs(self.html_restore_path)
        json_dict = {}
        self.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        data = self.crawl_page_main()
        json_dict[ent_num] = data
        # json_dump_to_file(self.json_restore_path , json_dict)
        # 2016-2-16
        return json.dumps(json_dict)

    def work(self, ent_num= ""):

        # if not os.path.exists(self.html_restore_path):
        #     os.makedirs(self.html_restore_path)
        # self.json_dict = {}
        self.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        data = self.crawl_page_main()
        json_dump_to_file('shandong_json.json', data)

        #url = "http://218.57.139.24/pub/gsgsdetail/1223/6e0948678bfeed4ac8115d5cafef819ad6951a24f0c0188cd6c047570329c9b6"
        #data = self.crawl_ind_comm_pub_pages(url)
        #self.ents= ['/platform/saic/viewBase.ftl?entId=349DDA405D520231E04400306EF52828']
        #data = self.crawl_page_main()

        # txt = html_from_file('test.html')
        # data = self.parse_page(txt)
        # print data
        #txt = html_from_file('next.html')

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
    shandong = ShandongCrawler('./enterprise_crawler/shandong.json')
    #shandong.work('370000018067809')
    shandong.work('371400400000937')


if __name__ == "__main__":
    reload (sys)
    sys.setdefaultencoding('utf8')
    import run
    run.config_logging()
    if not os.path.exists("./enterprise_crawler"):
        os.makedirs("./enterprise_crawler")
    shandong = ShandongCrawler('./enterprise_crawler/shandong.json')
    ents = read_ent_from_file("./enterprise_list/shandong.txt")
    shandong = ShandongCrawler('./enterprise_crawler/shandong.json')
    for ent_str in ents:
        logging.error(u'###################   Start to crawl enterprise with id %s   ###################\n' % ent_str[2])
        shandong.run(ent_num = ent_str[2])
        logging.error(u'###################   Enterprise with id  %s Finished!  ###################\n' % ent_str[2])

"""
