# coding=utf-8
''' gravatar imgs
'''

from django.utils.safestring import mark_safe
from django import template
from django.template import Context
from django import forms


register = template.Library()

@register.inclusion_tag("html5helper/tags/formfield.html", name="form_field")
def do_form_field(field, is_show_label=True):
    is_hidden = False
    if isinstance(field.field.widget, forms.HiddenInput):
        is_hidden = True
    return {"field":field, "is_hidden":is_hidden, "is_show_label":is_show_label}