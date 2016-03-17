# -*- coding: utf-8 -*-

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
    u"填报时间":"license_register_time",
    u"变更事项":"license_change_item",
    u"变更时间":"license_change_time",
    u"变更前内容":"license_content_before",
    u"变更后内容":"license_content_after",
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
