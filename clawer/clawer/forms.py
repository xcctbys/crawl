#encoding=utf-8

from django import forms

from clawer.models import Clawer, ClawerSetting
from clawer.utils import Download



class AddClawer(forms.Form):
    name = forms.CharField(max_length=128)
    info = forms.CharField(max_length=1024)
    customer = forms.CharField(max_length=128)
    

class UpdateClawerTaskGenerator(forms.Form):
    clawer = forms.ModelChoiceField(queryset=Clawer.objects)
    code_file = forms.FileField()
    cron = forms.CharField(max_length=64)
    
    
class UpdateClawerAnalysis(forms.Form):
    clawer = forms.ModelChoiceField(queryset=Clawer.objects)
    code_file = forms.FileField()
    

class AddClawerTask(forms.Form):
    clawer = forms.ModelChoiceField(queryset=Clawer.objects)
    uri = forms.CharField(max_length=4096)
    cookie = forms.CharField(max_length=4096, required=False)
    

class UpdateClawerSetting(forms.Form):
    clawer = forms.ModelChoiceField(queryset=Clawer.objects)
    dispatch = forms.IntegerField()
    analysis = forms.IntegerField()
    proxy = forms.CharField(max_length=4096, required=False)
    cookie = forms.CharField(max_length=4096, required=False)
    download_js = forms.CharField(max_length=4096, required=False)
    download_engine = forms.ChoiceField(choices=Download.ENGINE_CHOICES)
    status = forms.ChoiceField(choices=Clawer.STATUS_CHOICES)
    prior = forms.ChoiceField(choices=ClawerSetting.PRIOR_CHOICES)
    report_mails = forms.CharField(max_length=1024, required=False)
    
