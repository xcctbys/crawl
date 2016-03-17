#coding:utf8
import os
import os.path
import sys
import random
import cPickle as pickle

import requests

from . import settings


class Proxies(object):
	def __init__(self):
		# self.dir = os.path.join(os.getcwd(), 'proxies')
		# self.filename = self.get_last_time_filename(self.dir)
		self.filename = settings.proxies_file_path
		self.reqst = requests.Session()
		self.reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

	def load_pickle(self):
		f = file(self.filename, 'rb')
		a_list = pickle.load(f)
		return a_list

	def test_OK(self, proxies):
		try:
			resp = self.reqst.get('http://www.baidu.com',timeout=5, proxies=proxies)
			if resp.status_code == 200:
				return True
			return False
		except:
			return False

	def get_proxies(self):
		a_list = self.load_pickle()
		# count = 0
		# while count < 2:
		# 	proxies = {'http':random.choice(a_list), 'https': random.choice(a_list)}
		# 	if self.test_OK(proxies):
		# 		return proxies
		# 	count+= 1
		return {'http':random.choice(a_list), 'https': random.choice(a_list)}
"""
if __name__ == '__main__':
	stand = GetProxies()
	print stand.get_proxies()
"""
