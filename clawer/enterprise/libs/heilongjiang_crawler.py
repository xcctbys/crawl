#!/usr/bin/env python
# encoding=utf-8
import os
import requests
import time
import re
import random
import threading
import unittest
from bs4 import BeautifulSoup
from crawler import Crawler
from crawler import Parser
from crawler import CrawlerUtils
from . import settings
import logging
from enterprise.libs.CaptchaRecognition import CaptchaRecognition

class HeilongjiangClawer(Crawler):
    """黑龙江工商公示信息网页爬虫
    """
    # html数据的存储路径
    html_restore_path = settings.json_restore_path + '/heilongjiang/'

    # 验证码图片的存储路径
    ckcode_image_path = settings.json_restore_path + '/heilongjiang/ckcode.jpg'
    code_cracker = CaptchaRecognition('heilongjiang')
    # 多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {'host': 'www.hljaic.gov.cn',
            'get_checkcode': 'http://gsxt.hljaic.gov.cn/validateCode.jspx?type=0',
            'post_checkcode': 'http://gsxt.hljaic.gov.cn/checkCheckNo.jspx',
            'get_info_entry': 'http://gsxt.hljaic.gov.cn/searchList.jspx',

            'ind_comm_pub_skeleton': 'http://gsxt.hljaic.gov.cn/businessPublicity.jspx?id=',
            'ent_pub_skeleton': 'http://gsxt.hljaic.gov.cn/enterprisePublicity.jspx?id=',
            'other_dept_pub_skeleton': 'http://gsxt.hljaic.gov.cn/otherDepartment.jspx?id=',
            'judical_assist_skeleton': 'http://gsxt.hljaic.gov.cn/justiceAssistance.jspx?id=',

            'ind_comm_pub_reg_shareholder': 'http://gsxt.hljaic.gov.cn/QueryInvList.jspx?',# 股东信息
            'ind_comm_pub_reg_modify': 'http://gsxt.hljaic.gov.cn/QueryAltList.jspx?',  # 变更信息翻页
            'ind_comm_pub_arch_key_persons': 'http://gsxt.hljaic.gov.cn/QueryMemList.jspx?',  # 主要人员信息翻页
            'ind_comm_pub_spot_check': 'http://gsxt.hljaic.gov.cn/QuerySpotCheckList.jspx?',  # 抽样检查信息翻页
            'ind_comm_pub_movable_property_reg': 'http://gsxt.hljaic.gov.cn/QueryMortList.jspx?',  # 动产抵押登记信息翻页
            'ind_comm_pub_business_exception': 'http://gsxt.hljaic.gov.cn/QueryExcList.jspx?',  # 经营异常信息

            'shareholder_detail': 'http://gsxt.hljaic.gov.cn/queryInvDetailAction.jspx?id=',  # 投资人详情
            'movable_property_reg_detail': 'http://gsxt.hljaic.gov.cn/mortInfoDetail.jspx?id=',  # 动产抵押登记详情
            'annual_report': 'http://gsxt.hljaic.gov.cn/QueryYearExamineDetail.jspx?id=',  # 企业年报详情
            }

    def __init__(self, json_restore_path):
        self.json_restore_path = json_restore_path
        self.parser = HeilongjiangParser(self)
        self.img_count = 1
        if not os.path.exists(self.html_restore_path):
            os.makedirs(self.html_restore_path)

    def run(self, ent_number=0):
        """爬取的主函数
        """
        return Crawler.run(self, ent_number)
        # return super(HeilongjiangClawer, self).run(ent_number)

    def crawl_check_page(self):
        """爬取验证码页面，包括下载验证码图片以及破解验证码
        :return true or false
        """
        count = 0
        while count < 10:
            ck_code = self.crack_check_code()

            data = {'checkNo': ck_code}
            resp = self.reqst.post(self.urls['post_checkcode'], data=data)

            if resp.status_code != 200:
                logging.error("crawl post check page failed!")
                count += 1
                continue
            if resp.content[10] == 't':
                data = {'checkNo': ck_code, 'entName': self.ent_number}
                resp = self.reqst.post(self.urls['get_info_entry'], data=data)
                soup = BeautifulSoup(resp.text, "html5lib")
                div = soup.find("div", {"style": "height:500px;"})
                a = div.find("a")
                if a:
                    company_id = a["href"].split('?')[1]
                    self.company_id = company_id.split("=")[1]
                    return True
                else:
                    return False
            else:
                logging.error("crawl post check page failed!")
                count += 1
                continue
        return False

    def crack_check_code(self):
        """破解验证码
        :return 破解后的验证码
        """
        resp = self.reqst.get(self.urls['get_checkcode'])
        if resp.status_code != 200:
            logging.error('failed to get get_checkcode')
            return None

        time.sleep(random.uniform(2, 4))

        self.write_file_mutex.acquire()
        with open(self.ckcode_image_path, 'wb') as f:
            f.write(resp.content)
        try:
            ckcode = self.code_cracker.predict_result(self.ckcode_image_path)
        except Exception as e:
            logging.warn('exception occured when crack checkcode')
            ckcode = ('', '')
        finally:
            pass
        self.write_file_mutex.release()

        return ckcode[1]

    def crawl_ind_comm_pub_pages(self):
        """爬取工商公示信息
        """
        url = "%s%s" % (self.urls['ind_comm_pub_skeleton'], self.company_id)
        resp = self.reqst.get(url)
        if resp.status_code != 200:
            logging.error('failed to get ind_comm_pub_skeleton')
        self.parser.parse_ind_comm_pub_pages(resp.content)

    def crawl_ent_pub_pages(self):
        """爬取企业公示信息
        """
        url ="%s%s" % (self.urls['ent_pub_skeleton'], self.company_id)
        resp = self.reqst.get(url)
        if resp.status_code != 200:
            logging.error('failed to get ent_pub_skeleton')
        self.parser.parse_ent_pub_pages(resp.content)

    def crawl_other_dept_pub_pages(self):
        """爬取其他部门公示信息
        """
        url = "%s%s" % (self.urls['other_dept_pub_skeleton'], self.company_id)
        resp = self.reqst.get(url)
        if resp.status_code != 200:
            logging.error('failed to get other_dept_pub_skeleton')
        self.parser.crawl_other_dept_pub_pages(resp.content)

    def crawl_judical_assist_pub_pages(self):
        """爬取司法协助信息
        """
        url = "%s%s" % (self.urls['judical_assist_skeleton'], self.company_id)
        resp = self.reqst.get(url)
        if resp.status_code != 200:
            logging.error('failed to get judical_assist_skeleton')
        self.parser.parse_judical_assist_pub_pages(resp.content)


class HeilongjiangParser(Parser):
    """黑龙江工商页面的解析类
    """
    def __init__(self, crawler):
        self.crawler = crawler

    def parse_ind_comm_pub_pages(self, page):
        """解析工商公示信息-页面，在黑龙江的页面中，工商公示信息所有信息都通过一个http get返回
        """
        soup = BeautifulSoup(page, "html5lib")
        # 一类表:一个th对应一个td
        name_table_map = {
            u'基本信息': 'ind_comm_pub_reg_basic',  # 登记信息-基本信息
            u'清算信息': 'ind_comm_pub_arch_liquidation',  # 备案信息-清算信息
        }

        for table in soup.find_all('table'):
            list_table_title = table.find("th")
            if not list_table_title:
                continue
            if list_table_title.text in name_table_map.keys():
                table_name = name_table_map[list_table_title.text]
                logging.info('crawler to get %s', table_name)

                self.crawler.json_dict[table_name] = self.parse_table1(table)

        # 二类表:id_table_map为表格内容的div,表列名在内容div同级的上一张表格中，页数在同级下一张表中
        id_table_map = {
            'altDiv': 'ind_comm_pub_reg_modify',  # 登记信息-变更信息
            "memDiv": 'ind_comm_pub_arch_key_persons',  # 主要人员信息
            "childDiv": 'ind_comm_pub_arch_branch',  # 备案信息-分支机构信息
            "pledgeDiv": 'ind_comm_pub_equity_ownership_reg',  # 股权出质登记信息
            "punDiv": 'ind_comm_pub_administration_sanction',  # 行政处罚信息
            "excDiv": 'ind_comm_pub_business_exception',  # 经营异常信息
            "serillDiv": 'ind_comm_pub_serious_violate_law',  # 严重违法信息
            "spotCheckDiv": 'ind_comm_pub_spot_check',  # 抽查检查信息
            "invDiv": 'ind_comm_pub_reg_shareholder',  # 股东信息
            "mortDiv": 'ind_comm_pub_movable_property_reg',  # 动产抵押登记信息
        }
        for table_id in id_table_map.keys():
            table_name = id_table_map[table_id]
            table = soup.find("div", {"id": table_id})
            if not table:  # 如果没找到内容表，返回空列表
                self.crawler.json_dict[table_name] = []
                continue

            table_tds = table.find_all("td")
            if not table_tds:
                self.crawler.json_dict[table_name] = []  # 若表格内没有td则视为空，返回空列表
                continue

            logging.info('crawler to get %s', table_name)
            table_content = self.parse_table2(table, table_name)
            if table_name == "ind_comm_pub_reg_shareholder":  # 股东信息需调用获取详情函数，特殊处理
                if table_content[1] != "None":  # table_content[1]为tr的内容
                    for i in range(0, len(table_content[1])):
                        table_content[0][i][u'详情'] = self.get_shareholder_detail(table_content[1][i])
                self.crawler.json_dict[table_name] = table_content[0]

            elif table_name == "ind_comm_pub_movable_property_reg":  # 动产抵押登记信息需调用获取详情函数，特殊处理
                if table_content[1] != "None":
                    for i in range(0, len(table_content[1])):
                        table_content[0][i][u'详情'] = self.get_movable_property_reg_detail(table_content[1][i])
                self.crawler.json_dict[table_name] = table_content[0]

            else:
                self.crawler.json_dict[table_name] = table_content[0]

    def parse_ent_pub_pages(self, page):
        """解析企业公示信息
        """
        soup = BeautifulSoup(page, "html5lib")

        # 三类表：name_table_map为表格的table,列名和列表内容在同一张表中
        name_table_map = {
            u'股权变更信息': 'ent_pub_equity_change',
            u'变更信息': 'ent_pub_reg_modify',
            u'行政许可信息': 'ent_pub_administration_license',
            u'知识产权出质登记信息': 'ent_pub_knowledge_property',
            u'行政处罚信息': 'ent_pub_administration_sanction',
        }
        for table in soup.find_all('table'):
            list_table_title = table.find("th")
            if not list_table_title:
                continue
            if list_table_title.text in name_table_map.keys():
                table_name1 = name_table_map[list_table_title.text]
                logging.info('crawler to get %s', table_name1)
                self.crawler.json_dict[table_name1] = self.parse_table3(table)

        # 股东及出资信息
        gdDiv = soup.find("div", {"id": "gdDiv"})
        if gdDiv:
                # 股东及出资信息为有二级表头的表，需通过coarse_page_table函数处理
            logging.info('crawler to get ent_pub_shareholder_and_investment')
            table = gdDiv.find("table")
            self.crawler.json_dict['ent_pub_shareholder_and_investment'] = self.coarse_page_table(table)

        #企业年报
        qiyenianbao = soup.find("div", {"id": "qiyenianbao"})
        list_th = []  # 所有不跨列的th
        table_save_all = []

        table_ths = qiyenianbao.find_all("th")
        for th in table_ths:
            if 'colspan' in th.attrs:
                continue
            list_th.append(th.text)

        table_trs = qiyenianbao.find_all("tr")
        for tr in table_trs[2:]:
            table_content = {}  # 每行th、td对应后的表格解析内容
            list_td = []  # 每行的td
            content_tds = tr.find_all("td")
            for table_td in content_tds:
                list_td.append(table_td.text.strip())
            for i in range(0, len(list_th)):
                table_content[list_th[i]] = list_td[i]
            detail = {}
            a = qiyenianbao.find("a")
            if not a:
                table_save_all.append(table_content)
                self.crawler.json_dict['ent_pub_ent_annual_report'] = table_save_all
                continue
            m = re.search(r'id=(.*?)\"', str(a))
            args = m.group(1)
            host = self.crawler.urls['annual_report']
            url = '%s%s' % (host, args)
            rep = requests.get(url)
            soup = BeautifulSoup(rep.content, 'html5lib')

            tables = soup.find_all("table")
            for table in tables:
                table_tiiles = table.find("th")
                if table_tiiles.attrs['style'] == 'text-align:center;color:red':
                    table_tiiles = table_tiiles.parent
                    table_tiiles = table_tiiles.next_sibling.next_sibling

                name_table_map2 = [u'企业资产状况信息', u'企业基本信息', u'基本信息']
                if table_tiiles.text in name_table_map2:
                    detail[table_tiiles.text] = self.parse_table1(table)
                # 三类表
                name_table_map = [u'网站或网店信息', u'股东及出资信息', u'行政许可情况', u'对外投资信息',
                                  u'对外提供保证担保信息', u'股权变更信息', u'修改记录']
                if table_tiiles.text in name_table_map:
                    detail[table_tiiles.text] = self.parse_table3(table)

            table_content[u'详情'] = detail
            table_save_all.append(table_content)

        self.crawler.json_dict['ent_pub_ent_annual_report'] = table_save_all

    def crawl_other_dept_pub_pages(self, page):
        """解析其他部门公示信息
        """
        soup = BeautifulSoup(page, "html5lib")
        id_table_map = {
            'licenseRegDiv': 'other_dept_pub_administration_license',  # 行政许可信息
            'xzcfDiv': 'other_dept_pub_administration_sanction',  # 行政处罚信息
        }
        table_ids = id_table_map.keys()
        for table_id in table_ids:
            table_name = id_table_map[table_id]
            table = soup.find("div", {"id": table_id})

            if not table:
                self.crawler.json_dict[table_name] = []
                continue
            if table_id is 'xzcfDiv':
                table = table.next_sibling.next_sibling

            self.crawler.json_dict[table_name] = self.parse_table2(table, table_name,)[0]

    def parse_judical_assist_pub_pages(self, page):
        """司法协助信息
        """
        soup = BeautifulSoup(page, "html5lib")
        id_table_map = {
            'EquityFreezeDiv': 'judical_assist_pub_shareholder_modify',  # 股东变更信息
            'xzcfDiv': 'judical_assist_pub_equity_freeze',  # 股权冻结信息
        }
        table_ids = id_table_map.keys()

        for table_id in table_ids:
            table_name = id_table_map[table_id]
            div = soup.find("div", {"id": table_id})
            table = div.next_sibling.next_sibling

            if not table:
                self.crawler.json_dict[table_name] = []
                continue

            self.crawler.json_dict[table_name] = self.parse_table2(table, table_name,)[0]

    def parse_table1(self, table):
        """一类解析表：一个th对应一个td
        Args:
            table: 需要解析的表
        thinking:
            获取所有不跨列的th，获得所有td，将th与td一一对应
        Returns:
            table_save: 将th与td对应，得到解析好的内容，返回字典
        """
        table_ths = table.find_all("th")
        list_th = []
        for th in table_ths:
            if 'colspan' in th.attrs:
                continue
            if th.text.strip() == "":
                continue
            list_th.append(th.text.strip())

        table_tds = table.find_all("td")
        list_td = [td.text.strip() for td in table_tds]

        table_save = {}
        for i in range(0, len(list_th)):
            table_save[list_th[i]] = list_td[i]

        return table_save

    def parse_table2(self, table, table_name):
        """二类表格解析：解析表列名、内容、页数为三个同级的表格
        Args:
            table: 内容表
            table_name： 表的名字
        thinking:
            1.读取内容表同级上一张表，获得列名
            2.读取内容表同级下一张表，获得页数
                2.1若没有页数，直接通过get_td解析表格，返回需要保存的表
                2.2若只有一页，直接通过get_td解析表格，返回需要保存的表
                2.3若有多页，依次发送请求，通过get_td解析表格，返回需要保存的表
        Returns:
            [table_content, content_tr]:有详情页时返回解析的表table_content列表和每一行的内容content_tr列表
            [table_ts, "None"]:若没有详情，返回解析的表table_content列表
            ["", "None"]:若出现页面读取错误返回""和"None"
        """

        # 获得表头
        previous_table = table.previous_sibling.previous_sibling
        table_title = previous_table.find("tr")

        # 获得列名
        table_column = table_title.next_sibling.next_sibling

        # 将列名存在列表里
        table_columns = [column for column in table_column.stripped_strings]

        # 若没有翻页,直接通过get_td解析表格，返回需要保存的表
        if not table.next_sibling.next_sibling:
            table_save = self.get_td(table, table_columns)
            return [table_save, 'None']

        # 获得页数的表
        pages = table.next_sibling.next_sibling
        status1 = False  # 状态值1判断pages是否为id为invPagination的div（特例）
        status2 = False  # 状态值2判断pages是否为table,若不是table找不到页数a

        if 'id' in pages.attrs and pages.attrs['id'] == 'invPagination':
            status1 = True
        if str(pages.name) == 'table':
            status2 = True
        table_name_map = ["ind_comm_pub_arch_key_persons", "ind_comm_pub_reg_shareholder", "ind_comm_pub_movable_property_reg"]
        if status1 or status2:
            total_page = pages.find_all("a")   # 获得页数

            if int(len(total_page)) <= 1 and table_name not in table_name_map:  # 若只有一页，且没有详情也不是主要人员信息表直接解析，不发请求
                table_save = self.get_td(table, table_columns)
                return [table_save, 'None']

            elif self.crawler.urls.has_key(table_name):  # 判断翻页信息链接在urls里能否找到
                table_content = []
                content_tr = []
                for j in range(1, len(total_page)+1):
                    url = '%s%s%s%s%s' % (self.crawler.urls[table_name], "pno=", j, '&mainId=', self.crawler.company_id)
                    rep = requests.get(url)

                    soup = BeautifulSoup(rep.text.strip('"'), "html5lib")
                    table = soup.find("table")
                    if not table:  # 如出现错误，网页信息获取不到直接返回
                        return ['', 'None']

                    if table_name == "ind_comm_pub_arch_key_persons":  # 主要人员列名重复，需特殊处理
                        trs = table.find_all("tr")
                        table_save = []
                        for tr in trs:
                            content1 = {}
                            content2 = {}
                            list_td = []
                            tds = tr.find_all("td")
                            if not tds:
                                continue
                            for td in tds:
                                list_td.append(td.text.strip())
                            for i in range(0, 3):
                                content1[table_columns[i]] = list_td[i]
                            for i in range(3, 6):
                                content2[table_columns[i]] = list_td[i]
                            table_save.append(content1)
                            table_save.append(content2)
                        return [table_save, 'None']

                    table_save = self.get_td(table, table_columns)
                    tr = table.find_all("tr")
                    content_tr.extend(tr)
                    table_content.extend(table_save)
                return [table_content, content_tr]
            else:
                return ['', 'None']

        else:
            table_save = self.get_td(table, table_columns)
            return [table_save, 'None']

    def parse_table3(self, table):
        # 三类解析表：name_table_mapp为表格的table,列名和列表内容在同一张表中，返回列表
        table_ths = table.find_all("th")
        list_th = []
        trs = table.find_all("tr")
        list_tr = []
        table_all = []
        for th in table_ths:
            if 'colspan' in th.attrs:
                continue
            else:
                list_th.append(th.text)
        for tr in trs:
            list_tr.append(tr)
        for con_tr in list_tr[2:]:
            list_td = []
            table3 = {}
            content_tds = con_tr.find_all("td")
            for table_td_text in content_tds:
                list_td.append(table_td_text.text.strip())
            if not list_td:
                continue
            if not list_th:
                continue
            for i in range(0, len(list_th)):
                table3[list_th[i]] = list_td[i]
            table_all.append(table3)

        return table_all

    def get_td(self, table, table_columns):
        """内容解析表：将内容的表和列名对应
        Args:
            table: 需要解析的内容表
            table_columns:表格列名
        thinking:
             获取内容表的每一列，并将每一列做成一个字典，返回列表
        """
        table_save = []
        if not table:
            return table_save

        content_trs = table.find_all("tr")
        for content_tr in content_trs:
            content_tds = content_tr.find_all("td")
            list_td = []
            test = {}
            for content_td in content_tds:
                list_td.append(content_td.text.strip())
            if not list_td:
                continue
            for i in range(0, len(table_columns)):
                test[table_columns[i]] = list_td[i]
            table_save.append(test)

        return table_save

    def get_shareholder_detail(self, content_tr):
        """股东信息详情页面内容解析：
        Args:
            content_tr: 表格的某一行内容
        thinking:
             找出a里的目标网也id，访问并通过coarse_page_table解析，若页面访问出错，返回空字典
        return:
             detail:详情页字典
        """
        detail = {}
        if not content_tr.find("a"):
            return ""

        link = content_tr.find("a")
        m = re.search(r'id=(.\d+)', str(link))

        int1 = m.group(1)
        url1 = '%s%s' % (self.crawler.urls["shareholder_detail"], int1)
        rep1 = requests.get(url1)
        soup = BeautifulSoup(rep1.text, "html5lib")

        table = soup.find("table")
        if not table:
            return detail
        table_title1 = table.find("th").text  # 获取表头

        detail[table_title1] = self.coarse_page_table(table)

        return detail

    def get_movable_property_reg_detail(self, content_tr):
        """动产抵押信息详情页面内容解析：
        Args:
            content_tr: 表格的某一行内容
        thinking:
             找出a里的目标网也id，访问并更具不用的表格类型选择不同解析方式
        return:
             detail:详情页字典
        """
        if not content_tr.find("a"):
            return ""

        link = content_tr.find("a")
        m = re.search(r'id=(.\d+)', str(link))
        int1 = m.group(1)
        url1 = '%s%s' % (self.crawler.urls['movable_property_reg_detail'], int1)
        rep1 = requests.get(url1)
        soup = BeautifulSoup(rep1.text, "html5lib")

        name_table_map1 = [u"抵押权人概况"]
        name_table_map2 = [u'动产抵押登记信息', u'被担保债权概况']
        detail = {}
        for table in soup.find_all('table'):
            list_table_title = table.find("th")

            if list_table_title and list_table_title.text in name_table_map2:
                detail[list_table_title.text] = self.parse_table1(table)
            elif list_table_title and list_table_title.text in name_table_map1:
                detail[list_table_title.text] = self.parse_table3(table)
        table = soup.find("div", {"id": "guaDiv"})
        if table:
            detail[u"抵押物概况"] = self.parse_table2(table, 1)[0]
        return detail

    def coarse_page_table(self, table):
        # 有二级表头的表格解析：
        colspan_list = []  # 跨列的列数
        list_frist_row_not_cross_column_title_th = []  # 第一行不跨列的列名
        list_second_row_title_th = []  # 第二行的列名

        table_trs = table.find_all("tr")
        list_tr = [tr for tr in table_trs]
        table_title = list_tr[1].find_all("th")

        for title_wrap in table_title:
            if 'colspan' in title_wrap.attrs:
                for colspan in title_wrap['colspan']:
                    colspan_list.append(int(colspan))
            else:
                list_frist_row_not_cross_column_title_th.append(title_wrap.text)

        table_title = list_tr[2].find_all("th")
        for title_wrap in table_title:
            list_second_row_title_th.append(title_wrap.text)
        my_sum = 0  # 第一行跨列的总数
        for i in colspan_list:
            my_sum = my_sum + i

        total = []  # 若有多行td
        total_th = list_frist_row_not_cross_column_title_th + list_second_row_title_th  # 总列名

        for tr in table_trs[3:]:
            table_td = tr.find_all("td")
            list_td = [td.text.strip() for td in table_td]  # 表格td内容列表
            table_save = {}  # 保存的表格
            if len(list_td) == len(total_th):
                status = "1"
                for i in range(0, len(list_frist_row_not_cross_column_title_th)):
                    table_save[list_frist_row_not_cross_column_title_th[i]] = list_td[i]
                del list_td[0:len(list_frist_row_not_cross_column_title_th)]
            elif len(list_td) == my_sum:
                status = "0"
            else:
                del list_second_row_title_th[0: colspan_list[0]]
                status = "0"
                my_sum = len(list_td)

            list_test = []
            table_test = {}
            for i in range(0, my_sum):
                if list_second_row_title_th[i] == "公示日期":
                    if "认缴_公示日期" in table_test.keys():
                        table_test[u"实缴_公示日期"] = list_td[i]
                        continue
                    else:
                        table_test[u"认缴_公示日期"] = list_td[i]
                        continue
                table_test[list_second_row_title_th[i]] = list_td[i]
            list_test.append(table_test)
            table_save[u"list"] = list_test
            if status == "1":
                total.append(table_save)
            else:
                total[-1][u"list"].append(table_test)

            table_title = list_tr[2].find_all("th")
            for title_wrap in table_title:
                list_second_row_title_th.append(title_wrap.text)

        return total


class TestParser(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.crawler = HeilongjiangClawer('./enterprise_crawler/heilongjiang.json')
        self.parser = self.crawler.parser
        self.crawler.json_dict = {}
        self.crawler.ent_number = '00000'

    def test_parse_ind_comm_pub_page(self):
        with open('./enterprise_crawler/heilongjiang/ind_comm_pub.html') as f:
            page = f.read()
            self.parser.parse_ind_comm_pub_pages(page)

    def test_parse_ent_pub_skeleton(self):
        with open('./enterprise_crawler/heilongjiang/ent_pub.html') as f:
            page = f.read()
            self.parser.parse_ent_pub_pages(page)

    def test_parse_other_dept_pub_skeleton(self):
        with open('./enterprise_crawler/heilongjiang/other_dept_pub.html') as f:
            page = f.read()
            self.parser.crawl_other_dept_pub_pages(page)

    def test_parse_judical_assist_pub_skeleton(self):
        with open('./enterprise_crawler/heilongjiang/judical_assist_pub.html') as f:
            page = f.read()
            self.parser.parse_judical_assist_pub_pages(page)
"""
if __name__ == '__main__':
    from CaptchaRecognition import CaptchaRecognition
    import run
    run.config_logging()
    HeilongjiangClawer.code_cracker = CaptchaRecognition('heilongjiang')
    crawler = HeilongjiangClawer('./enterprise_crawler/heilongjiang.json')
    enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/heilongjiang.txt')
    # enterprise_list = ['230199100002865']
    for ent_number in enterprise_list:
        ent_number = ent_number.rstrip('\n')
        logging.info('############   Start to crawl enterprise with id %s   ################\n' % ent_number)
        crawler.run(ent_number=ent_number)
"""
