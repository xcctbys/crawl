# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Enterprise'
        db.create_table('enterprise_enterprise', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('province', self.gf('django.db.models.fields.IntegerField')(max_length=128)),
            ('register_no', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('add_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('enterprise', ['Enterprise'])

        # Adding model 'Basic'
        db.create_table('basic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('credit_code', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('enter_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('enter_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('corporation', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('register_capital', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('establish_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('place', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('time_start', self.gf('django.db.models.fields.DateField')(null=True)),
            ('time_end', self.gf('django.db.models.fields.DateField')(null=True)),
            ('business_scope', self.gf('django.db.models.fields.TextField')(null=True)),
            ('register_gov', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('check_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('register_status', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('register_num', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('enterprise', ['Basic'])

        # Adding model 'IndustryCommerceAdminiPenalty'
        db.create_table('industry_commerce_admini_penalty', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('penalty_decision_num', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('illegal_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('penalty_content', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('penalty_decision_gov', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('penalty_decision_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('detail', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('penalty_register_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('enter_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('creidit_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('corporation', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('penalty_publicity_time', self.gf('django.db.models.fields.DateField')(null=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('bas_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['IndustryCommerceAdminiPenalty'])

        # Adding model 'IndustryCommerceBranch'
        db.create_table('industry_commerce_branch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('enter_code', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('branch_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('register_gov', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['IndustryCommerceBranch'])

        # Adding model 'IndustryCommerceChange'
        db.create_table('industry_commerce_change', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('modify_item', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('modify_before', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('modify_after', self.gf('django.db.models.fields.TextField')(max_length=50, null=True, blank=True)),
            ('modify_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['IndustryCommerceChange'])

        # Adding model 'IndustryCommerceCheck'
        db.create_table('industry_commerce_check', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('check_gov', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('check_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('check_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('check_result', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('check_comment', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['IndustryCommerceCheck'])

        # Adding model 'IndustryCommerceClear'
        db.create_table('industry_commerce_clear', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person_in_charge', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('persons', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['IndustryCommerceClear'])

        # Adding model 'IndustryCommerceDetailGuarantee'
        db.create_table('industry_commerce_detail_guarantee', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('register_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('sharechange_register_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('register_gov', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('register_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['IndustryCommerceDetailGuarantee'])

        # Adding model 'IndustryCommerceException'
        db.create_table('industry_commerce_exception', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('list_on_reason', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('list_on_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('list_out_reason', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('list_out_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('list_gov', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('list_on_gov', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('list_out_gov', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['IndustryCommerceException'])

        # Adding model 'IndustryCommerceIllegal'
        db.create_table('industry_commerce_illegal', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('list_on_reason', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('list_on_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('list_out_reason', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('list_out_date', self.gf('django.db.models.fields.DateField')(max_length=100, null=True, blank=True)),
            ('decision_gov', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('bas_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['IndustryCommerceIllegal'])

        # Adding model 'IndustryCommerceMainperson'
        db.create_table('industry_commerce_mainperson', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('position', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('bas_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['IndustryCommerceMainperson'])

        # Adding model 'IndustryCommerceMortgage'
        db.create_table('industry_commerce_mortgage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('register_num', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('sharechange_register_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('register_gov', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('guarantee_debt_amount', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('publicity_time', self.gf('django.db.models.fields.DateField')(null=True)),
            ('details', self.gf('django.db.models.fields.TextField')(null=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('bas_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['IndustryCommerceMortgage'])

        # Adding model 'IndustryCommerceMortgageChange'
        db.create_table('industry_commerce_mortgage_change', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('modify_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('modify_content', self.gf('django.db.models.fields.TextField')(null=True)),
            ('register_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['IndustryCommerceMortgageChange'])

        # Adding model 'IndustryCommerceMortgageGuarantee'
        db.create_table('industry_commerce_cortgage_guarantee', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('check_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('guarantee_scope', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('debtor_duration', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('register_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['IndustryCommerceMortgageGuarantee'])

        # Adding model 'IndustryCommerceMortgageGuaranty'
        db.create_table('industry_commerce_mortgage_guaranty', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('ownership', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('details', self.gf('django.db.models.fields.TextField')(null=True)),
            ('coments', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('register_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['IndustryCommerceMortgageGuaranty'])

        # Adding model 'IndustryCommerceRevoke'
        db.create_table('industry_commerce_revoke', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('revoke_item', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('content_before_revoke', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('content_after_revoke', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('revoke_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('bas_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['IndustryCommerceRevoke'])

        # Adding model 'IndustryCommerceShareholders'
        db.create_table('industry_commerce_shareholders', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shareholder_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('shareholder_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('certificate_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('certificate_number', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('subscription_amount', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('paid_amount', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('subscription_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('subscription_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('subscription_money_amount', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('paid_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('paid_money_amount', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('paid_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['IndustryCommerceShareholders'])

        # Adding model 'IndustryCommerceSharepledge'
        db.create_table('industry_commerce_sharepledge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('register_num', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('pledgor', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('pledgor_certificate_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('share_pledge_num', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('mortgagee', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('mortgagee_certificate_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('sharechange_register_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('change_detail', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('publicity_time', self.gf('django.db.models.fields.DateField')(null=True)),
            ('modify_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('modify_content', self.gf('django.db.models.fields.TextField')(null=True)),
            ('register_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('bas_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['IndustryCommerceSharepledge'])

        # Adding model 'IndustryMortgageDetailMortgagee'
        db.create_table('industry_mortgage_detail_mortgagee', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mortgagee_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('mortgagee_certificate_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('pledgor_certificate_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['IndustryMortgageDetailMortgagee'])

        # Adding model 'EnterAdministrativeLicense'
        db.create_table('enter_administrative_license', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('license_num', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('license_filename', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('license_begin_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('license_end_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('license_authority', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('license_content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('license_status', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('license_detail', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('license_register_time', self.gf('django.db.models.fields.DateField')(null=True)),
            ('license_publicity_time', self.gf('django.db.models.fields.DateField')(null=True)),
            ('license_change_item', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('license_change_time', self.gf('django.db.models.fields.DateField')(null=True)),
            ('license_content_before', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('license_content_after', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('bas_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['EnterAdministrativeLicense'])

        # Adding model 'EnterAdministrativePenalty'
        db.create_table('enter_administrative_penalty', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('penalty_decision_num', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('illegal_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('administrative_penalty_content', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('decision_gov', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('decision_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('penalty_comment', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('penalty_publicit_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('bas_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['EnterAdministrativePenalty'])

        # Adding model 'EnterAnnualReport'
        db.create_table('enter_annual_report', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('report_year', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('publicity_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['EnterAnnualReport'])

        # Adding model 'EnterIntellectualPropertyPledge'
        db.create_table('enter_intellectual_property_pledge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('credit_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('enter_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('property_type', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('pledgor_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('mortgagee_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('mortgage_register_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('property_status', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('property_pledge_change', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('property_pledge_register_gov', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('property_pledge_register_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('property_pledge_publicity_time', self.gf('django.db.models.fields.DateField')(null=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('bas_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['EnterIntellectualPropertyPledge'])

        # Adding model 'EnterModification'
        db.create_table('enter_modification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('modify_item', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('modify_before', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('modify_after', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('modify_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('bas_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['EnterModification'])

        # Adding model 'EnterSharechange'
        db.create_table('enter_sharechange', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shareholder', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('share_ratio_before', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('share_ratio_after', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('share_change_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('sharechange_register_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('sharechange_publicity_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['EnterSharechange'])

        # Adding model 'EnterShareholder'
        db.create_table('enter_shareholder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shareholder_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('subscription_amount', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('paid_amount', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('subscription_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('subscription_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('subscription_money_amount', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('paid_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('paid_money_amount', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('paid_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('shareholder_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('subscription_publicity_time', self.gf('django.db.models.fields.DateField')(null=True)),
            ('paid_publicity_time', self.gf('django.db.models.fields.DateField')(null=True)),
            ('publicity_time', self.gf('django.db.models.fields.DateField')(null=True)),
            ('modify_time', self.gf('django.db.models.fields.DateField')(null=True)),
            ('detals', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('bas_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['EnterShareholder'])

        # Adding model 'JudicialShareFreeze'
        db.create_table('judicial_share_freeze', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('been_excute_person', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('share_num', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('excute_court', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('notice_num', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('freeze_status', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('freeze_detail', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('bas_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['JudicialShareFreeze'])

        # Adding model 'JudicialShareholderChange'
        db.create_table('judicial_shareholder_change', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('been_excute_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('share_num', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('excute_court', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('assignee', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('detail', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('bas_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['JudicialShareholderChange'])

        # Adding model 'OtherAdministrativeChange'
        db.create_table('other_administrative_change', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('administrative_change_item', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('administrative_change_tme', self.gf('django.db.models.fields.DateField')(null=True)),
            ('administrative_change_before', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('administrative_change_after', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('bas_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['OtherAdministrativeChange'])

        # Adding model 'OtherAdministrativeLicense'
        db.create_table('other_administrative_license', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('license_file_num', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('license_filename', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('license_begin_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('license_end_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('license_content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('license_authority_gov', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('license_status', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('license_detail', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('license_valid_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('update_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('bas_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['OtherAdministrativeLicense'])

        # Adding model 'OtherAdministrativePenalty'
        db.create_table('other_administrative_penalty', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('penalty_decision_num', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('illegal_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('penalty_content', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('penalty_decision_gov', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('penalty_decision_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('detail', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('penalty_type', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('forfeiture_money', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('confiscate_money', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('update_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('bas_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['OtherAdministrativePenalty'])

        # Adding model 'OtherProductionSecurity'
        db.create_table('other_production_security', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('accidient_number', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('accident_level', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('accidient_type', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('accidient_time', self.gf('django.db.models.fields.DateField')(null=True)),
            ('death_num', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('info_publish_gov', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('bas_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['OtherProductionSecurity'])

        # Adding model 'YearReportAssets'
        db.create_table('year_report_assets', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('asset_all', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('owner_asset', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('business_income', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('profit', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('main_business_income', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('net_income', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('tax', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('debts', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('year_report_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['YearReportAssets'])

        # Adding model 'YearReportBasic'
        db.create_table('year_report_basic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('credit_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('enter_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('enter_phone', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('enter_place', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('shareholder_change', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('web_onlinestore', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('staff_number', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('register_num', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('is_warrandice', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('is_invest', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('year_report_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['YearReportBasic'])

        # Adding model 'YearReportCorrect'
        db.create_table('year_report_correct', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('correct_item', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('correct_reason', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('correct_time', self.gf('django.db.models.fields.DateField')(null=True)),
            ('year_report_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['YearReportCorrect'])

        # Adding model 'YearReportInvestment'
        db.create_table('year_report_investment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('invest_enter_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('enter_code', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('year_report_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['YearReportInvestment'])

        # Adding model 'YearReportModification'
        db.create_table('year_report_modification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('modify_item', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('modify_before', self.gf('django.db.models.fields.TextField')(max_length=50, null=True, blank=True)),
            ('modify_after', self.gf('django.db.models.fields.TextField')(max_length=50, null=True, blank=True)),
            ('modify_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('year_report_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['YearReportModification'])

        # Adding model 'YearReportOnline'
        db.create_table('year_report_online', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('online_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('enter_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('enter_url', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('year_report_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['YearReportOnline'])

        # Adding model 'YearReportSharechange'
        db.create_table('year_report_sharechange', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shareholder', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('shares_before', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('shares_after', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('year_report_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['YearReportSharechange'])

        # Adding model 'YearReportShareholder'
        db.create_table('year_report_shareholder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shareholder', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('subscription_money_amount', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('subscription_time', self.gf('django.db.models.fields.DateField')(null=True)),
            ('subscription_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('paid_money_amount', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('paid_time', self.gf('django.db.models.fields.DateField')(null=True)),
            ('paid_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('year_report_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['YearReportShareholder'])

        # Adding model 'YearReportWarrandice'
        db.create_table('year_report_warrandice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creditor', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('debtor', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('main_creditor_right', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('main_creditor_right_amount', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('fullfill_debt_duration', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('guarantee_duration', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('guarantee_type', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('warrandice_scope', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('year_report_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('enter_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('invalidation', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('enterprise', ['YearReportWarrandice'])


    def backwards(self, orm):
        # Deleting model 'Enterprise'
        db.delete_table('enterprise_enterprise')

        # Deleting model 'Basic'
        db.delete_table('basic')

        # Deleting model 'IndustryCommerceAdminiPenalty'
        db.delete_table('industry_commerce_admini_penalty')

        # Deleting model 'IndustryCommerceBranch'
        db.delete_table('industry_commerce_branch')

        # Deleting model 'IndustryCommerceChange'
        db.delete_table('industry_commerce_change')

        # Deleting model 'IndustryCommerceCheck'
        db.delete_table('industry_commerce_check')

        # Deleting model 'IndustryCommerceClear'
        db.delete_table('industry_commerce_clear')

        # Deleting model 'IndustryCommerceDetailGuarantee'
        db.delete_table('industry_commerce_detail_guarantee')

        # Deleting model 'IndustryCommerceException'
        db.delete_table('industry_commerce_exception')

        # Deleting model 'IndustryCommerceIllegal'
        db.delete_table('industry_commerce_illegal')

        # Deleting model 'IndustryCommerceMainperson'
        db.delete_table('industry_commerce_mainperson')

        # Deleting model 'IndustryCommerceMortgage'
        db.delete_table('industry_commerce_mortgage')

        # Deleting model 'IndustryCommerceMortgageChange'
        db.delete_table('industry_commerce_mortgage_change')

        # Deleting model 'IndustryCommerceMortgageGuarantee'
        db.delete_table('industry_commerce_cortgage_guarantee')

        # Deleting model 'IndustryCommerceMortgageGuaranty'
        db.delete_table('industry_commerce_mortgage_guaranty')

        # Deleting model 'IndustryCommerceRevoke'
        db.delete_table('industry_commerce_revoke')

        # Deleting model 'IndustryCommerceShareholders'
        db.delete_table('industry_commerce_shareholders')

        # Deleting model 'IndustryCommerceSharepledge'
        db.delete_table('industry_commerce_sharepledge')

        # Deleting model 'IndustryMortgageDetailMortgagee'
        db.delete_table('industry_mortgage_detail_mortgagee')

        # Deleting model 'EnterAdministrativeLicense'
        db.delete_table('enter_administrative_license')

        # Deleting model 'EnterAdministrativePenalty'
        db.delete_table('enter_administrative_penalty')

        # Deleting model 'EnterAnnualReport'
        db.delete_table('enter_annual_report')

        # Deleting model 'EnterIntellectualPropertyPledge'
        db.delete_table('enter_intellectual_property_pledge')

        # Deleting model 'EnterModification'
        db.delete_table('enter_modification')

        # Deleting model 'EnterSharechange'
        db.delete_table('enter_sharechange')

        # Deleting model 'EnterShareholder'
        db.delete_table('enter_shareholder')

        # Deleting model 'JudicialShareFreeze'
        db.delete_table('judicial_share_freeze')

        # Deleting model 'JudicialShareholderChange'
        db.delete_table('judicial_shareholder_change')

        # Deleting model 'OtherAdministrativeChange'
        db.delete_table('other_administrative_change')

        # Deleting model 'OtherAdministrativeLicense'
        db.delete_table('other_administrative_license')

        # Deleting model 'OtherAdministrativePenalty'
        db.delete_table('other_administrative_penalty')

        # Deleting model 'OtherProductionSecurity'
        db.delete_table('other_production_security')

        # Deleting model 'YearReportAssets'
        db.delete_table('year_report_assets')

        # Deleting model 'YearReportBasic'
        db.delete_table('year_report_basic')

        # Deleting model 'YearReportCorrect'
        db.delete_table('year_report_correct')

        # Deleting model 'YearReportInvestment'
        db.delete_table('year_report_investment')

        # Deleting model 'YearReportModification'
        db.delete_table('year_report_modification')

        # Deleting model 'YearReportOnline'
        db.delete_table('year_report_online')

        # Deleting model 'YearReportSharechange'
        db.delete_table('year_report_sharechange')

        # Deleting model 'YearReportShareholder'
        db.delete_table('year_report_shareholder')

        # Deleting model 'YearReportWarrandice'
        db.delete_table('year_report_warrandice')


    models = {
        'enterprise.basic': {
            'Meta': {'object_name': 'Basic', 'db_table': "'basic'"},
            'business_scope': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'check_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'corporation': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'credit_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'enter_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'enter_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'establish_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'place': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'register_capital': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'register_gov': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'register_num': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'register_status': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'time_end': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'time_start': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.enteradministrativelicense': {
            'Meta': {'object_name': 'EnterAdministrativeLicense', 'db_table': "'enter_administrative_license'"},
            'bas_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'license_authority': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'license_begin_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'license_change_item': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'license_change_time': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'license_content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'license_content_after': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'license_content_before': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'license_detail': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'license_end_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'license_filename': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'license_num': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'license_publicity_time': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'license_register_time': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'license_status': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.enteradministrativepenalty': {
            'Meta': {'object_name': 'EnterAdministrativePenalty', 'db_table': "'enter_administrative_penalty'"},
            'administrative_penalty_content': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'bas_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'decision_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'decision_gov': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illegal_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'penalty_comment': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'penalty_decision_num': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'penalty_publicit_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.enterannualreport': {
            'Meta': {'object_name': 'EnterAnnualReport', 'db_table': "'enter_annual_report'"},
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publicity_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'report_year': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.enterintellectualpropertypledge': {
            'Meta': {'object_name': 'EnterIntellectualPropertyPledge', 'db_table': "'enter_intellectual_property_pledge'"},
            'bas_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'credit_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'enter_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mortgage_register_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'mortgagee_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'pledgor_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'property_pledge_change': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'property_pledge_publicity_time': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'property_pledge_register_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'property_pledge_register_gov': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'property_status': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'property_type': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.entermodification': {
            'Meta': {'object_name': 'EnterModification', 'db_table': "'enter_modification'"},
            'bas_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modify_after': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'modify_before': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'modify_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'modify_item': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.enterprise': {
            'Meta': {'object_name': 'Enterprise'},
            'add_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'province': ('django.db.models.fields.IntegerField', [], {'max_length': '128'}),
            'register_no': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'enterprise.entersharechange': {
            'Meta': {'object_name': 'EnterSharechange', 'db_table': "'enter_sharechange'"},
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'share_change_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'share_ratio_after': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'share_ratio_before': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'sharechange_publicity_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'sharechange_register_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'shareholder': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.entershareholder': {
            'Meta': {'object_name': 'EnterShareholder', 'db_table': "'enter_shareholder'"},
            'bas_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'detals': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modify_time': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'paid_amount': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'paid_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'paid_money_amount': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'paid_publicity_time': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'paid_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'publicity_time': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'shareholder_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shareholder_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'subscription_amount': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'subscription_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'subscription_money_amount': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'subscription_publicity_time': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'subscription_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.industrycommerceadminipenalty': {
            'Meta': {'object_name': 'IndustryCommerceAdminiPenalty', 'db_table': "'industry_commerce_admini_penalty'"},
            'bas_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'corporation': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'creidit_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'detail': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'enter_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illegal_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'penalty_content': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'penalty_decision_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'penalty_decision_gov': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'penalty_decision_num': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'penalty_publicity_time': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'penalty_register_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.industrycommercebranch': {
            'Meta': {'object_name': 'IndustryCommerceBranch', 'db_table': "'industry_commerce_branch'"},
            'branch_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'enter_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'register_gov': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.industrycommercechange': {
            'Meta': {'object_name': 'IndustryCommerceChange', 'db_table': "'industry_commerce_change'"},
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modify_after': ('django.db.models.fields.TextField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'modify_before': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'modify_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'modify_item': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.industrycommercecheck': {
            'Meta': {'object_name': 'IndustryCommerceCheck', 'db_table': "'industry_commerce_check'"},
            'check_comment': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'check_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'check_gov': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'check_result': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'check_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.industrycommerceclear': {
            'Meta': {'object_name': 'IndustryCommerceClear', 'db_table': "'industry_commerce_clear'"},
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'person_in_charge': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'persons': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.industrycommercedetailguarantee': {
            'Meta': {'object_name': 'IndustryCommerceDetailGuarantee', 'db_table': "'industry_commerce_detail_guarantee'"},
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'register_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'register_gov': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'register_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'sharechange_register_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.industrycommerceexception': {
            'Meta': {'object_name': 'IndustryCommerceException', 'db_table': "'industry_commerce_exception'"},
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'list_gov': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'list_on_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'list_on_gov': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'list_on_reason': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'list_out_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'list_out_gov': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'list_out_reason': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.industrycommerceillegal': {
            'Meta': {'object_name': 'IndustryCommerceIllegal', 'db_table': "'industry_commerce_illegal'"},
            'bas_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'decision_gov': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'list_on_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'list_on_reason': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'list_out_date': ('django.db.models.fields.DateField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'list_out_reason': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.industrycommercemainperson': {
            'Meta': {'object_name': 'IndustryCommerceMainperson', 'db_table': "'industry_commerce_mainperson'"},
            'bas_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.industrycommercemortgage': {
            'Meta': {'object_name': 'IndustryCommerceMortgage', 'db_table': "'industry_commerce_mortgage'"},
            'bas_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'details': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'guarantee_debt_amount': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publicity_time': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'register_gov': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'register_num': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'sharechange_register_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.industrycommercemortgagechange': {
            'Meta': {'object_name': 'IndustryCommerceMortgageChange', 'db_table': "'industry_commerce_mortgage_change'"},
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modify_content': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'modify_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'register_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.industrycommercemortgageguarantee': {
            'Meta': {'object_name': 'IndustryCommerceMortgageGuarantee', 'db_table': "'industry_commerce_cortgage_guarantee'"},
            'amount': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'check_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'debtor_duration': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'guarantee_scope': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'register_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.industrycommercemortgageguaranty': {
            'Meta': {'object_name': 'IndustryCommerceMortgageGuaranty', 'db_table': "'industry_commerce_mortgage_guaranty'"},
            'coments': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'details': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'ownership': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'register_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.industrycommercerevoke': {
            'Meta': {'object_name': 'IndustryCommerceRevoke', 'db_table': "'industry_commerce_revoke'"},
            'bas_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'content_after_revoke': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'content_before_revoke': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'revoke_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'revoke_item': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.industrycommerceshareholders': {
            'Meta': {'object_name': 'IndustryCommerceShareholders', 'db_table': "'industry_commerce_shareholders'"},
            'certificate_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'certificate_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paid_amount': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'paid_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'paid_money_amount': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'paid_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'shareholder_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shareholder_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'subscription_amount': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'subscription_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'subscription_money_amount': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'subscription_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.industrycommercesharepledge': {
            'Meta': {'object_name': 'IndustryCommerceSharepledge', 'db_table': "'industry_commerce_sharepledge'"},
            'bas_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'change_detail': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modify_content': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'modify_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'mortgagee': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'mortgagee_certificate_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'pledgor': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'pledgor_certificate_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'publicity_time': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'register_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'register_num': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'share_pledge_num': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'sharechange_register_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.industrymortgagedetailmortgagee': {
            'Meta': {'object_name': 'IndustryMortgageDetailMortgagee', 'db_table': "'industry_mortgage_detail_mortgagee'"},
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mortgagee_certificate_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'mortgagee_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'pledgor_certificate_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.judicialsharefreeze': {
            'Meta': {'object_name': 'JudicialShareFreeze', 'db_table': "'judicial_share_freeze'"},
            'bas_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'been_excute_person': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'excute_court': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'freeze_detail': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'freeze_status': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notice_num': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'share_num': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.judicialshareholderchange': {
            'Meta': {'object_name': 'JudicialShareholderChange', 'db_table': "'judicial_shareholder_change'"},
            'assignee': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'bas_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'been_excute_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'detail': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'excute_court': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'share_num': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.otheradministrativechange': {
            'Meta': {'object_name': 'OtherAdministrativeChange', 'db_table': "'other_administrative_change'"},
            'administrative_change_after': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'administrative_change_before': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'administrative_change_item': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'administrative_change_tme': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'bas_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.otheradministrativelicense': {
            'Meta': {'object_name': 'OtherAdministrativeLicense', 'db_table': "'other_administrative_license'"},
            'bas_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'license_authority_gov': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'license_begin_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'license_content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'license_detail': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'license_end_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'license_file_num': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'license_filename': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'license_status': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'license_valid_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'update_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.otheradministrativepenalty': {
            'Meta': {'object_name': 'OtherAdministrativePenalty', 'db_table': "'other_administrative_penalty'"},
            'bas_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'confiscate_money': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'detail': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'forfeiture_money': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illegal_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'penalty_content': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'penalty_decision_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'penalty_decision_gov': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'penalty_decision_num': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'penalty_type': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'update_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.otherproductionsecurity': {
            'Meta': {'object_name': 'OtherProductionSecurity', 'db_table': "'other_production_security'"},
            'accident_level': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'accidient_number': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'accidient_time': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'accidient_type': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'bas_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'death_num': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'enter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_publish_gov': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'enterprise.yearreportassets': {
            'Meta': {'object_name': 'YearReportAssets', 'db_table': "'year_report_assets'"},
            'asset_all': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'business_income': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'debts': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'enter_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'main_business_income': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'net_income': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'owner_asset': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'profit': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'tax': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'year_report_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'enterprise.yearreportbasic': {
            'Meta': {'object_name': 'YearReportBasic', 'db_table': "'year_report_basic'"},
            'credit_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'enter_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'enter_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'enter_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'enter_place': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_invest': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_warrandice': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'register_num': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'shareholder_change': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'staff_number': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'web_onlinestore': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'year_report_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'})
        },
        'enterprise.yearreportcorrect': {
            'Meta': {'object_name': 'YearReportCorrect', 'db_table': "'year_report_correct'"},
            'correct_item': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'correct_reason': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'correct_time': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'enter_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'year_report_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'enterprise.yearreportinvestment': {
            'Meta': {'object_name': 'YearReportInvestment', 'db_table': "'year_report_investment'"},
            'enter_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'enter_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'invest_enter_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'year_report_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'enterprise.yearreportmodification': {
            'Meta': {'object_name': 'YearReportModification', 'db_table': "'year_report_modification'"},
            'enter_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modify_after': ('django.db.models.fields.TextField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'modify_before': ('django.db.models.fields.TextField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'modify_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'modify_item': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'year_report_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'enterprise.yearreportonline': {
            'Meta': {'object_name': 'YearReportOnline', 'db_table': "'year_report_online'"},
            'enter_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'enter_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'enter_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'online_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'year_report_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'enterprise.yearreportsharechange': {
            'Meta': {'object_name': 'YearReportSharechange', 'db_table': "'year_report_sharechange'"},
            'enter_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'shareholder': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'shares_after': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'shares_before': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'year_report_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'enterprise.yearreportshareholder': {
            'Meta': {'object_name': 'YearReportShareholder', 'db_table': "'year_report_shareholder'"},
            'enter_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paid_money_amount': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'paid_time': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'paid_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'shareholder': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'subscription_money_amount': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'subscription_time': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'subscription_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'year_report_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'enterprise.yearreportwarrandice': {
            'Meta': {'object_name': 'YearReportWarrandice', 'db_table': "'year_report_warrandice'"},
            'creditor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'debtor': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'enter_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'fullfill_debt_duration': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'guarantee_duration': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'guarantee_type': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalidation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'main_creditor_right': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'main_creditor_right_amount': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'warrandice_scope': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'year_report_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['enterprise']