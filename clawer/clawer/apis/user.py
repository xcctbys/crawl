#coding=utf-8

import json
import hashlib
import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.models import User as DjangoUser, Group
from django.contrib.auth import login as djangologin
from django.contrib.auth import logout as djangologout
from django.core import exceptions
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_unicode

from html5helper.decorator import render_json
from clawer.utils import check_auth_for_api
from clawer.models import UserProfile, MenuPermission



@render_json
def login(request):
    username = request.GET.get("username")
    password = request.GET.get("password")
        
    if request.user.is_authenticated():
        {"is_ok":True, "profile":request.user.get_profile().as_json()}

    user = authenticate(username=username, password=password)
    if not user:
        return {"is_ok":False, "reason":u"用户不存在或密码错误"}
    
    if user.is_superuser and user.is_staff and user.is_active:
        djangologin(request, user)
        return {"is_ok":True, "profile":user.get_profile().as_json()}
    
    if MenuPermission.has_perm_to_enter(user) == False:
        return {'is_ok':False, "reason":u"权限不足"}
    
    djangologin(request, user)
    return {"is_ok":True, "profile":user.get_profile().as_json()}


@render_json
@check_auth_for_api
def keepalive(request):
    return {"is_ok":True, "profile":request.user.get_profile().as_json()}


@render_json
def logout(request):
    djangologout(request)
    return {"is_ok":True}


@render_json
@check_auth_for_api
def get_my_menus(request):
    return MenuPermission.user_menus(request.user)


@render_json
def is_logined(request):
    request.session["to"] = request.GET.get("to") or ""
    
    if request.user.is_authenticated() is False:
        result = {"is_ok":False}
        return result
    
    result = {"is_ok":True, "profile":request.user.get_profile().as_json()}
    return result
