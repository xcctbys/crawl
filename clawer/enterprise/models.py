# -*- coding: utf-8 -*-

import logging
from django.db import models
from django.utils import timezone
from enterprise.structured import Configs


class Province(object):
    (ANHUI,
     BEIJING,
     CHONGQING,
     FUJIAN,
     GANSU,
     GUANGDONG,
     GUANGXI,
     GUIZHOU,
     HAINAN,
     HEBEI,
     HEILONGJIANG,
     HENAN,
     HUBEI,
     HUNAN,
     JIANGSU,
     JIANGXI,
     JILIN,
     LIAONING,
     NEIMENGGU,
     NINGXIA,
     QINGHAI,
     SHAANXI,
     SHANDONG,
     SHANGHAI,
     SHANXI,
     SICHUAN,
     TIANJIN,
     XINJIANG,
     YUNNAN,
     ZHEJIANG,
     ZONGJU,
     XIZANG,) = range(1, 33)

    choices = (
        (ANHUI, u"安徽"),
        (BEIJING, u"北京"),
        (CHONGQING, u"重庆"),
        (FUJIAN, u"福建"),
        (GANSU, u"甘肃"),
        (GUANGDONG, u"广东"),
        (GUANGXI, u"广西"),
        (GUIZHOU, u"贵州"),
        (HAINAN, u"海南"),
        (HEBEI, u"河北"),
        (HEILONGJIANG, u"黑龙江"),
        (HENAN, u"河南"),
        (HUBEI, u"湖北"),
        (HUNAN, u"湖南"),
        (JIANGSU, u"江苏"),
        (JIANGXI, u"江西"),
        (JILIN, u"吉林"),
        (LIAONING, u"辽宁"),
        (NEIMENGGU, u"内蒙古"),
        (NINGXIA, u"宁夏"),
        (QINGHAI, u"青海"),
        (SHAANXI, u"陕西"),
        (SHANDONG, u"山东"),
        (SHANGHAI, u"上海"),
        (SHANXI, u"山西"),
        (SICHUAN, u"四川"),
        (TIANJIN, u"天津"),
        (XINJIANG, u"新疆"),
        (YUNNAN, u"云南"),
        (ZHEJIANG, u'浙江'),
        (ZONGJU, u"总局"),
        (XIZANG, u"西藏"),
    )

    @classmethod
    def to_name(cls, province):
        for item in cls.choices:
            if item[0] == province:
                return item[1]

        return None

    @classmethod
    def to_id(cls, name):
        for item in cls.choices:
            if item[1] == name:
                return item[0]

        return None


class Enterprise(models.Model):
    name = models.CharField(max_length=128)
    province = models.IntegerField(max_length=128, choices=Province.choices)
    register_no = models.CharField(max_length=128)
    add_datetime = models.DateTimeField(auto_now_add=True)

    def as_json(self):
        result = {
            "id": self.id,
            "name": self.name,
            "province": self.province,
            "province_name": Province.to_name(self.province),
            "register_no": self.register_no,
            "add_datetime": self.add_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return result


class Operation(object):
    def __init__(self, data):
        self.data = data
        self.register_num = data.get('register_num')
        self.models = self.get_structured_models()

    def write_db_by_dict(self):
        models = self.models
        logger = logging.getLogger(__name__)

        if self.is_company_in_db():
            logger.info("Add " + self.register_num.encode('utf-8'))
            for model in models:
                self.insert(model)
        else:
            logger.info("Update " + self.register_num.encode('utf-8'))
            for model in models:
                self.update(model)

    def is_company_in_db(self):
        register_num = self.register_num

        query = Basic.objects.filter(register_num=register_num)

        return not query

    def insert(self, model):
        data = self.data
        special_tables = Configs.special_tables
        fields = model._meta.get_all_field_names()
        name = model._meta.db_table
        register_num = self.register_num

        try:
            enter_id = Basic.objects.get(register_num=register_num).id
        except:
            enter_id = Configs.DEFAULT_ENTER_ID

        try:
            version = Basic.objects.get(register_num=register_num).version
        except:
            version = Configs.DEFAULT_VERSION

        if name in special_tables:
            self.insert_one_row(model, name, fields, enter_id, version, {})
        elif name in data:
            for row in data[name]:
                self.insert_one_row(model, name, fields, enter_id, version, row)

    def update(self, model):
        data = self.data
        basic = Configs.special_tables[0]
        fields = model._meta.get_all_field_names()
        name = model._meta.db_table
        register_num = data.get('register_num')
        version = Basic.objects.get(register_num=register_num).version
        enter_id = Basic.objects.get(register_num=register_num).id

        if name == basic:
            query = Basic.objects.get(register_num=register_num)
            for field in fields:
                value = data.get(field)
                if value is not None:
                    setattr(query, field, value)
            query.version = version + 1
            query.timestamp = timezone.now()
            query.save()

        else:
            self.update_rows(model, name, fields, enter_id, version)

    def update_rows(self, model, name, fields, enter_id, version):
        data = self.data
        clear = Configs.special_tables[1]

        model.objects.filter(enter_id=enter_id,
                             invalidation=False).update(invalidation=True)

        if data.get(name) is not None:
            for row in data[name]:
                self.insert_one_row(model, name, fields, enter_id, version, row)
        elif name == clear:
            self.insert_one_row(model, name, fields, enter_id, version, {})
        else:
            pass

    def insert_one_row(self, model, name, fields, enter_id, version, row):
        data = self.data
        query = model()
        is_all_fields_null = True

        for field in fields:
            if row is not None:
                value = row.get(field) or data.get(field)
            else:
                value = data.get(field)

            if value is not None and value != u"":
                setattr(query, field, value)

                if field != "year_report_id" and field != "enter_id":
                    is_all_fields_null = False

        query.enter_id = enter_id
        query.version = version
        query.invalidation = False
        if not is_all_fields_null:
            query.save()
        else:
            del query

    def get_structured_models(self):
        models = (
            Basic,
            IndustryCommerceAdminiPenalty,
            IndustryCommerceBranch,
            IndustryCommerceChange,
            IndustryCommerceCheck,
            IndustryCommerceClear,
            IndustryCommerceDetailGuarantee,
            IndustryCommerceException,
            IndustryCommerceIllegal,
            IndustryCommerceMainperson,
            IndustryCommerceMortgage,
            IndustryCommerceMortgageChange,
            IndustryCommerceMortgageGuarantee,
            IndustryCommerceMortgageGuaranty,
            IndustryCommerceRevoke,
            IndustryCommerceShareholders,
            IndustryCommerceSharepledge,
            IndustryMortgageDetailMortgagee,
            EnterAdministrativeLicense,
            EnterAdministrativePenalty,
            EnterAnnualReport,
            EnterIntellectualPropertyPledge,
            EnterModification,
            EnterSharechange,
            EnterShareholder,
            JudicialShareFreeze,
            JudicialShareholderChange,
            OtherAdministrativeChange,
            OtherAdministrativeLicense,
            OtherAdministrativePenalty,
            OtherProductionSecurity,
            YearReportAssets,
            YearReportBasic,
            YearReportCorrect,
            YearReportInvestment,
            YearReportModification,
            YearReportOnline,
            YearReportSharechange,
            YearReportShareholder,
            YearReportWarrandice,
        )

        return models


class Basic(models.Model):
    """公司基本类
    """

    credit_code = models.CharField(max_length=50, null=True, blank=True)
    enter_name = models.CharField(max_length=50, null=True, blank=True)
    enter_type = models.CharField(max_length=100, null=True, blank=True)
    corporation = models.CharField(max_length=30, null=True, blank=True)
    register_capital = models.FloatField(null=True)
    establish_date = models.DateField(null=True)
    place = models.CharField(max_length=100, null=True, blank=True)
    time_start = models.DateField(null=True)
    time_end = models.DateField(null=True)
    business_scope = models.TextField(null=True)
    register_gov = models.CharField(max_length=50, null=True, blank=True)
    check_date = models.DateField(null=True)
    register_status = models.CharField(max_length=50, null=True, blank=True)
    register_num = models.CharField(max_length=50, null=True, blank=True)
    version = models.IntegerField(default=1)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "basic"


class IndustryCommerceAdminiPenalty(models.Model):
    """工商-行政处罚
    """

    penalty_decision_num = models.CharField(max_length=30, null=True, blank=True)
    illegal_type = models.CharField(max_length=100, null=True, blank=True)
    penalty_content = models.CharField(max_length=1024, null=True, blank=True)
    penalty_decision_gov = models.CharField(max_length=50, null=True, blank=True)
    penalty_decision_date = models.DateField(null=True)
    detail = models.TextField(null=True, blank=True)
    penalty_register_date = models.DateField(null=True)
    enter_name = models.CharField(max_length=50, null=True, blank=True)
    creidit_code = models.CharField(max_length=20, null=True, blank=True)
    corporation = models.CharField(max_length=30, null=True, blank=True)
    penalty_publicity_time = models.DateField(null=True)
    enter_id = models.CharField(max_length=30, null=True, blank=True)
    bas_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "industry_commerce_admini_penalty"


class IndustryCommerceBranch(models.Model):
    """工商-分支机构
    """

    enter_code = models.CharField(max_length=100, null=True, blank=True)
    branch_name = models.CharField(max_length=100, null=True, blank=True)
    register_gov = models.CharField(max_length=50, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "industry_commerce_branch"


class IndustryCommerceChange(models.Model):
    """工商-变更
    """

    modify_item = models.TextField(null=True, blank=True)
    modify_before = models.TextField(null=True, blank=True)
    modify_after = models.TextField(max_length=50, null=True, blank=True)
    modify_date = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "industry_commerce_change"


class IndustryCommerceCheck(models.Model):
    """工商-抽查检查
    """

    check_gov = models.CharField(max_length=50, null=True, blank=True)
    check_type = models.CharField(max_length=20, null=True, blank=True)
    check_date = models.DateField(null=True)
    check_result = models.CharField(max_length=50, null=True, blank=True)
    check_comment = models.CharField(max_length=50, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "industry_commerce_check"


class IndustryCommerceClear(models.Model):
    """工商-清算
    """

    person_in_charge = models.CharField(max_length=30, null=True, blank=True)
    persons = models.CharField(max_length=100, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "industry_commerce_clear"


class IndustryCommerceDetailGuarantee(models.Model):
    """工商-动产抵押-详情-动产抵押
    """

    register_code = models.CharField(max_length=20, null=True, blank=True)
    sharechange_register_date = models.DateField(null=True)
    register_gov = models.CharField(max_length=50, null=True, blank=True)
    register_id = models.CharField(max_length=20, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "industry_commerce_detail_guarantee"


class IndustryCommerceException(models.Model):
    """工商-经营异常
    """

    list_on_reason = models.CharField(max_length=100, null=True, blank=True)
    list_on_date = models.DateField(null=True)
    list_out_reason = models.CharField(max_length=100, null=True, blank=True)
    list_out_date = models.DateField(null=True)
    list_gov = models.CharField(max_length=50, null=True, blank=True)
    list_on_gov = models.CharField(max_length=50, null=True, blank=True)
    list_out_gov = models.CharField(max_length=50, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "industry_commerce_exception"


class IndustryCommerceIllegal(models.Model):
    """工商-严重违法
    """

    list_on_reason = models.CharField(max_length=100, null=True, blank=True)
    list_on_date = models.DateField(null=True)
    list_out_reason = models.CharField(max_length=100, null=True, blank=True)
    list_out_date = models.DateField(max_length=100, null=True, blank=True)
    decision_gov = models.CharField(max_length=30, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "industry_commerce_illegal"


class IndustryCommerceMainperson(models.Model):
    """工商-主要人员
    """

    name = models.CharField(max_length=30, null=True, blank=True)
    position = models.CharField(max_length=20, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "industry_commerce_mainperson"


class IndustryCommerceMortgage(models.Model):
    """工商-动产抵押登记
    """

    register_num = models.CharField(max_length=50, null=True, blank=True)
    sharechange_register_date = models.DateField(null=True)
    register_gov = models.CharField(max_length=50, null=True, blank=True)
    guarantee_debt_amount = models.FloatField(null=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    publicity_time = models.DateField(null=True)
    details = models.TextField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "industry_commerce_mortgage"


class IndustryCommerceMortgageChange(models.Model):
    """工商-抵押-详情-变更
    """

    modify_date = models.DateField(null=True)
    modify_content = models.TextField(null=True)
    register_id = models.CharField(max_length=20, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "industry_commerce_mortgage_change"


class IndustryCommerceMortgageGuarantee(models.Model):
    """工商-抵押-详情-抵押权人
    """

    check_type = models.CharField(max_length=20, null=True, blank=True)
    amount = models.FloatField(null=True)
    guarantee_scope = models.CharField(max_length=100, null=True, blank=True)
    debtor_duration = models.CharField(max_length=20, null=True, blank=True)
    comment = models.CharField(max_length=100, null=True, blank=True)
    register_id = models.CharField(max_length=20, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "industry_commerce_cortgage_guarantee"


class IndustryCommerceMortgageGuaranty(models.Model):
    """工商-抵押-详情-抵押物
    """

    name = models.CharField(max_length=30, null=True, blank=True)
    ownership = models.CharField(max_length=30, null=True, blank=True)
    details = models.TextField(null=True)
    coments = models.CharField(max_length=100, null=True, blank=True)
    register_id = models.CharField(max_length=20, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "industry_commerce_mortgage_guaranty"


class IndustryCommerceRevoke(models.Model):
    """工商-撤销
    """

    revoke_item = models.CharField(max_length=30, null=True, blank=True)
    content_before_revoke = models.CharField(max_length=50, null=True, blank=True)
    content_after_revoke = models.CharField(max_length=50, null=True, blank=True)
    revoke_date = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "industry_commerce_revoke"


class IndustryCommerceShareholders(models.Model):
    """工商-股东
    """

    shareholder_type = models.CharField(max_length=20, null=True, blank=True)
    shareholder_name = models.CharField(max_length=200, null=True, blank=True)
    certificate_type = models.CharField(max_length=20, null=True, blank=True)
    certificate_number = models.CharField(max_length=50, null=True, blank=True)
    subscription_amount = models.FloatField(null=True)
    paid_amount = models.FloatField(null=True)
    subscription_type = models.CharField(max_length=100, null=True, blank=True)
    subscription_date = models.DateField(null=True)
    subscription_money_amount = models.FloatField(null=True)
    paid_type = models.CharField(max_length=100, null=True, blank=True)
    paid_money_amount = models.FloatField(null=True)
    paid_date = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "industry_commerce_shareholders"


class IndustryCommerceSharepledge(models.Model):
    """
    """

    register_num = models.CharField(max_length=50, null=True, blank=True)
    pledgor = models.CharField(max_length=30, null=True, blank=True)
    pledgor_certificate_code = models.CharField(max_length=20, null=True, blank=True)
    share_pledge_num = models.FloatField(null=True)
    mortgagee = models.CharField(max_length=30, null=True, blank=True)
    mortgagee_certificate_code = models.CharField(max_length=20, null=True, blank=True)
    sharechange_register_date = models.DateField(null=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    change_detail = models.CharField(max_length=100, null=True, blank=True)
    publicity_time = models.DateField(null=True)
    modify_date = models.DateField(null=True)
    modify_content = models.TextField(null=True)
    register_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "industry_commerce_sharepledge"


class IndustryMortgageDetailMortgagee(models.Model):
    """工商-抵押-详情-抵押权人
    """

    mortgagee_name = models.CharField(max_length=30, null=True, blank=True)
    mortgagee_certificate_type = models.CharField(max_length=20, null=True, blank=True)
    pledgor_certificate_code = models.CharField(max_length=20, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "industry_mortgage_detail_mortgagee"


class EnterAdministrativeLicense(models.Model):
    """企业-行政许可
    """

    license_num = models.CharField(max_length=100, null=True, blank=True)
    license_filename = models.CharField(max_length=50, null=True, blank=True)
    license_begin_date = models.DateField(null=True)
    license_end_date = models.DateField(null=True)
    license_authority = models.CharField(max_length=30, null=True, blank=True)
    license_content = models.TextField(null=True, blank=True)
    license_status = models.TextField(null=True, blank=True)
    license_detail = models.TextField(null=True, blank=True)
    license_register_time = models.DateField(null=True)
    license_publicity_time = models.DateField(null=True)
    license_change_item = models.CharField(max_length=20, null=True, blank=True)
    license_change_time = models.DateField(null=True)
    license_content_before = models.CharField(max_length=50, null=True, blank=True)
    license_content_after = models.CharField(max_length=50, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "enter_administrative_license"


class EnterAdministrativePenalty(models.Model):
    """企业-行政处罚
    """

    penalty_decision_num = models.CharField(max_length=30, null=True, blank=True)
    illegal_type = models.CharField(max_length=100, null=True, blank=True)
    administrative_penalty_content = models.CharField(max_length=30, null=True, blank=True)
    decision_gov = models.CharField(max_length=30, null=True, blank=True)
    decision_date = models.DateField(null=True)
    penalty_comment = models.CharField(max_length=1024, null=True, blank=True)
    penalty_publicit_date = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "enter_administrative_penalty"


class EnterAnnualReport(models.Model):
    """企业年报
    """

    report_year = models.IntegerField(null=True)
    publicity_date = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "enter_annual_report"


class EnterIntellectualPropertyPledge(models.Model):
    """企业-知识产权出质
    """

    credit_code = models.CharField(max_length=20, null=True, blank=True)
    enter_name = models.CharField(max_length=50, null=True, blank=True)
    property_type = models.CharField(max_length=30, null=True, blank=True)
    pledgor_name = models.CharField(max_length=30, null=True, blank=True)
    mortgagee_name = models.CharField(max_length=30, null=True, blank=True)
    mortgage_register_date = models.DateField(null=True)
    property_status = models.CharField(max_length=40, null=True, blank=True)
    property_pledge_change = models.CharField(max_length=40, null=True, blank=True)
    property_pledge_register_gov = models.CharField(max_length=30, null=True, blank=True)
    property_pledge_register_date = models.DateField(null=True)
    property_pledge_publicity_time = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "enter_intellectual_property_pledge"


class EnterModification(models.Model):
    """企业-变更
    """

    modify_item = models.TextField(null=True, blank=True)
    modify_before = models.CharField(max_length=50, null=True, blank=True)
    modify_after = models.CharField(max_length=50, null=True, blank=True)
    modify_date = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "enter_modification"


class EnterSharechange(models.Model):
    """企业-股权变更
    """

    shareholder = models.CharField(max_length=100, null=True, blank=True)
    share_ratio_before = models.FloatField(null=True)
    share_ratio_after = models.FloatField(null=True)
    share_change_date = models.DateField(null=True)
    sharechange_register_date = models.DateField(null=True)
    sharechange_publicity_date = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "enter_sharechange"


class EnterShareholder(models.Model):
    """企业-股东及出资
    """

    shareholder_name = models.CharField(max_length=200, null=True, blank=True)
    subscription_amount = models.FloatField(null=True)
    paid_amount = models.FloatField(null=True)
    subscription_type = models.CharField(max_length=100, null=True, blank=True)
    subscription_date = models.DateField(null=True)
    subscription_money_amount = models.FloatField(null=True)
    paid_type = models.CharField(max_length=100, null=True, blank=True)
    paid_money_amount = models.FloatField(null=True)
    paid_date = models.DateField(null=True)
    shareholder_type = models.CharField(max_length=20, null=True, blank=True)
    subscription_publicity_time = models.DateField(null=True)
    paid_publicity_time = models.DateField(null=True)
    publicity_time = models.DateField(null=True)
    modify_time = models.DateField(null=True)
    detals = models.CharField(max_length=256, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "enter_shareholder"


class JudicialShareFreeze(models.Model):
    """司法股权冻结
    """

    been_excute_person = models.CharField(max_length=30, null=True, blank=True)
    share_num = models.IntegerField(null=True)
    excute_court = models.CharField(max_length=30, null=True, blank=True)
    notice_num = models.CharField(max_length=30, null=True, blank=True)
    freeze_status = models.CharField(max_length=30, null=True, blank=True)
    freeze_detail = models.TextField(null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "judicial_share_freeze"


class JudicialShareholderChange(models.Model):
    """司法-司法股东变更登记
    """

    been_excute_name = models.CharField(max_length=30, null=True, blank=True)
    share_num = models.IntegerField(null=True)
    excute_court = models.CharField(max_length=30, null=True, blank=True)
    assignee = models.CharField(max_length=30, null=True, blank=True)
    detail = models.TextField(null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "judicial_shareholder_change"


class OtherAdministrativeChange(models.Model):
    """其他-行政许可变更
    """

    administrative_change_item = models.CharField(max_length=30, null=True, blank=True)
    administrative_change_tme = models.DateField(null=True)
    administrative_change_before = models.CharField(max_length=50, null=True, blank=True)
    administrative_change_after = models.CharField(max_length=50, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "other_administrative_change"


class OtherAdministrativeLicense(models.Model):
    """其他部门-行政许可
    """

    license_file_num = models.CharField(max_length=30, null=True, blank=True)
    license_filename = models.CharField(max_length=50, null=True, blank=True)
    license_begin_date = models.DateField(null=True)
    license_end_date = models.DateField(null=True)
    license_content = models.TextField(null=True, blank=True)
    license_authority_gov = models.CharField(max_length=50, null=True, blank=True)
    license_status = models.TextField(null=True, blank=True)
    license_detail = models.TextField(null=True, blank=True)
    license_valid_date = models.DateField(null=True)
    source = models.CharField(max_length=10, null=True, blank=True)
    update_date = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "other_administrative_license"


class OtherAdministrativePenalty(models.Model):
    """其他部门-行政处罚
    """

    penalty_decision_num = models.IntegerField(null=True)
    illegal_type = models.CharField(max_length=100, null=True, blank=True)
    penalty_content = models.CharField(max_length=1024, null=True, blank=True)
    penalty_decision_gov = models.CharField(max_length=50, null=True, blank=True)
    penalty_decision_date = models.DateField(null=True)
    detail = models.TextField(null=True, blank=True)
    penalty_type = models.CharField(max_length=30, null=True, blank=True)
    forfeiture_money = models.FloatField(null=True)
    confiscate_money = models.FloatField(null=True)
    source = models.CharField(max_length=20, null=True, blank=True)
    update_date = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "other_administrative_penalty"


class OtherProductionSecurity(models.Model):
    """其他-生产安全事故
    """

    accidient_number = models.IntegerField(null=True)
    accident_level = models.IntegerField(null=True)
    accidient_type = models.CharField(max_length=30, null=True, blank=True)
    accidient_time = models.DateField(null=True)
    death_num = models.IntegerField(null=True)
    info_publish_gov = models.CharField(max_length=30, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "other_production_security"


class YearReportAssets(models.Model):
    """年报-企业资产状况
    """

    asset_all = models.FloatField(null=True)
    owner_asset = models.FloatField(null=True)
    business_income = models.FloatField(null=True)
    profit = models.FloatField(null=True)
    main_business_income = models.FloatField(null=True)
    net_income = models.FloatField(null=True)
    tax = models.FloatField(null=True)
    debts = models.FloatField(null=True)
    year_report_id = models.CharField(max_length=20, null=True, blank=True)
    enter_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "year_report_assets"


class YearReportBasic(models.Model):
    """年报-基本
    """

    credit_code = models.CharField(max_length=20, null=True, blank=True)
    enter_name = models.CharField(max_length=50, null=True, blank=True)
    enter_phone = models.CharField(max_length=50, null=True, blank=True)
    zipcode = models.CharField(max_length=30, null=True, blank=True)
    enter_place = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    shareholder_change = models.BooleanField(default=False)
    status = models.CharField(max_length=20, null=True, blank=True)
    web_onlinestore = models.BooleanField(default=False)
    staff_number = models.IntegerField(null=True)
    register_num = models.CharField(max_length=50, null=True, blank=True)
    is_warrandice = models.CharField(max_length=10, null=True, blank=True)
    is_invest = models.BooleanField(default=False)
    year_report_id = models.CharField(max_length=20, null=True, blank=True)
    enter_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "year_report_basic"


class YearReportCorrect(models.Model):
    """年报-年报信息更正声明
    """

    correct_item = models.CharField(max_length=30, null=True, blank=True)
    correct_reason = models.CharField(max_length=50, null=True, blank=True)
    correct_time = models.DateField(null=True)
    year_report_id = models.CharField(max_length=20, null=True, blank=True)
    enter_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "year_report_correct"


class YearReportInvestment(models.Model):
    """年报-对外投资
    """

    invest_enter_name = models.CharField(max_length=50, null=True, blank=True)
    enter_code = models.CharField(max_length=100, null=True, blank=True)
    year_report_id = models.CharField(max_length=20, null=True, blank=True)
    enter_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "year_report_investment"


class YearReportModification(models.Model):
    """年报-修改记录
    """

    modify_item = models.TextField(null=True, blank=True)
    modify_before = models.TextField(max_length=50, null=True, blank=True)
    modify_after = models.TextField(max_length=50, null=True, blank=True)
    modify_date = models.DateField(null=True)
    year_report_id = models.CharField(max_length=20, null=True, blank=True)
    enter_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "year_report_modification"


class YearReportOnline(models.Model):
    """年报-网站或网店
    """

    online_type = models.CharField(max_length=100, null=True, blank=True)
    enter_name = models.CharField(max_length=50, null=True, blank=True)
    enter_url = models.TextField(null=True, blank=True)
    year_report_id = models.CharField(max_length=20, null=True, blank=True)
    enter_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "year_report_online"


class YearReportSharechange(models.Model):
    """年报-股权变更
    """

    shareholder = models.CharField(max_length=100, null=True, blank=True)
    shares_before = models.FloatField(null=True)
    shares_after = models.FloatField(null=True)
    year_report_id = models.CharField(max_length=20, null=True, blank=True)
    enter_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "year_report_sharechange"


class YearReportShareholder(models.Model):
    """年报-股东及出资
    """

    shareholder = models.CharField(max_length=100, null=True, blank=True)
    subscription_money_amount = models.FloatField(null=True)
    subscription_time = models.DateField(null=True)
    subscription_type = models.CharField(max_length=100, null=True, blank=True)
    paid_money_amount = models.FloatField(null=True)
    paid_time = models.DateField(null=True)
    paid_type = models.CharField(max_length=100, null=True, blank=True)
    year_report_id = models.CharField(max_length=20, null=True, blank=True)
    enter_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "year_report_shareholder"


class YearReportWarrandice(models.Model):
    """年报-对外提供保证担保
    """

    creditor = models.CharField(max_length=100, null=True, blank=True)
    debtor = models.CharField(max_length=30, null=True, blank=True)
    main_creditor_right = models.CharField(max_length=30, null=True, blank=True)
    main_creditor_right_amount = models.FloatField(null=True)
    fullfill_debt_duration = models.CharField(max_length=100, null=True, blank=True)
    guarantee_duration = models.CharField(max_length=30, null=True, blank=True)
    guarantee_type = models.CharField(max_length=30, null=True, blank=True)
    warrandice_scope = models.CharField(max_length=100, null=True, blank=True)
    year_report_id = models.CharField(max_length=20, null=True, blank=True)
    enter_id = models.IntegerField(null=True)
    version = models.IntegerField(default=1)
    invalidation = models.BooleanField(default=False)

    class Meta:
        db_table = "year_report_warrandice"
