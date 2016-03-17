# coding=utf-8

import datetime

from django.utils.safestring import mark_safe
from django import template

from html5helper.utils import make_markdown
from emoji import Emoji


register = template.Library()

@register.filter("markdown")
def do_markdown(text):
    if not text:
        return ""
    return mark_safe(make_markdown(text))


@register.filter("markdown_emoji")
def do_markdown_emoji(text):
    if not text:
        return ""
    emoji_text = Emoji.replace(text)
    return mark_safe(make_markdown(emoji_text))

