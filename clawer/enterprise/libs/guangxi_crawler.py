#!/usr/bin/env python
#encoding=utf-8

from heilongjiang_crawler import HeilongjiangClawer
from heilongjiang_crawler import HeilongjiangParser
from common_func import get_proxy


class GuangxiCrawler(HeilongjiangClawer):
    """广西爬虫， 与黑龙江爬虫一致 """

    urls = {'host': 'http://gxqyxygs.gov.cn',
            'get_checkcode': 'http://gxqyxygs.gov.cn/validateCode.jspx?type=0',
            'post_checkcode': 'http://gxqyxygs.gov.cn/checkCheckNo.jspx',
            'get_info_entry': 'http://gxqyxygs.gov.cn/searchList.jspx',
            'ind_comm_pub_skeleton': 'http://gxqyxygs.gov.cn/businessPublicity.jspx?id=',
            'ent_pub_skeleton': 'http://gxqyxygs.gov.cn/enterprisePublicity.jspx?id=',
            'other_dept_pub_skeleton': 'http://gxqyxygs.gov.cn/otherDepartment.jspx?id=',
            'judical_assist_skeleton': 'http://gxqyxygs.gov.cn/justiceAssistance.jspx?id=',
            'ind_comm_pub_reg_shareholder': 'http://gxqyxygs.gov.cn/QueryInvList.jspx?',    # 股东信息
            'ind_comm_pub_reg_modify': 'http://gxqyxygs.gov.cn/QueryAltList.jspx?',    # 变更信息翻页
            'ind_comm_pub_arch_key_persons': 'http://gxqyxygs.gov.cn/QueryMemList.jspx?',    # 主要人员信息翻页
            'ind_comm_pub_spot_check': 'http://gxqyxygs.gov.cn/QuerySpotCheckList.jspx?',    # 抽样检查信息翻页
            'ind_comm_pub_movable_property_reg': 'http://gxqyxygs.gov.cn/QueryMortList.jspx?',    # 动产抵押登记信息翻页
            'ind_comm_pub_business_exception': 'http://gxqyxygs.gov.cn/QueryExcList.jspx?',    # 经营异常信息
            'ent_pub_administration_license': 'http://gxqyxygs.gov.cn/QueryLicenseRegList.jspx?',    # 行政许可信息
            'shareholder_detail': 'http://gxqyxygs.gov.cn/queryInvDetailAction.jspx?id=',    # 投资人详情
            'movable_property_reg_detail': 'http://gxqyxygs.gov.cn/mortInfoDetail.jspx?id=',    # 动产抵押登记详情
            'annual_report': 'http://gxqyxygs.gov.cn/QueryYearExamineDetail.jspx?id=',    # 企业年报详情
            }

    def __init__(self, json_restore_path=None):
        super(GuangxiCrawler, self).__init__(json_restore_path)
        self.json_restore_path = json_restore_path
        #html数据的存储路径
        self.html_restore_path = self.json_restore_path + '/Guangxi/'

        #验证码图片的存储路径
        self.ckcode_image_path = self.json_restore_path + '/Guangxi/ckcode.jpg'
        self.parser = GuangxiParser(self)
        self.proxies = get_proxy('guangxi')


class GuangxiParser(HeilongjiangParser):
    def __init__(self, crawler):
        self.crawler = crawler
