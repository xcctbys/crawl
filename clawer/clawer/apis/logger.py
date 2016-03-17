#coding=utf-8

from html5helper.decorator import render_json
from clawer.models import Logger
from clawer.utils import EasyUIPager, check_auth_for_api


@render_json
@check_auth_for_api
def all(request):
    qs = Logger.objects
    pager = EasyUIPager(qs, request)
    return pager.query()