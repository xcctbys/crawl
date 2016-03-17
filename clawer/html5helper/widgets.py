#!/bin/env python
# coding=utf-8
''' widget define.
'''

import logging

from django import forms
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django.forms.widgets import Input

from html5helper.decorator import static



class MarkdownWidget(forms.Textarea):
    def __init__(self, attrs = None):
        super(MarkdownWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        logging.debug("widget name %s, value %s, attrs %s", name, value, attrs)
        html = super(MarkdownWidget, self).render(name, value, attrs)
        input_id = attrs.get("id")
        html += '<script src="%s"></script>' % static("markdown/markDownEditor2.js")
        html += '<script>new MarkdownEditor("%s");</script>' % input_id
        return mark_safe(html)


class InlineCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def __init__(self, attrs=None, ul_attrs=None):
        self.ul_attrs = ul_attrs
        super(InlineCheckboxSelectMultiple, self).__init__(attrs)
    
    def render(self, name, value, attrs=None, choices=()):
        html = super(InlineCheckboxSelectMultiple, self).render(name, value, attrs, choices)
        
        final_attrs = self.build_attrs(self.ul_attrs)
        #replace ul            
        html = html.replace("<ul>", "<div%s>" % flatatt(final_attrs))
        html = html.replace("</ul>", "</div>")
        #replace li
        html = html.replace("<li>", "<div class='checkbox'>")
        html = html.replace("</li>", "</div>")
        return mark_safe(html)
    
    
class InlineRadioSelect(forms.RadioSelect):
    def __init__(self, attrs=None, ul_attrs=None):
        self.ul_attrs = ul_attrs
        super(InlineRadioSelect, self).__init__(attrs)
    
    def render(self, name, value, attrs=None, choices=()):
        html = super(InlineRadioSelect, self).render(name, value, attrs, choices)
        final_attrs = self.build_attrs(self.ul_attrs)
        if "class" in final_attrs:
            final_attrs["class"] += " list-inline"
        else:
            final_attrs["class"] = "list-inline"
        html = html.replace('<ul>','<ul%s>' % flatatt(final_attrs))
        html = html.replace("<label", "<label class='radio-inline' ")
        return mark_safe(html)
    
    
class DateTimeInput(forms.DateTimeInput):
    input_type = "datetime"
    def render(self, name, value, attrs=None):
        ctrl = super(DateTimeInput, self).render(name, value, attrs)
        html = '\
        <div class="input-append date" id="datetimepicker" data-date-language="zh-CN" data-date-format="yyyy-mm-dd hh:ii:ss"> \
            %s \
            <span class="add-on"><i class="icon-th"></i></span> \
        </div>\
        <script>$("#datetimepicker").datetimepicker({keyboardNavigation:true, todayBtn:true, todayHighlight:true, autoclose:true, forceParse:true}, "update");</script> \
        ' % ctrl
        return mark_safe(html)
    

class DateInput(forms.DateInput):
    input_type = "date"
    
    
class TimeInput(forms.TimeInput):
    
    def render(self, name, value, attrs=None):
        ctr = super(TimeInput, self).render(name, value, attrs)
        ctr_id = attrs.get("id")
        html = '\
        <div class="input-append date" id="datetimepicker_%s" data-date-language="zh-CN" data-date-format="hh:ii:ss"> \
            %s \
            <span class="add-on"><i class="icon-th"></i></span> \
        </div>\
        <script>$("#datetimepicker_%s").datetimepicker({ \
                      keyboardNavigation: true, \
                      todayBtn: true, \
                      todayHighlight: true, \
                      startView: 1}, "update");</script> \
        ' % (ctr_id, ctr, ctr_id)
        return mark_safe(html)
    
class NumberInput(Input):
    input_type = "number"
    
class EmailInput(Input):
    input_type = "email"
    
class UrlInput(Input):
    input_type = "url"