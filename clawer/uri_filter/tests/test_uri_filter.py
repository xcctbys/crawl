#coding=utf-8
#!
from api.api_uri_filter import *
from uri_fileter.api import FilterAPI


def filterapiclient(filter_typename='', uri_list=[]):
    urilist = ['www.baidu.com','www.baidu.com','www.prittn.com']
    filter_typename = 'urigenerator'
    list = FilterAPI(filter_typename,urilist)
    list.filter()
    return 0