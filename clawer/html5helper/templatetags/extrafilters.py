#coding=utf-8

import re
import types

from django.template import Library



register = Library()



@register.filter
def human_int(value):
    if isinstance(value, types.StringType) is False:
        value = str(value)
    r=re.compile(r'(\d)(?=(\d\d\d)+(?!\d))')
    return r.sub(r"\1,", value)

