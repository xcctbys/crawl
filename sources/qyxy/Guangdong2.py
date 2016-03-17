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
from bs4 import BeautifulSoup
import CaptchaRecognition as CR


urls = {
    'host': 'http://gsxt.gdgs.gov.cn/aiccips/',
    'prefix_url':'http://www.szcredit.com.cn/web/GSZJGSPT/',
    'page_search': 'http://gsxt.gdgs.gov.cn/aiccips/index',
    'page_Captcha': 'http://gsxt.gdgs.gov.cn/aiccips/verify.html',
    'page_showinfo': 'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/showInfo.html',
    'checkcode':'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/checkCode.html',
    'ind_comm_pub_reg_basic': 'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo',
    'prefix_GSpublicity':'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=',
}
#debug control parameter


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
    def crawl_ind_comm_pub_pages(self, url, types=2, post_data= {}):
        sub_json_dict={}
        try:


            tabs = (
                    'entInfo',          # 登记信息
                    'curStoPleInfo',    #股权出质
                    'entCheckInfo',     #备案信息
                    'pleInfo',          #动产抵押登记信息
                    'cipPenaltyInfo',   #行政处罚
                    'cipUnuDirInfo',    #经营异常
                    'cipBlackInfo',     #严重违法
                    'cipSpotCheInfo',   #抽查检查
                    )

            div_names = (
                            'jibenxinxi',
                            'guquanchuzhi',
                            'beian',
                            'dongchandiya',
                            'xingzhengchufa',
                            'jingyingyichang',
                            'yanzhongweifa',
                            'chouchajiancha',
                        )
            for tab, div_name in zip(tabs, div_names):
                #url = "http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=" + tab
                url = urls['prefix_GSpublicity'] + tab
                page = self.crawl_page_by_url_post(url, post_data)['page']
                if div_name == 'jibenxinxi':
                    dict_jiben = self.analysis.parse_page_2(page, div_name, post_data)
                    sub_json_dict['ind_comm_pub_reg_modify'] = dict_jiben[u'变更信息'] if dict_jiben.has_key(u"变更信息") else {}
                    sub_json_dict['ind_comm_pub_reg_basic'] =  dict_jiben[u'基本信息'] if dict_jiben.has_key(u"基本信息") else []
                    sub_json_dict['ind_comm_pub_reg_shareholder']= dict_jiben[u'股东信息'] if dict_jiben.has_key(u"股东信息") else []
                elif div_name == 'beian':
                    dict_beian = self.analysis.parse_page_2(page, div_name, post_data)
                    sub_json_dict['ind_comm_pub_arch_key_persons']=  dict_beian[u'主要人员信息'] if dict_beian.has_key(u"主要人员信息") else []
                    sub_json_dict['ind_comm_pub_arch_branch'] = dict_beian[u'分支机构信息'] if dict_beian.has_key(u"分支机构信息") else []
                    sub_json_dict['ind_comm_pub_arch_liquidation'] = dict_beian[u"清算信息"] if dict_beian.has_key(u'清算信息') else []
                elif div_name == 'guquanchuzhi':
                    dj = self.analysis.parse_page_2(page, div_name, post_data)
                    sub_json_dict['ind_comm_pub_equity_ownership_reg'] = dj[u'股权出质登记信息'] if dj.has_key(u'股权出质登记信息') else []
                elif div_name == 'dongchandiya':
                    dj = self.analysis.parse_page_2(page, div_name, post_data)
                    sub_json_dict['ind_comm_pub_movable_property_reg'] = dj[u'动产抵押信息'] if dj.has_key(u'动产抵押信息') else []
                elif div_name == 'xingzhengchufa':
                    dj = self.analysis.parse_page_2(page, div_name, post_data)
                    sub_json_dict['ind_comm_pub_administration_sanction'] = dj[u'行政处罚信息'] if dj.has_key(u'行政处罚信息') else []
                elif div_name == 'jingyingyichang':
                    dj = self.analysis.parse_page_2(page, div_name, post_data)
                    sub_json_dict['ind_comm_pub_business_exception'] = dj[u'经营异常信息'] if dj.has_key(u'经营异常信息') else []
                elif div_name == 'yanzhongweifa':
                    dj = self.analysis.parse_page_2(page, div_name, post_data)
                    sub_json_dict['ind_comm_pub_serious_violate_law'] =  dj[u'严重违法信息'] if dj.has_key(u'严重违法信息') else []
                elif div_name == 'chouchajiancha':
                    dj = self.analysis.parse_page_2(page, div_name, post_data)
                    sub_json_dict['ind_comm_pub_spot_check'] = dj[u'抽查检查信息'] if dj.has_key(u'抽查检查信息') else []

        except Exception as e:
            settings.logger.debug(u"An error ocurred in crawl_ind_comm_pub_pages: %s, type is %d"% (type(e), types))
            raise e
        finally:
            return sub_json_dict
    #爬取 企业公示信息 页面
    def crawl_ent_pub_pages(self, url, types=2, post_data={}):
        sub_json_dict = {}
        try:
            page = self.crawl_page_by_url_post("http://gsxt.gdgs.gov.cn/aiccips/BusinessAnnals/BusinessAnnalsList.html", post_data)['page']
            p = self.analysis.parse_page_2(page, 'qiyenianbao', post_data)
            sub_json_dict['ent_pub_ent_annual_report'] = p[u'qiyenianbao'] if p.has_key(u'qiyenianbao') else []

            page = self.crawl_page_by_url_post("http://gsxt.gdgs.gov.cn/aiccips/AppPerInformation.html", post_data)['page']
            p = self.analysis.parse_page_2(page, 'appPer', post_data)
            sub_json_dict['ent_pub_administration_license'] = p[u'行政许可情况'] if p.has_key(u'行政许可情况') else []

            page = self.crawl_page_by_url_post("http://gsxt.gdgs.gov.cn/aiccips/XZPunishmentMsg.html", post_data)['page']
            p = self.analysis.parse_page_2(page, 'xzpun', post_data)
            sub_json_dict['ent_pub_administration_sanction'] = p[u'行政处罚情况'] if p.has_key(u'行政处罚情况') else []

            page = self.crawl_page_by_url_post("http://gsxt.gdgs.gov.cn/aiccips/ContributionCapitalMsg.html", post_data)['page']
            p = self.analysis.parse_page(page, 'sifapanding', post_data)
            sub_json_dict['ent_pub_shareholder_capital_contribution'] = p[u'股东及出资信息'] if p.has_key(u'股东及出资信息') else []
            sub_json_dict['ent_pub_reg_modify'] = p[u'变更信息'] if p.has_key(u'变更信息') else []

            page = self.crawl_page_by_url_post("http://gsxt.gdgs.gov.cn/aiccips/GDGQTransferMsg/shareholderTransferMsg.html", post_data)['page']
            p = self.analysis.parse_page_2(page, 'guquanbiangeng', post_data)
            sub_json_dict['ent_pub_equity_change'] = p[u'股权变更信息'] if p.has_key(u'股权变更信息') else []

            page = self.crawl_page_by_url_post("http://gsxt.gdgs.gov.cn/aiccips/intPropertyMsg.html", post_data)['page']
            p = self.analysis.parse_page_2(page, 'inproper', post_data)
            sub_json_dict['ent_pub_knowledge_property'] = p[u'知识产权出质登记信息'] if p.has_key(u'知识产权出质登记信息') else []
        except Exception as e:
            settings.logger.debug(u"An error ocurred in crawl_ent_pub_pages: %s, types = %d"% (type(e), types))
            raise e
        finally:
            return sub_json_dict
        #json_dump_to_file("json_dict.json", self.json_dict)

    #爬取 其他部门公示信息 页面
    def crawl_other_dept_pub_pages(self, url, types=2, post_data={}):
        sub_json_dict={}
        # titles =(   'other_dept_pub_administration_license',#行政许可信息
        #             'other_dept_pub_administration_sanction',#行政处罚信息
        #         )
        try:
            # other_dept_urls = {
            #     "xzxk"  :   "http://gsxt.gdgs.gov.cn/aiccips/OtherPublicity/environmentalProtection.html",
            #     "czcf"  :   "http://gsxt.gdgs.gov.cn/aiccips/OtherPublicity/environmentalProtection.html",
            #     }
            # for title, ids in zip(titles, other_dept_urls):
            #     url = other_dept_urls[ids]
            #     page = self.crawl_page_by_url_post(url, post_data)['page']
            #     sub_json_dict[title] = self.analysis.parse_page_2(page, ids, post_data)
            page = self.crawl_page_by_url_post("http://gsxt.gdgs.gov.cn/aiccips/OtherPublicity/environmentalProtection.html", post_data)['page']
            xk = self.analysis.parse_page_2(page, "xzxk", post_data)
            sub_json_dict["other_dept_pub_administration_license"] =  xk[u'行政许可信息'] if xk.has_key(u'行政许可信息') else []
            page = self.crawl_page_by_url_post("http://gsxt.gdgs.gov.cn/aiccips/OtherPublicity/environmentalProtection.html", post_data)['page']
            xk = self.analysis.parse_page_2(page, "czcf", post_data)
            sub_json_dict["other_dept_pub_administration_sanction"] = xk[u'行政处罚信息'] if xk.has_key(u'行政处罚信息') else []  # 行政处罚信息
        except Exception as e:
            settings.logger.debug(u"An error ocurred in crawl_other_dept_pub_pages: %s, types = %d"% (type(e), types))
            raise e
        finally:
            return sub_json_dict
    #judical assist pub informations
    def crawl_judical_assist_pub_pages(self, url, types=2, post_data= {}):
        sub_json_dict={}
        # titles = (  'judical_assist_pub_equity_freeze', # 股权冻结信息
        #             'judical_assist_pub_shareholder_modify', #股东变更信息
        #             )
        try:

            # judical_assist_url = {
            #     "guquandongjie"   :   "http://gsxt.gdgs.gov.cn/aiccips/judiciaryAssist/judiciaryAssistInit.html",
            #     "gudongbiangeng"  :   "http://gsxt.gdgs.gov.cn/aiccips/sfGuQuanChange/guQuanChange.html",
            #     }

            # for (title, ids) in zip(titles, judical_assist_url):
            #     url = judical_assist_url[ids]
            #     page = self.crawl_page_by_url_post(url, post_data)['page']
            #     sub_json_dict[title] = self.analysis.parse_page_2(page, ids, post_data)
            page = self.crawl_page_by_url_post('http://gsxt.gdgs.gov.cn/aiccips/judiciaryAssist/judiciaryAssistInit.html', post_data)['page']
            xz  = self.analysis.parse_page_2(page, 'guquandongjie', post_data)
            sub_json_dict['judical_assist_pub_equity_freeze'] = xz[u'司法股权冻结信息'] if xz.has_key(u'司法股权冻结信息') else []
            page = self.crawl_page_by_url_post('http://gsxt.gdgs.gov.cn/aiccips/sfGuQuanChange/guQuanChange.html', post_data)['page']
            xz  = self.analysis.parse_page_2(page, 'gudongbiangeng', post_data)
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
        # url = "http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo_GmjYOaEEX9Xx3eeM0JcrtOywZcfQzs3Ry0M6NPS1/iCr+cQwm+oHVoPBzdIqEiYb-7vusEl1hPU+qjV70QwcUXQ=="
        print "work"
        url = "http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo_3au/If33vWye5UuPp+iY6u6FQtJGDUruMalngHz1ONi2UJ96uTS+QaKhmOwDSFMD-7kW54gFL28iQmsO8Qn3cTA=="

        page_entInfo = self.crawl_page_by_url(url)['page']
        post_data = self.analysis.parse_page_data_2(page_entInfo)
        print post_data
        data = self.crawl_ind_comm_pub_pages(url, 2, post_data)
        print data
        # self.crawl_ent_pub_pages(url, 2, post_data)
        #
        #self.crawl_other_dept_pub_pages(url, 2)
        #self.crawl_judical_assist_pub_pages(url, 2)

        #datas = html_from_file('next.html')
        #self.analysis.parse_ent_pub_annual_report_page_2(datas, "_detail")
        """
        sub_json_dict = {}
        datas = html_from_file('next.html')
        sub_json_dict['guquanbiangeng'] = self.analysis.parse_page_2(datas, 'guquanbiangeng', {})
        json_dump_to_file("crawl_ent_pub_pages.json", sub_json_dict)
        """

    def run(self, ent):
        sub_json_dict= {}
        url = ent
        page_entInfo = self.crawl_page_by_url(url)['page']
        post_data = self.analysis.parse_page_data_2(page_entInfo)

        sub_json_dict.update(self.crawl_ind_comm_pub_pages(url, 2, post_data))
        url = "http://gsxt.gdgs.gov.cn/aiccips/BusinessAnnals/BusinessAnnalsList.html"
        sub_json_dict.update(self.crawl_ent_pub_pages(url, 2, post_data))
        url = "http://gsxt.gdgs.gov.cn/aiccips/OtherPublicity/environmentalProtection.html"
        sub_json_dict.update(self.crawl_other_dept_pub_pages(url, 2, post_data))
        url = "http://gsxt.gdgs.gov.cn/aiccips/judiciaryAssist/judiciaryAssistInit.html"
        sub_json_dict.update(self.crawl_judical_assist_pub_pages(url, 2, post_data))
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

    def get_detail_link(self, bs4_tag):
        if bs4_tag['href'] and bs4_tag['href'] != '#':
            pattern = re.compile(r'http')
            if pattern.search(bs4_tag['href']):
                return bs4_tag['href']
            return urls['prefix_url'] + bs4_tag['href']
        elif bs4_tag['onclick']:
            return self.get_detail_link_onclick(bs4_tag)

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
            tbody= bs_table.find_all('tbody')[1]
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
            settings.logger.error(u'exception occured in get_table_columns, except_type = %s, table_name = %s' % (type(e), table_name))
        finally:
            return columns

    def parse_ent_pub_annual_report_page_2(self, base_page, page_type):

        page_data = {}
        soup = BeautifulSoup(base_page, 'html5lib')
        if soup.body.find('table'):
            try:
                base_table = soup.body.find('table')
                table_name = u'企业基本信息'#self.get_table_title(base_table)
                #这里需要连续两个nextSibling，一个nextSibling会返回空
                detail_base_table = base_table.nextSibling.nextSibling
                if detail_base_table.name == 'table':
                    page_data[table_name] = self.parse_table_2(detail_base_table )
                    pass
                else:
                    settings.logger.error(u"Can't find details of base informations for annual report")
            except Exception as e:
                settings.logger.error(u"fail to get table name with exception %s" % (type(e)))
            try:
                table = detail_base_table.nextSibling.nextSibling
                while table:
                    if table.name == 'table':
                        table_name = self.get_table_title(table)
                        page_data[table_name] = []
                        columns = self.get_columns_of_record_table(table, base_page, table_name)
                        page_data[table_name] =self.parse_table_2(table, columns, {}, table_name)
                    table = table.nextSibling
            except Exception as e:
                settings.logger.error(u"fail to parse the rest tables with exception %s" %(type(e)))
        else:
            pass
        return page_data


    def parse_page_data_2(self, page):
        data= {
            "aiccipsUrl": "",
            "entNo": "",
            "entType":"",
            "regOrg":"",
        }
        try:
            soup = BeautifulSoup(page, "html5lib")
            data['aiccipsUrl'] = soup.find("input", {"id": "aiccipsUrl"})['value']
            data['entNo'] = soup.find("input", {"id": "entNo"})['value']
            data['entType'] = soup.find("input", {"id": "entType"})['value'].strip()+"++"
            data['regOrg'] = soup.find("input", {"id": "regOrg"})['value']

        except Exception as e:
            settings.logger.error(u"parse page failed in function parse_page_data_2\n" )
            raise e
        finally:
            return data

    def get_particular_table(self, table, page):
        """ 获取 股东及出资信息的表格，按照指定格式输出
        """
        table_dict={}
        sub_dict = {}
        table_list=[]
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
                    sub_dict={}
                    sub_dict[u'实缴出资额（万元）'] = self.get_raw_text_by_tag(tds[5])
                    sub_dict[u'实缴出资方式'] = self.get_raw_text_by_tag(tds[6])
                    sub_dict[u'实缴出资时间'] = self.get_raw_text_by_tag(tds[7])
                    table_dict['实缴明细'] = sub_dict

                    table_dict['实缴额（万元）']= self.get_raw_text_by_tag(tds[5])
                    table_dict['认缴额（万元）']= self.get_raw_text_by_tag(tds[2])
                    table_list.append(table_dict)
        except Exception as e:
            settings.logger.error(u'parse 股东及出资信息 table failed! : %s'% e)
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
                    else :
                        table = divs.find('table')
                    #print table
                    table_name = ""
                    columns = []
                    while table:
                        if table.name == 'table':
                            table_name = self.get_table_title(table)
                            if table_name is None :
                                table_name = div_id
                            if table_name == u'股东及出资信息':
                                page_data[table_name] = self.get_particular_table(table, page)
                                table = table.nextSibling
                                continue
                            page_data[table_name] = []
                            columns = self.get_columns_of_record_table(table, page, table_name)
                            result =self.parse_table_2(table, columns, post_data, table_name)
                            if  not columns and not result :
                                del page_data[table_name]
                            else:
                                page_data[table_name] = result

                        elif table.name == 'div':
                            if not columns:
                                settings.logger.error(u"Can not find columns when parsing page 2, table :%s"%div_id)
                                break
                            page_data[table_name] =  self.parse_table_2(table, columns, post_data, table_name)
                            columns = []
                        table = table.nextSibling


                except Exception as e:
                    settings.logger.error(u'parse failed, with exception %s' % e)
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
                    else :
                        table = divs.find('table')
                    #print table
                    table_name = ""
                    columns = []
                    while table:
                        if table.name == 'table':
                            table_name = self.get_table_title(table)
                            if table_name is None :
                                table_name = div_id

                            page_data[table_name] = []
                            columns = self.get_columns_of_record_table(table, page, table_name)
                            result =self.parse_table_2(table, columns, post_data, table_name)
                            if  not columns and not result :
                                del page_data[table_name]
                            else:
                                page_data[table_name] = result

                        elif table.name == 'div':
                            if not columns:
                                settings.logger.error(u"Can not find columns when parsing page, table :%s"%div_id)
                                break
                            page_data[table_name] =  self.parse_table_2(table, columns, post_data, table_name)
                            columns = []
                        table = table.nextSibling


                except Exception as e:
                    settings.logger.error(u'parse failed, with exception %s' % e)
                    raise e

                finally:
                    pass
        return page_data

    def parse_table_2(self, bs_table, columns=[] , post_data= {}, table_name= ""):
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
                if len(tables)==2 and tables[1].find('a'):

                    # 获取下一页的url
                    clickstr = tables[1].find('a')['onclick']
                    re1='.*?'   # Non-greedy match on filler
                    re2='\\\'.*?\\\''   # Uninteresting: strng
                    re3='.*?'   # Non-greedy match on filler
                    re4='(\\\'.*?\\\')' # Single Quote String 1
                    re5='.*?'   # Non-greedy match on filler
                    re6='(\\\'.*?\\\')' # Single Quote String 2

                    rg = re.compile(re1+re2+re3+re4+re5+re6,re.IGNORECASE|re.DOTALL)
                    m = rg.search(clickstr)
                    url = ""
                    if m:
                        string1=m.group(1)
                        string2=m.group(2)
                        url = string1.strip('\'')+string2.strip('\'')
                        print url
                    else:
                        print "Can not find"
                    data = {
                        "pageNo" : 2 ,
                        "entNo" : post_data["entNo"].encode('utf-8'),
                        "regOrg" : post_data["regOrg"],
                        "entType" : post_data["entType"].encode('utf-8'),
                    }
                    res = self.crawler.crawl_page_by_url_post(url, data, {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',})
                    #print res['page']
                    if table_name == u"变更信息":
                        # chaToPage
                        d = json.loads(res['page'])
                        titles = [column[0] for column in columns]
                        for i, model in enumerate(d['list']):
                            data = [model['altFiledName'], model['altBe'], model['altAf'], model['altDate']]
                            item_array.append(dict(zip(titles, data)))
                    elif table_name == u"主要人员信息":
                        # vipToPage
                        d = json.loads(res['page'], encoding="utf-8")
                        titles = [column[0] for column in columns]
                        for i, model in enumerate(d['list']):
                            data = [ i+1, model['name'], model['position']]
                            item_array.append(dict(zip(titles, data)))

                    elif table_name == u"分支机构信息":
                        #braToPage
                        #print u"分支机构"
                        d = json.loads(res['page'])
                        titles = [column[0] for column in columns]
                        for i, model in enumerate(d['list']):
                            data = [ i+1, model['regNO'], model['brName'].encode('utf8').decode('utf8'), model['regOrg'].encode('utf8')]
                            item_array.append(dict(zip(titles, data)))

                    elif table_name == u"股东信息":
                        #print "股东信息"
                        d = json.loads(res['page'])
                        titles = [column[0] for column in columns]
                        surl = "http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/invInfoDetails.html?"+"entNo="+ str(post_data['entNo'])+"&regOrg="+str(post_data['regOrg'])
                        for model in (d['list']):
                            # 详情
                            nurl = surl+"&invNo="+str(model['invNo'])
                            print nurl
                            nres = self.crawler.crawl_page_by_url(nurl)['page']
                            detail_page = self.parse_page_2(nres, table_name+'_detail')
                            data = [ model['invType'], model['inv'], model['certName'], model['certNo'], detail_page]
                            item_array.append(dict(zip(titles, data)))

                    table_dict = item_array

                else:
                    #print "else "+table_name
                    if not tbody:
                        #records_tag = bs_table
                        records_tag = tables[0]
                    else:
                        records_tag = tbody
                    for tr in records_tag.find_all('tr'):
                        if tr.find('td') and len(tr.find_all('td', recursive=False)) % column_size == 0:
                            col_count = 0
                            item = {}
                            print "table_name=%s"%table_name
                            for td in tr.find_all('td',recursive=False):
                                if td.find('a'):
                                    next_url = self.get_detail_link(td.find('a'))
                                    #print next_url
                                    #has detail link
                                    if re.match(r"http", next_url):
                                        detail_page = self.crawler.crawl_page_by_url(next_url)
                                        #html_to_file("next.html", detail_page['page'])
                                        if table_name == u'企业年报':
                                            #settings.logger.debug(u"next_url = %s, table_name= %s\n", detail_page['url'], table_name)
                                            page_data = self.parse_ent_pub_annual_report_page(detail_page['page'], table_name + '_detail')
                                            item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                            item[u'详情'] = page_data
                                            #item[columns[col_count][0]] = page_data #this may be a detail page data
                                        elif table_name == u'qiyenianbao':
                                            print "in table_name"
                                            page_data = self.parse_ent_pub_annual_report_page_2(detail_page['page'], table_name+ '_detail')
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
                                    next_url = self.get_detail_link(td.find('a'))
                                    #has detail link
                                    if next_url:
                                        detail_page = self.crawler.crawl_page_by_url(next_url)['page']
                                        #html_to_file("next.html", detail_page['page'])

                                        if table_name == u'企业年报':
                                            #settings.logger.debug(u"2next_url = %s, table_name= %s\n", next_url, table_name)

                                            page_data = self.parse_ent_pub_annual_report_page(detail_page['page'], table_name + '_detail')
                                            item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                            item[u'详情'] = page_data
                                        elif table_name == 'qiyenianbao':
                                            page_data = self.parse_ent_pub_annual_report_page_2(detail_page['page'], table_name+ '_detail')
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



class Guangdong2(object):
    def __init__(self):
        self.analysis = Analyze()
        self.crawler = Crawler(self.analysis)
        self.analysis.crawler = self.crawler

    def run(self, url):
        return self.crawler.run(url)
    def work(self):
        self.crawler.work()


# if __name__ == "__main__":
    # reload (sys)
    # sys.setdefaultencoding('utf8')
    # guangdong = Guangdong2()
    # guangdong.work()


