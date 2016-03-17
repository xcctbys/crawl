#encoding=utf-8
from django import forms


class AddEnterpriseForm(forms.Form):
    names_file = forms.FileField()