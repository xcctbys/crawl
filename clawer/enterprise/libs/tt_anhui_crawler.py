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
		if not os.path.exists(self.ckcode_image_path):
			os.makedirs(os.path.dirname(self.ckcode_image_path))
		self.urls = {'eareName':'http://www.ahcredit.gov.cn',
				'search':'http://www.ahcredit.gov.cn/search.jspx',
				'checkCheckNo':'http://www.ahcredit.gov.cn/checkCheckNo.jspx',
				'searchList':'http://www.ahcredit.gov.cn/searchList.jspx',
				'validateCode':'http://www.ahcredit.gov.cn/validateCode.jspx?type=0&id=0.22788021906613765',
				'QueryInvList':'http://www.ahcredit.gov.cn/QueryInvList.jspx?',
				'queryInvDetailAction':'http://www.ahcredit.gov.cn/queryInvDetailAction.jspx?',

				'businessPublicity':'http://www.ahcredit.gov.cn/businessPublicity.jspx?',
				'enterprisePublicity':'http://www.ahcredit.gov.cn/enterprisePublicity.jspx?',
				'otherDepartment':'http://www.ahcredit.gov.cn/otherDepartment.jspx?',
				'justiceAssistance':'http://www.ahcredit.gov.cn/justiceAssistance.jspx?'}
		self.timeout = 30
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
		print 'self.info.ckcode_image_path:', self.info.ckcode_image_path
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
	def __init__(self, info=None, crawler=None, *args, **kwargs):
		self.info = info

	def zip_ths_tds(self, ths=None, tds=None):
		if len(tds) > len(ths):
			temp_list = []
			x = 0
			y = x + len(ths)
			while y <= len(tds):
				temp_list.append(dict(zip(ths, tds[x:y])))
				x = y
				y = x + len(ths)
			return temp_list
		else:
			need_dict = dict(zip(ths, tds))
			return [need_dict] if need_dict else []

	def parser_classic_ths_from_exists_table(self, what=None, content=None):
		table = content
		# print table
		ths = [th.get_text().strip() for th in table.find_all('th') if th.get_text()][1:]
		for i, th in enumerate(ths):
			if th[:2] == '<<' or th[-2:] == '>>':
				ths = ths[:i]
				break
		if what == 'ent_pub_ent_annual_report':
			ths.insert(2, u'详情')
		if what == 'ind_comm_pub_arch_key_persons':
			ths = ths[:int(len(ths)/2)]
		print 'len(ths):', len(ths)
		for th in ths:
			print th
		return ths

	def parser_classic_tds_from_exists_table(self, what=None, content=None):
		table = content
		if what == 'ent_pub_ent_annual_report':
			tds = []
			for td in table.find_all('td'):
				if td.find_all('a'):
					tds.append(td.get_text().strip())
					tds.append(self.info.urls['eareName'] + td.a['href'])
				else:
					tds.append(td.get_text().strip() if td.get_text() else None)
		elif what == 'ind_comm_pub_reg_shareholder':
			tds = []
			for td in table.find_all('td'):
				if td.find_all('a'):
					# tds.append(td.get_text().strip())
					tds.append(self.info.urls['eareName'] + td.a['onclick'][13:-2])
				else:
					tds.append(td.get_text().strip() if td.get_text() else None)
			
		else:
			try:
				tds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]
			except Exception as e:
				tds = []
		
		print 'len(tds):', len(tds)
		for td in tds:
			print td
		return tds




	def parser_ind_comm_pub_reg_shareholder_detail(self, what=None, content=None):
		table = content
		ths = [th.get_text().strip() for th in table.find_all('th') if th.get_text()][1:]
		ths = ths[:3]+ths[5:]
		tds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]
		return self.zip_ths_tds(ths, tds)

		pass

	def parser_get_a_table_by_head(self, table_head_list=None):   #通过一个table的head 返回这个 table
		tables = self.info.page_soup_tables
		count_table = len(tables)
		for i,table in enumerate(tables):
			try:
				if table.tr.th.get_text().split('\n')[0].strip() in table_head_list:
					if i !=0 and i+2 < count_table and len(tables[i+2].find_all('a'))>1:
						#print i,'have next',
						# print tables[i]
						# print tables[i+2]
						return (tables[i], tables[i+2], True)
					elif  i+1<count_table:
						#print i,'no next'
						return (tables[i], tables[i+1], False)
			except AttributeError:
				return ([], [], False)
				pass

	def parser_ent_pub_ent_annual_report(self, content):  #单独解析企业年报详情页面。
		annual_dict = {}
		tables = BeautifulSoup(content, 'html.parser').find_all('table')
		for i, table in enumerate(tables):
			ths = [th.get_text().strip() for th in table.find_all('th') if th.get_text]
			if i==0:
				ths = ths[1:]
			for i, th in enumerate(ths):
				if th[:2] == '<<' or th[-2:] == '>>':
					ths = ths[:i]
					break
			head = ths[0]
			ths = ths[1:]
			tds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]
			annual_dict[head] = self.zip_ths_tds(ths, tds)
		return annual_dict


# 工商公示信息
class IndustrialPubliction(object):
	def __init__(self, info=None, crawler=None, parser=None, *args, **kwargs):
		self.info = info
		self.crawler = crawler
		self.parser = parser
	# 登记信息
	def get_registration_info(self, *args, **kwargs):
		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'基本信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='ind_comm_pub_reg_basic', content=table)
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_reg_basic', content=table)
			self.info.result_json['ind_comm_pub_reg_basic'] = self.parser.zip_ths_tds(ths, tds)
		else:
			print u'---------在工商公示信息里登记信息中没有发现基本信息表----------------'

		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'股东信息', u'股东（发起人）信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='ind_comm_pub_reg_shareholder', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 股东信息表----------------'
		if is_next_page:
			pass
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_reg_shareholder', content=next_table)
			for i, td in enumerate(tds):
				if td.find('http:')!=-1:
					page = self.crawler.crawl_page_by_url(td).content
					soup = BeautifulSoup(page, 'html.parser').find_all('table')[0]
					tds[i] = self.parser.parser_ind_comm_pub_reg_shareholder_detail(what='ind_comm_pub_reg_shareholder', content=soup)
		self.info.result_json['ind_comm_pub_reg_shareholder'] = self.parser.zip_ths_tds(ths, tds)
		pass

		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'变更信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='ind_comm_pub_reg_modify', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现变更信息表----------------'
		if is_next_page:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_reg_modify', content=next_table)
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_reg_modify', content=next_table)
		self.info.result_json['ind_comm_pub_reg_modify'] = self.parser.zip_ths_tds(ths, tds)
		pass
	# 备案信息
	def get_record_info(self, *args, **kwargs):
		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'主要人员信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='ind_comm_pub_arch_key_persons', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现变 主要人员信息----------------'
		if is_next_page:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_arch_key_persons', content=next_table)
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_arch_key_persons', content=next_table)
		self.info.result_json['ind_comm_pub_arch_key_persons'] = self.parser.zip_ths_tds(ths, tds)

		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'分支机构信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='ind_comm_pub_arch_branch', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 分支机构信息----------------'
		if is_next_page:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_arch_branch', content=next_table)
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_arch_branch', content=next_table)
		self.info.result_json['ind_comm_pub_arch_branch'] = self.parser.zip_ths_tds(ths, tds)

		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'清算信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='ind_comm_pub_arch_liquidation', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 清算信息---------------'
		if is_next_page:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_arch_liquidation', content=next_table)
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_arch_liquidation', content=next_table)
		self.info.result_json['ind_comm_pub_arch_liquidation'] = self.parser.zip_ths_tds(ths, tds)
		pass
	# 动产抵押登记信息
	def get_movable_property_registration_info(self, *args, **kwargs):
		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'动产抵押登记信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='ind_comm_pub_movable_property_reg', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 动产抵押登记信息---------------'
		if is_next_page:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_movable_property_reg', content=next_table)
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_movable_property_reg', content=next_table)
		self.info.result_json['ind_comm_pub_movable_property_reg'] = self.parser.zip_ths_tds(ths, tds)
		pass
	# 股权出质登记信息
	def get_stock_equity_pledge_info(self, *args, **kwargs):
		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'股权出质登记信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='ind_comm_pub_equity_ownership_reg', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 股权出质登记信息---------------'
		if is_next_page:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_equity_ownership_reg', content=next_table)
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_equity_ownership_reg', content=next_table)
		self.info.result_json['ind_comm_pub_equity_ownership_reg'] = self.parser.zip_ths_tds(ths, tds)
		pass
	# 行政处罚信息
	def get_administrative_penalty_info(self, *args, **kwargs):
		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'行政处罚信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='ind_comm_pub_administration_sanction', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 行政处罚信息---------------'
		if is_next_page:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_administration_sanction', content=next_table)
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_administration_sanction', content=next_table)
		self.info.result_json['ind_comm_pub_administration_sanction'] = self.parser.zip_ths_tds(ths, tds)
		pass
	# 经营异常信息
	def get_abnormal_operation_info(self, *args, **kwargs):
		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'经营异常信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='ind_comm_pub_business_exception', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 经营异常信息---------------'
		if is_next_page:
			pass
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_business_exception', content=next_table)
		self.info.result_json['ind_comm_pub_business_exception'] = self.parser.zip_ths_tds(ths, tds)
		pass
	# 严重违法信息
	def get_serious_illegal_info(self, *args, **kwargs):
		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'严重违法信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='ind_comm_pub_serious_violate_law', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 严重违法信息---------------'
		if is_next_page:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_serious_violate_law', content=next_table)
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_serious_violate_law', content=next_table)
		self.info.result_json['ind_comm_pub_serious_violate_law'] = self.parser.zip_ths_tds(ths, tds)
		pass
	# 抽查检查信息
	def get_spot_check_info(self, *args, **kwargs):
		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'抽查检查信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='ind_comm_pub_spot_check', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 抽查检查信息---------------'
		if is_next_page:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_spot_check', content=next_table)
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ind_comm_pub_spot_check', content=next_table)
		self.info.result_json['ind_comm_pub_spot_check'] = self.parser.zip_ths_tds(ths, tds)
		pass
	# 运行逻辑
	def run(self, *args, **kwargs):
		self.get_registration_info()
		self.get_record_info()
		self.get_movable_property_registration_info()
		self.get_stock_equity_pledge_info()
		self.get_administrative_penalty_info()
		self.get_abnormal_operation_info()
		self.get_serious_illegal_info()
		self.get_spot_check_info()

# 企业公示信息
class EnterprisePubliction(object):
	def __init__(self, info=None, crawler=None, parser=None, *args, **kwargs):
		self.info = info
		self.crawler = crawler
		self.parser = parser
	# 企业年报
	def get_corporate_annual_reports_info(self, *args, **kwargs):
		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'企业年报'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='ent_pub_ent_annual_report', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 企业年报---------------'
		if is_next_page:
			pass
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ent_pub_ent_annual_report', content=table)
			for i, td in enumerate(tds):
				if td.find('http:') != -1:
					page = self.crawler.crawl_page_by_url(td).content
					tds[i] = self.parser.parser_ent_pub_ent_annual_report(page)
		self.info.result_json['ent_pub_ent_annual_report'] = self.parser.zip_ths_tds(ths, tds)
		pass
	# 股东及出资信息
	def get_shareholder_contribution_info(self, *args, **kwargs):
		try:
			table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'股东及出资信息'])
		except Exception as e:
			print e
			self.info.result_json['ent_pub_shareholder_capital_contribution'] = []
			return 
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='ent_pub_shareholder_capital_contribution', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 股东及出资信息---------------'
		if is_next_page:
			pass
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ent_pub_shareholder_capital_contribution', content=next_table)
		self.info.result_json['ent_pub_shareholder_capital_contribution'] = self.parser.zip_ths_tds(ths, tds)
		pass
	# 股权变更信息
	def get_equity_change_info(self, *args, **kwargs):
		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'股权变更信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='ent_pub_equity_change', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 股权变更信息---------------'
		if is_next_page:
			pass
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ent_pub_equity_change', content=next_table)
		self.info.result_json['ent_pub_equity_change'] = self.parser.zip_ths_tds(ths, tds)
		pass
	# 行政许可信息
	def get_administrative_licensing_info(self, *args, **kwargs):
		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'行政许可信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='ent_pub_administration_license', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 行政许可信息---------------'
		if is_next_page:
			pass
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ent_pub_administration_license', content=next_table)
		self.info.result_json['ent_pub_administration_license'] = self.parser.zip_ths_tds(ths, tds)
		pass
	# 知识产权出质登记信息
	def get_intellectual_property_rights_pledge_registration_info(self, *args, **kwargs):
		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'知识产权出质登记信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='ent_pub_knowledge_property', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 知识产权出质登记信息---------------'
		if is_next_page:
			pass
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ent_pub_knowledge_property', content=next_table)
		self.info.result_json['ent_pub_knowledge_property'] = self.parser.zip_ths_tds(ths, tds)
		pass
	# 行政处罚信息
	def get_administrative_punishment_info(self, *args, **kwargs):
		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'行政处罚信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='ent_pub_administration_sanction', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 行政处罚信息---------------'
		if is_next_page:
			pass
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='ent_pub_administration_sanction', content=next_table)
		self.info.result_json['ent_pub_administration_sanction'] = self.parser.zip_ths_tds(ths, tds)
		pass
	# 运行逻辑
	def run(self, *args, **kwargs):
		self.get_corporate_annual_reports_info()
		self.get_shareholder_contribution_info()
		self.get_equity_change_info()
		self.get_administrative_licensing_info()
		self.get_intellectual_property_rights_pledge_registration_info()
		self.get_administrative_punishment_info()
		pass
		
# 其他部门公示信息
class OtherDepartmentsPubliction(object):
	def __init__(self, info=None, crawler=None, parser=None, *args, **kwargs):
		self.info = info
		self.crawler = crawler
		self.parser = parser
	# 行政许可信息
	def get_administrative_licensing_info(self, *args, **kwargs):
		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'行政许可信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='other_dept_pub_administration_license', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 行政许可信息---------------'
		if is_next_page:
			pass
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='other_dept_pub_administration_license', content=next_table)
		self.info.result_json['other_dept_pub_administration_license'] = self.parser.zip_ths_tds(ths, tds)
		pass
	# 行政处罚信息
	def get_administrative_punishment_info(self, *args, **kwargs):
		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'行政处罚信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='other_dept_pub_administration_sanction', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 行政处罚信息---------------'
		if is_next_page:
			pass
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='other_dept_pub_administration_sanction', content=next_table)
		self.info.result_json['other_dept_pub_administration_sanction'] = self.parser.zip_ths_tds(ths, tds)
		pass
	# 运行逻辑
	def run(self, *args, **kwargs):
		self.get_administrative_licensing_info()
		self.get_administrative_punishment_info()
		pass
		
# 司法协助公示信息
class JudicialAssistancePubliction(object):
	def __init__(self, info=None, crawler=None, parser=None, *args, **kwargs):
		self.info = info
		self.crawler = crawler
		self.parser = parser
	# 股权冻结信息
	def get_equity_freeze_info(self, *args, **kwargs):
		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'股权冻结信息', u'司法股权冻结信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='judical_assist_pub_equity_freeze', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 股权冻结信息---------------'
		if is_next_page:
			pass
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='judical_assist_pub_equity_freeze', content=next_table)
		self.info.result_json['judical_assist_pub_equity_freeze'] = self.parser.zip_ths_tds(ths, tds)
		pass
	# 股东变更信息
	def get_shareholders_change_info(self, *args, **kwargs):
		table, next_table, is_next_page = self.parser.parser_get_a_table_by_head([u'股东变更信息', u'司法股东变更登记信息'])
		if table:
			ths = self.parser.parser_classic_ths_from_exists_table(what='judical_assist_pub_shareholder_modify', content=table)
		else:
			ths = []
			print u'---------在工商公示信息里登记信息中没有发现 股东变更信息---------------'
		if is_next_page:
			pass
		else:
			tds = self.parser.parser_classic_tds_from_exists_table(what='judical_assist_pub_shareholder_modify', content=next_table)
		self.info.result_json['judical_assist_pub_shareholder_modify'] = self.parser.zip_ths_tds(ths, tds)
		pass
	# 运行逻辑
	def run(self, *args, **kwargs):
		self.get_equity_freeze_info()
		self.get_shareholders_change_info()
				
class AnhuiCrawler(object):
	"""江苏工商公示信息网页爬虫
	"""
	def __init__(self, json_restore_path= None, *args, **kwargs):
		self.info = InitInfo()
		self.crawler = MyCrawler(info=self.info)
		self.parser = MyParser(info=self.info, crawler=self.crawler)

	def json_dump_to_file(self, path, json_dict):
		write_type = 'wb'
		if os.path.exists(path):
			write_type = 'a'
		with codecs.open(path, write_type, 'utf-8') as f:
			f.write(json.dumps(json_dict, ensure_ascii=False)+'\n')
	
	def run(self, ent_number=None, *args, **kwargs):
		self.crack = CrackCheckcode(info=self.info, crawler=self.crawler)
		is_valid = self.crack.run(ent_number)
		if not is_valid:
			print 'error,the register is not valid...........'
			return
		# print 'self.info.mainId:', self.info.mainId
		self.info.result_json_list = []
		for item_page in BeautifulSoup(self.info.after_crack_checkcode_page, 'html.parser').find_all('div', attrs={'class':'list'}):
			# print item_page
			print self.info.ent_number
			self.info.result_json = {}
			start_time = time.time()
			self.crack.parse_post_check_page(item_page)
			print 'self.info.mainId:', self.info.mainId
			print 'self.info.enterprise_name:', self.info.enterprise_name
			print 'self.info.ent_number:', self.info.ent_number
			self.info.source_code_soup = BeautifulSoup(self.crawler.crawl_page_by_url(self.info.urls['businessPublicity'] + 'id=' +self.info.mainId).content, 'html.parser')
			print 'table_page:', self.info.source_code_soup
			self.info.page_soup_tables = self.info.source_code_soup.find_all('table')
			industrial = IndustrialPubliction(self.info, self.crawler, self.parser)
			industrial.run()
			self.info.source_code_soup = BeautifulSoup(self.crawler.crawl_page_by_url(self.info.urls['enterprisePublicity'] + 'id=' +self.info.mainId).content, 'html.parser')
			print 'table_page:', self.info.source_code_soup
			self.info.page_soup_tables = self.info.source_code_soup.find_all('table')
			enterprise = EnterprisePubliction(self.info, self.crawler, self.parser)
			enterprise.run()
			self.info.source_code_soup = BeautifulSoup(self.crawler.crawl_page_by_url(self.info.urls['otherDepartment'] + 'id=' +self.info.mainId).content, 'html.parser')
			print 'table_page:', self.info.source_code_soup
			self.info.page_soup_tables = self.info.source_code_soup.find_all('table')
			other = OtherDepartmentsPubliction(self.info, self.crawler, self.parser)
			other.run()
			self.info.source_code_soup = BeautifulSoup(self.crawler.crawl_page_by_url(self.info.urls['justiceAssistance'] + 'id=' +self.info.mainId).content, 'html.parser')
			print 'table_page:', self.info.source_code_soup
			self.info.page_soup_tables = self.info.source_code_soup.find_all('table')
			judical = JudicialAssistancePubliction(self.info, self.crawler, self.parser)
			judical.run()

			self.json_dump_to_file('anhui.json', {self.info.ent_number: self.info.result_json})
			self.info.result_json_list.append({self.info.ent_number: self.info.result_json})
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
		ent_list = [u'安徽省徽商集团化轻股份有限公司']
		for ent_number in ent_list:
			crawler.run(ent_number=ent_number)
