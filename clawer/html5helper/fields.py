#coding=utf-8
""" used in form
"""

from django import forms
from django.forms import ValidationError
from html5helper import widgets


class CharField(forms.CharField):
    def __init__(self, *args, **kwargs):
        self.attrs = {}
        self.attrs["class"] = "form-control"
        self.attrs["placeholder"] = kwargs.pop("placeholder", "")
        if kwargs.get("required", True):
            self.attrs["required"] = "required"
        
        if "widget" not in kwargs:
            kwargs["widget"] = forms.TextInput(attrs=self.attrs)
            
        super(CharField, self).__init__(*args, **kwargs)
        

class TextField(CharField):
    def __init__(self, *args, **kwargs):
        rows = kwargs.pop("rows", 4)
        super(TextField, self).__init__(*args, **kwargs)
        self.attrs["rows"] = rows
        if "widget" not in kwargs:
            self.widget = forms.Textarea(attrs=self.attrs)
        
        
class PasswordField(CharField):
    def __init__(self, *args, **kwargs):
        super(PasswordField, self).__init__(*args, **kwargs)
        if "widget" not in kwargs:
            self.widget = forms.PasswordInput(attrs=self.attrs)


class IntegerField(forms.IntegerField):
    def __init__(self, *args, **kwargs):
        min_value = kwargs.get("min_value", 0)
        max_value = kwargs.get("max_value", 99999999999)
        
        self.attrs = {}
        self.attrs["class"] = "form-control"
        self.attrs["placeholder"] = kwargs.pop("placeholder", "")
        if kwargs.get("required", True):
            self.attrs["required"] = "required"
        self.attrs["min"] = min_value
        self.attrs["max"] = max_value
        
        if "widget" not in kwargs:
            kwargs["widget"] = widgets.NumberInput(attrs=self.attrs)
            
        super(IntegerField, self).__init__(*args, **kwargs)
            
            
class UrlField(forms.URLField):
    def __init__(self, *args, **kwargs):
        self.attrs = {}
        self.attrs["class"] = "form-control"
        self.attrs["placeholder"] = kwargs.pop("placeholder", "")
        if kwargs.get("required", True):
            self.attrs["required"] = "required"
        
        if "widget" not in kwargs:
            kwargs["widget"] = forms.TextInput(attrs=self.attrs)
            
        super(UrlField, self).__init__(*args, **kwargs)
        
class BooleanField(forms.BooleanField):
    def __init__(self, *args, **kwargs):
        super(BooleanField, self).__init__(*args, **kwargs)
            

class ModelChoiceField(forms.ModelChoiceField):
    def __init__(self, **kwargs):
        required = kwargs.get("required", True)
        if "widget" not in kwargs:
            attrs = {"class": "form-control"}
            if required:
                attrs["required"] = "required"
            kwargs["widget"] = forms.Select(attrs = attrs)
        super(ModelChoiceField, self).__init__(**kwargs)
        

class ChoiceField(forms.ChoiceField):
    def __init__(self, **kwargs):
        self.attrs = {}
        self.attrs["class"] = "form-control"
        self.attrs["placeholder"] = kwargs.pop("placeholder", "")
        self.attrs["required"] = ""   
        if kwargs.get("required", True):
            self.attrs["required"] = "required"
        
        if "widget" not in kwargs:
            self.widget = forms.Select(attrs=self.attrs)
            
        super(ChoiceField, self).__init__(**kwargs)
        
        
class MultipleChoiceField(forms.MultipleChoiceField):
    def __init__(self, **kwargs):
        self.attrs = {}
        
        if "widget" not in kwargs:
            self.widget = widgets.InlineCheckboxSelectMultiple(attrs=self.attrs)
            
        super(MultipleChoiceField, self).__init__(**kwargs)
        
        
        
class DateTimeField(forms.DateTimeField):
    def __init__(self, **kwargs):
        required = kwargs.get("required", True)
        if "widget" not in kwargs:
            attrs = {"class": "form-control"}
            if required:
                attrs["required"] = "required"
            kwargs["widget"] = widgets.DateTimeInput(attrs = attrs)
        super(DateTimeField, self).__init__(**kwargs)
        

class DateField(forms.DateField):
    def __init__(self, **kwargs):
        required = kwargs.get("required", True)
        placeholder = ""
        if "placeholder" in kwargs:
            placeholder = kwargs.pop("placeholder")
        if "widget" not in kwargs:
            attrs = {"class": "form-control", "placeholder":placeholder}
            if required:
                attrs["required"] = "required"
            kwargs["widget"] = widgets.DateInput(attrs = attrs)
        super(DateField, self).__init__(**kwargs)
        

class TimeField(forms.TimeField):
    def __init__(self, **kwargs):
        required = kwargs.get("required", True)
        if "widget" not in kwargs:
            attrs = {"class": "form-control"}
            if required:
                attrs["required"] = "required"
            kwargs["widget"] = widgets.TimeInput(attrs = attrs)
        super(TimeField, self).__init__(**kwargs)
        

class EmailField(forms.EmailField):
    def __init__(self, **kwargs):
        required = kwargs.get("required", True)
        if "widget" not in kwargs:
            attrs = {"class": "form-control"}
            if required:
                attrs["required"] = "required"
            kwargs["widget"] = widgets.EmailInput(attrs = attrs)
        super(EmailField, self).__init__(**kwargs)
        
        
class MarkdownField(TextField):
    def __init__(self, *args, **kwargs):
        super(MarkdownField, self).__init__(*args, **kwargs)
        if "widget" not in kwargs:
            self.widget = widgets.MarkdownWidget(attrs=self.attrs)


class ImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        self.attrs = {}
        if kwargs.get("required", True):
            self.attrs["required"] = "required"
        
        if "widget" not in kwargs:
            kwargs["widget"] = forms.FileInput(attrs=self.attrs)
            
        super(ImageField, self).__init__(*args, **kwargs)