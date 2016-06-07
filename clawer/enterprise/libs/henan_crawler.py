#!/usr/bin/env python
#encoding=utf-8
import threading
from heilongjiang_crawler import HeilongjiangClawer
from heilongjiang_crawler import HeilongjiangParser
from common_func import get_proxy


class HenanCrawler(HeilongjiangClawer):
    """河南爬虫，与黑龙江爬虫一致"""
    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {
        'host': 'http://222.143.24.157',
        'get_checkcode': 'http://222.143.24.157/validateCode.jspx?type=0',
        'post_checkcode': 'http://222.143.24.157/checkCheckNo.jspx',
        'get_info_entry': 'http://222.143.24.157/searchList.jspx',
        'ind_comm_pub_skeleton':
        'http://222.143.24.157/businessPublicity.jspx?id=',
        'ent_pub_skeleton':
        'http://222.143.24.157/enterprisePublicity.jspx?id=',
        'other_dept_pub_skeleton':
        'http://222.143.24.157/otherDepartment.jspx?id=',
        'judical_assist_skeleton':
        'http://222.143.24.157/justiceAssistance.jspx?id=',
        'ind_comm_pub_reg_shareholder':
        'http://222.143.24.157/QueryInvList.jspx?',    # 股东信息
        'ind_comm_pub_reg_modify':
        'http://222.143.24.157/QueryAltList.jspx?',    # 变更信息翻页
        'ind_comm_pub_arch_key_persons':
        'http://222.143.24.157/QueryMemList.jspx?',    # 主要人员信息翻页
        'ind_comm_pub_spot_check':
        'http://222.143.24.157/QuerySpotCheckList.jspx?',    # 抽样检查信息翻页
        'ind_comm_pub_movable_property_reg':
        'http://222.143.24.157/QueryMortList.jspx?',    # 动产抵押登记信息翻页
        'ind_comm_pub_business_exception':
        'http://222.143.24.157/QueryExcList.jspx?',    # 经营异常信息
        'ent_pub_administration_license':
        'http://222.143.24.157/QueryLicenseRegList.jspx?',    # 行政许可信息
        'shareholder_detail':
        'http://222.143.24.157/queryInvDetailAction.jspx?id=',    # 投资人详情
        'movable_property_reg_detail':
        'http://222.143.24.157/mortInfoDetail.jspx?id=',    # 动产抵押登记详情
        'annual_report':
        'http://222.143.24.157/QueryYearExamineDetail.jspx?id=',    # 企业年报详情
    }

    def __init__(self, json_restore_path=None):
        super(HenanCrawler, self).__init__(json_restore_path)
        self.json_restore_path = json_restore_path
        #html数据的存储路径
        self.html_restore_path = self.json_restore_path + '/henan/'

        #验证码图片的存储路径
        self.ckcode_image_path = self.json_restore_path + '/henan/ckcode.jpg'
        self.parser = HenanParser(self)
        self.proxies = get_proxy('henan')


class HenanParser(HeilongjiangParser):
    def __init__(self, crawler):
        self.crawler = crawler
