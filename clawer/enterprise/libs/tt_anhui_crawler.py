#encoding=utf-8
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('/Users/princetechs3/Documents/pyenv/cr-clawer/clawer')
import re
import codecs
import json
import time
import random
import settings
import unittest
import threading
import requests
import logging
from crawler import Crawler, Parser
from bs4 import BeautifulSoup
# from smart_proxy.api import Proxy, UseProxy
from enterprise.libs.CaptchaRecognition import CaptchaRecognition

DEBUG = False

# 初始化信息
class InitInfo(object):
	def __init__(self, *args, **kwargs):
		self.ckcode_image_path = settings.json_restore_path + '/anhui/ckcode.jpg'
		self.code_cracker = CaptchaRecognition('qinghai')
		self.urls = {'eareName':'http://www.ahcredit.gov.cn',
				'search':'http://www.ahcredit.gov.cn/search.jspx',
				'checkCheckNo':'http://www.ahcredit.gov.cn/checkCheckNo.jspx',
				'searchList':'http://www.ahcredit.gov.cn/searchList.jspx',
				'validateCode':'http://www.ahcredit.gov.cn/validateCode.jspx?type=0&id=0.22788021906613765',
				'QueryInvList':'http://www.ahcredit.gov.cn/QueryInvList.jspx?',
				'queryInvDetailAction':'http://www.ahcredit.gov.cn/queryInvDetailAction.jspx?'}
		self.timeout = 20
		self.result_json = {}
		self.result_json_list = []
		pass
# 破解验证码类
class CrackCheckcode(object):
	def __init__(self, info=None, crawler=None, *args, **kwargs):
		self.info = info
		self.crawler = crawler

	def crack_checkcode(self):
		resp = self.crawler.crawl_page_by_url(self.info.urls['search'])
		if resp.status_code != 200:
			return None
		resp = self.crawler.crawl_page_by_url(self.info.urls['validateCode'])
		if resp.status_code != 200:
			return None
		with open(self.info.ckcode_image_path, 'wb') as f:
			f.write(resp.content)

		ck_code = self.info.code_cracker.predict_result(self.info.ckcode_image_path)
		print ck_code
		if not ck_code is None:
			return ck_code[1]
		else:
			return None

	def crawl_check_page(self):
		count = 0
		mainId = None
		while count < 20:
			check_num = self.crack_checkcode()
			print check_num
			if check_num is None:
				count += 1
				continue
			data = {'checkNo':check_num}
			print 'data:', data
			resp = self.crawler.crawl_page_by_url_post(url=self.info.urls['checkCheckNo'], data=data)
			if resp.status_code != 200:
				continue
			if resp.content.find('true')>=0:
				temp={'checkNo':check_num,'entName':self.info.ent_number}
				resp = self.crawler.crawl_page_by_url_post(self.info.urls['searchList'], data=temp)
				if resp.status_code != 200:
					count += 1
					continue
				soup = BeautifulSoup(resp.content, 'html.parser')
				divs = soup.find(class_='list')
				if divs == None:continue
				self.info.after_crack_checkcode_page = resp.content
				self.info.mainId = divs.ul.li.a['href'][divs.ul.li.a['href'].find('id=')+3:]
				return True
				break
			else:
				count += 1
				continue
		else:
			return False

	def parse_post_check_page(self, div_soup):
		self.info.mainId = div_soup.ul.li.a['href'][div_soup.ul.li.a['href'].find('id=')+3:]
		self.info.enterprise_name = div_soup.ul.li.a.get_text().strip()
		self.info.ent_number = div_soup.find_all('span')[0].get_text().strip()


	def run(self, ent_number=None, *args, **kwargs):
		self.info.ent_number = ent_number
		if not self.crawl_check_page():
			logging.error('crack check code failed, stop to crawl enterprise %s' % self.info.ent_number)
			return False
		return True
# 自己的爬取类，继承爬取类
class MyCrawler(Crawler):
	def __init__(self, info=None, parser=None, *args, **kwargs):
		# useproxy = UseProxy()
		# is_use_proxy = useproxy.get_province_is_use_proxy(province='anhui')
		# if not is_use_proxy:
		# 	self.proxies = []
		# else:
		# 	proxy = Proxy()
		# 	self.proxies = {'http':'http://'+random.choice(proxy.get_proxy(num=5, province='anhui')),
		# 				'https':'https://'+random.choice(proxy.get_proxy(num=5, province='anhui'))}
		# print 'self.proxies:', self.proxies

		self.proxies = []

		self.info = info
		self.parser = MyParser(info=self.info)
		self.reqst = requests.Session()
		self.reqst.headers.update({
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
				'Accept-Encoding': 'gzip, deflate, br',
				'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
				'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:46.0) Gecko/20100101 Firefox/46.0'})
	def crawl_page_by_url(self, url):
		"""通过url直接获取页面
		"""
		resp = self.reqst.get(url, proxies=self.proxies, timeout=self.info.timeout)#, verify=False)
		if resp.status_code != 200:
			logging.error('failed to crawl page by url' % url)
			return
		time.sleep(random.uniform(0.2, 1))
		return resp

	def crawl_page_by_url_post(self, url, data):
		resp = self.reqst.post(url, data=data, proxies=self.proxies, timeout=self.info.timeout)#, verify=False)
		if resp.status_code != 200:
			logging.error('failed to crawl page by url' % url)
			return
		time.sleep(random.uniform(0.2, 1))
		return resp
		pass
# 自己的解析类，继承解析类
class MyParser(Parser):
	def __init__(self, *args, **kwargs):
		pass
# 工商公示信息
class IndustrialPubliction(object):
	def __init__(self, *args, **kwargs):
		pass
	# 登记信息
	def get_registration_info(self, *args, **kwargs):
		pass
	# 备案信息
	def get_record_info(self, *args, **kwargs):
		pass
	# 动产抵押登记信息
	def get_movable_property_registration_info(self, *args, **kwargs):
		pass
	# 股权出质登记信息
	def get_stock_equity_pledge_info(self, *args, **kwargs):
		pass
	# 行政处罚信息
	def get_administrative_penalty_info(self, *args, **kwargs):
		pass
	# 经营异常信息
	def get_abnormal_operation_info(self, *args, **kwargs):
		pass
	# 严重违法信息
	def get_serious_illegal_info(self, *args, **kwargs):
		pass
	# 抽查检查信息
	def get_spot_check_info(self, *args, **kwargs):
		pass
	# 运行逻辑
	def run(self, *args, **kwargs):
		pass

# 企业公示信息
class EnterprisePubliction(object):
	def __init__(self, *args, **kwargs):
		pass
	# 企业年报
	def get_corporate_annual_reports_info(self, *args, **kwargs):
		pass
	# 股东及出资信息
	def get_shareholder_contribution_info(self, *args, **kwargs):
		pass
	# 股权变更信息
	def get_equity_change_info(self, *args, **kwargs):
		pass
	# 行政许可信息
	def get_administrative_licensing_info(self, *args, **kwargs):
		pass
	# 知识产权出质登记信息
	def get_intellectual_property_rights_pledge_registration_info(self, *args, **kwargs):
		pass
	# 行政处罚信息
	def get_administrative_punishment_info(self, *args, **kwargs):
		pass
	# 运行逻辑
	def run(self, *args, **kwargs):
		pass
		
# 其他部门公示信息
class OtherDepartmentsPubliction(object):
	def __init__(self, *args, **kwargs):
		pass
	# 行政许可信息
	def get_administrative_licensing_info(self, *args, **kwargs):
		pass
	# 行政处罚信息
	def get_administrative_punishment_info(self, *args, **kwargs):
		pass
	# 运行逻辑
	def run(self, *args, **kwargs):
		pass
		
# 司法协助公示信息
class JudicialAssistancePubliction(object):
	def __init__(self, *args, **kwargs):
		pass
	# 股权冻结信息
	def get_equity_freeze_info(self, *args, **kwargs):
		pass
	# 股东变更信息
	def get_shareholders_change_info(self, *args, **kwargs):
		pass
	# 运行逻辑
	def run(self, *args, **kwargs):
		pass
				
class AnhuiCrawler(object):
	"""江苏工商公示信息网页爬虫
	"""
	def __init__(self, json_restore_path= None, *args, **kwargs):
		self.info = InitInfo()
		self.crawler = MyCrawler(info=self.info)
		self.parser = MyParser(info=self.info, crawler=self.crawler)
	
	def run(self, ent_number=None, *args, **kwargs):
		self.crack = CrackCheckcode(info=self.info, crawler=self.crawler)
		is_valid = self.crack.run(ent_number)
		if not is_valid:
			print 'error,the register is not valid...........'
			return
		# print 'self.info.mainId:', self.info.mainId
		for item_page in BeautifulSoup(self.info.after_crack_checkcode_page, 'html.parser').find_all('div', attrs={'class':'list'}):
			# print item_page
			print self.info.ent_number
			self.info.result_json = {}
			start_time = time.time()
			self.crack.parse_post_check_page(item_page)
			print 'self.info.mainId:', self.info.mainId
			print 'self.info.enterprise_name:', self.info.enterprise_name
			print 'self.info.ent_number:', self.info.ent_number
			industrial = IndustrialPubliction(self.info, self.crawler, self.parser)
			industrial.run()
			enterprise = EnterprisePubliction(self.info, self.crawler, self.parser)
			enterprise.run()
			other = OtherDepartmentsPubliction(self.info, self.crawler, self.parser)
			other.run()
			judical = JudicialAssistancePubliction(self.info, self.crawler, self.parser)
			judical.run()
		return self.info.result_json_list
		
class TestAnhuiCrawler(unittest.TestCase):
	def setUp(self):
		self.info = InitInfo()
		self.crawler = MyCrawler(info=self.info)
		self.parser = MyParser(info=self.info, crawler=self.crawler)

	def test_checkcode(self):
		self.crack = CrackCheckcode(info=self.info, crawler=self.crawler)
		ent_number = '340100001355674'
		is_valid = self.crack.run(ent_number)
		self.assertTrue(is_valid)

	def test_crawler_register_num(self):
		crawler = ZongjuCrawler('./enterprise_crawler/anhui.json')
		ent_list = ['340100001355674']
		for ent_number in ent_list:
			result = crawler.run(ent_number=ent_number)
			self.assertTrue(result)
			self.assertEqual(type(result), list)
	def test_crawler_key(self):
		crawler = ZongjuCrawler('./enterprise_crawler/anhui.json')
		ent_list = [u'安徽信风投资管理有限公司']
		for ent_number in ent_list:
			crawler.run(ent_number=ent_number)
			self.assertTrue(result)
			self.assertEqual(type(result), list)
			
if __name__ == '__main__':
	if DEBUG:
		unittest.main()
	else:
		crawler = AnhuiCrawler('./enterprise_crawler/anhui.json')
		ent_list = [u'340100001355674']
		ent_list = [u'信用']
		for ent_number in ent_list:
			crawler.run(ent_number=ent_number)
