# -*- coding: utf-8 -*-

import json
import time
import raven
import logging
import datetime
import traceback
from django.conf import settings


class Configs(object):
    DEFAULT_ENTER_ID = 0
    DEFAULT_VERSION = 1

    PROVINCES = (
        "anhui",
        "beijing",
        "chongqing",
        "fujian",
        "gansu",
        "guangdong",
        "guangxi",
        "guizhou",
        "hebei",
        "heilongjiang",
        "hehan",
        "hubei",
        "hunan",
        "jiangsu",
        "jilin",
        "liaoning",
        "neimenggu",
        "qinghai",
        "shaanxi",
        "shandong",
        "shanghai",
        "shanxi",
        "sichuan",
        "tianjin",
        "xinjiang",
        "yunnan",
        "zhejiang",
        "zongju",
    )

    keys = (
        "ind_comm_pub_reg_basic",
        "ind_comm_pub_reg_shareholder",
        "ind_comm_pub_reg_modify",
        "ind_comm_pub_arch_key_persons",
        "ind_comm_pub_arch_branch",
        "ind_comm_pub_arch_liquidation",
        "ind_comm_pub_movable_property_reg",
        "ind_comm_pub_equity_ownership_reg",
        "ind_comm_pub_administration_sanction",
        "ind_comm_pub_business_exception",
        "ind_comm_pub_serious_violate_law",
        "ind_comm_pub_spot_check",
        "ent_pub_ent_annual_report",
        "ent_pub_shareholder_capital_contribution",
        "ent_pub_equity_change",
        "ent_pub_administration_license",
        "ent_pub_knowledge_property",
        "ent_pub_administration_sanction",
        "ent_pub_shareholder_modify",
        "other_dept_pub_administration_license",
        "other_dept_pub_administration_sanction",
        "judical_assist_pub_equity_freeze",
        "judical_assist_pub_shareholder_modify",
    )

    special_parse_keys = (
        "ent_pub_ent_annual_report",
        "ind_comm_pub_reg_shareholder",
        "ent_pub_administration_license",
    )

    special_tables = (
        "basic",
        "industry_commerce_clear",
    )

    keys_to_tables = {}
    keys_to_tables["ind_comm_pub_reg_shareholder"] = "industry_commerce_shareholders"
    keys_to_tables["ind_comm_pub_reg_modify"] = "industry_commerce_change"
    keys_to_tables["ind_comm_pub_arch_key_persons"] = "industry_commerce_mainperson"
    keys_to_tables["ind_comm_pub_arch_branch"] = "industry_commerce_branch"
    keys_to_tables["ind_comm_pub_movable_property_reg"] = "industry_commerce_mortgage"
    keys_to_tables["ind_comm_pub_equity_ownership_reg"] = "industry_mortgage_detail_mortgagee"
    keys_to_tables["ind_comm_pub_administration_sanction"] = "industry_commerce_administrative_penalty"
    keys_to_tables["ind_comm_pub_business_exception"] = "industry_commerce_exception"
    keys_to_tables["ind_comm_pub_serious_violate_law"] = "industry_commerce_illegal"
    keys_to_tables["ind_comm_pub_spot_check"] = "industry_commerce_check"
    keys_to_tables["ent_pub_shareholder_capital_contribution"] = "enter_shareholder"
    keys_to_tables["ent_pub_equity_change"] = "enter_sharechange"
    keys_to_tables["ent_pub_administration_license"] = "enter_administrative_license"
    keys_to_tables["ent_pub_knowledge_property"] = "enter_intellectual_property_pledge"
    keys_to_tables["ent_pub_administration_sanction"] = "enter_administrative_penalty"
    keys_to_tables["ent_pub_ent_annual_report"] = "enter_annual_report"
    keys_to_tables["ent_pub_shareholder_modify"] = "enter_modification"
    keys_to_tables["other_dept_pub_administration_license"] = "other_administrative_license"
    keys_to_tables["other_dept_pub_administration_sanction"] = "other_administrative_penalty"
    keys_to_tables["judical_assist_pub_equity_freeze"] = "judicial_share_freeze"
    keys_to_tables["judical_assist_pub_shareholder_modify"] = "judicial_shareholder_change"
    keys_to_tables[u"股权变更信息"] = "year_report_sharechange"
    keys_to_tables[u"网站或网店信息"] = "year_report_online"
    keys_to_tables[u"对外投资信息"] = "year_report_investment"
    keys_to_tables[u"修改记录"] = "year_report_modification"
    keys_to_tables[u"企业资产状况信息"] = "year_report_assets"
    keys_to_tables[u"股东及出资信息"] = "year_report_shareholder"
    keys_to_tables[u"对外提供保证担保信息"] = "year_report_warrandice"
    keys_to_tables[u"企业基本信息"] = "year_report_basic"
    keys_to_tables[u"信息更正声明"] = "year_report_correct"

    type_date = (
        "check_date",
        "subscription_date",
        "paid_date",
        "modify_date",
        "sharechange_register_date",
        "penalty_publicit_date",
        "penalty_decision_date",
        "list_on_date",
        "list_out_date",
        "sharechange_publicity_date",
        "share_change_date",
        "license_end_date",
        "license_begin_date",
        "mortgage_register_date",
        "decision_date",
        "time_start",
        "time_end",
        "publicity_time",
        "license_publicity_time",
        "publicity_date",
        "paid_time",
        "subscription_time",
        "license_register_time",
        "license_change_time",
    )

    type_float = (
        "register_capital",
        "guarantee_debt_amount",
        "amount",
        "subscription_amount",
        "paid_amount",
        "subscription_money_amount",
        "paid_money_amount",
        "share_pledge_num",
        "share_ratio_before",
        "share_ratio_after",
        "share_num",
        "notice_num",
        "report_year",
        "asset_all",
        "owner_asset",
        "business_income",
        "profit",
        "main_business_income",
        "net_income",
        "tax",
        "debts",
        "staff_number",
        "main_creditor_right_amount",
        "shares_before",
        "shares_after",
    )

    mappings = {}

    mappings["ind_comm_pub_reg_basic"] = {
        u"注册资本": "register_capital",
        u"经营范围": "business_scope",
        u"注册号/统一社会信用代码": "credit_code",
        u"营业期限至": "time_end",
        u"成立日期": "time_start",
        u"注册号": "register_num",
        u"住所": "place",
        u"名称": "enter_name",
        u"核准日期": "check_date",
        u"类型": "enter_type",
        u"登记状态": "register_status",
        u"法定代表人": "corporation",
        u"登记机关": "register_gov",
        u"营业期限自": "time_start",
    }

    mappings["ind_comm_pub_reg_shareholder"] = {
        u"股东类型": "shareholder_type",
        u"股东（发起人）类型": "shareholder_type",
        u"证照/证件号码": "certificate_number",
        u"认缴出资日期": "subscription_date",
        u"认缴额（万元）": "subscription_amount",
        u"认缴出资方式": "subscription_type",
        u"认缴出资额（万元）": "subscription_money_amount",
        u"实缴出资方式": "paid_type",
        u"实缴明细": None,
        u"实缴额（万元）": "paid_amount",
        u"实缴出资日期": "paid_date",
        u"实缴出资额（万元）": "paid_money_amount",
        u"股东": "shareholder_name",
        u"股东（发起人）": "shareholder_name",
        u"证照/证件类型": "certificate_type",
    }

    mappings["ind_comm_pub_reg_modify"] = {
        u"变更事项": "modify_item",
        u"变更日期": "modify_date",
        u"变更后内容": "modify_after",
        u"变更前内容": "modify_before",
    }

    mappings["ind_comm_pub_arch_key_persons"] = {
        u"序号": "bas_id",
        u"姓名": "name",
        u"职务": "position",
    }

    mappings["ind_comm_pub_arch_branch"] = {
        u"序号": "bas_id",
        u"登记机关": "register_gov",
        u"注册号/统一社会信用代码": "enter_code",
        u"名称": "branch_name",
    }

    mappings["ind_comm_pub_arch_liquidation"] = {
        u"清算组成员": "persons",
        u"清算组负责人": "person_in_change",
    }

    mappings["ind_comm_pub_movable_property_reg"] = {
        u"状态": "status",
        u"公示日期": "publicity_time",
        u"登记日期": "sharechange_register_date",
        u"登记编号": "register_num",
        u"被担保债权数额": "guarantee_debt_amount",
        u"序号": "bas_id",
        u"登记机关": "register_gov",
    }

    mappings["ind_comm_pub_equity_ownership_reg"] = {
        u"登记编号": "register_num",
        u"质权人": "mortgagee_name",
        u"证照/证件号码": "pledgor_certificate_code",
        u"出质股权数额": "share_pledge_num",
        u"公示日期": "publicity_time",
        u"状态": "status",
        u"股权出质设立登记日期": None,
        u"出质人": "pledgor",
        u"变化情况": "change_detail",
    }

    mappings["ind_comm_pub_administration_sanction"] = {
        u"行政处罚内容": "penalty_content",
        u"公示日期": "penalty_publicit_date",
        u"作出行政处罚决定机关名称": "penalty_decision_gov",
        u"违法行为类型": "illegal_type",
        u"作出行政处罚决定日期": "penalty_decision_date",
        u"详情": "detail",
        u"行政处罚决定书文号": "penalty_decision_num",
        u"序号": None,
    }

    mappings["ind_comm_pub_business_exception"] = {
        u"公示日期": None,
        u"移出经营异常名录原因": "list_out_reason",
        u"作出决定机关": "list_gov",
        u"列入经营异常名录原因": "list_on_reason",
        u"列入日期": "list_on_date",
        u"移出日期": "list_out_date",
        u"序号": None,
    }

    mappings["ind_comm_pub_serious_violate_law"] = {
        u"移出严重违法企业名单原因": "list_out_reason",
        u"列入严重违法企业名单原因": "list_on_reason",
        u"作出决定机关": "decision_gov",
        u"列入日期": "list_on_date",
        u"移出日期": "list_out_date",
    }

    mappings["ind_comm_pub_spot_check"] = {
        u"检查实施机关": "check_gov",
        u"公示日期": "check_date",
        u"结果": "check_result",
        u"类型": "check_type",
        u"日期": "check_date",
    }

    mappings["ent_pub_shareholder_capital_contribution"] = {
        u"认缴出资日期": "subscription_date",
        u"认缴额（万元）": "subscription_amount",
        u"认缴出资方式": "subscription_type",
        u"认缴出资额（万元）": "subscription_money_amount",
        u"公示日期": "publicity_time",
        u"实缴额（万元）": "paid_amount",
        u"股东（发起人）": "shareholder_name",
        u"股东": "shareholder_name",
        u"实缴明细": None,
        u"认缴明细": None,
        u"实缴出资日期": "paid_date",
        u"实缴出资方式": "paid_type",
        u"实缴出资额（万元）": "paid_money_amount",
    }

    mappings["ent_pub_equity_change"] = {
        u"变更前股权比例": "share_ratio_before",
        u"公示日期": "sharechange_publicity_date",
        u"登记日期": "sharechange_register_date",
        u"股权变更日期": "share_change_date",
        u"变更后股权比例": "share_ratio_after",
        u"序号": None,
        u"股东": "shareholder",
    }

    mappings["ent_pub_administration_license"] = {
        u"状态": "license_status",
        u"有效期至": "license_end_date",
        u"公示日期": "license_publicity_time",
        u"许可内容": "license_content",
        u"许可文件名称": "license_filename",
        u"许可文件编号": "license_num",
        u"详情": "license_detail",
        u"序号": None,
        u"许可机关": "license_authority",
        u"有效期自": "license_begien_date",
        u"公示时间": "license_publicity_time",
        u"填报时间": "license_register_time",
        u"变更事项": "license_change_item",
        u"变更时间": "license_change_time",
        u"变更前内容": "license_content_before",
        u"变更后内容": "license_content_after",
    }

    mappings["ent_pub_knowledge_property"] = {
        u"状态": "property_status",
        u"公示日期": "property_pledge_publicity_time",
        u"注册号": "credit_code",
        u"质权登记期限": "mortgage_register_date",
        u"出质人名称": "pledgor_name",
        u"变化情况": "property_pledge_change",
        u"质权人名称": "mortgagee_name",
        u"名称": "enter_name",
        u"序号": "property_type",
        u"种类": None,
    }

    mappings["ent_pub_administration_sanction"] = {
        u"行政处罚内容": "administrative_penalty_content",
        u"公示日期": "penalty_publicity_time",
        u"作出行政处罚决定机关名称": "decision_gov",
        u"违法行为类型": "illegal_type",
        u"作出行政处罚决定日期": "decision_date",
        u"行政处罚决定书文号": "penalty_decision_num",
        u"序号": None,
        u"备注": "penalty_comment",
        u"详情": "detail",
    }

    mappings["other_dept_pub_administration_license"] = {
        u"状态": "license_status",
        u"有效期至": "license_end_date",
        u"许可内容": "license_content",
        u"许可文件名称": "license_filename",
        u"许可文件编号": "license_file_num",
        u"详情": "license_detail",
        u"序号": None,
        u"许可机关": "license_authority_gov",
        u"有效期自": "license_begin_date",
    }

    mappings["other_dept_pub_administration_sanction"] = {
        u"行政处罚内容": "administrative_penalty_content",
        u"作出行政处罚决定机关名称": "decision_gov",
        u"违法行为类型": "illegal_type",
        u"作出行政处罚决定日期": "decision_date",
        u"行政处罚决定书文号": "penalty_decision_num",
        u"序号": None,
        u"详情": "detail",
    }

    mappings["judical_assist_pub_equity_freeze"] = {
        u"状态": "freeze_status",
        u"被执行人": "been_excute_person",
        u"股权数额": "share_num",
        u"详情": "freeze_detail",
        u"序号": None,
        u"执行法院": "excute_court",
        u"协助公示通知书文号": "notice_num",
    }

    mappings["judical_assist_pub_shareholder_modify"] = {
        u"被执行人": "been_excute_name",
        u"股权数额": "share_num",
        u"详情": "detail",
        u"序号": None,
        u"执行法院": "excute_court",
        u"受让人": "assignee",
    }

    mappings["ent_pub_ent_annual_report"] = {
        u"序号": "year_report_id",
        u"报送年度": "report_year",
        u"年报日期": "publicity_date",
        u"网站或网店信息": {
            u"网址": "enter_url",
            u"名称": "enter_name",
            u"类型": "online_type"
        },
        u"对外投资信息": {
            u"注册号/统一社会信用代码": "enter_code",
            u"投资设立企业或购买股权企业名称": "invest_enter_name"
        },
        u"修改记录": {
            u"修改前": "modify_before",
            u"修改事项": "modify_item",
            u"修改后": "modify_after",
            u"修改日期": "modify_date"
        },
        u"企业资产状况信息": {
            u"所有者权益合计": "owner_asset",
            u"营业总收入": "business_income",
            u"营业总收入中主营业务收入": "main_business_income",
            u"负债总额": "debts",
            u"利润总额": "profit",
            u"净利润": "net_income",
            u"资产总额": "asset_all",
            u"纳税总额": "tax"
        },
        u"股权变更信息": {
            u"股权变更日期": "",
            u"变更前股权比例": "shares_before",
            u"变更后股权比例": "shares_after",
            u"股东": "shareholder"
        },
        u"对外提供保证担保信息": {
            u"履行债务的期限": "fullfill_debt_duration",
            u"保证的方式": "guarantee_type",
            u"债务人": "debtor",
            u"保证的期间": "guarantee_duration",
            u"主债权数额": "main_creditor_right_amount",
            u"主债权种类": "main_creditor_right",
            u"债权人": "creditor",
            u"保证担保的范围": "warrandice_scope"
        },
        u"企业基本信息": {
            u"企业经营状态": "status",
            u"企业名称": "enter_name",
            u"企业电子邮箱": "email",
            u"从业人数": "staff_number",
            u"企业联系电话": "enter_phone",
            u"企业是否有投资信息或购买其他公司股权": "is_invest",
            u"企业通信地址": "enter_place",
            u"是否有网站或网店": "web_onlinestore",
            u"邮政编码": "zipcode",
            u"有限责任公司本年度是否发生股东股权转让": "shareholder_change",
            u"注册号/统一社会信用代码": "credit_code",
            u"登记编号": "register_num",
            u"是否有对外担保信息": "is_warrandice"
        },
        u"股东（发起人）及出资信息": {
            u"认缴出资方式": "subscription_type",
            u"认缴出资额（万元）": "subscription_money_amount",
            u"出资时间": "paid_time",
            u"认缴出资时间": "subscription_time",
            u"实缴出资额（万元）": "paid_money_amount",
            u"出资方式": "paid_type",
            u"股东": "shareholder"
        },
        u"股东及出资信息": {
            u"认缴出资方式": "subscription_type",
            u"认缴出资额（万元）": "subscription_money_amount",
            u"出资时间": "paid_time",
            u"认缴出资时间": "subscription_time",
            u"实缴出资额（万元）": "paid_money_amount",
            u"出资方式": "paid_type",
            u"股东": "shareholder"
        },
        u"发布日期": "publicity_date",
    }

    mappings["ent_pub_shareholder_modify"] = {
    }


class Parse(object):
    """解析爬虫生成的json结构，写入数据库
    """

    mappings = Configs.mappings

    def __init__(self, companies="", prinvince=""):
        self.prinvince = prinvince
        self.keys = Configs.keys
        self.companies = {}

        for line in companies:
            company = json.loads(line)
            for key, value in company.iteritems():
                if self.passed_validation(key, value):
                    self.companies[key] = value

    def passed_validation(self, key, value):
        passed = True

        if key == "_url":
            passed = False
        elif not value:
            passed = False
        else:
            is_null = self.is_data_null(value)
            passed = not is_null

        return passed

    def is_data_null(self, data):
        null = False

        if not data:
            null = True

        null = True
        for key, value in data.iteritems():
            if value:
                null = False
                break

        return null

    def parse_companies(self):
        for register_num in self.companies:
            company = self.companies[register_num]

            try:
                if len(str(register_num)) >= 15:
                    self.parse_company(company, register_num)
            except:
                self.send_sentry()
                self.write_log(register_num)

    def send_sentry(self):
        if settings.RAVEN_CONFIG and settings.RAVEN_CONFIG['dsn']:
            if not self.sentry_client:
                self.sentry_client = raven.Client(dsn=settings.RAVEN_CONFIG['dsn'])

            self.sentry_client.captureException()

    def write_log(self, register_num):
        logger = logging.getLogger(__name__)
        title = (u"❌  === 省份: %s === 公司ID: %s 解析错误: ❌ "
                 % (self.prinvince, register_num.encode('utf-8')))
        error = traceback.format_exc()
        logger.error(title + error)

    def parse_company(self, company={}, register_num=0):
        keys = self.keys
        mappings = self.mappings
        self.company_result = {}

        for key in company:
            if type(company[key]) == dict:
                if key in keys and key in mappings:
                    self.parse_dict(company[key], mappings[key])
            elif type(company[key] == list):
                if key in keys and key in mappings and company[key] is not None:
                    self.parse_list(key, company[key], mappings[key])

        self.company_result["register_num"] = register_num
        self.conversion_type()
        self.write_to_mysql(self.company_result)
        self.company_result = {}

    def parse_dict(self, dict_in_company, mapping):
        for field in dict_in_company:
            if field in mapping:
                self.company_result[mapping[field]] = dict_in_company[field]

    def parse_list(self, key, list_in_company, mapping):
        keys_to_tables = Configs.keys_to_tables
        special_parse_keys = Configs.special_parse_keys
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
        keys_to_tables = Configs.keys_to_tables
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
        keys_to_tables = Configs.keys_to_tables

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
        if not self.is_basic_null(data):
            from enterprise.models import Operation
            operation = Operation(data)
            operation.write_db_by_dict()
        else:
            pass

    def is_basic_null(self, data):
        return False

    def conversion_type(self):
        company_result = self.company_result

        for field in company_result:
            value = company_result[field]

            if self.is_type_date(field, value):
                company_result[field] = trans_time(value.encode('utf-8').strip())

            elif self.is_type_float(field, value):
                company_result[field] = trans_float(value.encode('utf-8'))

            elif type(value) == list:
                for d in value:
                    for d_field in d:
                        d_value = d[d_field]

                        if self.is_type_date(d_field, d_value):
                            d[d_field] = trans_time(d_value.encode('utf-8'))

                        elif self.is_type_float(d_field, d_value):
                            d[d_field] = trans_float(d_value.encode('utf-8'))

    def is_type_date(self, field, value):
        type_date = Configs.type_date

        return field in type_date and value is not None and type(value) == unicode

    def is_type_float(self, field, value):
        type_float = Configs.type_float

        return field in type_float and value is not None and type(value) == unicode


def trans_time(s):
    time_format = [
        '%Y年%m月%d日',
        '%Y-%m-%d',
        '%Y.%m.%d',
        '%Y-%m-%d %l:%M:%S',
        '%Y-%m-%d %H:%M:%S'
    ]

    for time_in in time_format:
        try:
            a = time.strptime(s, time_in)
            time1 = datetime.datetime(*a[:6])
            return time1
        except:
            pass
    return None


def trans_float(s):
    res = []
    for c in list(s):
        if '0' <= c and c <= '9' or c == '.':
            res.append(c)
    if res == []:
        return 0.0
    else:
        return float("".join(res))
