#!/usr/bin/env python
#encoding=utf-8
from . import settings
import threading
from heilongjiang_crawler import HeilongjiangClawer
from heilongjiang_crawler import HeilongjiangParser
from enterprise.libs.CaptchaRecognition import CaptchaRecognition

class ShanxiCrawler(HeilongjiangClawer):
    """山西爬虫
    """
    # html数据的存储路径
    html_restore_path = settings.json_restore_path + '/shanxi/'

    #验证码图片的存储路径
    ckcode_image_path = settings.json_restore_path + '/shanxi/ckcode.jpg'

    code_cracker = CaptchaRecognition('shanxi')
    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {'host': 'www.hljaic.gov.cn',
            'get_checkcode': 'http://218.26.1.108/validateCode.jspx?type=0',
            'post_checkcode': 'http://218.26.1.108/checkCheckNo.jspx',
            'get_info_entry': 'http://218.26.1.108/searchList.jspx',

            'ind_comm_pub_skeleton': 'http://218.26.1.108/businessPublicity.jspx?id=',
            'ent_pub_skeleton': 'http://218.26.1.108/enterprisePublicity.jspx?id=',
            'other_dept_pub_skeleton': 'http://218.26.1.108/otherDepartment.jspx?id=',
            'judical_assist_skeleton': 'http://218.26.1.108/justiceAssistance.jspx?id=',

            'ind_comm_pub_reg_shareholder': 'http://218.26.1.108/QueryInvList.jspx?',# 股东信息
            'ind_comm_pub_reg_modify': 'http://218.26.1.108/QueryAltList.jspx?',  # 变更信息翻页
            'ind_comm_pub_arch_key_persons': 'http://218.26.1.108/QueryMemList.jspx?',  # 主要人员信息翻页
            'ind_comm_pub_spot_check': 'http://218.26.1.108/QuerySpotCheckList.jspx?',  # 抽样检查信息翻页
            'ind_comm_pub_movable_property_reg': 'http://218.26.1.108/QueryMortList.jspx?',  # 动产抵押登记信息翻页
            'ind_comm_pub_business_exception': 'http://218.26.1.108/QueryExcList.jspx?',  # 经营异常信息

            'shareholder_detail': 'http://218.26.1.108/queryInvDetailAction.jspx?id=',  # 投资人详情
            'movable_property_reg_detail': 'http://218.26.1.108/mortInfoDetail.jspx?id=',  # 动产抵押登记详情
            'annual_report': 'http://218.26.1.108/QueryYearExamineDetail.jspx?id=',  # 企业年报详情


            }


    def __init__(self, json_restore_path):
        HeilongjiangClawer.__init__(self, json_restore_path)
        self.json_restore_path = json_restore_path
        self.parser = ShanxiParser(self)


class ShanxiParser(HeilongjiangParser):
    def __init__(self, crawler):
        self.crawler = crawler

"""
if __name__ == '__main__':
    from CaptchaRecognition import CaptchaRecognition
    import run
    run.config_logging()
    ShanxiCrawler.code_cracker = CaptchaRecognition('shanxi')

    crawler = ShanxiCrawler('./enterprise_crawler/shanxi.json')
    enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/shanxi.txt')
    # enterprise_list = ['310000000007622']
    for ent_number in enterprise_list:
        ent_number = ent_number.rstrip('\n')
        settings.logger.info('###################   Start to crawl enterprise with id %s   ###################\n' % ent_number)
        crawler.run(ent_number=ent_number)
"""
