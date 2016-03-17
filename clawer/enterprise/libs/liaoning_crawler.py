# !/usr/bin/env python
# encoding=utf-8
import os
import requests
import time
import re
import random
import threading
import json
import urllib
import unittest
from datetime import datetime, timedelta
from . import settings
from enterprise.libs.CaptchaRecognition import CaptchaRecognition
import logging
from bs4 import BeautifulSoup
from crawler import Crawler
from crawler import Parser
from crawler import CrawlerUtils


class LiaoningCrawler(Crawler):
    """辽宁工商爬虫
    """
    #html数据的存储路径
    html_restore_path = settings.json_restore_path + '/liaoning/'

    #验证码图片的存储路径
    ckcode_image_path = settings.json_restore_path + '/liaoning/ckcode.jpg'
    code_cracker = CaptchaRecognition('liaoning')
    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {'host': 'http://www.lngs.gov.cn/ecdomain/framework/lngs/index.jsp',
            'get_checkcode': 'http://gsxt.lngs.gov.cn/saicpub/commonsSC/loginDC/securityCode.action?',
            'post_checkcode': 'http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/lngsSearchFpc.action',
        }

    def __init__(self, json_restore_path):
        self.json_restore_path = json_restore_path
        self.parser = LiaoningParser(self)
        self.img_count = 1
        if not os.path.exists(self.html_restore_path):
            os.makedirs(self.html_restore_path)

    def run(self, ent_number=0):
        """爬取的主函数
        """

        return Crawler.run(self, ent_number)

    def crawl_check_page(self):
        """爬取验证码页面，包括获取验证码url，下载验证码图片，破解验证码并提交
        """
        count = 0
        while count < 30:
            count += 1

            ckcode = self.crack_checkcode()
            logging.info('crack code = %s, %s' % (ckcode[0], ckcode[1]))
            if ckcode == "":
                continue
            post_data = {
                'authCode': ckcode[1],
                'solrCondition': self.ent_number,
             }

            next_url = self.urls['post_checkcode']
            resp = self.reqst.post(next_url, data=post_data)
            if resp.status_code != 200:
                logging.error('failed to get crackcode image by url %s, fail count = %d' % (next_url, count))
                continue
            # logging.info('crack code = %s, %s, response =  %s' %(ckcode[0], ckcode[1], resp.content))
            m = re.search(r'codevalidator= \"(.*)\"', resp.content)

            status = m.group(1)
            if status == "fail":
                continue
            else:
                m = re.search(r'searchList_paging\(\[(.*)\]', resp.content)
                if m.group(1) != "null":

                    js = json.loads(m.group(1))
                    self.type = js["enttype"]
                    self.pripid = js['pripid']
                    self.entname = js["entname"]
                    self.optstate = js["optstate"]
                    self.regno = js["regno"]

                    return True
                else:
                    logging.error('crack checkcode failed, total fail count = %d' % (count))

            time.sleep(random.uniform(2, 4))
        return False

    def crack_checkcode(self):
        """破解验证码"""
        checkcode_url = self.urls['get_checkcode']

        resp = self.reqst.get(checkcode_url, verify=False)
        if resp.status_code != 200:
            logging.warn('failed to get checkcode img')
            return
        page = resp.content

        self.write_file_mutex.acquire()
        with open(self.ckcode_image_path, 'wb') as f:
            f.write(page)
        if not self.code_cracker:
            print 'invalid code cracker'
            return ''
        try:
            ckcode = self.code_cracker.predict_result(self.ckcode_image_path)
        except Exception as e:
            logging.warn('exception occured when crack checkcode')
            ckcode = ('', '')
            os.remove(self.ckcode_image_path)
            time.sleep(10)
        finally:
            pass
        self.write_file_mutex.release()
        f.close()
        return ckcode

    def crawl_ind_comm_pub_pages(self):
        """爬取工商公示信息
        """
        self.parser.parse_ind_comm_pub_pages()

    def crawl_ent_pub_pages(self):
        """爬取企业公示信息
        """
        self.parser.parse_ent_pub_pages()

    def crawl_other_dept_pub_pages(self):
        """爬取其他部门公示信息
        """
        self.parser.crawl_other_dept_pub_pages()

    def crawl_judical_assist_pub_pages(self):
        """爬取司法协助信息
        """
        self.parser.parse_judical_assist_pub_pages()

class LiaoningParser(Parser):
    """辽宁工商页面的解析类
    """
    def __init__(self, crawler):
        self.crawler = crawler

    def parse_ind_comm_pub_pages(self):
        host = 'http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/get'
        args1 = 'Action.action?pripid='
        args2 = '&type='

        # 股东信息
        url = "%s%s%s%s%s%s" % (host, "Zyryxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        m = re.search(r'tzr_paging\((\[.*?\])', resp.content)
        total = []
        if m:
            list_m = json.loads(m.group(1))
            for i,item in enumerate(list_m):
                table_save = {}
                table_save[u"股东类型"] = item["invtypeName"]
                table_save[u"股东"] = item["inv"]
                table_save[u"证照/证件类型"] = item["blictypeName"]
                table_save[u"证照/证件号码"] = item["blicno"]

                url = "http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/getGsgsTzrxxPojoList.action"
                next_url = url
                post_data = {'pripid': self.crawler.pripid,'invid': item["invid"]};
                resp = self.crawler.reqst.post(next_url, data=post_data)
                total1 = []
                if resp.content:
                    list_m = json.loads(resp.content)

                    for i,item in enumerate(list_m):
                        table_save1 = {}
                        table_save1[u"股东"] = item["tRegTzrxx"]["inv"]
                        table_save1[u"认缴万元"] = str(item["tRegTzrxx"]["lisubconam"])
                        table_save1[u"实缴万元"] = str(item["tRegTzrxx"]["liacconam"])
                        table_save1[u"公示时间"] = item["tRegTzrxx"]["gstimeStr"]

                        list = []
                        rj = item["tRegTzrrjxxList"]
                        sj = item["tRegTzrsjxxList"]
                        for i in range(0, len(rj)):
                            table_detail = {}
                            table_detail[u"认缴出资方式"] = rj[i]["subconformName"]
                            table_detail[u"认缴出资额（万元）"] = str(rj[i]["subconam"])
                            table_detail[u"认缴出资到日期"] = rj[i]["subcondateStr"]

                            table_detail[u"实缴出资方式"] = sj[i]["acconformName"]
                            table_detail[u"实缴出资额（万元）"] = str(sj[i]["acconam"])
                            table_detail[u"实缴出资到日期"] = sj[i]["accondateStr"]
                            list.append(table_detail)

                        table_save1[u"list"] = list
                        total1.append(table_save1)

                table_save[u"详情"] = total1
                total.append(table_save)
        self.crawler.json_dict["ind_comm_pub_reg_shareholder"] = total

        # 主要人员
        url = "%s%s%s%s%s%s" % (host, "Zyryxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        m = re.search(r'zyry_nz_paging\((\[.*?\])', resp.content)
        total = []
        if m:
            list_m = json.loads(m.group(1))
            for i,item in enumerate(list_m):
                table_save = {}
                table_save[u"序号"] = str(i+1)
                table_save[u"姓名"] = item["name"]
                table_save[u"职务"] = item["positionName"]
                total.append(table_save)
        self.crawler.json_dict["ind_comm_pub_arch_key_persons"] = total

        # 清算信息
        url = "%s%s%s%s%s%s" % (host, "Qsxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)
        soup = BeautifulSoup(resp.content, "lxml")

        table = soup.find("table")
        self.crawler.json_dict["ind_comm_pub_arch_liquidation"] = self.parse_table2(table)

        # 变更信息
        url = "%s%s%s%s%s%s" % (host, "Bgxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        m = re.search(r'paging\((\[.*?\]),', resp.content)
        total = []
        if m:
            list_m = json.loads(m.group(1))
            for i,item in enumerate(list_m):
                table_save = {}
                table_save[u"变更事项"] = item["altitemName"]
                table_save[u"变更前内容"] = item["altbe"]
                table_save[u"变更后内容"] = item["altaf"]
                table_save[u"变更日期"] = item["altdate"]
                total.append(table_save)
            self.crawler.json_dict["ind_comm_pub_reg_modify"] = total

        # 分支结构信息
        url = "%s%s%s%s%s%s" % (host, "Fgsxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        m = re.search(r'fzjgPaging\((\[.*?\])', resp.content)
        total = []
        if m:
            list_m = json.loads(m.group(1))
            for i,item in enumerate(list_m):
                table_save = {}
                table_save[u"序号"] = str(i+1)
                table_save[u"统一社会信用代码/注册号"] = item["regno"]
                table_save[u"名称"] = item["brname"]
                table_save[u"登记机关"] = item["regorgName"]
                total.append(table_save)
        self.crawler.json_dict["ind_comm_pub_arch_branch"] = total

        # 股权出质登记信息
        url = "%s%s%s%s%s%s" % (host, "GsgsGqczxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        m = re.search(r'gqczdjPaging\((\[.*?\])', resp.content)
        total = []

        if m:
            list_m = json.loads(m.group(1))
            for i,item in enumerate(list_m):
                table_save = {}
                table_save[u"序号"] = str(i+1)
                table_save[u"登记编号"] = item["equityno"]
                table_save[u"出质人"] = item["pledgor"]
                table_save[u"出质人_证照/证件号码"] = item["blicno"]
                table_save[u"出质股权数额"] = item["impam"]+item["pledamunitName"]
                table_save[u"质权人"] = item["imporg"]
                table_save[u"质权人_证照/证件号码"] = item["impcerno"]
                table_save[u"股权出质设立登记日期"] = item["regdateStr"]

                table_save[u"状态"] = item["typeName"]
                table_save[u"公示时间"] = item["gstimeStr"]
                url = "%s%s%s%s%s%s" % (host, "Gqczbgxx", args1, self.crawler.pripid, "&gqczdjid=", item["gqczdjid"])
                resp = self.crawler.reqst.get(url)
                m = re.search(r'gqczbgPaging\((\[.*?\])', resp.content)

                table_save[u"变化情况"] = m.group(1)

                total.append(table_save)
            self.crawler.json_dict["ind_comm_pub_equity_ownership_reg"] = total

        # 动产抵押登记
        url = "%s%s%s%s%s%s" % (host, "Dcdydj", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        m = re.search(r'dcdydjPaging\((\[.*?\])', resp.content)
        total = []
        if m:
            list_m = json.loads(m.group(1))
            for i,item in enumerate(list_m):
                table_save = {}
                table_save[u"序号"] = str(i+1)
                table_save[u"登记编号"] = item["morregcno"]
                table_save[u"登记日期"] = item["regidateStr"]
                table_save[u"登记机关"] = item["regorgName"]
                table_save[u"被担保债权数额"] = item["priclasecam"]+"万元"
                table_save[u"状态"] = item["typeName"]
                table_save[u"公示时间"] = item["gstimeStr"]

                detail = {}
                url = "%s%s%s%s%s%s" % (host, "DcdyDetail", args1, self.crawler.pripid, "&dcdydjid=", item["dcdydjid"])
                resp = self.crawler.reqst.get(url)

                dyqr = re.search(r'dyqrPaging\((\[.*?\])', resp.content)
                dyqr_list = []
                if dyqr.group(1) != "null":
                    list_dyqr = json.loads(dyqr.group(1))
                    for i,item in enumerate(list_dyqr):
                        table_dyqr = {}
                        table_dyqr[u"序号"] = str(i+1)
                        table_dyqr[u"抵押权人名称"] = item["more"]
                        table_dyqr[u"抵押权人证照/证件类型"] = item["certypeName"]
                        table_dyqr[u"证照/证件号码"] = item["cerno"]
                        dyqr_list.append(table_dyqr)
                detail[u"抵押权人概况"] = dyqr_list

                dyw = re.search(r'dywPaging\((\[.*?\])', resp.content)
                dyw_list = []

                if dyw.group(1) != "null":
                    list_dyw = json.loads(dyw.group(1))
                    for i,item in enumerate(list_dyw):
                        table_dyw = {}
                        table_dyw[u"序号"] = str(i+1)
                        table_dyw[u"名称"] = item["guaname"]
                        table_dyw[u"所有权归属"] = item["own"]
                        table_dyw[u"数量、质量、状况、所在地等情况"] = item["guades"]
                        table_dyw[u"备注"] = item["remark"]
                        dyw_list.append(table_dyw)
                detail[u"抵押物概况"] = dyw_list

                soup = BeautifulSoup(resp.content, "lxml")
                name_table_map = [u'被担保债权概况',u'动产抵押登记信息']
                for table in soup.find_all('table'):
                    list_table_title = table.find("th")
                    if list_table_title.text in name_table_map:
                        detail[list_table_title.text] = self.parse_table1(table)

                table_save[u"详情"] = detail
                total.append(table_save)
        self.crawler.json_dict["ind_comm_pub_movable_property_reg"] = total

        # 行政处罚信息
        url = "%s%s%s%s%s%s" % (host, "Xzcfxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        m = re.search(r'xzcfPaging\((\[.*?\])', resp.content)
        total = []
        if m:
            if len(m.group(1)) <= 2:
                self.crawler.json_dict["ind_comm_pub_administration_sanction"] = total
            else:
                self.crawler.json_dict["ind_comm_pub_administration_sanction"] = m.group(1)
        else:
            self.crawler.json_dict["ind_comm_pub_administration_sanction"] = total

        # 经营异常信息
        url = "%s%s%s%s%s%s" % (host, "Jyycxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        m = re.search(r'jyyc_paging\((\[.*?\])', resp.content)
        total = []
        if m:
            if len(m.group(1)) <= 2:
                self.crawler.json_dict["ind_comm_pub_business_exception"] = total
            else:
                self.crawler.json_dict["ind_comm_pub_business_exception"] = m.group(1)
        else:
            self.crawler.json_dict["ind_comm_pub_business_exception"] = total

        # 严重违法信息
        url = "%s%s%s%s%s%s" % (host, "Yzwfxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        m = re.search(r'yzwf_paging\((\[.*?\])', resp.content)
        total = []
        if m:
            if len(m.group(1)) <= 2:
                self.crawler.json_dict["ind_comm_pub_serious_violate_law"] = []
            else:
                self.crawler.json_dict["ind_comm_pub_serious_violate_law"] = m.group(1)
        else:
            self.crawler.json_dict["ind_comm_pub_serious_violate_law"] = total

        # 抽查检查信息
        url = "%s%s%s%s%s%s" % (host, "Ccjcxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        m = re.search(r'ccjc_paging\((\[.*?\])', resp.content)
        total = []
        if m:
            if len(m.group(1)) <= 2:
                self.crawler.json_dict["ind_comm_pub_spot_check"] = []
            else:
                self.crawler.json_dict["ind_comm_pub_spot_check"] = m.group(1)
        else:
            self.crawler.json_dict["ind_comm_pub_spot_check"] = total

        # 基本信息
        url = "%s%s%s%s%s%s" % (host, "Jbxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        soup = BeautifulSoup(resp.content, "lxml")
        table = soup.find("table")
        self.crawler.json_dict["ind_comm_pub_reg_basic"] = self.parse_table1(table)

    def parse_ent_pub_pages(self):

        host = 'http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/get'
        args1 = 'Action.action?pripid='
        args2 = '&type='

        # 股东及出资信息
        url = "http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/getTzrxxPojoList.action"
        next_url = url
        post_data = {'pripid': self.crawler.pripid};
        resp = self.crawler.reqst.post(next_url, data=post_data)
        total = []
        list_m = json.loads(resp.content)

        for i,item in enumerate(list_m):
            table_save = {}
            table_save[u"股东"] = item["tJsTzrxx"]["inv"]
            table_save[u"认缴万元"] = str(item["tJsTzrxx"]["lisubconam"])
            table_save[u"实缴万元"] = str(item["tJsTzrxx"]["liacconam"])
            table_save[u"公示时间"] = item["tJsTzrxx"]["gstimeStr"]

            list = []
            rj = item["tJsTzrrjxxList"]
            sj = item["tJsTzrsjxxList"]
            for i in range(0, len(rj)):
                table_detail = {}
                table_detail[u"认缴出资方式"] = rj[i]["subconformName"]
                table_detail[u"认缴出资额（万元）"] = str(rj[i]["subconam"])
                table_detail[u"认缴出资到日期"] = rj[i]["subcondateStr"]

                table_detail[u"实缴出资方式"] = sj[i]["acconformName"]
                table_detail[u"实缴出资额（万元）"] = str(sj[i]["acconam"])
                table_detail[u"实缴出资到日期"] = sj[i]["accondateStr"]

                list.append(table_detail)
            table_save[u"list"] = list
            total.append(table_save)
        self.crawler.json_dict["ent_pub_shareholder_and_investment"] = total

        # 修改信息
        url = "%s%s%s%s%s%s" % (host, "QygsJsGdjczbgxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        m = re.search(r'tzrbgPaging\((\[.*?\])', resp.content)
        total = []
        if m:
            list_m = json.loads(m.group(1))
            for i,item in enumerate(list_m):
                table_save = {}
                table_save[u"序号"] = str(i+1)
                table_save[u"变更事项"] = item["alt"]
                table_save[u"变更日期"] = item["altdateStr"]
                table_save[u"变更前内容"] = item["altbe"]
                table_save[u"变更后内容"] = item["altaf"]
                total.append(table_save)
        self.crawler.json_dict["ent_pub_reg_modify"] = total

        # 股权变更信息
        url = "%s%s%s%s%s%s" % (host, "QygsJsGqbgxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        m = re.search(r'gqbgPaging\((\[.*?\])', resp.content)
        total = []
        if m:
            if len(m.group(1)) <= 2:
                self.crawler.json_dict["ent_pub_equity_change"] = []
            else:
                self.crawler.json_dict["ent_pub_equity_change"] = m.group(1)
        else:
            self.crawler.json_dict["ent_pub_equity_change"] = total
        # if m:
        #     list_m = json.loads(m.group(1))
        #     for i,item in enumerate(list_m):
        #         table_save = {}
        #         table_save[u"序号"] = str(i+1)
        #         table_save[u"股东"] = item["111111111"]
        #         table_save[u"变更前股权比例"] = item["11111111"]
        #         table_save[u"变更后股权比例"] = item["1111111"]
        #         table_save[u"股权变更日期"] = item["11111111"]
        #         table_save[u"公示时间"] = item["11111111"]
        #         total.append(table_save)
        #     self.crawler.json_dict["ent_pub_equity_change"] = total

        # 行政许可信息
        url = "%s%s%s%s%s%s" % (host, "QygsJsGqbgxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        m = re.search(r'xzxkPaging\((\[.*?\])', resp.content)
        total = []
        if m:
            list_m = json.loads(m.group(1))
            for i,item in enumerate(list_m):
                table_save = {}
                table_save[u"序号"] = str(i+1)
                table_save[u"许可文件编号"] = item["licno"]
                table_save[u"有效文件名称"] = item["licnamevalue"]
                table_save[u"有效期自"] = item["valfromStr"]
                table_save[u"有效期至"] = item["valtoStr"]
                table_save[u"许可机关"] = item["licanth"]
                table_save[u"许可内容"] = item["licitem"]
                table_save[u"状态"] = item["typename"]
                table_save[u"公示时间"] = item["gstimeStr"]

                url = "%s%s%s%s" % ("http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/getQygsJsBgxx.action?", self.crawler.pripid, "&refid=", item["id"])
                resp = self.crawler.reqst.get(url)

                m = re.search(r'xzxkbgPaging\((\[.*?\])', resp.content)

                table_save[u"详情"] = m.group(1)
                # table_detail = {}
                # m_list = []
                # if m.group(1) != "null":
                #     table_xzxkbg = json.loads(m.group(1))
                #     for i,item in enumerate(table_xzxkbg):
                #         table_xzxkbg = {}
                #         table_xzxkbg[u"序号"] = str(i+1)
                #         table_xzxkbg[u"变更事项"] = item["111111"]
                #         table_xzxkbg[u"变更时间"] = item["111111"]
                #         table_xzxkbg[u"变更前内容"] = item["111111"]
                #         table_xzxkbg[u"变更后内容"] = item["11111"]
                #
                #         m_list.append(table_xzxkbg)
                #     table_detail[u"变更信息"] = m_list
                #
                # table_save[u"详情"] = table_detail
                total.append(table_save)
        self.crawler.json_dict["ent_pub_administration_license"] = total

        # 知识产权出质登记信息
        url = "%s%s%s%s%s%s" % (host, "QygsJsZscqczxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        m = re.search(r'czdjPaging\((\[.*?\])', resp.content)
        total = []
        if m:
            if len(m.group(1)) <= 2:
                self.crawler.json_dict["ent_pub_knowledge_property"] = []
            else:
                self.crawler.json_dict["ent_pub_knowledge_property"] = m.group(1)
        else:
            self.crawler.json_dict["ent_pub_knowledge_property"] = total
        # if m:
        #     list_m = json.loads(m.group(1))
        #     for i,item in enumerate(list_m):
        #         table_save = {}
        #         table_save[u"序号"] = str(i+1)
        #         table_save[u"统一社会信用代码/注册号"] = item["111111111"]
        #         table_save[u"名称"] = item["11111111"]
        #         table_save[u"种类"] = item["1111111"]
        #         table_save[u"出质人名称"] = item["11111111"]
        #         table_save[u"质权人名称"] = item["11111111"]
        #         table_save[u"质权登记期限"] = item["11111111"]
        #         table_save[u"状态"] = item["11111111"]
        #         table_save[u"公示时间"] = item["1111111"]
        #         table_save[u"变化情况"] = item["1111111"]
        #         total.append(table_save)
        #     self.crawler.json_dict["ent_pub_equity_change"] = total

        # 行政处罚信息
        url = "%s%s%s%s%s%s" % (host, "QygsJsXzcfxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        m = re.search(r'qycfPaging\((\[.*?\])', resp.content)
        total = []
        if m:
            if len(m.group(1)) <= 2:
                self.crawler.json_dict["ent_pub_administration_sanction"] = []
            else:
                self.crawler.json_dict["ent_pub_administration_sanction"] = m.group(1)
        else:
            self.crawler.json_dict["ent_pub_administration_sanction"] = total
        # if m:
        #     list_m = json.loads(m.group(1))
        #     for i,item in enumerate(list_m):
        #         table_save = {}
        #         table_save[u"序号"] = str(i+1)
        #         table_save[u"行政处罚决定书文号"] = item["111111111"]
        #         table_save[u"违法行为类型"] = item["11111111"]
        #         table_save[u"行政处罚内容"] = item["1111111"]
        #         table_save[u"作出行政处罚决定机关名称"] = item["11111111"]
        #         table_save[u"作出行政处罚决定日期"] = item["11111111"]
        #         table_save[u"备注"] = item["11111111"]
        #         table_save[u"公示时间"] = item["11111111"]
        #         total.append(table_save)
        #     self.crawler.json_dict["ent_pub_equity_change"] = total

        # 企业年报
        url = "%s%s%s%s%s%s" % (host, "QygsQynbxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        m = re.search(r'qynbPaging\((\[.*?\])', resp.content)
        total = []
        if m:
            list_m = json.loads(m.group(1))
            for i,item in enumerate(list_m):
                table_save = {}
                table_save[u"序号"] = str(i+1)
                table_save[u"报送年度"] = item["ancheyear"]+"年度报告"
                table_save[u"发布日期"] = item["anchedateStr"]

                detail = {}
                url = "%s%s%s%s" % ("http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/nbDeatil.action?artId=", item["artid"], "&entType=", self.crawler.type)
                # print url
                resp = self.crawler.reqst.get(url)

                m = re.search(r'swPaging\((\[.*?\])', resp.content)
                sw_list = []
                if m:
                    list_m = json.loads(m.group(1))
                    for i,item in enumerate(list_m):
                        table_detail = {}
                        table_detail[u"类型"] = item["typofwebName"]
                        table_detail[u"名称"] = item["websitname"]
                        table_detail[u"网址"] = item["domain"]
                        sw_list.append(table_detail)
                detail[u"网站或网店信息"] = sw_list

                m = re.search(r'czPaging\((\[.*?\])', resp.content)
                sw_list = []
                if m:
                    list_m = json.loads(m.group(1))
                    for i,item in enumerate(list_m):
                        table_detail = {}
                        table_detail[u"股东"] = item["inv"]
                        table_detail[u"认缴出资额（万元）"] = item["lisubconam"]
                        table_detail[u"认缴出资到期时间"] = item["subcondatelabel"]
                        table_detail[u"认缴出资方式"] = item["subconformvalue"]
                        table_detail[u"实缴出资额（万元）"] = item["liacconam"]
                        table_detail[u"出资时间"] = item["accondatelabel"]
                        table_detail[u"出资方式"] = item["acconformvalue"]

                        sw_list.append(table_detail)
                detail[u"股东及出资信息"] = sw_list

                m = re.search(r'tzPaging\((\[.*?\])', resp.content)
                sw_list = []
                if m:
                    list_m = json.loads(m.group(1))
                    for i,item in enumerate(list_m):
                        table_detail = {}
                        table_detail[u"投资设立企业或购买股权企业名称 "] = item["inventname"]
                        table_detail[u"统一社会信用代码/注册号"] = item["regno"]


                        sw_list.append(table_detail)
                detail[u"对外投资信息"] = sw_list

                m = re.search(r'dbPaging\((\[.*?\])', resp.content)
                # sw_list = []
                # if m:
                #     list_m = json.loads(m.group(1))
                #     for i,item in enumerate(list_m):
                #         table_detail = {}
                #         table_detail[u"债权人 "] = item["1111111"]
                #         table_detail[u"债务人"] = item["111111"]
                #         table_detail[u"主债权种类 "] = item["1111111"]
                #         table_detail[u"主债权数额"] = item["111111"]
                #         table_detail[u"履行债务的期限"] = item["111111"]
                #         table_detail[u"保证的期间 "] = item["1111111"]
                #         table_detail[u"保证的方式"] = item["111111"]
                #         table_detail[u"保证担保的范围"] = item["111111"]
                #
                #
                #         sw_list.append(table_detail)
                # detail[u"对外投资信息"] = sw_list
                if m:
                    if len(m.group(1)) <= 2:
                        detail[u"对外提供保证担保信息"] = []
                    else:
                        detail[u"对外提供保证担保信息"] = m.group(1)
                else:
                    detail[u"对外提供保证担保信息"] = []

                m = re.search(r'bgPaging\((\[.*?\])', resp.content)
                sw_list = []
                if m:
                    list_m = json.loads(m.group(1))
                    for i,item in enumerate(list_m):
                        table_detail = {}
                        table_detail[u"股东 "] = item["inv"]
                        table_detail[u"变更前股权比例"] = item["transbmpr"]
                        table_detail[u"变更后股权比例 "] = item["transampr"]
                        table_detail[u"股权变更日期"] = item["altdatelabel"]


                        sw_list.append(table_detail)
                detail[u"股权变更信息"] = sw_list

                m = re.search(r'xgPaging\((\[.*?\])', resp.content)
                sw_list = []
                if m:
                    list_m = json.loads(m.group(1))
                    for i,item in enumerate(list_m):
                        table_detail = {}
                        table_detail[u"序号 "] = str(i+1)
                        table_detail[u"修改事项"] = item["alt"]
                        table_detail[u"修改前 "] = item["altbe"]
                        table_detail[u"修改后"] = item["altaf"]
                        table_detail[u"修改日期"] = item["getAltdatevalue"]


                        sw_list.append(table_detail)
                detail[u"修改记录"] = sw_list

                soup = BeautifulSoup(resp.content, "lxml")
                name_table_map = [u'企业基本信息', u'企业资产状况信息']
                for table in soup.find_all('table'):
                    list_table_title = table.find("th")
                    if list_table_title.attrs['style'] == 'text-align:center;color: red;':
                        list_table_title = list_table_title.parent
                        list_table_title = list_table_title.next_sibling.next_sibling

                    if list_table_title.text.strip() in name_table_map:
                        detail[list_table_title.text.strip()] = self.parse_table1(table)

                table_save[u"详情"] = detail
                total.append(table_save)
            self.crawler.json_dict["ent_pub_ent_annual_report"] = total

    def crawl_other_dept_pub_pages(self):
        next_url = 'http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/sEntDetail.action'
        post_data = {
                'entname': self.crawler.entname,
                'enttype': self.crawler.type,
                'optstate': self.crawler.optstate,
                'pripid': self.crawler.pripid,
                'regno': self.crawler.regno,
                'revdate': 'undefined',
             }
        resp = self.crawler.reqst.post(next_url, data=post_data)
        soup = BeautifulSoup(resp.content, "lxml")

        id_table_map = {
            's_qt_xzxkxx': 'other_dept_pub_administration_license',  # 行政许可信息
            's_qt_xzcfxx': 'other_dept_pub_administration_sanction',  # 行政处罚信息
            's_qt_bgxx': 'other_dept_pub_reg_modify',  # 变更信息
        }
        table_ids = id_table_map.keys()
        for table_id in table_ids:
            table_name = id_table_map[table_id]

            div = soup.find("div", {"id": table_id})
            if div:
                table = div.find("table")
                self.crawler.json_dict[table_name] = self.parse_table2(table)
            else:
                self.crawler.json_dict[table_name] = []

    def parse_judical_assist_pub_pages(self):
        host = 'http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/get'
        args1 = 'Action.action?pripid='
        args2 = '&type='

        # 司法股权冻结信息
        url = "%s%s%s%s%s%s" % (host, "SfgsGqdjxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        m = re.search(r'gqdj_paging\((\[.*?\])', resp.content)
        if m:
            if len(m.group(1)) <= 2:
                self.crawler.json_dict["judical_assist_pub_equity_freeze"] = []
            else:
                self.crawler.json_dict["judical_assist_pub_equity_freeze"] = m.group(1)
        else:
            self.crawler.json_dict["judical_assist_pub_equity_freeze"] = []
        total = []
        # if m:
        #     list_m = json.loads(m.group(1))
        #     for i,item in enumerate(list_m):
        #         table_save = {}
        #         table_save[u"序号"] = str(i+1)
        #         table_save[u"被执行人"] = item["name"]
        #         table_save[u"股权数额"] = item["positionName"]
        #         table_save[u"执行法院"] = item["name"]
        #         table_save[u"协助公示通知书文号"] = item["positionName"]
        #         table_save[u"状态"] = item["positionName"]
        #         table_save[u"详情"] = item["positionName"]
        #         total.append(table_save)
        # self.crawler.json_dict["judical_assist_pub_equity_freeze"] = total

        # 司法股东变更登记信息
        url = "%s%s%s%s%s%s" % (host, "SfgsGdbgxx", args1, self.crawler.pripid, args2, self.crawler.type)
        resp = self.crawler.reqst.get(url)

        m = re.search(r'gdbg_paging\((\[.*?\])', resp.content)
        if m:
            if len(m.group(1)) <= 2:
                self.crawler.json_dict["judical_assist_pub_shareholder_modify"] = []
            else:
                self.crawler.json_dict["judical_assist_pub_shareholder_modify"] = m.group(1)
        else:
            self.crawler.json_dict["judical_assist_pub_shareholder_modify"] = []
        total = []
        # if m:
        #     list_m = json.loads(m.group(1))
        #     for i,item in enumerate(list_m):
        #         table_save = {}
        #         table_save[u"序号"] = str(i+1)
        #         table_save[u"被执行人"] = item["name"]
        #         table_save[u"股权数额"] = item["positionName"]
        #         table_save[u"受让人"] = item["name"]
        #         table_save[u"执行法院"] = item["positionName"]
        #         table_save[u"详情"] = item["positionName"]
        #         total.append(table_save)
        # self.crawler.json_dict["judical_assist_pub_shareholder_modify"] = total

    def parse_table1(self, table):
        table_ths = table.find_all("th")
        table_th = []
        for th in table_ths:
            if 'colspan' in th.attrs:
                continue
            if th.text.strip() == "":
                continue
            table_th.append(th.text.strip())

        table_tds = table.find_all("td")

        table_td = [td.text.strip() for td in table_tds]

        table_save = {}
        for i in range(0, len(table_th)):
            table_save[table_th[i]] = table_td[i]
        return table_save

    def parse_table2(self, table):

        table_trs = table.find_all("tr")
        table_th = [th for th in table_trs[1].stripped_strings]
        total = []
        for tr in table_trs[2:]:
            table_td =[]
            table_tds = tr.find_all("td")
            for td in table_tds:
                if 'colspan' in td.attrs:
                    continue
                else:
                    table_td.append(td.text.strip())
            if table_td:
                for i in range(0, len(table_th)):
                    table_save = {}
                    table_save[table_th[i]] = table_td[i]
                    total.append(table_save)

        return total

"""
if __name__ == '__main__':
    from CaptchaRecognition import CaptchaRecognition
    import run
    run.config_logging()
    LiaoningCrawler.code_cracker = CaptchaRecognition('liaoning')

    crawler = LiaoningCrawler('./enterprise_crawler/liaoning.json')
    enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/liaoning.txt')
    # enterprise_list = ['210000004920321']
    # enterprise_list = ['210200400016720']
    for ent_number in enterprise_list:
        ent_number = ent_number.rstrip('\n')
        logging.info('###################   Start to crawl enterprise with id %s   ###################\n' % ent_number)
        crawler.run(ent_number=ent_number)
"""
