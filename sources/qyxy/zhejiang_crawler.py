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
from bs4 import BeautifulSoup
import CaptchaRecognition as CR
import time
import random

urls = {
    'host': 'http://gsxt.zjaic.gov.cn/',
    'webroot' : 'http://gsxt.zjaic.gov.cn',
    'page_search': 'http://gsxt.zjaic.gov.cn/zhejiang.jsp',
    'page_Captcha': 'http://gsxt.zjaic.gov.cn/common/captcha/doReadKaptcha.do',
    'page_showinfo': 'http://gsxt.zjaic.gov.cn/search/doGetAppSearchResult.do',
    'prefix_url_0':'http://gsxt.zjaic.gov.cn/appbasicinfo/',
    'checkcode':'http://gsxt.zjaic.gov.cn//search/doValidatorVerifyCode.do',
}

headers = { 'Connetion': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36",
            #在获取验证码图片的时候，构造请求头的时候，要添加Referer
            "Referer" : "http://gsxt.zjaic.gov.cn/zhejiang.jsp",
        }

class ZhejiangCrawler(object):
    """浙江省爬虫代码"""
    def __init__(self, json_restore_path):
        self.CR = CR.CaptchaRecognition("zhejiang")
        self.requests = requests.Session()
        self.requests.headers.update(headers)
        self.ents = []
        self.json_restore_path = json_restore_path
        self.html_restore_path = settings.html_restore_path + '/zhejiang/'
        #验证码图片的存储路径
        self.path_captcha = settings.json_restore_path + '/zhejiang/ckcode.jpg'
        self.path_captcha_diff = settings.json_restore_path +'/zhejiang/'
        self.corpid = ""
        self.regNo = ""
        self.reportNo = ""
        self.year = ""

    # 破解搜索页面
    def crawl_page_search(self, url):
        r = self.requests.get( url)
        if r.status_code != 200:
            settings.logger.error(u"Something wrong when getting the url:%s , status_code=%d", url, r.status_code)
            return
        r.encoding = "utf-8"
        #settings.logger.debug("searchpage html :\n  %s", r.text)
        return r.text

    #分析 展示页面， 获得搜索到的企业列表
    def analyze_showInfo(self, url, datas):
        r = self.requests.post( url, datas )
        if r.status_code != 200:
            settings.logger.error(u"Getting Page ShowInfo failed\n")
            return False
        Ent = []
        soup = BeautifulSoup(r.text, "html5lib")
        divs = soup.find_all("dl", {"class":"list"})
        if divs:
            for div in divs:
                if div.find('a') and div.find('a').has_attr('href'):
                    Ent.append(div.find('a')['href'])
        self.ents = Ent

    # 破解验证码页面
    def crawl_page_captcha(self, url_search, url_Captcha, url_CheckCode,url_showInfo,  textfield= '330000000050426'):
        html_search = self.crawl_page_search(url_search)
        if not html_search:
            settings.logger.error(u"There is no search page")
        count = 0
        while True:
            count+= 1
            r = self.requests.get( url_Captcha)
            if r.status_code != 200:
                settings.logger.error(u"Something wrong when getting the Captcha url:%s , status_code=%d", url_Captcha, r.status_code)
                return
            if self.save_captcha(r.content):
                result = self.crack_captcha()
                #print result
                datas= {
                        'name': textfield,
                        'verifyCode': result,
                }
                response = self.get_check_response(url_CheckCode, datas)
                #response 成功则返回 {u'nameResponse': {u'totalCount': 0, u'message': u'true', u'name': u'', u'appConInfoList': []}}
                if response['nameResponse']['message'] == 'true':
                    datas['clickType'] = 1
                    self.analyze_showInfo(url_showInfo, datas)
                    break
                else:
                    settings.logger.debug(u"crack Captcha failed, the %d time(s)", count)
                    if count> 25:
                        break
        return
    def get_check_response(self, url, datas):
        """获得验证的结果信息"""
        r = self.requests.post( url, data = datas )
        if r.status_code != 200:
            return False
        return r.json()
    def crack_captcha(self):
        """调用函数，破解验证码图片并返回结果"""
        if os.path.exists(self.path_captcha) is False:
            settings.logger.error(u"Captcha path is not found\n")
            return
        result = self.CR.predict_result(self.path_captcha)
        return result[1]
    # 保存验证码图片
    def save_captcha(self, Captcha):
        # 保存300张图片
        #url_Captcha = ("%scaptcha%f.jpeg")%(self.path_captcha_diff, random.uniform(1, 300))
        url_Captcha = self.path_captcha
        if Captcha is None:
            settings.logger.error(u"Can not store Captcha: None\n")
            return False

        f = open(url_Captcha, 'w')
        try:
            f.write(Captcha)
        except IOError:
            settings.logger.debug("%s can not be written", url_Captcha)
        finally:
            f.close
        return True
    """
    The following functions are for main page
        1. iterate enterprises in ents
        2. for each ent: decide host so that choose functions by pattern
        3. for each pattern, iterate urls
        4. for each url, iterate item in tabs
    """
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
                corpid = ent[ent.rfind('corpid')+7:]
                self.corpid = corpid
                url = ent
                sub_json_dict.update(self.crawl_ind_comm_pub_pages(url))
                url = urls['host']+ "annualreport/doViewAnnualReportIndex.do?corpid="+corpid
                sub_json_dict.update(self.crawl_ent_pub_pages(url))
                url = urls['host'] + "other/doGetOtherInfoAction.do?corpid=" + corpid
                sub_json_dict.update(self.crawl_other_dept_pub_pages(url ))
                url = urls['host']+"jsp/client/biz/view/justiceInfoPublic.jsp?corpid=" + corpid
                sub_json_dict.update(self.crawl_judical_assist_pub_pages(url))
        except Exception as e:
            settings.logger.error(u"An error ocurred when getting the main page, error: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #工商公式信息页面
    def crawl_ind_comm_pub_pages(self, url=""):
        """工商公式信息页面"""
        sub_json_dict={}
        try:
            settings.logger.info( u"crawl the crawl_ind_comm_pub_pages page %s."%(url))
            main_page = self.crawl_page_by_url(url)['page']
            url = urls['host'] + "/appbasicinfo/doReadAppBasicInfo.do?corpid=" + self.corpid
            page = self.crawl_page_by_url(url)['page']
            dj = self.parse_page_jibenxinxi(page) #
            sub_json_dict['ind_comm_pub_reg_basic'] = dj[u'基本信息'] if dj.has_key(u'基本信息') else []        # 登记信息-基本信息
            sub_json_dict['ind_comm_pub_reg_shareholder'] =dj[u'股东信息'] if dj.has_key(u'股东信息') else []   # 股东信息
            sub_json_dict['ind_comm_pub_reg_modify'] =  dj[u'变更信息'] if dj.has_key(u'变更信息') else []      # 变更信息
            url = urls['host']+ "/filinginfo/doViewFilingInfo.do?corpid=" + self.corpid
            page = self.crawl_page_by_url(url )['page']
            ba = self.parse_page_beian(page)
            sub_json_dict['ind_comm_pub_arch_key_persons'] = ba[u'主要人员信息'] if ba.has_key(u'主要人员信息') else []   # 备案信息-主要人员信息
            sub_json_dict['ind_comm_pub_arch_branch'] = ba[u'分支机构信息'] if ba.has_key(u'分支机构信息') else []       # 备案信息-分支机构信息
            sub_json_dict['ind_comm_pub_arch_liquidation'] = ba[u'清算信息'] if ba.has_key(u'清算信息') else []   # 备案信息-清算信息
            url = urls['host']+ "/dcdyapplyinfo/doReadDcdyApplyinfoList.do?regNo="+self.regNo+"&uniSCID="
            page = self.crawl_page_by_url(url)['page']
            dcdy = self.parse_page(page, 'dongchandiya')
            sub_json_dict['ind_comm_pub_movable_property_reg'] = dcdy[u'动产抵押登记信息'] if dcdy.has_key(u'动产抵押登记信息') else []
            url = urls['host']+ "/equityall/doReadEquityAllListFromPV.do?corpid=" + self.corpid
            page = self.crawl_page_by_url(url)['page']
            gqcz = self.parse_page(page, 'guquanchuzhi')
            sub_json_dict['ind_comm_pub_equity_ownership_reg'] = gqcz[u'股权出质登记信息'] if gqcz.has_key(u'股权出质登记信息') else []
            url = urls['host']+ "/punishment/doViewPunishmentFromPV.do?corpid=" + self.corpid
            page = self.crawl_page_by_url(url)['page']
            xzcf = self.parse_page(page)
            sub_json_dict['ind_comm_pub_administration_sanction'] = xzcf[u'行政处罚信息'] if xzcf.has_key(u'行政处罚信息') else []
            url = urls['host']+ "/catalogapply/doReadCatalogApplyList.do?corpid=" + self.corpid
            page = self.crawl_page_by_url(url)['page']
            jyyc= self.parse_page(page, 'yichangminglu')
            sub_json_dict['ind_comm_pub_business_exception'] = jyyc[u'经营异常信息'] if jyyc.has_key(u'经营异常信息') else []
            url = urls['host']+ "/blacklist/doViewBlackListInfo.do?corpid=" + self.corpid
            page = self.crawl_page_by_url(url)['page']
            yzwf = self.parse_page(page, 'yanzhongweifa')
            sub_json_dict['ind_comm_pub_serious_violate_law'] = yzwf[u'严重违法信息'] if yzwf.has_key(u'严重违法信息') else []
            url = urls['host']+ "/pubcheckresult/doViewPubCheckResultList.do?corpid=" + self.corpid
            page = self.crawl_page_by_url(url)['page']
            cyjc= self.parse_page(page, 'chouchaxinxi')
            sub_json_dict['ind_comm_pub_spot_check'] = cyjc[u'抽查检查信息'] if cyjc.has_key(u'抽查检查信息') else []
        except Exception as e:
            settings.logger.debug(u"An error ocurred in crawl_ind_comm_pub_pages: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #爬取 企业公示信息 页面
    def crawl_ent_pub_pages(self, url= "", post_data={}):
        """爬取 企业公示信息 页面"""
        sub_json_dict = {}
        try:
            settings.logger.info( u"crawl the crawl_ent_pub_pages page %s."%(url))
            main_page = self.crawl_page_by_url(url)['page']
            url = urls['host']+"/pubreportinfo/doReadPubReportInfoList.do?corpid="+self.corpid+"&appConEntTypeCatg=11"
            page = self.crawl_page_by_url(url)['page']
            nb = self.parse_page(page, 'qynb')
            sub_json_dict['ent_pub_ent_annual_report'] = nb[u'企业年报'] if nb.has_key(u'企业年报') else []
            url = urls['host']+"/pubfunded/doReadPubFunded.do?pubFunded.corpid="+ self.corpid
            page = self.crawl_page_by_url(url)['page']
            tzr= self.parse_page_touziren(page)
            sub_json_dict['ent_pub_shareholder_capital_contribution'] = tzr #tzr[u'股东及出资信息'] if tzr.has_key(u'股东及出资信息') else []
            bg = self.parse_page_biangeng(page)
            sub_json_dict['ent_pub_reg_modify'] = bg#bg[u'变更信息'] if bg.has_key(u'变更信息') else []
            url = urls['host']+"/pubinstantstock/doReadPubStock.do?pubInstantStock.corpid="+ self.corpid
            page = self.crawl_page_by_url(url)['page']
            gq = self.parse_page_gqbg(page)
            sub_json_dict['ent_pub_equity_change'] = gq#gq[u'股权变更信息'] if gq.has_key(u'股权变更信息') else []
            url = urls['host']+"/publicense/doReadPubLicense.do?pubLicense.corpid="+ self.corpid
            page = self.crawl_page_by_url(url)['page']
            xk = self.parse_page_xzxk(page, 'xingzhengxuke')
            sub_json_dict['ent_pub_administration_license'] =  xk#xk[u'行政许可信息'] if xk.has_key(u'行政许可信息') else []
            url = urls['host']+"/pubinstantpunish/doReadPubInstantPunish.do?pubInstantPunish.corpid="+ self.corpid
            page = self.crawl_page_by_url(url)['page']
            cf = self.parse_page_xzcf(page, 'xingzhengchufa')
            sub_json_dict['ent_pub_administration_sanction'] = cf#cf[u'行政处罚信息'] if cf.has_key(u'行政处罚信息') else []
            url = urls['host']+"/pubinstantintellectual/doReadPubInstantIntellectual.do?pubInstantIntellectual.corpid="+ self.corpid
            page = self.crawl_page_by_url(url)['page']
            zscq = self.parse_page_zscq(page, 'zhishichanquan')
            sub_json_dict['ent_pub_knowledge_property'] =  zscq #zscq[u'知识产权出质登记信息'] if zscq.has_key(u'知识产权出质登记信息') else []
        except Exception as e:
            settings.logger.debug(u"An error ocurred in crawl_ent_pub_pages: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    def parse_page_zscq(self, page="", div_id=""):
        """企业公示信息  知识产权出质登记信息"""
        table_data = []
        try:
            url = urls['host']+"/pubinstantintellectual/doReadPubInstantIntellectualJSON.do?_id="+"doReadPubInstantintelNo"+str(int(time.time()))
            data = {
                "intelFlag":"1",
                "corpid": self.corpid,
                "pagination.currentPage": 1,
                "pagination.pageSize": 5,
            }
            settings.logger.info( u"crawl the crawl_ent_pub_pages- zscq page with %s."%(url))
            res = json.loads(self.crawl_page_by_url_post(url, data)['page'])
            row = {}
            lists = res["pagination"]["dataList"]
            for i,l in enumerate(lists):
                if int(l['intelTypeSelect']) == 1:
                    url = urls['host']+ "/pubinstantintellectual/doEnIntelDetail.do?pubInstantIntellectual.intelNo="+l['intelNo']+"&pubInstantIntellectual.corpid="+ self.corpid
                else:
                    url = urls['host'] + "/pubinstantintellectual/doEnPubIntel.do?pubInstantIntellectual.intelNo=" + l['intelNo']
                detail_page = self.crawl_page_by_url(url)['page']
                detail_data = self.parse_page(detail_page)
                intelStartDate =time.strftime(u"%Y年%m月%d日",time.localtime(l['intelStartDate']['time']/1000))
                intelEndDate =time.strftime(u"%Y年%m月%d日",time.localtime(l['intelEndDate']['time']/1000))

                row[u"序号"],row[u"注册号"],row[u"名称"],row[u"种类"],row[u"出质人名称"],row[u"质权人名称"],row[u"质权登记期限"],row[u"状态"],row[u"变化情况"]=\
                    i+1, l['intelMarkRegno'], l['intelMarkName'], l['intelType'], l['intelPledgorName'], l['intelPledgeeName'],intelStartDate+'-'+intelEndDate, u"有效" if int(l['intelTypeSelect']) == 1 else u"无效", detail_data
                table_data.append(row)
        except Exception as e:
            settings.logger.error(u'parse zhishichanquanchuzhi page failed, with exception %s' % e)
            raise e
        finally:
            return table_data
    def parse_page_xzcf(self, page="", div_id=""):
        """企业公示信息  行政处罚信息"""
        table_data = []
        try:
            url = urls['host']+"/pubinstantpunish/doReadPubInstantPunishJSON.do?_id="+"doReadPubInstantPunish"+str(int(time.time()))
            data = {
                "punFlag":"1",
                "corpid": self.corpid,
                "pagination.currentPage": 1,
                "pagination.pageSize": 10,
            }
            settings.logger.info( u"crawl the crawl_ent_pub_pages- xzcf page with %s."%(url))
            res = json.loads(self.crawl_page_by_url_post(url, data)['page'])
            row = {}
            lists = res["pagination"]["dataList"]
            for i,l in enumerate(lists):
                punDocDate =time.strftime(u"%Y年%m月%d日",time.localtime(l['punDocDate']['time']/1000))
                row[u"序号"],row[u"行政处罚决定书文号"],row[u"行政处罚内容"],row[u"作出行政处罚决定机关名称"],row[u"作出行政处罚决定日期"],row[u"备注"]=\
                    i+1, l['punDocNum'], l['punFormName'], l['punRegOrg'], punDocDate, l['punReason']
                table_data.append(row)
        except Exception as e:
            settings.logger.error(u'parse xingzhengchufa page failed, with exception %s' % e)
            raise e
        finally:
            return table_data
    def parse_page_xzxk(self, page="", div_id=""):
        """企业公示信息  行政许可信息"""
        table_data = []
        try:
            url = urls['host']+"/publicense/doReadPubLicenseJSON.do?_id="+"doReadPubLicense"+str(int(time.time()))
            data = {
                "licFlag": "1",
                "corpid": self.corpid,
                "pagination.currentPage": 1,
                "pagination.pageSize": 10,
            }
            settings.logger.info( u"crawl the crawl_ent_pub_pages- xzxk page with %s."%(url))
            res = json.loads(self.crawl_page_by_url_post(url, data)['page'])
            row = {}
            lists = res["pagination"]["dataList"]
            for i,l in enumerate(lists):
                if int(l['licType']) == 1:
                    url = urls['host'] +'/publicense/doReadDetail.do?pubLicense.licNo='+str(l['licNo'])+'&pubLicense.corpid='+self.corpid
                else:
                    url = urls['host']+ '/publicense/doEnPubLic.do?pubLicense.licNo='+ l['licNo']
                detail_page = self.crawl_page_by_url(url)['page']
                detail_data = self.parse_page(detail_page)
                licStartDate =time.strftime(u"%Y年%m月%d日",time.localtime(l['licStartDate']['time']/1000))
                licEndDate =time.strftime(u"%Y年%m月%d日",time.localtime(l['licEndDate']['time']/1000))
                row[u"序号"],row[u"许可文件编号"],row[u"许可文件名称"],row[u"有效期自"],row[u"有效期至"],row[u"许可机关"],row[u"许可内容"],row[u"状态"],row[u"详情"] =\
                    i+1, l['licNumber'], l['licName'],licStartDate, licEndDate,  l['licAgreeOrg'], l['licContent'],  u"有效" if int(l['licType']) == 1 else u"无效",  detail_data
                table_data.append(row)
        except Exception as e:
            settings.logger.error(u'parse xingzhengxuke page failed, with exception %s' % e)
            raise e
        finally:
            return table_data
    def parse_page_gqbg(self, page="", div_id=""):
        """企业公示信息  股权变更信息"""
        table_data = []
        try:
            url = urls['host']+"/pubinstantstock/doReadPubStockJSON.do?_id="+"doReadPubLicense"+str(int(time.time()))
            data = {
                "stockFlag": "1",
                "corpid": self.corpid,
                "pagination.currentPage": 1,
                "pagination.pageSize": 10,
            }
            settings.logger.info( u"crawl the crawl_ent_pub_pages- gqbg page with %s."%(url))
            res = json.loads(self.crawl_page_by_url_post(url, data)['page'])
            row = {}
            lists = res["pagination"]["dataList"]
            for i,l in enumerate(lists):
                stockChangeDate =time.strftime(u"%Y年%m月%d日",time.localtime(l['stockChangeDate']['time']/1000))
                row[u"序号"],row[u"股东"],row[u"变更前股权比例"],row[u"变更后股权比例"],row[u"股权变更日期"] =\
                  i+1, l["stockBeforeInv"], l['stockBeforeTransampr'], l['stockAfterTransampr'],  stockChangeDate
                table_data.append(row)
        except Exception as e:
            settings.logger.error(u'parse biangeng page failed, with exception %s' % e)
            raise e
        finally:
            return table_data
    def parse_page_touziren(self, page="", div_id=""):
        """企业公示信息 股东及出资情况"""
        #soup = BeautifulSoup(page, 'html5lib')
        table_data = []
        try:
            #tables = soup.find_all('table')
            url = urls['host']+"/pubfunded/doReadPubFundedJSON.do?_id="+"doReadPubFunded"+str(int(time.time()))
            data = {
                "corpid": self.corpid,
                "fundFlag":"1",
                "pagination.currentPage": 1,
                "pagination.pageSize": 10,
            }
            settings.logger.info( u"crawl the crawl_ent_pub_pages- touziren page with %s."%(url))
            res = json.loads(self.crawl_page_by_url_post(url, data)['page'])
            row = {}
            lists = res["pagination"]["dataList"]
            for l in lists:
                fundDate =time.strftime(u"%Y年%m月%d日",time.localtime(l['pubFundedList']['fundDate']['time']/1000))
                row[u"股东"],row[u"认缴额（万元）"],row[u"实缴额（万元）"],row[u"认缴出资方式"],row[u"认缴出资额（万元）"],row[u"认缴出资日期"],row[u"实缴出资方式"],row[u"实缴出资额（万元）"], row[u'实缴出资日期'] =\
                  l["fundInvestor"], l["payAmountCount"],l["actAmountCount"], l['pubFundedList']["fundFormName"], l['pubFundedList']['fundAmount'],fundDate, l['pubFundedList']["fundFormName"], l['pubFundedList']["fundAmount"], fundDate
                table_data.append(row)

        except Exception as e:
            settings.logger.error(u'parse touziren page failed, with exception %s' % e)
            raise e
        finally:
            return table_data
    def parse_page_biangeng(self, page="", div_id=""):
        """企业公示信息 股东及出资情况-变更信息"""
        table_data = []
        try:
            url = urls['host']+"/pubreportmodhis/doReadPubReportModHisJSON.do?_id="+"doReadPubReportModHisJSON"+str(int(time.time()))
            data = {
                "modTable":"PubFunded",
                "dicColumn":"FUND_FORM",
                "corpid": self.corpid,
                "pagination.currentPage": 1,
                "pagination.pageSize": 5,
            }
            settings.logger.info( u"crawl the crawl_ent_pub_pages- biangeng page with %s."%(url))
            res = json.loads(self.crawl_page_by_url_post(url, data)['page'])
            row = {}
            lists = res["pagination"]["dataList"]

            for i,l in enumerate(lists):
                if l['modItem'] =="fundForm":
                    modContentBefore = self.fundFormList(modContentBefore)
                    modContentAfter = self.fundFormList(modContentAfter)
                if l['modItem'] == "fundDate":
                    modContentBefore = time.strftime(u"%Y年%m月%d日",time.localtime(l['modContentBefore']['time']/1000))
                    modContentAfter = time.strftime(u"%Y年%m月%d日",time.localtime(l['modContentAfter']['time']/1000))
                modDate =time.strftime(u"%Y年%m月%d日",time.localtime(l['modDate']['time']/1000))
                row[u"序号"],row[u"变更事项"],row[u"变更时间"],row[u"变更前内容"],row[u"变更后内容"] =\
                  i+1, l["modItemName"], modDate, modContentBefore,  modContentAfter
                table_data.append(row)

        except Exception as e:
            settings.logger.error(u'parse biangeng page failed, with exception %s' % e)
            raise e
        finally:
            return table_data
    def fundFormList(self, ids):
        if str(ids) ==  "1": return  u"货币"
        if str(ids) ==  "2": return  u"实物"
        if str(ids) ==  "3": return  u"知识产权"
        if str(ids) ==  "4": return  u"债权"
        if str(ids) ==  "6": return  u"土地使用权"
        if str(ids) ==  "7": return  u"股权"
        if str(ids) ==  "9": return  u"其他"
    def parse_page_beian(self, page):
        """备案信息页面， 主要人员信息； 分支机构信息和 清算信息分页，由POST请求数据"""
        soup = BeautifulSoup(page, 'html5lib')
        page_data = {}
        try:
            tables = soup.find_all('table')
            #  清算信息
            qingsuan_table = tables[2]
            table_name = self.get_table_title(qingsuan_table)
            if table_name:
                page_data[table_name] = self.parse_table(qingsuan_table, table_name, page)
            url = urls['host'] + "/filinginfo/doViewFilingInfo.do?corpid=" + self.corpid
            # 主要人员信息；
            people_table = tables[0]
            data_list=[]
            table_name = self.get_table_title(people_table)
            if table_name and table_name== u"主要人员信息":
                data_list.extend(self.parse_table(people_table, table_name, page))
            if people_table.find('th', {'colspan':True, 'align':"right"}): # 说明有分页
                th_str =self.get_raw_text_by_tag(people_table.find('th', {'colspan': True, 'align':"right"}))
                page_num = int(re.compile(r'\d+').search(th_str).group())
                pageSize = people_table.find('input', {'name':'entMemberPagination.pageSize'})['value']

                for i in xrange(page_num):
                    data = {
                        "entMemberPagination.currentPage": i+2, "entMemberPagination.pageSize": int(pageSize),
                    }
                    new_page = self.crawl_page_by_url_post(url, data)['page']
                    # html_to_file('new_page.html', new_page)
                    new_soup = BeautifulSoup(new_page, 'html5lib')
                    people_table = new_soup.find_all('table')[0]
                    table_name = self.get_table_title(people_table)
                    if table_name and table_name == u"主要人员信息":
                        data_list.extend(self.parse_table(people_table, table_name))
            page_data[u"主要人员信息"] = data_list

            branch_table = tables[1]
            data_list=[]
            table_name = self.get_table_title(branch_table)
            if table_name and table_name== u"分支机构信息":
                data_list.extend(self.parse_table(branch_table, table_name, page))
            if branch_table.find('th', {'colspan': True, 'align':"right"}):
                th_str =self.get_raw_text_by_tag(branch_table.find('th', {'colspan': True, 'align':"right"}))
                page_num = int(re.compile(r'\d+').search(th_str).group())
                pageSize = branch_table.find('input', {'name':'branchInfoPagination.pageSize'})['value']
                for i in xrange(page_num):
                    data = {
                        "branchInfoPagination.currentPage": i+2, "branchInfoPagination.pageSize": int(pageSize),
                    }
                    new_page = self.crawl_page_by_url_post(url, data)['page']
                    new_soup = BeautifulSoup(new_page, 'html5lib')
                    branch_table = new_soup.find_all('table')[1]
                    table_name = self.get_table_title(branch_table)
                    if table_name and table_name == u"分支机构信息":
                        data_list.extend(self.parse_table(branch_table, table_name))
            page_data[u"分支机构信息"] = data_list
        except Exception as e:
            settings.logger.error(u'parse beian page failed, with exception %s' % e)
            raise e
        finally:
            return page_data
    def parse_page_jibenxinxi(self, page):
        """登记信息页面， 基本信息表； 股东信息表和变更信息表分页，由POST请求数据"""
        soup = BeautifulSoup(page, 'html5lib')
        page_data = {}
        try:
            tables = soup.find_all('table')
            basic_table = tables[0]
            table_name = self.get_table_title(basic_table)
            if table_name:
                page_data[table_name] = self.parse_table(basic_table, table_name, page)
            url = urls['host'] + "/appbasicinfo/doReadAppBasicInfo.do?corpid=" + self.corpid
            # 股东表
            gudong_table = tables[1]
            data_list=[]
            table_name = self.get_table_title(gudong_table)
            if table_name and table_name== u"股东信息":
                data_list.extend(self.parse_table(gudong_table, table_name, page))
            if gudong_table.find('th', {'colspan': True, 'align':"right"}): # 说明有分页
                th_str =self.get_raw_text_by_tag(gudong_table.find('th', {'colspan':"5", 'align':"right"}))
                page_num = int(re.compile(r'\d+').search(th_str).group())
                pageSize = gudong_table.find('input', {'name':'entInvestorPagination.pageSize'})['value']

                for i in xrange(page_num):
                    data = {
                        "entInvestorPagination.currentPage": i+2, "entInvestorPagination.pageSize": int(pageSize),
                    }
                    new_page = self.crawl_page_by_url_post(url, data)['page']
                    # html_to_file('new_page.html', new_page)
                    new_soup = BeautifulSoup(new_page, 'html5lib')
                    gudong_table = new_soup.find_all('table')[1]
                    table_name = self.get_table_title(gudong_table)
                    if table_name and table_name == u"股东信息":
                        data_list.extend(self.parse_table(gudong_table, table_name))
            page_data[u"股东信息"] = data_list

            biangeng_table = tables[2]
            data_list=[]
            table_name = self.get_table_title(biangeng_table)
            if table_name and table_name== u"变更信息":
                data_list.extend(self.parse_table(biangeng_table, table_name, page))
            if biangeng_table.find('th', {'colspan': True, 'align':"right"}):
                th_str =self.get_raw_text_by_tag(biangeng_table.find('th', {'colspan':"5", 'align':"right"}))
                page_num = int(re.compile(r'\d+').search(th_str).group())
                pageSize = biangeng_table.find('input', {'name':'checkAlterPagination.pageSize'})['value']
                data_list=[]
                for i in xrange(page_num):
                    data = {
                        "checkAlterPagination.currentPage": i+2, "checkAlterPagination.pageSize": int(pageSize),
                    }
                    new_page = self.crawl_page_by_url_post(url, data)['page']
                    # html_to_file('new_page.html', new_page)
                    new_soup = BeautifulSoup(new_page, 'html5lib')
                    biangeng_table = new_soup.find_all('table')[2]
                    table_name = self.get_table_title(biangeng_table)
                    if table_name and table_name == u"变更信息":
                        data_list.extend(self.parse_table(biangeng_table, table_name))
            page_data[u"变更信息"] = data_list
        except Exception as e:
            settings.logger.error(u'parse jibenxinxi page failed, with exception %s' % e)
            raise e
        finally:
            return page_data
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
            m = re.compile(r"\"webReportNo\":\s*(\".*?\")").search(page)
            if m:
                ReportNo = m.group(1).strip('\"')
                self.reportNo = ReportNo
            m = re.compile(r"\"year\":\s*(\".*?\")").search(page)
            if m:
                self.year = m.group(1).strip('\"')
            content_table = soup.find_all('table')[1:]
            for table in content_table:
                table_name = self.get_table_title(table)
                if table_name:
                    if table_name == u"网站或网店信息":
                        print table_name
                        sub_dict[table_name] = self.parse_table_busiWeb(table)
                    elif table_name == u"股东及出资信息":
                        print table_name
                        sub_dict[table_name] = self.parse_table_conInfo(table)
                    elif table_name == u"对外投资信息":
                        print table_name
                        sub_dict[table_name] = self.parse_table_investInfo(table)
                    elif table_name == u"对外提供保证担保信息":
                        print table_name
                        sub_dict[table_name] = self.parse_table_guarInfo(table)
                    elif table_name == u"股权变更信息":
                        print table_name
                        sub_dict[table_name] = self.parse_table_stockInfo(table)
                    elif table_name == u"修改记录":
                        print table_name
                        sub_dict[table_name] = self.parse_table_modHis(table)
                    else:
                        sub_dict[table_name] = self.parse_table(table, table_name, page)
        except Exception as e:
            settings.logger.error(u'annual page: fail to get table data with exception %s' % e)
            raise e
        finally:
            return sub_dict
    def parse_table_modHis(self, table):
        """ 企业年报 修改记录"""
        table_data = []
        try:
            url = urls['host']+"/pubreportmodhis/doReadPubReportModHisJSON.do?_id="+"doReadPubReportModHis"+str(int(time.time()))
            data = {
                "modReportNo": self.reportNo,
                "corpid": self.corpid,
                "year": self.year,
                "modType": "1",
                "pagination.currentPage": 1,
                "pagination.pageSize": 5,
            }
            res = json.loads(self.crawl_page_by_url_post(url, data)['page'])
            row = {}
            lists = res["pagination"]["dataList"]
            for i, l in enumerate(lists):
                modDate =time.strftime(u"%Y年%m月%d日",time.localtime(l['modDate']['time']/1000))
                modContentBefore, modContentAfter = self.selectModItem(l['modItem'], l['modContentBefore'], l['modContentAfter'])
                row[u"序号"],row[u"修改事项"],row[u"修改前"],row[u"修改后"], row[u'修改日期'] =\
                  i+1, l["modItemName"], modContentBefore, modContentAfter, modDate
                table_data.append(row)
        except Exception as e:
            settings.logger.error(u"parse annual report busi web failed with exception:"% e)
        finally:
            return table_data
    def selectModItem(self, modItem, modContentBefore, modContentAfter):
        """ 企业年报 修改记录, item 选择"""
        if (modItem == "guarDateStart" or modItem == "guarDateEnd" or modItem == "conInfoPayDate" or modItem=="conInfoActDate" or modItem=="stockChangeDate"):
            if modContentBefore!="" :
                modContentBefore = time.strftime(u"%Y年%m月%d日",time.localtime(modContentBefore['time']/1000))
            if modContentAfter!="":
                modContentAfter = time.strftime(u"%Y年%m月%d日",time.localtime(modContentAfter['time']/1000))
        if (modItem=="conInfoInvForm" or modItem=="conInfoActForm" ):
            modContentBefore = self.formList(modContentBefore)
            modContentAfter = self.formList(modContentAfter)
        if (modItem=="guarRange"):
            modContentBefore = self.guarRange(modContentBefore)
            modContentAfter = self.guarRange(modContentAfter)
        if (modItem =="guarCreditType"):
            modContentBefore = self.guarCreditTypeList(modContentBefore)
            modContentAfter = self.guarCreditTypeList(modContentAfter)
        if (modItem =="guarType"):
            modContentBefore = self.guarTypeList(modContentBefore)
            modContentAfter = self.guarTypeList(modContentAfter)
        if (modItem =="guarPeriod"):
            modContentBefore = self.guarPeriodList(modContentBefore)
            modContentAfter = self.guarPeriodList(modContentAfter)
        if (modItem=="busWebType"):
            if(modContentBefore =="0"):
                modContentBefore=u"网站"
            elif(modContentBefore =="1"):
                modContentBefore=u"网 店 "
            if(modContentAfter =="0"):
                modContentAfter=u"网站"
            elif(modContentAfter =="1"):
                modContentAfter=u"网店"
        return (modContentBefore, modContentAfter)
    def guarPeriodList(self, ids):
        if ids ==  1 : return u"期间"
        if ids ==  2 : return u"未约定"
    def guarTypeList(self, ids):
        if ids == 1 : return u"一般保证"
        if ids == 2 : return u"连带保证"
        if ids == 3 : return u"未约定"
    def guarCreditTypeList(self, ids):
        if ids == 1 : return u"合同"
        if ids == 2 : return u"其他"
    def formList(self, ids):
        if ids ==  1: return u"货币"
        if ids ==  2: return u"实物"
        if ids ==  3: return u"知识产"
        if ids ==  4: return u"债权"
        if ids ==  6: return u"土地使权"
        if ids ==  7: return u"股权"
        if ids ==  9: return u"其他"
    def parse_table_stockInfo(self, table):
        """ 企业年报 股权变更信息"""
        table_data = []
        try:
            url = urls['host']+"/pubreportstockinfo/doReadPubReportStockInfoListJSON.do?_id="+"doReadPubReportConInfo"+str(int(time.time()))
            data = {
                "stockReportNo": self.reportNo,
                "corpid": self.corpid,
                "year": self.year,
                "pagination.currentPage": 1,
                "pagination.pageSize": 5,
            }
            res = json.loads(self.crawl_page_by_url_post(url, data)['page'])
            row = {}
            lists = res["pagination"]["dataList"]
            for l in lists:
                stockChangeDate =time.strftime(u"%Y年%m月%d日",time.localtime(l['stockChangeDate']['time']/1000))
                row[u"股东"],row[u"变更前股权比例"],row[u"变更后股权比例"],row[u"股权变更日期"] =\
                  l["stockHolder"], l["stockBeforePercent"],l["stockAfterPercent"], stockChangeDate
                table_data.append(row)
        except Exception as e:
            settings.logger.error(u"parse annual report busi web failed with exception:"% e)
        finally:
            return table_data

    def guarRange(self, ids):
        """企业年报 对外提供保证担保信息,获取担保范围"""
        if ids == 1:
            return u"主债权"
        if ids == 2:
            return u"利息"
        if ids == 3:
            return u"违约金"
        if ids == 4:
            return u"损害赔偿金"
        if ids == 5:
            return u"实现债权的费用"
        if ids == 6:
            return u"其他约金"
    def parse_table_guarInfo(self, table):
        """ 企业年报 对外提供保证担保信息"""
        table_data = []
        try:
            url = urls['host']+"/pubreportguaranteeinfo/doReadPubReportGuaranteeInfoListJSON.do?_id="+"doReadPubReportConInfo"+str(int(time.time()))
            data = {
                "guarReportNo": self.reportNo,
                "corpid": self.corpid,
                "year": self.year,
                "guarIsp": "1",
                "pagination.currentPage": 1,
                "pagination.pageSize": 5,
            }
            res = json.loads(self.crawl_page_by_url_post(url, data)['page'])
            lists = res["pagination"]["dataList"]
            row = {}
            for l in lists:
                guarDateStart = time.strftime( u"%Y年%m月%d日" , time.localtime(l["guarDateStart"]['time']/1000))
                guarDateEnd = time.strftime( u"%Y年%m月%d日" , time.localtime(l["guarDateEnd"]['time']/1000))
                guarCreditType = u"合同" if l['guarCreditType']==1 else u"其他"
                guarPeriod =  u"期间" if l['guarPeriod']== 1 else u"未约定"
                guarType =  u"一般保证" if l['guarType']==1 else u"连带保证" if l['guarType']==2 else u"未约定"
                guarRange = self.guarRange(l['guarRange'])

                row[u"债权人"],row[u"债务人"],row[u"主债权种类"],row[u"主债权数额"],row[u"履行债务的期限"],row[u"保证的期间"],row[u"保证的方式"],row[u"保证担保的范围"] = \
                     l["guarCreditor"], l["guarName"], guarCreditType, str(l["guarCreditAmount"])+"万元", guarDateStart+'-'+ guarDateEnd, guarPeriod, guarType, guarRange
                table_data.append(row)
        except Exception as e:
            settings.logger.error(u"parse annual report busi web failed with exception:"% e)
        finally:
            return table_data
    def parse_table_investInfo(self, table):
        """ 企业年报 投资信息"""
        table_data = []
        try:
            url = urls['host']+"/pubreportinvestinfo/doReadPubReportInvestInfoListJSON.do?_id="+"doReadPubReportConInfo"+str(int(time.time()))
            data = {
                "investReportNo": self.reportNo,
                "corpid": self.corpid,
                "year": self.year,
                "pagination.currentPage": 1,
                "pagination.pageSize": 5,
            }
            res = json.loads(self.crawl_page_by_url_post(url, data)['page'])
            row = {}
            lists = res["pagination"]["dataList"]
            for l in lists:
                row[u"投资设立或购买股权境内企业名称"],row[u"对外投资企业注册号"] =  l["investInfoEntName"], l["investInfoEntRegNo"]
                table_data.append(row)
        except Exception as e:
            settings.logger.error(u"parse annual report busi web failed with exception:"% e)
        finally:
            return table_data
    def parse_table_busiWeb(self, table):
        """ 企业年报 网站或网店信息"""
        table_data = []
        try:
            url = urls['host']+"/pubreportbusiweb/doReadPubReportBusiWebListJSON.do?_id="+"doReadPubReportBusiWeb"+str(int(time.time()))
            data = {
                "webReportNo": self.reportNo,
                "corpid": self.corpid,
                "year": self.year,
                "pagination.currentPage": 1,
                "pagination.pageSize": 5,
            }
            res = json.loads(self.crawl_page_by_url_post(url, data)['page'])
            lists = res["pagination"]["dataList"]
            row = {}
            for l in lists:
                row[u"类型"],row[u"名称"], row[u"网址"]  = u'网店' if int(l["busWebType"])==0 else r'网站', l["busWebWebsiteName"], l["busWebWebsite"]
                table_data.append(row)
        except Exception as e:
            settings.logger.error(u"parse annual report busi web failed with exception:"% e)
        finally:
            return table_data
    def parse_table_conInfo(self, table):
        """ 企业年报 查询股东及出资信息"""
        table_data = []
        try:
            url = urls['host']+"/pubreportconinfo/doReadPubReportConInfoListJSON.do?_id="+"doReadPubReportConInfo"+str(int(time.time()))
            data = {
                "conReportNo": self.reportNo,
                "corpid": self.corpid,
                "year": self.year,
                "pagination.currentPage": 1,
                "pagination.pageSize": 5,
            }
            res = json.loads(self.crawl_page_by_url_post(url, data)['page'])
            lists = res["pagination"]["dataList"]
            row = {}
            for l in lists:
                conInfoPayDate = time.localtime(l["conInfoPayDate"]['time']/1000)
                conInfoActDate =  time.localtime(l["conInfoActDate"]['time']/1000)
                row[u"股东"],row[u"认缴出资额（万元人民币）"], row[u"认缴出资时间"], row[u'认缴出资方式'], row[u'实缴出资额（万元人民币）'], row[u'实缴出资时间'], row[u'实缴出资方式'] =\
                    l["conInfoName"], l["conInfoPayConAmount"], time.strftime(u"%Y年%m月%d日", conInfoPayDate), l["conInfoInvForm"], l["conInfoActConAmount"], time.strftime(u"%Y年%m月%d日", conInfoActDate),l["conInfoActForm"]
                table_data.append(row)
        except Exception as e:
            settings.logger.error(u"parse annual report busi web failed with exception:"% e)
        finally:
            return table_data
    #爬取 其他部门公示 页面
    def crawl_other_dept_pub_pages(self, url="", post_data={}):
        """爬取 其他部门公示 页面"""
        sub_json_dict = {}
        try:
            settings.logger.info( u"crawl the crawl_other_dept_pub_pages page %s."%(url))
            main_page = self.crawl_page_by_url(url)['page']
            url = urls['host'] + "/pubotherlicence/readPubOtherLicenceInfo.do?corpid="+ self.corpid
            page = self.crawl_page_by_url(url)['page']
            xk = self.parse_page(page, "xingzhengxuke")#行政许可信息
            sub_json_dict["other_dept_pub_administration_license"] =  xk[u'行政许可信息'] if xk.has_key(u'行政许可信息') else []
            url = urls['host'] + "/pubotherpunish/readPubOtherPunishInfo.do?corpid=" + self.corpid
            page = self.crawl_page_by_url(url)['page']
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
            settings.logger.info( u"crawl the crawl_judical_assist_pub_pages page %s."%(url))
            main_page = self.crawl_page_by_url(url)['page']
            url = urls['host'] + "/jsp/client/biz/view/justice/readJusticeEquityInfo.jsp"
            page = self.crawl_page_by_url(url)['page']
            xz = self.parse_page(page, 'sifaxiezhu')
            sub_json_dict['judical_assist_pub_equity_freeze'] = xz[u'司法股权冻结信息'] if xz.has_key(u'司法股权冻结信息') else []
            url = urls['host'] + "/jsp/client/biz/view/justice/readJusticeEquityChangeInfo.jsp"
            page = self.crawl_page_by_url(url)['page']
            gd = self.parse_page(page, 'sifagudong')
            sub_json_dict['judical_assist_pub_shareholder_modify'] = gd[u'司法股东变更登记信息'] if gd.has_key(u'司法股东变更登记信息') else []
        except Exception as e:
            settings.logger.debug(u"An error ocurred in crawl_judical_assist_pub_pages: %s"% (type(e)))
            raise e
        finally:
            return sub_json_dict

    def parse_page(self, page, div_id='sifapanding', post_data= {}):
        soup = BeautifulSoup(page, 'html5lib')
        page_data = {}
        try:
            div = soup.find('div', {'id' : div_id})
            if div:
                tables = div.find_all('table')
            else:
                tables = soup.find_all('table')
            for table in tables:
                table_name = self.get_table_title(table)
                if table_name:
                    page_data[table_name] = self.parse_table(table, table_name, page)

        except Exception as e:
            settings.logger.error(u'parse page failed, with exception %s' % e)
            raise e
        finally:
            return page_data
    def parse_table(self, bs_table, table_name="", page=None):
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

    def get_columns_of_record_table(self, bs_table, page, table_name):
        """获得表格的列名"""
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
        """通过tr逐一获得"""
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

    def get_detail_link(self, bs4_tag):
        if bs4_tag.has_attr('href') and (bs4_tag['href'] != '###' and bs4_tag['href'] != '#' and bs4_tag['href'] != 'javascript:void(0);'):
            if bs4_tag['href'].find('http') != -1 :
                return bs4_tag['href']
            return urls['webroot'] + bs4_tag['href']
        elif bs4_tag.has_attr('onclick'):
            pass
        return None

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
            return self.get_raw_text_by_tag(td_tag)

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
    def run(self, ent_num):
        if not os.path.exists(self.html_restore_path):
            os.makedirs(self.html_restore_path)
        json_dict = {}
        self.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        data = self.crawl_page_main()
        json_dict[ent_num] = data
        json_dump_to_file(self.json_restore_path , json_dict)

    def work(self, ent_num):
        if not os.path.exists(self.html_restore_path):
            os.makedirs(self.html_restore_path)
        self.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        self.regNo = ent_num
        data = self.crawl_page_main()
        json_dump_to_file( 'zhejiang.json' , data)

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

"""
if __name__ == "__main__":
    reload (sys)
    sys.setdefaultencoding('utf8')
    import run
    run.config_logging()
    if not os.path.exists("./enterprise_crawler"):
        os.makedirs("./enterprise_crawler")
    zhejiang = ZhejiangCrawler('./enterprise_crawler/zhejiang.json')
    #zhejiang.work('330000000050426')
    #zhejiang.work('330000000000503')
    zhejiang.work('330000000050426')

if __name__ == "__main__":
    reload (sys)
    sys.setdefaultencoding('utf8')
    import run
    run.config_logging()
    if not os.path.exists("./enterprise_crawler"):
        os.makedirs("./enterprise_crawler")
    zhejiang = ZhejiangCrawler('./enterprise_crawler/zhejiang.json')
    ents = read_ent_from_file("./enterprise_list/zhejiang.txt")
    zhejiang = ZhejiangCrawler('./enterprise_crawler/zhejiang.json')
    for ent_str in ents:
        settings.logger.info(u'###################   Start to crawl enterprise with id %s   ###################\n' % ent_str[2])
        zhejiang.run(ent_num = ent_str[2])
        settings.logger.info(u'###################   Enterprise with id  %s Finished!  ###################\n' % ent_str[2])

"""
