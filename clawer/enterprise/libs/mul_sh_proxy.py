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

proxy_url = 'http://proxy.ipcn.org/country/'
xici_url = 'http://www.xicidaili.com/'
sixsix_url = 'http://www.66ip.cn/areaindex_'

set_path = '/tmp/proxies/proxies.pik'
lock = Lock()
http_list = []

reqst = requests.Session()
reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

def get_proxy_from_proxy_url(proxy_url):
	resp = reqst.get(proxy_url, timeout=60)
	table = BeautifulSoup(resp.content).find_all('table', attrs={'border':'1', 'size':'85%'})[-1]
	print [td.get_text().strip() for td in table.find_all('td')[:30]]
	return [td.get_text().strip() for td in table.find_all('td')[:30]]

def get_proxy_from_xici_url(xici_url):
	resp = reqst.get(xici_url, timeout=60)
	trs = BeautifulSoup(resp.content).find_all('tr')[:6]
	a_list = []
	for tr in trs[2:]:
		tds = [td.get_text().strip() for td in tr.find_all('td')]
		http =  "%s:%s" % (tds[1],tds[2])
		a_list.append(http)
	print a_list
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
		trs = table.find_all('tr')[1:4]
		for tr in trs:
			tds = [td.get_text() for td in tr.find_all('td')]
			http = "%s:%s" % (tds[0],tds[1])
			a_list.append(http)
	print a_list
	return a_list

def test_OK(http):
	print http
	proxies = {'http':'http://'+http,'https':'https://'+http}
	try:
		resp = reqst.get('http://lwons.com/wx', timeout=10, proxies=proxies)
		if resp.status_code == 200:
			# print 'yes:', http
			# global http_list
			# http_list.append('http://'+http)
			# print http_list
			return True
		return False
	except:
		return False


if __name__ == '__main__':
	a_list = []
	# http_list = []
	temp_list = get_proxy_from_proxy_url(proxy_url)
	a_list.extend(temp_list)
	temp_list = get_proxy_from_sixsix_url(sixsix_url)
	a_list.extend(temp_list)
	temp_list = get_proxy_from_xici_url(xici_url)
	a_list.extend(temp_list)

	print a_list
	# pool = Pool(processes=12)
	for http in a_list:
		if test_OK(http):
			http_list.append('http://'+http)
		# pool.apply_async(test_OK, args=(http,))
	# pool.map(test_OK, args=(a_list, http_list))
	pool.close()
	pool.join()
	print http_list

	if not os.path.exists(os.path.dirname(set_path)):
		os.makedirs(os.path.dirname(set_path))
	if http_list:
		f = file(set_path, 'wb')
		pickle.dump(http_list, f, True)
		f.close()

	f = file(set_path, 'rb')
	http_list = pickle.load(f)
	print http_list
	f.close()

