#!/usr/bin/env python
#encoding=utf-8
import os
import codecs
import random
import time
import datetime
from smart_proxy.api import UseProxy, Proxy

PATH = '/data/clawer/html/'
# PATH = '/Users/princetechs5/'
def save_to_html(path, name, html):
    write_type = 'w'
    if not os.path.exists(path):
    	os.makedirs(path)
    new_path = os.path.join(path, name)
    with codecs.open(new_path, write_type, 'utf-8') as f:
        f.write(html)


def html_to_file(path, html):
    write_type = 'w'
    if os.path.exists(path):
        write_type = 'a'
    with codecs.open(path, write_type, 'utf-8') as f:
        f.write(html)

def json_dump_to_file(path, json_dict):
    write_type = 'w'
    if os.path.exists(path):
        write_type = 'a'
    with codecs.open(path, write_type, 'utf-8') as f:
        f.write(json.dumps(json_dict, ensure_ascii=False)+'\n')

def read_ent_from_file(path):
    read_type = 'r'
    if not os.path.exists(path):
        logging.error(u"There is no path : %s"% path )
    lines = []
    with codecs.open(path, read_type, 'utf-8') as f:
        lines = f.readlines()
    lines = [ line.split(',') for line in lines ]
    return lines

def html_from_file(path):
    read_type = 'r'
    if not os.path.exists(path):
        return None
    datas = None
    with codecs.open(path, read_type, 'utf8') as f:
        datas = f.read()
        f.close()
    return datas

def exe_time(func):
    def fnc(*args, **kwargs):
        start = datetime.datetime.now()
        print "call "+ func.__name__ + "()..."
        print func.__name__ +" start :"+ str(start)
        func(*args, **kwargs)
        end = datetime.datetime.now()
        print func.__name__ +" end :"+ str(end)
    return fnc

def get_proxy(province = '' ):
    useproxy = UseProxy()
    is_use_proxy = useproxy.get_province_is_use_proxy(province)
    if not is_use_proxy:
        proxies = {}
    else:
        proxy = Proxy()
        proxies = {'http':'http://'+random.choice(proxy.get_proxy(num=5, province='beijing')),
                    'https':'https://'+random.choice(proxy.get_proxy(num=5, province='beijing'))}
    return proxies
