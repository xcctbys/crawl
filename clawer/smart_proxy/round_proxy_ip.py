# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
import requests
from django.conf import settings
from smart_proxy.models import ProxyIp
from multiprocessing.dummy import Pool

sys.path.append(os.getcwd())
reqst = requests.Session()
reqst.headers.update({'Accept': 'text/html, application/xhtml+xml, */*',
                      'Accept-Encoding': 'gzip, deflate',
                      'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
                      'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})


def check_is_valid(ip_port):
    try:
        proxy = {'http': 'http://' + ip_port}
        resp = reqst.get('http://baidu.com', timeout=12, proxies=proxy)
        if resp.status_code == 200:
            return True
        return False
    except Exception:
        return False


def delete_item(item):
    try:
        item.delete()
        return True
    except Exception:
        return False


def change_valid(one_ip):
    proxy = {'http': 'http://' + one_ip.ip_port}
    try:
        resp = reqst.get('http://baidu.com', timeout=12, proxies=proxy)
    except Exception:
        if one_ip.is_valid is False:
            print proxy, 'already died......'
            return False
        one_ip.is_valid = False
        one_ip.save()
        print proxy, 'died......'
        return False
    if resp.status_code == 200:
        if one_ip.is_valid is True:
            print proxy, 'living!'
            return True
        one_ip.is_valid = True
        one_ip.save()
        print proxy, 'live again!'
        return True
    if one_ip.is_valid is False:
        return False
    one_ip.is_valid = False
    one_ip.save()
    return False


def run():
    t1 = time.time()
    total_ip = ProxyIp.objects.all()
    total_count = len(total_ip)
    pool = Pool()
    pool.map(change_valid, total_ip)
    pool.close()
    pool.join()

    if total_count > settings.MAX_PROXY_NUM:
        num = total_count - settings.MAX_PROXY_NUM
        need_delete = ProxyIp.objects.filter(is_valid=False).order_by('-create_datetime')[:num]
        pool = Pool()
        pool.map(delete_item(), need_delete)
        pool.close()
        pool.join()
    t2 = time.time()

    logging.info(t2-t1)
