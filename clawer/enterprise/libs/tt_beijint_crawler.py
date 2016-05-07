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
from crawler import CrawlerUtils
from bs4 import BeautifulSoup
from enterprise.libs.CaptchaRecognition import CaptchaRecognition

DEBUG = False

# 初始化信息
class InitInfo(object):
	def __init__(self, *args, **kwargs):
		#html数据的存储路径
		self.html_restore_path = settings.json_restore_path + '/beijing/'
		#验证码图片的存储路径
		self.ckcode_image_path = settings.json_restore_path + '/beijing/ckcode.jpg'
		self.code_cracker = CaptchaRecognition('beijing')
		#多线程爬取时往最后的json文件中写时的加锁保护
		self.write_file_mutex = threading.Lock()
		# self.json_restore_path = settings.json_restore_path
		self.credit_ticket = None
		if not os.path.exists(self.html_restore_path):
			os.makedirs(self.html_restore_path)
		self.timeout = 20
		self.ent_id = ''

		self.urls = {'host': 'http://qyxy.baic.gov.cn',
				'official_site': 'http://qyxy.baic.gov.cn/beijing',
				'get_checkcode': 'http://qyxy.baic.gov.cn',
				'post_checkcode': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!checkCode.dhtml',
				'open_info_entry': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!getBjQyList.dhtml',
				'ind_comm_pub_reg_basic': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!openEntInfo.dhtml?',
				'ind_comm_pub_reg_shareholder': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!tzrFrame.dhtml?',
				'ind_comm_pub_reg_modify': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!biangengFrame.dhtml?',
				'ind_comm_pub_arch_key_persons': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!zyryFrame.dhtml?',
				'ind_comm_pub_arch_branch': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!fzjgFrame.dhtml?',
				'ind_comm_pub_arch_liquidation': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!qsxxFrame.dhtml?',
				'ind_comm_pub_movable_property_reg': 'http://qyxy.baic.gov.cn/gjjbjTab/gjjTabQueryCreditAction!dcdyFrame.dhtml?',
				'ind_comm_pub_equity_ownership_reg': 'http://qyxy.baic.gov.cn/gdczdj/gdczdjAction!gdczdjFrame.dhtml?',
				'ind_comm_pub_administration_sanction': 'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list.dhtml?',
				'ind_comm_pub_business_exception': 'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list_jyycxx.dhtml?',
				'ind_comm_pub_serious_violate_law':   'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list_yzwfxx.dhtml?',
				'ind_comm_pub_spot_check':   'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list_ccjcxx.dhtml?',
				'ent_pub_ent_annual_report':   'http://qyxy.baic.gov.cn/qynb/entinfoAction!qyxx.dhtml?',
				'ent_pub_shareholder_capital_contribution':   'http://qyxy.baic.gov.cn/gdcz/gdczAction!list_index.dhtml?',
				'ent_pub_equity_change':   'http://qyxy.baic.gov.cn/gdgq/gdgqAction!gdgqzrxxFrame.dhtml?',
				'ent_pub_administration_license':   'http://qyxy.baic.gov.cn/xzxk/xzxkAction!list_index.dhtml?',
				'ent_pub_knowledge_property':   'http://qyxy.baic.gov.cn/zscqczdj/zscqczdjAction!list_index.dhtml?',
				'ent_pub_administration_sanction':   'http://qyxy.baic.gov.cn/gdgq/gdgqAction!qyxzcfFrame.dhtml?',
				'other_dept_pub_administration_license':   'http://qyxy.baic.gov.cn/qtbm/qtbmAction!list_xzxk.dhtml?',
				'other_dept_pub_administration_sanction':   'http://qyxy.baic.gov.cn/qtbm/qtbmAction!list_xzcf.dhtml?',
				'shareholder_detail': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!touzirenInfo.dhtml?',
				'annual_report_detail' : 'http://qyxy.baic.gov.cn/entPub/entPubAction!gdcz_bj.dhtml',
				'annual_report_detail_for_fro' : 'http://qyxy.baic.gov.cn/entPub/entPubAction!qydwdb_bj.dhtml',
				'annual_report_detail_change' : 'http://qyxy.baic.gov.cn/entPub/entPubAction!qybg_bj.dhtml',
				}

# 破解验证码类
class CrackCheckcode(object):
	def __init__(self, info=None, crawler=None, parser=None, *args, **kwargs):
		self.info = info
		self.crawler = crawler
		self.parser = parser
	def crawl_check_page(self):
		"""爬取验证码页面，包括获取验证码url，下载验证码图片，破解验证码并提交
		"""
		resp = self.crawler.crawl_page_by_url(self.info.urls['official_site'])
		# if resp.status_code != 200:
		# 	logging.error('failed to get official site page!')
		# 	return False
		count = 0
		while count < 15:
			count += 1
			ckcode = self.crack_checkcode()
			if not ckcode[1]:
				logging.error('failed to get crackcode result, fail count = %d' % (count))
				continue

			post_data = {'currentTimeMillis': self.info.time_stamp, 'credit_ticket': self.info.credit_ticket, 'checkcode': ckcode[1], 'keyword': self.info.ent_number};
			next_url = self.info.urls['post_checkcode']
			resp = self.crawler.crawl_page_by_url_post(next_url, data=post_data)
			if resp.status_code != 200:
				logging.error('failed to get crackcode image by url %s, fail count = %d' % (next_url, count))
				continue

			logging.error('crack code = %s, %s, response =  %s' %(ckcode[0], ckcode[1], resp.content))

			if resp.content == 'fail':
			# if resp == 'fail':
				logging.error('crack checkcode failed, response content = failed, total fail count = %d' % count)
				time.sleep(random.uniform(0.1,2))
				continue

			next_url = self.info.urls['open_info_entry']
			resp = self.crawler.crawl_page_by_url_post(next_url, data=post_data)
			if resp.status_code != 200:
				logging.error('failed to open info entry by url %s, fail count = %d' % (next_url, count))
				continue

			# crack_result = self.parse_post_check_page(resp.content)
			self.info.after_crack_checkcode_page = resp.content
			return True
			# crack_result = self.parser.parse_post_check_page(resp)
			# if crack_result:
			# 	return True
			# else:
			# 	logging.error('crack checkcode failed, total fail count = %d' % count)
			# time.sleep(random.uniform(3,5))
		return False
	def crack_checkcode(self):
		"""破解验证码"""
		ckcode = ('', '')
		checkcode_url = self.get_checkcode_url()
		# print 'checkcode_url',checkcode_url
		if checkcode_url == None:
			return ckcode
		resp = self.crawler.crawl_page_by_url(checkcode_url)
		if resp.status_code != 200:
			logging.error('failed to get checkcode img')
			return ckcode
		page = resp.content
		# page = resp
		time.sleep(random.uniform(1,2))
		self.crawler.write_file_mutex.acquire()
		with open(self.info.ckcode_image_path, 'wb') as f:
			f.write(page)
		if not self.info.code_cracker:
			logging.error('invalid code cracker\n')
			return ckcode
		try:
			ckcode = self.info.code_cracker.predict_result(self.info.ckcode_image_path)
		except Exception as e:
			logging.error('exception occured when crack checkcode')
			ckcode = ('', '')
		finally:
			pass
		self.crawler.write_file_mutex.release()
		return ckcode

	def get_checkcode_url(self):
		count  = 0
		while count < 5:
			count+=1
			resp = self.crawler.crawl_page_by_url(self.info.urls['official_site'])
			time.sleep(random.uniform(1, 5))
			if resp.status_code != 200:
				logging.error('failed to get crackcode url')
				continue
			response = resp.content
			# response = resp
			soup = BeautifulSoup(response, 'html.parser')
			ckimg_src = soup.find_all('img', id='MzImgExpPwd')[0].get('src')
			ckimg_src = str(ckimg_src)
			re_checkcode_captcha=re.compile(r'/([\s\S]*)\?currentTimeMillis')
			# re_currenttime_millis=re.compile(r'/CheckCodeCaptcha\?currentTimeMillis=([\s\S]*)')
			checkcode_type = re_checkcode_captcha.findall(ckimg_src)[0]

			if checkcode_type == 'CheckCodeCaptcha':
				#parse the pre check page, get useful information
				self.parser.parse_pre_check_page(response)
				checkcode_url= self.info.urls['get_checkcode'] + ckimg_src
				return checkcode_url

			# elif checkcode_type == 'CheckCodeYunSuan':
			logging.error('can not get CheckCodeCaptcha type of checkcode img, count times = %d \n'%(count))
		return None

	def generate_time_stamp(self):
		"""生成时间戳
		"""
		return int(time.time())

	def run(self, ent_number=None, *args, **kwargs):
		self.info.ent_number = ent_number
		if not self.crawl_check_page():
			logging.error('crack check code failed, stop to crawl enterprise %s' % self.info.ent_number)
			return False
		return True
# 自己的爬取类，继承爬取类
class MyCrawler(Crawler):
	def __init__(self, info=None, parser=None, *args, **kwargs):
		self.proxies = []
		self.info = info
		self.parser = MyParser(info=self.info)
		self.write_file_mutex = threading.Lock()
		self.reqst = requests.Session()
		self.reqst.headers.update({
				'Accept': 'text/html, application/xhtml+xml, */*',
				'Accept-Encoding': 'gzip, deflate',
				'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
				'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})
	def crawl_page_by_url(self, url, *args, **kwargs):
		"""根据url直接爬取页面
		"""
		try:
			resp = self.reqst.get(url, proxies= self.proxies, **kwargs)
			if resp.status_code != 200:
				logging.error('crawl page by url failed! url = %s' % url)
			# page = resp.content
			page = resp
			time.sleep(random.uniform(0.2, 1))
			return page
		except Exception as e:
			logging.error("crawl page by url exception %s:%s"%(type(e), str(e)))
		return None
	def crawl_page_by_url_post(self, url, data):
		""" 根据url和post数据爬取页面
		"""
		r = self.reqst.post(url, data, proxies = self.proxies)
		time.sleep(random.uniform(0.2, 1))
		if r.status_code != 200:
			logging.error(u"Getting page by url with post:%s\n, return status %s\n"% (url, r.status_code))
			return False
		# return r.content
		return r
		
	def generate_time_stamp(self):
		"""生成时间戳
		"""
		return int(time.time())

	
# 自己的解析类，继承解析类
class MyParser(Parser):
	def __init__(self, info=None, crawler=None, *args, **kwargs):
		self.info = info
		
	def parse_pre_check_page(self, page):
		"""解析提交验证码之前的页面
		"""
		soup = BeautifulSoup(page, 'html.parser')
		ckimg_src = soup.find_all('img', id='MzImgExpPwd')[0].get('src')
		ckimg_src = str(ckimg_src)
		re_currenttime_millis = re.compile(r'/CheckCodeCaptcha\?currentTimeMillis=([\s\S]*)')
		self.info.credit_ticket = soup.find_all('input',id='credit_ticket')[0].get('value')
		self.info.time_stamp = re_currenttime_millis.findall(ckimg_src)[0]
	def parse_post_check_page(self, page):
		"""解析提交验证码之后的页面，获取必要的信息
		"""
		if page == 'fail':
			logging.error('checkcode error!')
			# if senting_open:
			#     senting_client.captureMessage('checkcode error!')
			return False
		# print 'page:', page
		# soup = BeautifulSoup(page, 'html.parser')
		soup = page
		r = soup.find_all('a', {'href': "#", 'onclick': re.compile(r'openEntInfo')})
		# print 'r:', r
		ent = ''
		if r:
			ent = r[0]['onclick']
		else:
			logging.error('fail to find openEntInfo')
			return False

		# print 'ent:', ent
		m = re.search(r'\'([\w]*)\'[ ,]+\'([\w]*)\'[ ,]+\'([\w]*)\'', ent)
		if m:
			self.info.ent_id = m.group(1)
			self.info.credit_ticket = m.group(3)
			self.info.ent_number = m.group(2)
			# print 'm:',m.group(1),m.group(2), m.group(3)

		# r = soup.find_all('input', {'type': "hidden", 'name': "currentTimeMillis", 'id': "currentTimeMillis"})
		r = BeautifulSoup(self.info.after_crack_checkcode_page, 'html.parser').find_all('input', {'type': "hidden", 'name': "currentTimeMillis", 'id': "currentTimeMillis"})
		if r:
			self.info.time_stamp = r[0]['value']
		else:
			logging.error('fail to get time stamp')
		return True

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
			return [dict(zip(ths, tds))]

	def parser_ent_pub_ent_annual_report(self, what=None, content=None, element=None, attrs=None): # 针对企业年报，
		table = content.find_all(element, attrs=attrs)[0]
		ths = [th.get_text().strip() for th in table.find_all('th') if th.get_text()]
		tds = []
		for td in table.find_all('td'):
			if td.find('a'):
				tds.append(td.a['href'])
				tds.append(td.get_text().strip())
			else:
				if td.get_text():
					tds.append(td.get_text().strip())
				else:
					tds.append(None)
		print 'len(ths):', len(ths)
		for th in ths:
			print th
		print 'len(tds):', len(tds)
		for td in tds:
			print td
		return (ths, tds)

	def parser_ent_pub_ent_annual_report_for_detail(self, what=None, content=None, element=None, attrs=None):#返回企业年报的每一个表。
		table = content
		ths = [th.get_text().strip() for th in table.find_all('th') if th.get_text()]
		for i, th in enumerate(ths):
			if th[:2] == '<<' or th[-2:] == '>>':
				ths = ths[:i]
				break
		if what=='basic':
			ths = ths[2:]
		else:
			ths = ths[1:]
		tds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]
		return self.zip_ths_tds(ths, tds)

	def parser_ind_comm_pub_reg_modefy(self, content=None): # 得到变更信息的 td,包括详细页面的地址。
		# print '---------------content-------------------'
		# print content
		tds = content.find_all('td')
		my_tds = []
		for td in tds:
			if td.find('a'):
				my_tds.append(td.a['onclick'])
				my_tds.append(td.a['onclick'])
			else:
				if td.get_text():
					my_tds.append(td.get_text().strip())
				else:
					my_tds.append(None)
		return my_tds

	def parser_classic_ths_tds_data_for_ind_comm_pub(self, what=None, content=None, element=None, attrs=None): #单独处理变更信息的详细页面地址。
		table = content
		ths = [th.get_text().strip() for th in table.find_all('th') if th.get_text()]
		tds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')][1:]
		return self.zip_ths_tds(ths, tds)

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

		if what == 'ind_comm_pub_reg_modify':
			tds = self.parser_ind_comm_pub_reg_modefy(content=content)
			return (ths, tds)
			pass
		elif what == 'wait':
			pass
		else:
			# print table.find_all('tr')
			tds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]
		# print 'len(ths):', len(ths)
		# for th in ths:
		# 	print th
		# print 'len(tds):', len(tds)
		# for td in tds:
		# 	print td

		return self.zip_ths_tds(ths=ths, tds=tds)
	
# 工商公示信息
class IndustrialPubliction(object):
	def __init__(self, info=None, crawler=None, parser=None, *args, **kwargs):
		self.info = info
		self.crawler = crawler
		self.parser = parser
	# 登记信息
	def get_regirster_info(self, *args, **kwargs):
		param = {'entId':self.info.ent_id, 'credit_ticket':self.info.credit_ticket, 'entNo':self.info.ent_number, 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['ind_comm_pub_reg_basic'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_reg_basic', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		self.info.result_json['ind_comm_pub_reg_basic'] = result

		param = {'ent_id':self.info.ent_id, 'clear':'true', 'entName':'', 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['ind_comm_pub_reg_shareholder'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		# print content
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_reg_shareholder', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		self.info.result_json['ind_comm_pub_reg_shareholder'] = result

		param = {'ent_id':self.info.ent_id, 'clear':'true', 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['ind_comm_pub_reg_modify'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		# print content
		ths, tds = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_reg_modify', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		for i, td in enumerate(tds):
			if isinstance(td, basestring) and td.find('show')==0:
				# print td.split(',')[0][12:-1]
				resp = self.crawler.crawl_page_by_url(self.info.urls['host']+td.split(',')[0][12:-1])
				content = BeautifulSoup(resp.content, 'html.parser')
				# print content
				tables = content.find_all('table', attrs={'cellspacing':"0", 'id':"tableIdStyle"})
				# print '---------table_one----len(tables):%s----------' % len(tables)
				# print tables[0]
				# print tables[1]
				tds[i] = self.parser.parser_classic_ths_tds_data_for_ind_comm_pub(what='parser_ind_comm_pub_reg_modefy', content=tables[0], element='table')
				# print tds[i]
				tds[i+1] = self.parser.parser_classic_ths_tds_data_for_ind_comm_pub(what='parser_ind_comm_pub_reg_modefy', content=tables[1], element='table')
				# print tds[i+1]
			else:
				pass
				# print td
		self.info.result_json['ind_comm_pub_reg_modify'] = self.parser.zip_ths_tds(ths, tds)
		# self.crawler.get_page_json_data('ind_comm_pub_reg_basic', 1)
		# self.crawler.get_page_json_data('ind_comm_pub_reg_shareholder', 1)
		# self.crawler.get_page_json_data('ind_comm_pub_reg_modify', 1)
	# 备案信息
	def get_record_info(self, *args, **kwargs):
		param = {'ent_id':self.info.ent_id, 'clear':'true', 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['ind_comm_pub_arch_key_persons'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		# print content
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_arch_key_persons', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		self.info.result_json['ind_comm_pub_arch_key_persons'] = result

		param = {'ent_id':'', 'clear':'true', 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['ind_comm_pub_arch_branch'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		# print content
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_arch_branch', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		self.info.result_json['ind_comm_pub_arch_branch'] = result

		param = {'ent_id':self.info.ent_id, 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['ind_comm_pub_arch_liquidation'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		# print content
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_arch_liquidation', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		self.info.result_json['ind_comm_pub_arch_liquidation'] = result
		# self.crawler.get_page_json_data('ind_comm_pub_arch_key_persons', 1)
		# self.crawler.get_page_json_data('ind_comm_pub_arch_branch', 1)
		# self.crawler.get_page_json_data('ind_comm_pub_arch_liquidation', 1)
	# 动产抵押登记信息
	def get_movable_property_register_info(self, *args, **kwargs):
		param = {'entId':self.info.ent_id, 'clear':'true', 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['ind_comm_pub_movable_property_reg'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_movable_property_reg', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		self.info.result_json['ind_comm_pub_movable_property_reg'] = result
		# self.crawler.get_page_json_data('ind_comm_pub_movable_property_reg', 1)
	# 股权出质登记信息
	def get_stock_equity_pledge_info(self, *args, **kwargs):
		param = {'entId':self.info.ent_id, 'clear':'true', 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['ind_comm_pub_equity_ownership_reg'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_equity_ownership_reg', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		self.info.result_json['ind_comm_pub_equity_ownership_reg'] = result
		# self.crawler.get_page_json_data('ind_comm_pub_equity_ownership_reg', 1)
	# 行政处罚信息
	def get_administrative_penalty_info(self, *args, **kwargs):
		param = {'entId':self.info.ent_id, 'clear':'true', 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['ind_comm_pub_administration_sanction'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_administration_sanction', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		self.info.result_json['ind_comm_pub_administration_sanction'] = result
		# self.crawler.get_page_json_data('ind_comm_pub_administration_sanction', 1)
	# 经营异常信息
	def get_abnormal_operation_info(self, *args, **kwargs):
		param = {'entId':self.info.ent_id, 'clear':'true', 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['ind_comm_pub_business_exception'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_business_exception', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		self.info.result_json['ind_comm_pub_business_exception'] = result
		# self.crawler.get_page_json_data('ind_comm_pub_business_exception', 1)
	# 严重违法信息
	def get_serious_illegal_info(self, *args, **kwargs):
		param = {'ent_id':self.info.ent_id, 'clear':'true', 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['ind_comm_pub_serious_violate_law'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_serious_violate_law', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		self.info.result_json['ind_comm_pub_serious_violate_law'] = result
		# self.crawler.get_page_json_data('ind_comm_pub_serious_violate_law', 1)
	# 抽查检查信息
	def get_spot_check_info(self, *args, **kwargs):
		param = {'ent_id':self.info.ent_id, 'clear':'true', 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['ind_comm_pub_spot_check'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		result = self.parser.parser_classic_ths_tds_data(what='ind_comm_pub_spot_check', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		self.info.result_json['ind_comm_pub_spot_check'] = result
		# self.crawler.get_page_json_data('ind_comm_pub_spot_check', 1)
	# 运行逻辑
	def run(self, *args, **kwargs):
		self.get_regirster_info()
		self.get_record_info()
		self.get_movable_property_register_info()
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
		param = {'entid':self.info.ent_id, 'clear':'true', 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['ent_pub_ent_annual_report'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		print '-------------get_corporate_annual_reports_info--------------'
		print content
		ths, tds = self.parser.parser_ent_pub_ent_annual_report(what='parser_ent_pub_ent_annual_report', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0"})
		ths.insert(2, u'详情')
		for i,td in enumerate(tds):
			if td.find('qynb') != -1:
				# print td
				# http://qyxy.baic.gov.cn/qynb/entinfoAction!qynbxx.dhtml?cid=e8a67d252a0347378ccdbc9738129e95&entid=20e38b8c33c9804a0133ee29ecaa17b5&credit_ticket=5A3B020816AE7E1B8937AC076710E6AB
				# print self.info.urls['host'] + '/' + td[1:]
				# print self.info.ent_id
				# print self.info.credit_ticket
				resp = self.crawler.crawl_page_by_url(self.info.urls['host']+ '/' + tds[i][1:])
				content = BeautifulSoup(resp.content, 'html.parser').find_all('table')
				# print content
				temp = {}
				temp[u'企业基本信息'] = self.parser.parser_ent_pub_ent_annual_report_for_detail(what='basic', content=content[0])
				temp[u'企业资产状况信息'] = self.parser.parser_ent_pub_ent_annual_report_for_detail(what='', content=content[1])
				cid = td[td.find('cid=')+4:td.find('cid=')+4+32]
				# print cid
				param = {'clear':'true', 'cid':cid, 'entnature':''}
				resp = self.crawler.crawl_page_by_url(self.info.urls['annual_report_detail'], params=param)
				content = BeautifulSoup(resp.content, 'html.parser').find_all('table')
				# print content
				temp[u'股东及出资信息'] = self.parser.parser_ent_pub_ent_annual_report_for_detail(what='', content=content[0])

				param = {'clear':'true', 'cid':cid}
				resp = self.crawler.crawl_page_by_url(self.info.urls['annual_report_detail_for_fro'], params=param)
				content = BeautifulSoup(resp.content, 'html.parser').find_all('table')
				# print content
				temp[u'对外提供保证担保信息'] = self.parser.parser_ent_pub_ent_annual_report_for_detail(what='', content=content[0])
				# print 'year:',tds[i+1][0:4]
				param = {'clear':'true', 'cid':cid, 'year':tds[i+1][0:4]}
				resp = self.crawler.crawl_page_by_url(self.info.urls['annual_report_detail_change'], params=param)
				content = BeautifulSoup(resp.content, 'html.parser').find_all('table')
				print content
				temp[u'修改记录'] = self.parser.parser_ent_pub_ent_annual_report_for_detail(what='', content=content[0])
				tds[i] = temp
				# tds[i] = self.parser.parser_ent_pub_ent_annual_report_for_detail(tds[i])
		# result = self.parser.parser_classic_ths_tds_data(what='ent_pub_ent_annual_report', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0"})
		self.info.result_json['ent_pub_ent_annual_report'] = self.parser.zip_ths_tds(ths[1:], tds)
		# self.crawler.get_page_json_data('ent_pub_ent_annual_report', 2)
	# 股东及出资信息
	def get_shareholder_contribution_info(self, *args, **kwargs):
		param = {'entId':self.info.ent_id, 'clear':'true', 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['ent_pub_shareholder_capital_contribution'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		result = self.parser.parser_classic_ths_tds_data(what='ent_pub_shareholder_capital_contribution', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		self.info.result_json['ent_pub_shareholder_capital_contribution'] = result
		# self.crawler.get_page_json_data('ent_pub_shareholder_capital_contribution', 2)
	# 股权变更信息
	def get_equity_change_info(self, *args, **kwargs):
		param = {'entId':self.info.ent_id, 'clear':'true', 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['ent_pub_equity_change'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		result = self.parser.parser_classic_ths_tds_data(what='ent_pub_equity_change', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		self.info.result_json['ent_pub_equity_change'] = result
		# self.crawler.get_page_json_data('ent_pub_equity_change', 2)
	# 行政许可信息
	def get_administrative_licensing_info(self, *args, **kwargs):
		param = {'entId':self.info.ent_id, 'clear':'true', 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['ent_pub_administration_license'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		result = self.parser.parser_classic_ths_tds_data(what='ent_pub_administration_license', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		self.info.result_json['ent_pub_administration_license'] = result
		# self.crawler.get_page_json_data('ent_pub_administration_license', 2)
	# 知识产权出质登记信息
	def get_intellectual_property_rights_pledge_registration_info(self, *args, **kwargs):
		param = {'entId':self.info.ent_id, 'clear':'true', 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['ent_pub_knowledge_property'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		result = self.parser.parser_classic_ths_tds_data(what='ent_pub_knowledge_property', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		self.info.result_json['ent_pub_knowledge_property'] = result
		# self.crawler.get_page_json_data('ent_pub_knowledge_property', 2)
	# 行政处罚信息
	def get_administrative_punishment_info(self, *args, **kwargs):
		param = {'entId':self.info.ent_id, 'clear':'true', 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['ent_pub_administration_sanction'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		result = self.parser.parser_classic_ths_tds_data(what='ent_pub_administration_sanction', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		self.info.result_json['ent_pub_administration_sanction'] = result
		# self.crawler.get_page_json_data('ent_pub_administration_sanction', 2)
	# 运行逻辑
	def run(self, *args, **kwargs):
		pass
		self.get_corporate_annual_reports_info()
		self.get_shareholder_contribution_info()
		self.get_equity_change_info()
		self.get_administrative_licensing_info()
		self.get_intellectual_property_rights_pledge_registration_info()
		self.get_administrative_punishment_info()
		
# 其他部门公示信息
class OtherDepartmentsPubliction(object):
	def __init__(self, info=None, crawler=None, parser=None, *args, **kwargs):
		self.info = info
		self.crawler = crawler
		self.parser = parser
	# 行政许可信息
	def get_administrative_licensing_info(self, *args, **kwargs):
		param = {'entId':self.info.ent_id, 'clear':'true', 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['other_dept_pub_administration_license'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		result = self.parser.parser_classic_ths_tds_data(what='other_dept_pub_administration_license', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		self.info.result_json['other_dept_pub_administration_license'] = result
		# self.crawler.get_page_json_data('other_dept_pub_administration_license', 3)
	# 行政处罚信息
	def get_administrative_punishment_info(self, *args, **kwargs):
		param = {'entId':self.info.ent_id, 'clear':'true', 'timeStamp':self.info.time_stamp}
		resp = self.crawler.crawl_page_by_url(self.info.urls['other_dept_pub_administration_sanction'], params=param)
		content = BeautifulSoup(resp.content, 'html.parser')
		result = self.parser.parser_classic_ths_tds_data(what='other_dept_pub_administration_sanction', content=content, element='table', attrs={'cellspacing':"0", 'cellpadding':"0", 'class':"detailsList"})
		self.info.result_json['other_dept_pub_administration_sanction'] = result
		# self.crawler.get_page_json_data('other_dept_pub_administration_sanction', 3)
	# 运行逻辑
	def run(self, *args, **kwargs):
		pass
		self.get_administrative_licensing_info()
		self.get_administrative_punishment_info()
		
# 司法协助公示信息
class JudicialAssistancePubliction(object):
	def __init__(self, info=None, crawler=None, parser=None, *args, **kwargs):
		self.info = info
		self.crawler = crawler
		self.parser = parser
	# 股权冻结信息
	def get_equity_freeze_info(self, *args, **kwargs):
		pass
	# 股东变更信息
	def get_shareholders_change_info(self, *args, **kwargs):
		pass
	# 运行逻辑
	def run(self, *args, **kwargs):
		self.get_equity_freeze_info()
		self.get_shareholders_change_info()
		pass

# 省份的爬取类
class BeijingCrawler(object):
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
		self.crack = CrackCheckcode(info=self.info, crawler=self.crawler, parser=self.parser)
		is_valid = self.crack.run(ent_number)
		if not is_valid:
			print 'error,the register is not valid...........'
			return
		self.info.result_json_list = []
		for item_page in BeautifulSoup(self.info.after_crack_checkcode_page, 'html.parser').find_all('div', attrs= {'class':"list", 'style':"min-height: 400px;"})[0].find_all('ul'):
			# print item_page
			# print self.info.ent_number
			self.info.result_json = {}
			self.crack.parser.parse_post_check_page(item_page)
			industrial = IndustrialPubliction(self.info, self.crawler, self.parser)
			industrial.run()
			enterprise = EnterprisePubliction(self.info, self.crawler, self.parser)
			enterprise.run()
			other = OtherDepartmentsPubliction(self.info, self.crawler, self.parser)
			other.run()
			judical = JudicialAssistancePubliction(self.info, self.crawler, self.parser)
			judical.run()
			print self.info.result_json
			self.info.result_json_list.append( {self.info.ent_number: self.info.result_json})

		# return self.info.result_json_list
		for item in self.info.result_json_list:
			self.json_dump_to_file('beijing.json',  item )
			# self.json_dump_to_file('jiangsu.json', {self.info.ent_number: self.info.result_json})
		

class TestBeijingCrawler(unittest.TestCase):
	def __init__(self):
		pass
	def setUp(self):
		self.info = InitInfo()
		self.crawler = MyCrawler(info=self.info)
		self.parser = MyParser(info=self.info, crawler=self.crawler)

	# def test_checkcode(self):
	# 	self.crack = CrackCheckcode(info=self.info, crawler=self.crawler)
	# 	is_valid = self.crack.run(ent_number)
	# 	self.assertTrue(is_valid)

	def test_crawler_register_num(self):
		crawler = JiangsuCrawler('./enterprise_crawler/beijing.json')
		ent_list = [u'110113014453083']
		for ent_number in ent_list:
			result = crawler.run(ent_number=ent_number)
	def test_crawler_key(self):
		crawler = JiangsuCrawler('./enterprise_crawler/beijing.json')
		ent_list = [u'创业投资中心']
		for ent_number in ent_list:
			crawler.run(ent_number=ent_number)


if __name__ == '__main__':

	if DEBUG:
		unittest.main()
	crawler = BeijingCrawler('./enterprise_crawler/beijing.json')
	ent_list = [u'110113014453083']
	ent_list = [u'创业投资中心']
	# ent_list = [u'北京仙瞳创业投资中心（有限合伙）']
	for ent_number in ent_list:
		crawler.run(ent_number=ent_number)
