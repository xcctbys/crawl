#encoding=utf-8
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
# sys.path.append('/home/clawer/cr-clawer/clawer')
# sys.path.append('/Users/princetechs3/Documents/pyenv/cr-clawer/clawer')
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
from crawler import CrawlerUtils
from bs4 import BeautifulSoup
from smart_proxy.api import Proxy, UseProxy
from enterprise.libs.CaptchaRecognition import CaptchaRecognition

# from gevent import monkey
# monkey.patch_all()

DEBUG = False

# 初始化信息
class InitInfo(object):
	def __init__(self, *args, **kwargs):
		# 验证码图片的存储路径
		self.ckcode_image_path = settings.json_restore_path + '/shanghai/ckcode.jpg'

		self.code_cracker = CaptchaRecognition('zongju')
		if not os.path.exists(os.path.dirname(self.ckcode_image_path)):
			os.makedirs(os.path.dirname(self.ckcode_image_path))
		# 多线程爬取时往最后的json文件中写时的加锁保护
		self.write_file_mutex = threading.Lock()
		self.timeout = 40
		self.urls = {
				'host': 'http://qyxy.baic.gov.cn',
				'official_site': 'https://www.sgs.gov.cn/notice/home',
				'get_checkcode': 'https://www.sgs.gov.cn/notice/captcha?preset=',
				'post_checkcode': 'https://www.sgs.gov.cn/notice/search/ent_info_list',
				# 'get_info_entry': 'http://gsxt.saic.gov.cn/zjgs/search/ent_info_list',  # 获得企业入口
				'open_info_entry': 'https://www.sgs.gov.cn/notice/notice/view?',
				# 获得企业信息页面的url，通过指定不同的tab=1-4来选择不同的内容（工商公示，企业公示...）
				'open_detail_info_entry': ''
				}
# 破解验证码类
class CrackCheckcode(object):
	def __init__(self, info=None, crawler=None, parser=None, *args, **kwargs):
		self.info = info
		self.crawler = crawler
		self.parser = parser
	def crack_checkcode(self):
		"""破解验证码"""
		checkcode_url = self.info.urls['get_checkcode'] + '&ra=' + str(random.random())
		ckcode = ('', '')
		resp = self.crawler.crawl_page_by_url(checkcode_url)
		if resp.status_code != 200:
			logging.error('failed to get checkcode img')
			return ckcode
		page = resp.content
		time.sleep(random.uniform(1, 2))

		with open(self.info.ckcode_image_path, 'wb') as f:
			f.write(page)
		if not self.info.code_cracker:
			logging.error('invalid code cracker with ckcode= None')
			return ckcode
		try:
			ckcode = self.info.code_cracker.predict_result(self.info.ckcode_image_path)
		except Exception as e:
			logging.warn('exception occured when crack checkcode')
			ckcode = ('', '')
			os.remove(self.info.ckcode_image_path)
			time.sleep(10)
		finally:
			pass
		return ckcode
		
	def crawl_check_page(self):
		"""爬取验证码页面，包括获取验证码url，下载验证码图片，破解验证码并提交
		"""
		count = 0
		next_url = self.info.urls['official_site']
		resp = self.crawler.crawl_page_by_url(next_url)
		if resp.status_code != 200:
			logging.error('failed to get official site')
			return False
		if not self.parse_pre_check_page(resp.content):
			logging.error('failed to parse pre check page')
			return False
		print 'self.info.session_token:', self.info.session_token

		while count < 30:
			count += 1
			ckcode = self.crack_checkcode()
			print 'ckcode:', ckcode
			if not ckcode[1]:
				continue
			next_url = self.info.urls['post_checkcode']
			self.info.post_data = {
				'searchType': '1',
				'captcha': ckcode[1],
				'session.token': self.info.session_token,
				'condition.keyword': self.info.ent_number
			}
			print self.info.post_data
			resp = self.crawler.crawl_page_by_url_post(next_url, data=self.info.post_data)
			# print 'resp.requests.headers:', resp.request.headers
			if resp.status_code != 200:
				# print 'resp.status_code:', resp.status_code
				logging.error('faild to crawl url %s' % next_url)
				continue
				# return False
			# print resp.content
			self.info.after_crack_checkcode_page = resp.content
			if self.parse_post_check_page(resp.content):
				return True

			logging.error('crack checkcode failed, total fail count = %d' % count)

			time.sleep(random.uniform(5,10))
		return False

	def parse_post_check_page(self, page):
		"""解析提交验证码之后的页面，获取必要的信息
		"""
		soup = BeautifulSoup(page, 'html.parser')
		# print soup
		div_tag = soup.find('div', attrs={'class': 'link'})
		if not div_tag:
			return False
		open_info_url = div_tag.find('a').get('href')
		m = re.search(r'[/\w\.\?]+=([\w\.=]+)&.+', open_info_url)
		if m:
			self.info.uuid = m.group(1)
			return True
		else:
			return False

	def parse_pre_check_page(self, page):
		"""解析提交验证码之前的页面
		"""
		soup = BeautifulSoup(page, 'html.parser')
		input_tag = soup.find('input', attrs={'type': 'hidden', 'name': 'session.token'})
		if input_tag:
			self.info.session_token = input_tag.get('value')
			return True
		return False
		
	def run(self, ent_number=None):
		self.info.ent_number = ent_number
		print self.info.ent_number
		if not self.crawl_check_page():
			logging.error('crack check code failed, stop to crawl enterprise %s' % self.info.ent_number)
			return False
		return True
	pass
# 自己的爬取类，继承爬取类
class MyCrawler(Crawler):
	def __init__(self, info=None, parser=None, *args, **kwargs):
		useproxy = UseProxy()
		is_use_proxy = useproxy.get_province_is_use_proxy(province='shanghai')
		if not is_use_proxy:
			self.proxies = []
		else:
			proxy = Proxy()
			self.proxies = {'http':'http://'+random.choice(proxy.get_proxy(num=5, province='shanghai')),
						'https':'https://'+random.choice(proxy.get_proxy(num=5, province='shanghai'))}
		print 'self.proxies:', self.proxies

		# self.proxies = []

		self.info = info
		self.parser = MyParser(info=self.info)
		self.write_file_mutex = threading.Lock()
		self.reqst = requests.Session()
		self.reqst.headers.update({
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
				'Accept-Encoding': 'gzip, deflate, br',
				'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
				'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:46.0) Gecko/20100101 Firefox/46.0'})
	def crawl_page_by_url(self, url):
		"""通过url直接获取页面
		"""
		resp = self.reqst.get(url, proxies=self.proxies, timeout=self.info.timeout, verify=False)
		if resp.status_code != 200:
			logging.error('failed to crawl page by url' % url)
			return
		time.sleep(random.uniform(0.2, 1))
		# if saveingtml:
		#     CrawlerUtils.save_page_to_file(self.html_restore_path + 'detail.html', page)
		return resp

	def crawl_page_by_url_post(self, url, data):
		resp = self.reqst.post(url, data=data, proxies=self.proxies, timeout=self.info.timeout, verify=False)
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
		pass

	def parse_post_check_page(self, page):
		"""解析提交验证码之后的页面，获取必要的信息
		"""
		soup = BeautifulSoup(page)
		div_tag = soup.find('div', attrs={'class': 'link'})
		if not div_tag:
			return False
		open_info_url = div_tag.find('a').get('href')
		m = re.search(r'[/\w\.\?]+=([\w\.=]+)&.+', open_info_url)
		if m:
			self.info.uuid = m.group(1)
			return True
		else:
			return False

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

	def parser_classic_ths_tds_from_exists_table(self, what=None, content=None):
		table = content
		# print table
		ths = [th.get_text().strip() for th in table.find_all('th') if th.get_text()][1:]
		for i, th in enumerate(ths):
			if th[:2] == '<<' or th[-2:] == '>>':
				ths = ths[:i]
				break
		if what == 'ent_pub_ent_annual_report':
			tds = []
			for td in table.find_all('td'):
				if td.find_all('a'):
					tds.append(td.get_text().strip())
					tds.append(td.a['href'])
				else:
					tds.append(td.get_text().strip() if td.get_text() else None)
			ths.insert(2, u'详情')
			return (ths, tds)
		tds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]
		print 'len(ths):', len(ths)
		for th in ths:
			print th
		print 'len(tds):', len(tds)
		for td in tds:
			print td

		return self.zip_ths_tds(ths=ths, tds=tds)


	def parser_classic_ths_tds_data(self, what=None, content=None, element=None, attrs=None):
		# print '---------------content-------------------'
		# print content
		table = content.find_all(element, attrs=attrs)[0]
		# print table
		# table = content
		if what == 'ind_comm_pub_arch_liquidation' :
			ths = [th.get_text().strip() for th in table.find_all('th') if th.get_text()]
		else:
			ths = [th.get_text().strip() for th in table.find_all('th') if th.get_text()][1:]
		for i, th in enumerate(ths):
			if th[:2] == '<<' or th[-2:] == '>>':
				ths = ths[:i]
				break
		if what == 'ind_comm_pub_arch_key_persons':
			ths = ths[:int(len(ths)/2)]

		if what == 'ind_comm_pub_reg_shareholder':  # 分析 投资人信息，只返回链接。
			tds = []
			for td in table.find_all('td'):
				if td.find('a'):
					tds.append(td.find('a')['href'])
				else:
					tds.append(td.get_text().strip() if td.get_text() else None)
			return (ths, tds)
		else:
			tds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]
		print 'len(ths):', len(ths)
		for th in ths:
			print th
		print 'len(tds):', len(tds)
		for td in tds:
			print td

		return self.zip_ths_tds(ths=ths, tds=tds)

	def parser_get_a_table_by_head(self, table_head=None):
		all_tables = self.info.source_code_soup.find_all('table')
		for table in all_tables:
			ths = table.find_all('th')
			if ths and ths[0].get_text().strip() == table_head or (ths and ths[0].get_text().strip().find(table_head)!=-1):
				return table
		else:
			return None

	def parser_ent_pub_ent_annual_report(self, content):
		annual_dict = {}
		tables = BeautifulSoup(content, 'html.parser').find_all('table')
		for i, table in enumerate(tables):
			ths = [th.get_text().strip() for th in table.find_all('th') if th.get_text]
			if i==0:
				ths = ths[1:]
			head = ths[0]
			ths = ths[1:]
			tds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]
			annual_dict[head] = self.zip_ths_tds(ths, tds)
		return annual_dict

	def parser_ind_comm_pub_reg_shareholder(self, content):
		page = content
		detail_dict = {}
		list_content = []
		m = re.search(r'investor\.invName = \"(.+)\";', page)
		if m:
			detail_dict[u'股东'] = unicode(m.group(1), 'utf8')

		detail = {}
		m = re.search(r'invt\.subConAm = \"([\d\.]+)\";', page)
		if m:
			detail[u'认缴出资额（万元）'] = m.group(1)

		m = re.search(r'invt\.conDate = \'([\w\-\.]*)\';', page)
		if m:
			detail[u'认缴出资日期'] = m.group(1)

		m = re.search(r'invt\.conForm = \"(.+)\";', page)
		if m:
			detail[u'认缴出资方式'] = m.group(1)

		# paid_in_detail = {}
		m = re.search(r'invtActl\.acConAm = \"([\d\.]+)\";', page)
		if m:
			detail[u'实缴出资额（万元）'] = m.group(1)

		m = re.search(r'invtActl\.conForm = \"(.+)\";', page)
		if m:
			detail[u'实缴出资方式'] = m.group(1)

		m = re.search(r'invtActl\.conDate = \'([\w\-\.]*)\';', page)
		if m:
			detail[u'实缴出资日期'] = m.group(1)

		detail_dict[u'认缴额（万元）'] = detail.get(u'认缴出资额（万元）', '0')
		detail_dict[u'实缴额（万元）'] = detail.get(u'实缴出资额（万元）', '0')
		# detail_dict[u'认缴明细'] = subscribe_detail
		# detail_dict[u'实缴明细'] = paid_in_detail
		list_content.append(detail)
		detail_dict[u"list"] = list_content
		return [detail_dict]

# 工商公示信息
class IndustrialPubliction(object):
	def __init__(self, info=None, crawler=None, parser=None, *args, **kwargs):
		self.info = info
		self.crawler = crawler
		self.parser = parser
	# 登记信息
	def get_registration_info(self, *args, **kwargs):
		table = self.parser.parser_get_a_table_by_head(u'基本信息')
		if table:
			result = self.parser.parser_classic_ths_tds_from_exists_table(what='ind_comm_pub_reg_basic', content=table)
			self.info.result_json['ind_comm_pub_reg_basic'] = result
		else:
			print u'---------在工商公示信息里登记信息中没有发现基本信息表----------------'

		ths, tds = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_reg_shareholder', content=self.info.source_code_soup, element='table', attrs={'id':'investorTable'})
		for i, td in enumerate(tds):
			if td.find('http:')!=-1:
				content = self.crawler.crawl_page_by_url(td).content
				tds[i] = self.parser.parser_ind_comm_pub_reg_shareholder(content)  #再次分析详情。
		self.info.result_json['ind_comm_pub_reg_shareholder'] = self.parser.zip_ths_tds(ths, tds)

		table = self.parser.parser_get_a_table_by_head(u'变更信息')
		if table:
			result = self.parser.parser_classic_ths_tds_from_exists_table(what='ind_comm_pub_reg_modify', content=table)
			self.info.result_json['ind_comm_pub_reg_modify'] = result
		else:
			print u'---------在工商公示信息里登记信息中没有发现变更信息表----------------'
		pass
	# 备案信息
	def get_record_info(self, *args, **kwargs):
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_arch_key_persons', content=self.info.source_code_soup, element='table', attrs={'id':'memberTable'})
		self.info.result_json['ind_comm_pub_arch_key_persons'] = result
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_arch_branch', content=self.info.source_code_soup, element='table', attrs={'id':'branchTable'})
		self.info.result_json['ind_comm_pub_arch_branch'] = result
		# result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_arch_liquidation', content=self.info.source_code_soup, element='table', attrs={'id':'spotcheckTable'})
		self.info.result_json['ind_comm_pub_arch_liquidation'] = [] #result
		pass
	# 动产抵押登记信息
	def get_movable_property_registration_info(self, *args, **kwargs):
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_movable_property_reg', content=self.info.source_code_soup, element='table', attrs={'id':'mortageTable'})
		self.info.result_json['ind_comm_pub_movable_property_reg'] = result
		pass
	# 股权出质登记信息
	def get_stock_equity_pledge_info(self, *args, **kwargs):
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_equity_ownership_reg', content=self.info.source_code_soup, element='table', attrs={'id':'pledgeTable'})
		self.info.result_json['ind_comm_pub_equity_ownership_reg'] = result
		pass
	# 行政处罚信息
	def get_administrative_penalty_info(self, *args, **kwargs):
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_administration_sanction', content=self.info.source_code_soup, element='table', attrs={'id':'punishTable'})
		self.info.result_json['ind_comm_pub_administration_sanction'] = result
		pass
	# 经营异常信息
	def get_abnormal_operation_info(self, *args, **kwargs):
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_business_exception', content=self.info.source_code_soup, element='table', attrs={'id':'exceptTable'})
		self.info.result_json['ind_comm_pub_business_exception'] = result
		pass
	# 严重违法信息
	def get_serious_illegal_info(self, *args, **kwargs):
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_serious_violate_law', content=self.info.source_code_soup, element='table', attrs={'id':'blackTable'})
		self.info.result_json['ind_comm_pub_serious_violate_law'] = result
		pass
	# 抽查检查信息
	def get_spot_check_info(self, *args, **kwargs):
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_spot_check', content=self.info.source_code_soup, element='table', attrs={'id':'spotcheckTable'})
		self.info.result_json['ind_comm_pub_spot_check'] = result
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
		pass

# 企业公示信息
class EnterprisePubliction(object):
	def __init__(self, info=None, crawler=None, parser=None, *args, **kwargs):
		self.info = info
		self.crawler = crawler
		self.parser = parser
	# 企业年报
	def get_corporate_annual_reports_info(self, *args, **kwargs):
		table = self.parser.parser_get_a_table_by_head(u'企业年报')
		if table:
			ths, tds = self.parser.parser_classic_ths_tds_from_exists_table(what='ent_pub_ent_annual_report', content=table)
			for i, td in enumerate(tds):
				if td.find('https:')!=-1:
					resp = self.crawler.crawl_page_by_url(td)
					result = self.parser.parser_ent_pub_ent_annual_report(resp.content)
					tds[i] = result
			self.info.result_json['ent_pub_ent_annual_report'] = self.parser.zip_ths_tds(ths, tds)
		else:
			print u'---------在企业公示信息里没有发现企业年报----------------'
		pass
	# 股东及出资信息
	def get_shareholder_contribution_info(self, *args, **kwargs):
		table = self.parser.parser_get_a_table_by_head(u'股东及出资信息')
		if table:
			result = self.parser.parser_classic_ths_tds_from_exists_table(what='ent_pub_shareholder_capital_contribution', content=table)
			self.info.result_json['ent_pub_shareholder_capital_contribution'] = result
		else:
			print u'---------在企业公示信息里没有发现 股东及出资信息----------------'
		pass
	# 股权变更信息
	def get_equity_change_info(self, *args, **kwargs):
		table = self.parser.parser_get_a_table_by_head(u'变更信息')
		if table:
			result = self.parser.parser_classic_ths_tds_from_exists_table(what='ent_pub_equity_change', content=table)
			self.info.result_json['ent_pub_equity_change'] = result
		else:
			print u'---------在企业公示信息里没有发现 股权变更信息----------------'
		pass
	# 行政许可信息
	def get_administrative_licensing_info(self, *args, **kwargs):
		table = self.parser.parser_get_a_table_by_head(u'行政许可信息')
		if table:
			result = self.parser.parser_classic_ths_tds_from_exists_table(what='ent_pub_administration_license', content=table)
			self.info.result_json['ent_pub_administration_license'] = result
		else:
			print u'---------在企业公示信息里没有发现 行政许可信息----------------'
		pass
	# 知识产权出质登记信息
	def get_intellectual_property_rights_pledge_registration_info(self, *args, **kwargs):
		table = self.parser.parser_get_a_table_by_head(u'知识产权出质登记信息')
		if table:
			result = self.parser.parser_classic_ths_tds_from_exists_table(what='ent_pub_knowledge_property', content=table)
			self.info.result_json['ent_pub_knowledge_property'] = result
		else:
			print u'---------在企业公示信息里没有发现 知识产权出质登记信息----------------'
		pass
	# 行政处罚信息
	def get_administrative_punishment_info(self, *args, **kwargs):
		table = self.parser.parser_get_a_table_by_head(u'行政处罚信息')
		if table:
			result = self.parser.parser_classic_ths_tds_from_exists_table(what='ent_pub_administration_sanction', content=table)
			self.info.result_json['ent_pub_administration_sanction'] = result
		else:
			print u'---------在企业公示信息里没有发现 行政处罚信息----------------'
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
		table = self.parser.parser_get_a_table_by_head(u'行政许可信息')
		if table:
			result = self.parser.parser_classic_ths_tds_from_exists_table(what='other_dept_pub_administration_license', content=table)
			self.info.result_json['other_dept_pub_administration_license'] = result
		else:
			print u'---------在其他部门公示信息信息里没有发现 行政许可信息----------------'
		pass
	# 行政处罚信息
	def get_administrative_punishment_info(self, *args, **kwargs):
		table = self.parser.parser_get_a_table_by_head(u'行政处罚信息')
		if table:
			result = self.parser.parser_classic_ths_tds_from_exists_table(what='other_dept_pub_administration_sanction', content=table)
			self.info.result_json['other_dept_pub_administration_sanction'] = result
		else:
			print u'---------在其他部门公示信息里没有发现 行政处罚信息----------------'
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
		table = self.parser.parser_get_a_table_by_head(u'股权冻结信息')
		if table:
			result = self.parser.parser_classic_ths_tds_from_exists_table(what='judical_assist_pub_equity_freeze', content=table)
			self.info.result_json['judical_assist_pub_equity_freeze'] = result
		else:
			print u'---------在其他部门公示信息里没有发现 股权冻结信息----------------'
		pass
	# 股权冻结信息
	def get_shareholders_change_info(self, *args, **kwargs):
		table = self.parser.parser_get_a_table_by_head(u'股权冻结信息')
		if table:
			result = self.parser.parser_classic_ths_tds_from_exists_table(what='judical_assist_pub_shareholder_modify', content=table)
			self.info.result_json['judical_assist_pub_shareholder_modify'] = result
		else:
			print u'---------在其他部门公示信息里没有发现 股权冻结信息----------------'
		pass
	# 运行逻辑
	def run(self, *args, **kwargs):
		self.get_equity_freeze_info()
		self.get_shareholders_change_info()
		pass

# 省份的爬取类
class ShanghaiCrawler(object):
	"""北京工商公示信息网页爬虫
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
		start_time = time.time()
		self.crack = CrackCheckcode(info=self.info, crawler=self.crawler, parser=self.parser)
		is_valid = self.crack.run(ent_number)
		if not is_valid:
			print 'error,the register is not valid...........'
			return
		end_time = time.time()
		print '------------------------------------crack_spent_time:%s--------------------' % (end_time - start_time)
		
		self.info.result_json_list = []
		self.info.result_json = {}
		# print self.info.after_crack_checkcode_page

		for item_page in BeautifulSoup(self.info.after_crack_checkcode_page, 'html.parser').find_all('div', attrs={'class':'list-item'}):


			self.crack.parser.parse_post_check_page(str(item_page.find_all('a')[0]))
			self.info.ent_number = item_page.find_all('span')[0].get_text().strip()

			print self.info.uuid
			print self.info.ent_number

			print self.info.urls['open_info_entry']+'uuid='+self.info.uuid+'&tab=01'
			self.info.source_code_soup = BeautifulSoup(self.crawler.crawl_page_by_url(self.info.urls['open_info_entry']+'uuid='+self.info.uuid+'&tab=01').content, 'html.parser')

			start_time = time.time()
			industrial = IndustrialPubliction(self.info, self.crawler, self.parser)
			industrial.run()

			print self.info.urls['open_info_entry']+'uuid='+self.info.uuid+'&tab=02'
			self.info.source_code_soup = BeautifulSoup(self.crawler.crawl_page_by_url(self.info.urls['open_info_entry']+'uuid='+self.info.uuid+'&tab=02').content, 'html.parser')

			enterprise = EnterprisePubliction(self.info, self.crawler, self.parser)
			enterprise.run()

			print self.info.urls['open_info_entry']+'uuid='+self.info.uuid+'&tab=03'
			self.info.source_code_soup = BeautifulSoup(self.crawler.crawl_page_by_url(self.info.urls['open_info_entry']+'uuid='+self.info.uuid+'&tab=03').content, 'html.parser')

			other = OtherDepartmentsPubliction(self.info, self.crawler, self.parser)
			other.run()

			print self.info.urls['open_info_entry']+'uuid='+self.info.uuid+'&tab=06'
			self.info.source_code_soup = BeautifulSoup(self.crawler.crawl_page_by_url(self.info.urls['open_info_entry']+'uuid='+self.info.uuid+'&tab=06').content, 'html.parser')

			judical = JudicialAssistancePubliction(self.info, self.crawler, self.parser)
			judical.run()
			end_time = time.time()
			print '---------------------------------------------spent_time---%s----------------------------' % (end_time - start_time)
			print unicode(self.info.result_json).encode('utf-8')
			self.json_dump_to_file('shanghai.json', {self.info.ent_number: self.info.result_json})
			self.info.result_json_list.append( {self.info.ent_number: self.info.result_json})

		# for item in self.info.result_json_list:
		# 	self.json_dump_to_file('beijing.json',  item )
			# self.json_dump_to_file('jiangsu.json', {self.info.ent_number: self.info.result_json})

		return self.info.result_json_list
		

class TestShanghaiCrawler(unittest.TestCase):
	def setUp(self):
		self.info = InitInfo()
		self.crawler = MyCrawler(info=self.info)
		self.parser = MyParser(info=self.info, crawler=self.crawler)

	def test_checkcode(self):
		self.crack = CrackCheckcode(info=self.info, crawler=self.crawler)
		ent_number = '100000000018983'
		is_valid = self.crack.run(ent_number)
		self.assertTrue(is_valid)

	def test_crawler_register_num(self):
		crawler = ShanghaiCrawler('./enterprise_crawler/shanghai.json')
		ent_list = [u'310108000565783']
		for ent_number in ent_list:
			result = crawler.run(ent_number=ent_number)
			self.assertTrue(result)
			self.assertEqual(type(result), list)
	def test_crawler_key(self):
		crawler = ShanghaiCrawler('./enterprise_crawler/shanghai.json')
		ent_list = [u'创业投资中心']
		for ent_number in ent_list:
			crawler.run(ent_number=ent_number)
			self.assertTrue(result)
			self.assertEqual(type(result), list)

if __name__ == '__main__':

	if DEBUG:
		unittest.main()
	crawler = ShanghaiCrawler('./enterprise_crawler/shanghai.json')
	ent_list = [u'310108000565783'] #, u'310000000124581']
	# ent_list = [u'上海爱华投资管理有限公司']
	for ent_number in ent_list:
		crawler.run(ent_number=ent_number)

