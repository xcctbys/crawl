#!/usr/bin/env python
#encoding=utf-8
import threading
from heilongjiang_crawler import HeilongjiangClawer
from heilongjiang_crawler import HeilongjiangParser
# from enterprise.libs.CaptchaRecognition import CaptchaRecognition
from common_func import get_proxy


class XizangCrawler(HeilongjiangClawer):
    """西藏爬虫 , 继承黑龙江爬虫."""
    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {
        'host': 'www.xzaic.gov.cn',
        'get_checkcode': 'http://gsxt.xzaic.gov.cn/validateCode.jspx?type=0',
        'post_checkcode': 'http://gsxt.xzaic.gov.cn/checkCheckNo.jspx',
        'get_info_entry': 'http://gsxt.xzaic.gov.cn/searchList.jspx',
        'ind_comm_pub_skeleton':
        'http://gsxt.xzaic.gov.cn/businessPublicity.jspx?id=',
        'ent_pub_skeleton':
        'http://gsxt.xzaic.gov.cn/enterprisePublicity.jspx?id=',
        'other_dept_pub_skeleton':
        'http://gsxt.xzaic.gov.cn/otherDepartment.jspx?id=',
        'judical_assist_skeleton':
        'http://gsxt.xzaic.gov.cn/justiceAssistance.jspx?id=',
        'ind_comm_pub_reg_shareholder':
        'http://gsxt.xzaic.gov.cn/QueryInvList.jspx?',    # 股东信息
        'ind_comm_pub_reg_modify':
        'http://gsxt.xzaic.gov.cn/QueryAltList.jspx?',    # 变更信息翻页
        'ind_comm_pub_arch_key_persons':
        'http://gsxt.xzaic.gov.cn/QueryMemList.jspx?',    # 主要人员信息翻页
        'ind_comm_pub_spot_check':
        'http://gsxt.xzaic.gov.cn/QuerySpotCheckList.jspx?',    # 抽样检查信息翻页
        'ind_comm_pub_movable_property_reg':
        'http://gsxt.xzaic.gov.cn/QueryMortList.jspx?',    # 动产抵押登记信息翻页
        'ind_comm_pub_business_exception':
        'http://gsxt.xzaic.gov.cn/QueryExcList.jspx?',    # 经营异常信息
        'ent_pub_administration_license':
        'http://gsxt.xzaic.gov.cn/QueryLicenseRegList.jspx?',    # 行政许可信息
        'shareholder_detail':
        'http://gsxt.xzaic.gov.cn/queryInvDetailAction.jspx?id=',    # 投资人详情
        'movable_property_reg_detail':
        'http://gsxt.xzaic.gov.cn/mortInfoDetail.jspx?id=',    # 动产抵押登记详情
        'annual_report':
        'http://gsxt.xzaic.gov.cn/QueryYearExamineDetail.jspx?id=',    # 企业年报详情
    }

    def __init__(self, json_restore_path=None):
        super(XizangCrawler, self).__init__(json_restore_path)
        self.json_restore_path = json_restore_path
        # html数据的存储路径
        self.html_restore_path = self.json_restore_path + '/xizang/'

        #验证码图片的存储路径
        self.ckcode_image_path = self.json_restore_path + '/xizang/ckcode.jpg'
        self.parser = XizangParser(self)
        self.proxies = get_proxy('xizang')


class XizangParser(HeilongjiangParser):
    def __init__(self, crawler):
        self.crawler = crawler
