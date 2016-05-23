 #!/usr/bin/env python
#encoding=utf-8
from . import settings
import threading
from heilongjiang_crawler import HeilongjiangClawer
from heilongjiang_crawler import HeilongjiangParser
# from enterprise.libs.CaptchaRecognition import CaptchaRecognition
from common_func import get_proxy

class HainanCrawler(HeilongjiangClawer):
    """海南爬虫
    """
    # code_cracker = CaptchaRecognition('hainan')
    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {'host': 'aic.hainan.gov.cn:1888',
            'get_checkcode': 'http://aic.hainan.gov.cn:1888/validateCode.jspx?type=0',
            'post_checkcode': 'http://aic.hainan.gov.cn:1888/checkCheckNo.jspx',
            'get_info_entry': 'http://aic.hainan.gov.cn:1888/searchList.jspx',

            'ind_comm_pub_skeleton': 'http://aic.hainan.gov.cn:1888/businessPublicity.jspx?id=',
            'ent_pub_skeleton': 'http://aic.hainan.gov.cn:1888/enterprisePublicity.jspx?id=',
            'other_dept_pub_skeleton': 'http://aic.hainan.gov.cn:1888/otherDepartment.jspx?id=',
            'judical_assist_skeleton': 'http://aic.hainan.gov.cn:1888/justiceAssistance.jspx?id=',

            'ind_comm_pub_reg_shareholder': 'http://aic.hainan.gov.cn:1888/QueryInvList.jspx?',# 股东信息
            'ind_comm_pub_reg_modify': 'http://aic.hainan.gov.cn:1888/QueryAltList.jspx?',  # 变更信息翻页
            'ind_comm_pub_arch_key_persons': 'http://aic.hainan.gov.cn:1888/QueryMemList.jspx?',  # 主要人员信息翻页
            'ind_comm_pub_spot_check': 'http://aic.hainan.gov.cn:1888/QuerySpotCheckList.jspx?',  # 抽样检查信息翻页
            'ind_comm_pub_movable_property_reg': 'http://aic.hainan.gov.cn:1888/QueryMortList.jspx?',  # 动产抵押登记信息翻页
            'ind_comm_pub_business_exception': 'http://aic.hainan.gov.cn:1888/QueryExcList.jspx?',  # 经营异常信息
            'ent_pub_administration_license': 'http://aic.hainan.gov.cn:1888/QueryLicenseRegList.jspx?', # 行政许可信息

            'shareholder_detail': 'http://aic.hainan.gov.cn:1888/queryInvDetailAction.jspx?id=',  # 投资人详情
            'movable_property_reg_detail': 'http://aic.hainan.gov.cn:1888/mortInfoDetail.jspx?id=',  # 动产抵押登记详情
            'annual_report': 'http://aic.hainan.gov.cn:1888/QueryYearExamineDetail.jspx?id=',  # 企业年报详情
            }

    def __init__(self, json_restore_path=None):

        super(HainanCrawler, self).__init__(json_restore_path)
        # HeilongjiangClawer.__init__(self, json_restore_path)
        self.json_restore_path = json_restore_path
        # html数据的存储路径
        self.html_restore_path = self.json_restore_path + '/hainan/'

        #验证码图片的存储路径
        self.ckcode_image_path = self.json_restore_path + '/hainan/ckcode.jpg'

        self.parser = HainanParser(self)

        self.proxies = get_proxy('hainan')


class HainanParser(HeilongjiangParser):
    def __init__(self, crawler):
        self.crawler = crawler

