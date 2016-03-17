# -*- coding: utf-8 -*-

import json
import time
import traceback
from configs import configs
from clawer_parse import tools
from configs.mappings import mappings
from clawer_parse.models import Operation
from django.conf import settings
from clawer_parse.mail import SendMail
from globalval import GlobalVal


class Parse(object):
    """解析爬虫生成的json结构，写入数据库
    """

    mappings = mappings

    def __init__(self, companies="", prinvince=""):
        self.prinvince = prinvince
        self.keys = configs.keys
        self.companies = {}
        self.is_parse = True

        for line in companies:
            company = json.loads(line)
            for key, value in company.iteritems():
                if key == "_url":
                    pass
                else:
                    if value:
                        self.companies[key] = value

    def parse_companies(self):
        for register_num in self.companies:
            company = self.companies[register_num]
            GlobalVal.count_all_plusone()
            self.is_parse = True

            try:
                self.parse_company(company, register_num)
            except:
                self.send_mail(register_num)
                self.write_log(register_num)

    def send_mail(self, register_num):
        mail = SendMail(settings.EMAIL_HOST,
                        settings.EMAIL_PORT,
                        settings.EMAIL_HOST_USER,
                        settings.EMAIL_HOST_PASSWORD,
                        ssl=True)
        title = u"%s 结构化转换错误日志" % (time.strftime("%Y-%m-%d"))
        content = u"❌  === 省份: %s === 公司ID: %s 解析错误: ❌ \n" % (self.prinvince, register_num.encode('utf-8'))
        content += traceback.format_exc()
        to_admins = [x[1] for x in settings.ADMINS]
        mail.send_text(settings.EMAIL_HOST_USER, to_admins,
                       title, content)

    def write_log(self, register_num):
        logger = settings.logger
        title = u"❌  === 省份: %s === 公司ID: %s 解析错误: ❌ " % (self.prinvince, register_num.encode('utf-8'))
        error = traceback.format_exc()
        logger.error(title + error)

    def parse_company(self, company={}, register_num=0):
        keys = self.keys
        logger = settings.logger

        self.company_result = {}

        for key in company:
            if type(company[key]) == dict:
                if key in keys and key in mappings:
                    self.parse_dict(key, company[key], mappings[key])
            elif type(company[key] == list):
                if key in keys and key in mappings and company[key] is not None:
                    self.parse_list(key, company[key], mappings[key])

            if key == "ind_comm_pub_reg_basic":
                if not company[key]:
                    logger.info(register_num + "  The basic of the company is empty")
                    self.is_parse = False
                elif type(company[key]) == dict:
                    if max(company[key].values()) == "":
                        logger.info(register_num + " The basic of the company is empty")
                        self.is_parse = False
        
        if self.company_result and self.is_parse:
            if self.company_result.get('credit_code') is None:
                self.company_result['credit_code'] = register_num
            if self.company_result.get('register_num') is None:
                credit_code = self.company_result.get('credit_code')
                self.company_result['register_num'] = credit_code

            self.conversion_type()
            self.write_to_mysql(self.company_result)
            self.company_result = {}

    def parse_dict(self, key, dict_in_company, mapping):
        for field in dict_in_company:
            if field in mapping:
                self.company_result[mapping[field]] = dict_in_company[field]

    def parse_list(self, key, list_in_company, mapping):
        keys_to_tables = configs.keys_to_tables
        special_parse_keys = configs.special_parse_keys
        name = keys_to_tables.get(key)
        parse_func = self.key_to_parse_function(key)

        if key not in special_parse_keys:
            for d in list_in_company:
                value = parse_func(d, mapping)
                if name is not None and value is not None:
                    if self.company_result.get(name) is None:
                        self.company_result[name] = []
                    self.company_result[name].append(value)
        else:
            try:
                for d in list_in_company:
                    value = parse_func(d, mapping)
                    if name is not None and value is not None:
                        self.company_result[name] = value
            except:
                pass

    def key_to_parse_function(self, key):
        keys_to_functions = {
            "ind_comm_pub_reg_shareholder": self.parse_ind_shareholder,
            "ind_comm_pub_reg_modify": self.parse_general,
            "ind_comm_pub_arch_key_persons": self.parse_general,
            "ind_comm_pub_arch_branch": self.parse_general,
            "ind_comm_pub_movable_property_reg": self.parse_general,
            "ind_comm_pub_equity_ownership_reg": self.parse_general,
            "ind_comm_pub_administration_sanction": self.parse_general,
            "ind_comm_pub_business_exception": self.parse_general,
            "ind_comm_pub_serious_violate_law": self.parse_general,
            "ind_comm_pub_spot_check": self.parse_general,
            "ent_pub_ent_annual_report": self.parse_ent_report,
            "ent_pub_shareholder_capital_contribution": self.parse_general,
            "ent_pub_equity_change": self.parse_general,
            "ent_pub_administration_license": self.parse_enter_license,
            "ent_pub_knowledge_property": self.parse_general,
            "ent_pub_administration_sanction": self.parse_general,
            "ent_pub_shareholder_modify": self.parse_general,
            "other_dept_pub_administration_license": self.parse_general,
            "other_dept_pub_administration_sanction": self.parse_general,
            "judical_assist_pub_equity_freeze": self.parse_general,
            "judical_assist_pub_shareholder_modify": self.parse_general,
        }
        return keys_to_functions.get(key, self.parse_null)

    def parse_null(self, dict_in_company, mapping):
        pass

    def parse_general(self, dict_in_company, mapping):
        result = {}
        if type(dict_in_company) == dict:
            for field, value in dict_in_company.iteritems():
                if field in mapping and value is not None:
                    result[mapping[field]] = value
        return result

    def parse_ind_shareholder(self, dict_in_company, mapping):
        result = []
        dict_inner = {}
        for field, value in dict_in_company.iteritems():
            if type(value) == dict:
                result = self.handle_ind_shareholder_detail(value, result, mapping)

        for field, value in dict_in_company.iteritems():
            if field == u"详情":
                pass
            else:
                if not result:
                    dict_inner[mapping.get(field)] = value
                    result.append(dict_inner)
                    dict_inner = {}
                else:
                    for result_dict in result:
                        result_dict[mapping.get(field)] = dict_in_company[field]
        return result

    def handle_ind_shareholder_detail(self, dict_xq, result, mapping):
        """处理ind_shareholder中"详情"
        """
        if type(dict_xq) == str:
            pass
        else:
            for key_add in dict_xq:
                if key_add:
                    list_in = dict_xq.get(key_add)
                    for dict_in in list_in:
                        result = self.handle_ind_shareholder_detail_dict(result, mapping, dict_in)
        return result

    def handle_ind_shareholder_detail_dict(self, result, mapping, dict_in):
        """处理ind_shareholder中"详情中"股东（发起人）及出资信息"的value中的字典
        """
        dict_inner = {}
        judge = False
        for key_in in dict_in:
            if key_in == u"list":
                judge = True
                for dict_fuck in dict_in[key_in]:
                    for key_fuck in dict_fuck:
                        dict_inner[mapping.get(key_fuck)] = dict_fuck[key_fuck]
                    result.append(dict_inner)
                    dict_inner = {}
        for key_in in dict_in:
            if key_in == u"list":
                pass
            elif judge is True:
                if not result:
                    dict_inner[mapping.get(key_in)] = dict_in[key_in]
                    result.append(dict_inner)
                    dict_inner = {}
                else:
                    for result_dict in result:
                        result_dict[mapping.get(key_in)] = dict_in[key_in]
            else:
                if key_in == u"认缴明细":
                    for key_fuck in dict_in[key_in]:
                        if not result:
                            dict_inner[mapping.get(key_fuck)] = dict_in[key_in][key_fuck]
                            result.append(dict_inner)
                            dict_inner = {}
                        else:
                            for result_dict in result:
                                result_dict[mapping.get(key_fuck)] = dict_in[key_in][key_fuck]
                elif key_in == u"实缴明细":
                    for key_fuck in dict_in[key_in]:
                        if not result:
                            dict_inner[mapping.get(key_fuck)] = dict_in[key_in][key_fuck]
                            result.append(dict_inner)
                            dict_inner = {}
                        else:
                            for result_dict in result:
                                result_dict[mapping.get(key_fuck)] = dict_in[key_in][key_fuck]
                else:
                    if not result:
                        dict_inner[mapping.get(key_in)] = dict_in[key_in]
                        result.append(dict_inner)
                        dict_inner = {}
                    else:
                        for result_dict in result:
                            result_dict[mapping.get(key_in)] = dict_in[key_in]
        return result

    def parse_enter_license(self, dict_in_company, mapping):
        result = []
        dict_inner = {}
        for field, value in dict_in_company.iteritems():
            if type(value) == list:
                result = self.parse_enter_license_detail(value, result, mapping)

        for field, value in dict_in_company.iteritems():
            if field == u"详情":
                pass
            else:
                if not result:
                    dict_inner[mapping.get(field)] = value
                    result.append(dict_inner)
                    dict_inner = {}
                else:
                    for result_dict in result:
                        result_dict[mapping.get(field)] = dict_in_company[field]

        return result

    def parse_enter_license_detail(self, value, result, mapping):
        dict_inner = {}

        for dict_in in value:
            for key_in, value_in in dict_in.iteritems():
                dict_inner[mapping.get(key_in)] = value_in

            result.append(dict_inner)
            dict_inner = {}

        return result

    def parse_ent_report(self, dict_in_company, mapping):
        keys_to_tables = configs.keys_to_tables
        ent_report = {}

        for key, value in dict_in_company.iteritems():
            type_value = type(value)
            if type_value == unicode or type_value == str or type_value == int:
                ent_report[mapping[key]] = value
                self.company_result[mapping[key]] = value
            else:
                year_report_id = ent_report.get('year_report_id')
                self.parse_report_details(year_report_id, value, mapping)

        name = keys_to_tables.get('ent_pub_ent_annual_report')
        if self.company_result.get(name) is None:
            self.company_result[name] = []
        self.company_result[name].append(ent_report)

        return None

    def parse_report_details(self, year_report_id, details, mapping):
        keys_to_tables = configs.keys_to_tables

        for key, value in details.iteritems():
            name = keys_to_tables.get(key)
            if name is None:
                pass
            elif type(value) == list:
                for d in value:
                    self.parse_report_details_dict(d, name, mapping[key])

            elif type(value) == dict:
                self.parse_report_details_dict(value, name, mapping[key])

    def parse_report_details_dict(self, d, name, mapping):
        report = self.parse_general(d, mapping)

        if self.company_result.get(name) is None:
            self.company_result[name] = []

        if not self.is_null(report):
            self.company_result[name].append(report)

    def is_null(self, d):
        for key, value in d.iteritems():
            if value:
                return False
        return True

    def write_to_mysql(self, data):
        operation = Operation(data)
        operation.write_db_by_dict()

    def conversion_type(self):
        to_date = tools.trans_time
        to_float = tools.trans_float
        company_result = self.company_result

        for field in company_result:
            value = company_result[field]

            if self.is_type_date(field, value):
                company_result[field] = to_date(value.encode('utf-8').strip())

            elif self.is_type_float(field, value):
                company_result[field] = to_float(value.encode('utf-8'))

            elif type(value) == list:
                for d in value:
                    for d_field in d:
                        d_value = d[d_field]

                        if self.is_type_date(d_field, d_value):
                            d[d_field] = to_date(d_value.encode('utf-8'))

                        elif self.is_type_float(d_field, d_value):
                            d[d_field] = to_float(d_value.encode('utf-8'))

    def is_type_date(self, field, value):
        type_date = configs.type_date

        return field in type_date and value is not None and type(value) == unicode

    def is_type_float(self, field, value):
        type_float = configs.type_float

        return field in type_float and value is not None and type(value) == unicode
