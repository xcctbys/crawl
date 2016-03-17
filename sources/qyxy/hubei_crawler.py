#!/usr/bin/env python
#encoding=utf-8
import os
import threading

import importlib

ENT_CRAWLER_SETTINGS = os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS:
    settings = importlib.import_module(ENT_CRAWLER_SETTINGS)
else:
    import settings

from crawler import CrawlerUtils
from heilongjiang_crawler import HeilongjiangClawer
from heilongjiang_crawler import HeilongjiangParser
class HubeiCrawler(HeilongjiangClawer):
    """湖北爬虫
    """
    #html数据的存储路径
    html_restore_path = settings.html_restore_path + '/hubei/'

    #验证码图片的存储路径
    ckcode_image_path = settings.json_restore_path + '/hubei/ckcode.jpg'

    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {'host': 'www.hljaic.gov.cn',
            'get_checkcode': 'http://xyjg.egs.gov.cn/ECPS_HB/validateCode.jspx?type=0',
            'post_checkcode': 'http://xyjg.egs.gov.cn/ECPS_HB/checkCheckNo.jspx',
            'get_info_entry': 'http://xyjg.egs.gov.cn/ECPS_HB/searchList.jspx',

            'ind_comm_pub_skeleton': 'http://xyjg.egs.gov.cn/ECPS_HB/businessPublicity.jspx?id=',
            'ent_pub_skeleton': 'http://xyjg.egs.gov.cn/ECPS_HB/enterprisePublicity.jspx?id=',
            'other_dept_pub_skeleton': 'http://xyjg.egs.gov.cn/ECPS_HB/otherDepartment.jspx?id=',
            'judical_assist_skeleton': 'http://xyjg.egs.gov.cn/ECPS_HB/justiceAssistance.jspx?id=',

            'ind_comm_pub_reg_shareholder': 'http://xyjg.egs.gov.cn/ECPS_HB/QueryInvList.jspx?',# 股东信息
            'ind_comm_pub_reg_modify': 'http://xyjg.egs.gov.cn/ECPS_HB/QueryAltList.jspx?',  # 变更信息翻页
            'ind_comm_pub_arch_key_persons': 'http://xyjg.egs.gov.cn/ECPS_HB/QueryMemList.jspx?',  # 主要人员信息翻页
            'ind_comm_pub_spot_check': 'http://xyjg.egs.gov.cn/ECPS_HB/QuerySpotCheckList.jspx?',  # 抽样检查信息翻页
            'ind_comm_pub_movable_property_reg': 'http://xyjg.egs.gov.cn/ECPS_HB/QueryMortList.jspx?',  # 动产抵押登记信息翻页
            'ind_comm_pub_business_exception': 'http://xyjg.egs.gov.cn/ECPS_HB/QueryExcList.jspx?',  # 经营异常信息
            'ind_comm_pub_equity_ownership_reg': 'http://xyjg.egs.gov.cn/ECPS_HB/QueryPledgeList.jspx?',  # 股权出质登记信息翻页
            'ind_comm_pub_arch_branch': 'http://xyjg.egs.gov.cn/ECPS_HB/QueryChildList.jspx?',  # 分支机构信息

            'shareholder_detail': 'http://xyjg.egs.gov.cn/ECPS_HB/queryInvDetailAction.jspx?id=',  # 投资人详情
            'movable_property_reg_detail': 'http://xyjg.egs.gov.cn/ECPS_HB/mortInfoDetail.jspx?id=',  # 动产抵押登记详情
            'annual_report': 'http://xyjg.egs.gov.cn/ECPS_HB/QueryYearExamineDetail.jspx?id=',  # 企业年报详情
            }


    def __init__(self, json_restore_path):
        HeilongjiangClawer.__init__(self, json_restore_path)
        self.json_restore_path = json_restore_path
        self.parser = HubeiParser(self)


class HubeiParser(HeilongjiangParser):
    def __init__(self, crawler):
        self.crawler = crawler


if __name__ == '__main__':
    from CaptchaRecognition import CaptchaRecognition
    import run
    run.config_logging()
    HubeiCrawler.code_cracker = CaptchaRecognition('hubei')

    crawler = HubeiCrawler('./enterprise_crawler/hubei.json')
    enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/hubei.txt')
    # enterprise_list = ['420000400000283']
    # enterprise_list = ['420000000010087']
    # enterprise_list = ['914201133002117823']  # 股东信息二级表格
    # enterprise_list = ['420000000032278']
    for ent_number in enterprise_list:
        ent_number = ent_number.rstrip('\n')
        settings.logger.info('###################   Start to crawl enterprise with id %s   ###################\n' % ent_number)
        crawler.run(ent_number=ent_number)

