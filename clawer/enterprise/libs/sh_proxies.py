#!/usr/bin python
#coding:utf8

import requests
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import os
import os.path
import time
import datetime
import cPickle as pickle
from multiprocessing import Pool, Lock, Value
import multiprocessing

proxy_url = 'http://proxy.ipcn.org/country/'  #国内 IPCN 免费代理
xici_url = 'http://www.xicidaili.com/'			#西刺代理
sixsix_url = 'http://www.66ip.cn/areaindex_'    #66代理

set_path = '/tmp/proxies/proxies.pik'  # pickle 文件保存位置
http_list = []  #用于保存最终有效 ip代理，元素为 'http://x.x.x.x:x'

reqst = requests.Session()
reqst.headers.update(
            {'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

def get_proxy_from_proxy_url(proxy_url):
    resp = reqst.get(proxy_url, timeout=60)
    table = BeautifulSoup(resp.content).find_all('table', attrs={'border':'1', 'size':'85%'})[-1]
    # print [td.get_text().strip() for td in table.find_all('td')[:40]]
    return [td.get_text().strip() for td in table.find_all('td')[:40]]

def get_proxy_from_xici_url(xici_url):
    resp = reqst.get(xici_url, timeout=60)
    trs = BeautifulSoup(resp.content).find_all('tr')[:6]
    a_list = []
    for tr in trs[2:]:
        tds = [td.get_text().strip() for td in tr.find_all('td')]
        http =  "%s:%s" % (tds[1],tds[2])
        a_list.append(http)
    # print a_list
    return a_list

def get_proxy_from_sixsix_url(sixsix_url):
    a_list = []
    for i in range(1,33):
        url = sixsix_url+str(i)+'/'+'1.html'
        try:
            resp = reqst.get(url, timeout=30)
        except:
            continue
        table = BeautifulSoup(resp.content).find_all('table', attrs={'width':'100%', 'border':"2px", 'cellspacing':"0px", 'bordercolor':"#6699ff"})[0]
        trs = table.find_all('tr')[1:3]
        for tr in trs:
            tds = [td.get_text() for td in tr.find_all('td')]
            http = "%s:%s" % (tds[0],tds[1])
            a_list.append(http)
    # print a_list
    return a_list

def test_OK(http):
    print http
    proxies = {'http':'http://'+http,'https':'https://'+http}
    try:
        resp = reqst.get('http://lwons.com/wx', timeout=20, proxies=proxies)
        if resp.status_code == 200:
            return 'http://'+http
        return None
    except:
        return None


if __name__ == '__main__':
    a_list = []
    # http_list = []
    temp_list = get_proxy_from_proxy_url(proxy_url)
    a_list.extend(temp_list)
    temp_list = get_proxy_from_sixsix_url(sixsix_url)
    a_list.extend(temp_list)
    temp_list = get_proxy_from_xici_url(xici_url)
    a_list.extend(temp_list)

    # a_list = [u'119.254.84.90:80', u'122.95.4.75:8118',  u'110.117.204.40:8118',  u'222.39.64.74:8118', u'121.69.36.122:8118', u'121.42.220.79:8088', u'121.69.45.162:8118']

    # print a_list
    pool_size = multiprocessing.cpu_count() * 2
    pool = multiprocessing.Pool(processes= pool_size)
    pool_output = pool.map(test_OK, a_list)
    pool.close()
    pool.join()

    http_list = filter(lambda x: x is not None, pool_output)
    # print http_list

    if not os.path.exists(os.path.dirname(set_path)):
        os.makedirs(os.path.dirname(set_path))
    if http_list:
        f = file(set_path, 'wb')
        pickle.dump(http_list, f, True)
        f.close()

    # f = file(set_path, 'rb')
    # http_list = pickle.load(f)
    # print http_list
    # f.close()

