#!/usr/bin/env python
#encoding=utf-8

from heilongjiang_crawler import HeilongjiangClawer
from heilongjiang_crawler import HeilongjiangParser
from common_func import get_proxy


class AnhuiCrawler(HeilongjiangClawer):
    """青海爬虫
    """

    urls = {'host': 'http://www.ahcredit.gov.cn',
            'get_checkcode': 'http://www.ahcredit.gov.cn/validateCode.jspx?type=0',
            'post_checkcode': 'http://www.ahcredit.gov.cn/checkCheckNo.jspx',
            'get_info_entry': 'http://www.ahcredit.gov.cn/searchList.jspx',
            'ind_comm_pub_skeleton': 'http://www.ahcredit.gov.cn/businessPublicity.jspx?id=',
            'ent_pub_skeleton': 'http://www.ahcredit.gov.cn/enterprisePublicity.jspx?id=',
            'other_dept_pub_skeleton': 'http://www.ahcredit.gov.cn/otherDepartment.jspx?id=',
            'judical_assist_skeleton': 'http://www.ahcredit.gov.cn/justiceAssistance.jspx?id=',
            'ind_comm_pub_reg_shareholder': 'http://www.ahcredit.gov.cn/QueryInvList.jspx?',    # 股东信息
            'ind_comm_pub_reg_modify': 'http://www.ahcredit.gov.cn/QueryAltList.jspx?',    # 变更信息翻页
            'ind_comm_pub_arch_key_persons': 'http://www.ahcredit.gov.cn/QueryMemList.jspx?',    # 主要人员信息翻页
            'ind_comm_pub_spot_check': 'http://www.ahcredit.gov.cn/QuerySpotCheckList.jspx?',    # 抽样检查信息翻页
            'ind_comm_pub_movable_property_reg': 'http://www.ahcredit.gov.cn/QueryMortList.jspx?',    # 动产抵押登记信息翻页
            'ind_comm_pub_business_exception': 'http://www.ahcredit.gov.cn/QueryExcList.jspx?',    # 经营异常信息
            'ent_pub_administration_license': 'http://www.ahcredit.gov.cn/QueryLicenseRegList.jspx?',    # 行政许可信息
            'shareholder_detail': 'http://www.ahcredit.gov.cn/queryInvDetailAction.jspx?id=',    # 投资人详情
            'movable_property_reg_detail': 'http://www.ahcredit.gov.cn/mortInfoDetail.jspx?id=',    # 动产抵押登记详情
            'annual_report': 'http://www.ahcredit.gov.cn/QueryYearExamineDetail.jspx?id=',    # 企业年报详情
            }

    def __init__(self, json_restore_path=None):
        super(AnhuiCrawler, self).__init__(json_restore_path)
        self.json_restore_path = json_restore_path
        #html数据的存储路径
        self.html_restore_path = self.json_restore_path + '/anhui/'

        #验证码图片的存储路径
        self.ckcode_image_path = self.json_restore_path + '/anhui/ckcode.jpg'
        self.parser = AnhuiParser(self)
        self.proxies = get_proxy('anhui')


class AnhuiParser(HeilongjiangParser):
    def __init__(self, crawler):
        self.crawler = crawler
