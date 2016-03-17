#!/bin/env python
# coding=utf-8
''' base form define.
'''

from django import forms
from django import template
from django.utils.safestring import mark_safe

    
class BasisForm(forms.Form):
    """ must place forms/base.html in the templates
    """
    _custom_error = ""
    _success_tips = ""
    
    def __init__(self, *args, **kwargs):
        super(BasisForm, self).__init__(*args, **kwargs)
        for name,field in self.fields.items():
            if field.required:
                field.label = "* %s" % (field.label or name) 
        
    @property
    def custom_error(self):
        if self._custom_error == "":
            return ""
        return mark_safe(u"<div class=\"alert\">%s</div>" % self._custom_error)
    
    def set_custom_error(self, msg):
        self._custom_error = msg
        
    @property
    def success_tips(self):
        if self._success_tips == "":
            return ""
        return mark_safe(u"<div class=\"alert alert-success\">%s</div>" % self._success_tips)
    
    def set_success_tips(self, tips):
        self._success_tips = tips
        
    def as_div(self):
        tp = template.loader.get_template("html5helper/tags/form.html")
        ctx = template.Context({"form": self})
        return tp.render(ctx)