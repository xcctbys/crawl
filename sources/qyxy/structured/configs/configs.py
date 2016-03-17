# -*- coding: utf-8 -*-

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
    "license_change_time"
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
