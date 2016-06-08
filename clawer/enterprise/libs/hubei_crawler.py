#!/usr/bin/env python
#encoding=utf-8
import threading
from heilongjiang_crawler import HeilongjiangClawer
from heilongjiang_crawler import HeilongjiangParser
from common_func import get_proxy

# from enterprise.libs.CaptchaRecognition import CaptchaRecognition


class HubeiCrawler(HeilongjiangClawer):
    """湖北爬虫，与黑龙江爬虫一致"""
    # code_cracker = CaptchaRecognition('hubei')

    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {
        'host': 'xyjg.egs.gov.cn',
        'get_checkcode':
        'http://xyjg.egs.gov.cn/ECPS_HB/validateCode.jspx?type=0',
        'post_checkcode': 'http://xyjg.egs.gov.cn/ECPS_HB/checkCheckNo.jspx',
        'get_info_entry': 'http://xyjg.egs.gov.cn/ECPS_HB/searchList.jspx',
        'ind_comm_pub_skeleton':
        'http://xyjg.egs.gov.cn/ECPS_HB/businessPublicity.jspx?id=',
        'ent_pub_skeleton':
        'http://xyjg.egs.gov.cn/ECPS_HB/enterprisePublicity.jspx?id=',
        'other_dept_pub_skeleton':
        'http://xyjg.egs.gov.cn/ECPS_HB/otherDepartment.jspx?id=',
        'judical_assist_skeleton':
        'http://xyjg.egs.gov.cn/ECPS_HB/justiceAssistance.jspx?id=',
        'ind_comm_pub_reg_shareholder':
        'http://xyjg.egs.gov.cn/ECPS_HB/QueryInvList.jspx?',    # 股东信息
        'ind_comm_pub_reg_modify':
        'http://xyjg.egs.gov.cn/ECPS_HB/QueryAltList.jspx?',    # 变更信息翻页
        'ind_comm_pub_arch_key_persons':
        'http://xyjg.egs.gov.cn/ECPS_HB/QueryMemList.jspx?',    # 主要人员信息翻页
        'ind_comm_pub_spot_check':
        'http://xyjg.egs.gov.cn/ECPS_HB/QuerySpotCheckList.jspx?',    # 抽样检查信息翻页
        'ind_comm_pub_movable_property_reg':
        'http://xyjg.egs.gov.cn/ECPS_HB/QueryMortList.jspx?',    # 动产抵押登记信息翻页
        'ind_comm_pub_business_exception':
        'http://xyjg.egs.gov.cn/ECPS_HB/QueryExcList.jspx?',    # 经营异常信息
        'ind_comm_pub_equity_ownership_reg':
        'http://xyjg.egs.gov.cn/ECPS_HB/QueryPledgeList.jspx?',    # 股权出质登记信息翻页
        'ind_comm_pub_arch_branch':
        'http://xyjg.egs.gov.cn/ECPS_HB/QueryChildList.jspx?',    # 分支机构信息
        'ent_pub_administration_license':
        'http://xyjg.egs.gov.cn/ECPS_HB/QueryLicenseRegList.jspx?',    # 行政许可信息
        'shareholder_detail':
        'http://xyjg.egs.gov.cn/ECPS_HB/queryInvDetailAction.jspx?id=',    # 投资人详情
        'movable_property_reg_detail':
        'http://xyjg.egs.gov.cn/ECPS_HB/mortInfoDetail.jspx?id=',    # 动产抵押登记详情
        'annual_report':
        'http://xyjg.egs.gov.cn/ECPS_HB/QueryYearExamineDetail.jspx?id=',    # 企业年报详情
    }

    def __init__(self, json_restore_path=None):
        super(HubeiCrawler, self).__init__(json_restore_path)
        self.json_restore_path = json_restore_path
        #html数据的存储路径
        self.html_restore_path = self.json_restore_path + '/hubei/'
        #验证码图片的存储路径
        self.ckcode_image_path = self.json_restore_path + '/hubei/ckcode.jpg'
        self.parser = HubeiParser(self)
        self.proxies = get_proxy('hubei')


class HubeiParser(HeilongjiangParser):
    def __init__(self, crawler):
        self.crawler = crawler
