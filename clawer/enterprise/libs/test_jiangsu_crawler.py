#encoding=utf-8
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
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
from bs4 import BeautifulSoup
from smart_proxy.api import Proxy, UseProxy
from enterprise.libs.CaptchaRecognition import CaptchaRecognition

DEBUG = False
# 初始化信息类
class InitInfo(object):
	def __init__(self, *args, **kwargs):
		"""江苏工商公示信息网页爬虫初始化函数
		Args:
			json_restore_path: json文件的存储路径，所有江苏的企业，应该写入同一个文件，因此在多线程爬取时设置相同的路径。同时，
			 需要在写入文件的时候加锁
		Returns:
		"""
		self.ent_number = None
		#html数据的存储路径
		self.html_restore_path = settings.json_restore_path + '/jiangsu/'
		# 验证码图片的存储路径
		self.ckcode_image_path = settings.json_restore_path + '/jiangsu/ckcode.jpg'
		# if not os.path.exists(self.ckcode_image_path):
		# 	os.makedirs(os.path.dirname(self.ckcode_image_path))
		self.code_cracker = CaptchaRecognition('jiangsu')
		#多线程爬取时往最后的json文件中写时的加锁保护
		self.write_file_mutex = threading.Lock()
		
		self.urls = {'host': 'www.jsgsj.gov.cn',
				'official_site': 'http://www.jsgsj.gov.cn:58888/province/',
				'get_checkcode': 'http://www.jsgsj.gov.cn:58888/province/rand_img.jsp?type=7',
				'post_checkcode': 'http://www.jsgsj.gov.cn:58888/province/infoQueryServlet.json?queryCinfo=true',
				'ind_comm_pub_skeleton': 'http://www.jsgsj.gov.cn:58888/ecipplatform/inner_ci/ci_queryCorpInfor_gsRelease.jsp',
				'ent_pub_skeleton': 'http://www.jsgsj.gov.cn:58888/ecipplatform/inner_ci/ci_queryCorpInfo_qyRelease.jsp',
				'other_dept_pub_skeleton': 'http://www.jsgsj.gov.cn:58888/ecipplatform/inner_ci/ci_queryCorpInfo_qtbmRelease.jsp',
				'judical_assist_pub_skeleton': 'http://www.jsgsj.gov.cn:58888/ecipplatform/inner_ci/ci_queryJudicialAssistance.jsp',
				'annual_report_skeleton': 'http://www.jsgsj.gov.cn:58888/ecipplatform/reportCheck/company/cPublic.jsp',
				'ci_enter': 'http://www.jsgsj.gov.cn:58888/ecipplatform/ciServlet.json?ciEnter=true',
				'common_enter': 'http://www.jsgsj.gov.cn:58888/ecipplatform/commonServlet.json?commonEnter=true',
				'nb_enter': 'http://www.jsgsj.gov.cn:58888/ecipplatform/nbServlet.json?nbEnter=true',
				'ci_detail': 'http://www.jsgsj.gov.cn:58888/ecipplatform/ciServlet.json?ciDetail=true'}
		self.result_json = {}
		self.result_json_list = []

# 破解验证码类
class CrackCheckcode(object):
	def __init__(self, info=None, crawler=None, *args, **kwargs):
		self.info = info
		self.crawler = crawler
		pass
	def crack_checkcode(self, *args, **kwargs):
		"""破解验证码
		:return 破解后的验证码
		"""
		resp = self.crawler.crawl_page_by_url(self.info.urls['get_checkcode'])
		if not resp :
			logging.error('Failed, exception occured when getting checkcode')
			return ('', '')
		time.sleep(random.uniform(2, 4))

		self.info.write_file_mutex.acquire()
		ckcode = ('', '')
		with open(self.info.ckcode_image_path, 'wb') as f:
			f.write(resp)
		try:
			ckcode = self.info.code_cracker.predict_result(self.info.ckcode_image_path)
		except Exception as e:
			logging.error('exception occured when crack checkcode: %s' % str(e))
			ckcode = ('', '')
		finally:
			pass
		self.info.write_file_mutex.release()
		print ckcode
		return ckcode
		
	def crawl_check_page(self, *args, **kwargs):
		"""爬取验证码页面，包括下载验证码图片以及破解验证码
		:return true or false
		"""
		print self.info.urls['official_site']
		resp = self.crawler.crawl_page_by_url(self.info.urls['official_site'])
		if not resp:
			logging.error("crawl the first page page failed!\n")
			return False
		count = 0
		while count < 15:
			count += 1
			ckcode = self.crack_checkcode()
			if not ckcode[1]:
				logging.error("crawl checkcode failed! count number = %d\n"%(count))
				continue
			data = {'name': self.info.ent_number, 'verifyCode': ckcode[1]}
			resp = self.crawler.crawl_page_by_url_post(self.info.urls['post_checkcode'], data=data)

			print resp
			if resp.find("onclick") >= 0 : #and self.parse_post_check_page(resp):
				self.info.after_crack_checkcode_page = resp
				return True
			else:
				# if resp.find('onclick') == -1:
				# 	return False
				logging.error("crawl post check page failed! count number = %d\n"%(count))
			time.sleep(random.uniform(5, 8))
		return False
	
	def parse_post_check_page(self, page):
		"""解析提交验证码之后的页面，提取所需要的信息，比如corp id等
		Args:
			page: 提交验证码之后的页面
		"""
		self.info.enterprise_name = page.get_text().strip()

		page = str(page)
		m = page.split(',')
		if m:
			self.info.corp_org = m[1]
			self.info.corp_id = m[2]
			self.info.corp_seq_id = m[3]
			self.info.register_num = m[4]
			print 'self.info.ent_number:',self.info.ent_number
			if not (self.info.ent_number.isdigit() or ( self.info.ent_number[:-1].isdigit() and self.info.ent_number[-1:].isalpha()) ):
				self.info.ent_number = self.info.register_num
			print self.info.corp_org, self.info.corp_id, self.info.corp_seq_id, self.info.ent_number

			self.info.industrial_page_info_post_data ={
				'org': self.info.corp_org,
				'id': self.info.corp_id,
				'seq_id': self.info.corp_seq_id,
				'corp_name':self.info.enterprise_name,
				'reg_no':self.info.register_num,
				'existsAbnormal':"false",
				'sf_org': self.info.corp_org,
				'sf_id': self.info.corp_id,
				'sf_seq_id': self.info.corp_seq_id,
			}
			# 工商公示信息-基本信息post请求字典
			self.info.industrial_basic_info_post_data = {
				'org': self.info.corp_org,
				'id': self.info.corp_id,
				'seq_id': self.info.corp_seq_id,
				'specificQuery': 'basicInfo'
			}
			# 工商公示信息-股东发起人信息post请求字典
			self.info.industrial_shorehold_info_post_data = {
				'CORP_ORG': self.info.corp_org,
				'CORP_ID': self.info.corp_id,
				'CORP_SEQ_ID': self.info.corp_seq_id,
				'specificQuery': 'investmentInfor',
				'pageNo': '1',
				'pageSize': '100',
				'showRecordLine': '1'
			}
			# 工商公示信息-变理信息post请求字典
			self.info.industrial_change_info_post_data = {
				'showRecordLine': '1',
				'specificQuery': 'commonQuery',
				'propertiesName': 'biangeng',
				'corp_org': self.info.corp_org,
				'corp_id': self.info.corp_id,
				'pageNo': '1',
				'pageSize': '100'
			}
			# 企业工商信息-企业年报post请求数据
			self.info.enterprise_annual_report_info_post_data = {
				'REG_NO':self.info.ent_number,
				'showRecordLine':'0',
				'specificQuery':'gs_pb',
				'propertiesName':'query_report_list',
				'pageNo':'1',
				'pageSize':'100'
			}
			# 企业工商信息-投资人及出资信息post请求数据
			self.info.enterprise_shorehold_and_give_info_post_data = {
				'ID': '',
				'REG_NO': self.info.ent_number,
				'showRecordLine': '1',
				'specificQuery': 'gs_pb',
				'propertiesName': '"query_tzcz"',
				'pageNo': '1',
				'pageSize': '100',
				'ADMIT_MAIN': '08'
			}
			# 其他
			self.info.other_administrative_licensing_info_past_data = {
				'corp_org': self.info.corp_org,
				'corp_id': self.info.corp_id,
				'pageNo': '1',
				'pageSize': '100'
			}
			return True
		return False
	def run(self, ent_number=None, *args, **kwargs):
		self.info.ent_number = ent_number
		if not self.crawl_check_page():
			logging.error('crack check code failed, stop to crawl enterprise %s' % self.info.ent_number)
			return False
		return True

# 自己的爬取类，继承爬取类
class MyCrawler(Crawler):
	def __init__(self, info=None, *args, **kwargs):
		# 调用代理，及配置是否使用代理的接口。完成使用代理或者不使用代理。
		useproxy = UseProxy()
		is_use_proxy = useproxy.get_province_is_use_proxy(province='jiangsu')
		if not is_use_proxy:
			self.proxies = []
		else:
			proxy = Proxy()
			self.proxies = {'http':'http://'+random.choice(proxy.get_proxy(num=5, province='jiangsu')),
						'https':'https://'+random.choice(proxy.get_proxy(num=5, province='jiangsu'))}
		print 'self.proxies:', self.proxies		
		# self.proxies = []
		self.reqst = requests.Session()
		self.reqst.headers.update({
				'Accept': 'text/html, application/xhtml+xml, */*',
				'Accept-Encoding': 'gzip, deflate',
				'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
				'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})
	def crawl_page_by_url(self, url):
		"""根据url直接爬取页面
		"""
		try:
			resp = self.reqst.get(url, proxies=self.proxies)
			if resp.status_code != 200:
				logging.error('crawl page by url failed! url = %s' % url)
			page = resp.content
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
		return r.content

# 自己的解析类，继承解析类
class MyParser(Parser):
	def __init__(self, info=None, crawler=None, *args, **kwargs):
		self.info = info
		self.crawler = crawler

	def zip_ths_tds(self, ths, tds):
		return dict(zip(ths,tds))

	def test_print_ths_tds(self, ths, tds):
		for th, td in zip(ths, tds):
			print th,td
		# for th in ths:
		# 	print th
		# for td in tds:
		# 	print td
	def get_result_json_for_register_info(self, json_data, *args, **kwargs):
		# for key, value in json_data.items():
		# 	print key, value
		ths = [u'注册号', u'名称', u'类型', u'执行事务合伙人',  u'主要经营场所', u'合伙期限自', u'合伙期限至', u'经营范围', u'登记机关', u'核准日期', u'成立日期', u'登记状态']
		tds = [u'C1', u'C2', u'C3', u'C5', u'C7', u'C4', u'C10', u'C8', u'C11', u'C12', u'C9', u'C13']
		tds = [json_data.get(item) for item in tds]
		return self.zip_ths_tds(ths, tds)
		# self.test_print_ths_tds(ths, tds)
	def get_result_json_for_classic_dict_info(self, json_data, ths=None, tds=None, *args, **kwargs):
		sharehold_list = []
		for item in json_data:
			my_tds = [item.get(td) for td in tds]
			sharehold_list.append(self.zip_ths_tds(ths, my_tds))
			# self.test_print_ths_tds(ths, my_tds)
		return sharehold_list
	def get_result_json_for_corporate_annual_reports_info(self, json_data, *args, **kwargs):
		annual_list = []
		for i, item in enumerate(json_data):
			annual_dict = {}
			self.info.annual_reports_info_data = {
				'ID':item.get('ID'),
				'OPERATE_TYPE':'2',
				'showRecordLine':'0',
				'specificQuery':'fgsqyfr_pb',
				'propertiesName':'query_basicInfo'
			}
			self.info.annual_reports_enterprise_info_data = {
				'OPERATE_TYPE':'2015',
				'REG_NO':self.info.ent_number,
				'showRecordLine':'0',
				'specificQuery':'fgsqyfr_pb',
				'propertiesName':"query_setRed",
				'REPORT_YEAR':item.get('REPORT_RESULT')[:4]
			}
			self.info.annual_reports_security_info_data = {
				'ID':item.get('ID'),
				'OPERATE_TYPE':'2015',
				'showRecordLine':'1',
				'specificQuery':'fgsqyfr_pb',
				'propertiesName':"query_InformationSecurity",
				'REPORT_YEAR':item.get('REPORT_RESULT')[:4],
				'pageNo':'1',
				'pageSize':'100'
			}
			self.info.annual_reports_record_info_data = {
				'OPERATE_TYPE':'2015',
				'REG_NO':self.info.ent_number,
				'showRecordLine':'1',
				'specificQuery':'fgsqyfr_pb',
				'propertiesName':"query_RevisionRecord",
				'REPORT_YEAR':item.get('REPORT_RESULT')[:4],
				'pageNo':'1',
				'pageSize':'100'
			}
			page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/nbServlet.json?nbEnter=true', data=self.info.annual_reports_info_data)
			# print page
			ths = [u'注册号/统一社会信用代码', u'企业名称', u'企业联系电话', u'邮政编码', u'企业通信地址', u'企业电子邮箱', u'企业是否有投资信息或购买其他公司股权', u'企业经营状态', u'企业经营状态', u'从业人数']
			tds = [u'REG_NO', u'CORP_NAME', u'TEL', u'ZIP', u'ADDR', u'E_MAIL', u'IF_INVEST', u'PRODUCE_STATUS', u'IF_WEBSITE', u'NET_AMOUNT']
			tds = [json.loads(page)[0].get(td) for td in tds]
			annual_dict[u'企业基本信息'] = dict(zip(ths,tds))
			ths = [u'资产总额', u'所有者权益合计', u'营业总收', u'利润总额', u'营业总收入中主营业务收入', u'净利润', u'纳税总额', u'负债总额']
			tds = [u'TOTAL_EQUITY', u'SALE_INCOME', u'PROFIT_TOTAL', u'SERV_FARE_INCOME', u'PROFIT_RETA', u'TAX_TOTAL', u'DEBT_AMOUNT']
			tds = [json.loads(page)[0].get(td) for td in tds]
			annual_dict[u'企业资产状况信息'] = dict(zip(ths,tds))

			page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/nbServlet.json?nbEnter=true', data=self.info.annual_reports_security_info_data)
			# print page
			ths = []
			tds = []
			annual_dict[u'对外提供保证担保信息'] = dict(zip(ths,tds))
			page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/nbServlet.json?nbEnter=true', data=self.info.annual_reports_record_info_data)
			# print page
			ths = []
			tds = []
			annual_dict[u'修改记录'] = dict(zip(ths,tds))
			annual_list.append({u'序号':str(i+1), u'报送年度':item.get('REPORT_RESULT'), u'发布日期':item.get('REPORT_DATE'), u'详情':annual_dict})
		return annual_list

# 爬取工商公示信息类
class IndustrialPubliction(object):
	def __init__(self, info=None, crawler=None, parser=None, *args, **kwargs):
		self.info = info
		self.crawler = crawler
		self.parser = parser
	# 登记信息
	def get_regirster_info(self, *args, **kwargs):
		self.info.register_info_page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/inner_pb/pb_queryCorpInfor_gsRelease.jsp', data=self.info.industrial_page_info_post_data)
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/ciServlet.json?ciEnter=true', data=self.info.industrial_basic_info_post_data)
		self.info.result_json['ind_comm_pub_reg_basic'] = self.parser.get_result_json_for_register_info(json.loads(page)[0])
		# print self.info.result_json

		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/ciServlet.json?ciEnter=true', data=self.info.industrial_shorehold_info_post_data)
		# print page
		ths = [u'合伙人类型', u'合伙人', u'证照/证件类型', u'证照/证件号码']
		tds = [u'C1', u'C2', u'C3', u'C4']
		self.info.result_json['ind_comm_pub_reg_shareholder'] = self.parser.get_result_json_for_classic_dict_info(json.loads(page).get('items'), ths=ths, tds=tds)
		# print self.info.result_json

		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/commonServlet.json?commonEnter=true', data=self.info.industrial_change_info_post_data)
		ths = [u'变更事项', u'变更事项', u'变更事项', u'变更事项']
		tds = []
		self.info.result_json['ind_comm_pub_reg_modify'] = self.parser.get_result_json_for_classic_dict_info(json.loads(page).get('items'), ths=ths, tds=tds)
		# print self.info.result_json

	# 备案信息
	def get_record_info(self, *args, **kwargs):
		self.info.industrial_shorehold_info_post_data['specificQuery'] = 'personnelInformation'
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/ciServlet.json?ciEnter=true', data=self.info.industrial_shorehold_info_post_data)
		# print page


		self.info.industrial_shorehold_info_post_data['specificQuery'] = 'branchOfficeInfor'
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/ciServlet.json?ciEnter=true', data=self.info.industrial_shorehold_info_post_data)
		# print page
		ths = [u'序号', u'注册号/统一社会信用代码', u'名称', u'登记机关']
		tds = []
		self.info.result_json['ind_comm_pub_arch_branch'] = self.parser.get_result_json_for_classic_dict_info(json.loads(page).get('items'), ths=ths, tds=tds)
		# print self.info.result_json

		self.info.industrial_shorehold_info_post_data['specificQuery'] = 'qsfzr'
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/ciServlet.json?ciEnter=true', data=self.info.industrial_shorehold_info_post_data)
		# print page
		# ths = [u'清算组负责人', u'清算组成员']
		# tds = []
		# self.info.result_json = self.parser.get_result_json_for_classic_dict_info(json.loads(page).get('items'), ths=ths, tds=tds)
		# print self.info.result_json
		

	# 动产抵押登记信息
	def get_movable_property_register_info(self, *args, **kwargs):
		self.info.industrial_change_info_post_data['propertiesName']="dongchan"
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/commonServlet.json?commonEnter=true', data=self.info.industrial_change_info_post_data)
		# print page
		ths = [u'序号', u'登记编号', u'登记日期', u'登记机关', u'被担保债权数额', u'状态', u'详情']
		tds = []
		self.info.result_json['ind_comm_pub_movable_property_reg'] = self.parser.get_result_json_for_classic_dict_info(json.loads(page).get('items'), ths=ths, tds=tds)
		# print self.info.result_json

	# 股权出质登记信息
	def get_stock_equity_pledge_info(self, *args, **kwargs):
		self.info.industrial_change_info_post_data['propertiesName']="guquanchuzhi"
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/commonServlet.json?commonEnter=true', data=self.info.industrial_change_info_post_data)
		# print page

	# 行政处罚信息
	def get_administrative_penalty_info(self, *args, **kwargs):
		self.info.industrial_change_info_post_data['propertiesName']="chufa"
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/commonServlet.json?commonEnter=true', data=self.info.industrial_change_info_post_data)
		# print page
		ths = [u'序号', u'行政处罚决定书文号', u'违法行为类型', u'行政处罚内容', u'作出行政处罚决定机关名称', u'作出行政处罚决定日期 ', u'详情']
		tds = []
		self.info.result_json['ind_comm_pub_administration_sanction'] = self.parser.get_result_json_for_classic_dict_info(json.loads(page).get('items'), ths=ths, tds=tds)
		# print self.info.result_json

	# 经营异常信息
	def get_abnormal_operation_info(self, *args, **kwargs):
		self.info.industrial_change_info_post_data['propertiesName']="abnormalInfor"
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/commonServlet.json?commonEnter=true', data=self.info.industrial_change_info_post_data)
		# print page
		ths = [u'序号', u'列入经营异常名录原因', u'列入日期', u'移出经营异常名录原因', u'移出日期', u'作出决定机关']
		tds = [u'RN', u'C1', u'C2', u'C3', u'C4', u'C5']
		self.info.result_json['ind_comm_pub_business_exception'] = self.parser.get_result_json_for_classic_dict_info(json.loads(page).get('items'), ths=ths, tds=tds)
		# print self.info.result_json

	# 严重违法信息
	def get_serious_illegal_info(self, *args, **kwargs):
		self.info.industrial_change_info_post_data['propertiesName']="abnormalInfor"
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/commonServlet.json?commonEnter=true', data=self.info.industrial_change_info_post_data)
		# print page
		ths = [u'序号', u'列入经营异常名录原因', u'列入日期', u'移出经营异常名录原因', u'移出日期', u'作出决定机关']
		tds = []
		self.info.result_json['ind_comm_pub_serious_violate_law'] = self.parser.get_result_json_for_classic_dict_info(json.loads(page).get('items'), ths=ths, tds=tds)
		# print self.info.result_json


	# 抽查检查信息
	def get_spot_check_info(self, *args, **kwargs):
		self.info.industrial_change_info_post_data['propertiesName']="checkup"
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/commonServlet.json?commonEnter=true', data=self.info.industrial_change_info_post_data)
		# print page
		ths = [u'检查实施机关', u'类型', u'日期', u'结果']
		tds = [u'C1', u'C2', u'C3', u'C4']
		self.info.result_json['ind_comm_pub_spot_check'] = self.parser.get_result_json_for_classic_dict_info(json.loads(page).get('items'), ths=ths, tds=tds)
		for i,item in enumerate(self.info.result_json['ind_comm_pub_spot_check']):
			item[u'序号'] = str(i+1)
		# print self.info.result_json


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


# 爬取企业公示信息类
class EnterprisePubliction(object):
	def __init__(self, info=None, crawler=None, parser=None, *args, **kwargs):
		self.info = info
		self.crawler = crawler
		self.parser = parser
	# 企业年报
	def get_corporate_annual_reports_info(self, *args, **kwargs):
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/nbServlet.json?nbEnter=true',data=self.info.enterprise_annual_report_info_post_data)
		# print page
		ths = [u'序号', u'报送年度', u'发布日期', u'详情']
		tds = []
		self.info.result_json['ind_comm_pub_reg_shareholder_detail'] = self.parser.get_result_json_for_corporate_annual_reports_info(json.loads(page), ths=ths, tds=tds)
		# print self.info.result_json
		
	# 股东及出资信息
	def get_shareholder_contribution_info(self, *args, **kwargs):
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/nbServlet.json?nbEnter=true',data=self.info.enterprise_shorehold_and_give_info_post_data)
		# print page
		

	# 股权变更信息
	def get_equity_change_info(self, *args, **kwargs):
		pass
	# 行政许可信息
	def get_administrative_licensing_info(self, *args, **kwargs):
		self.info.enterprise_annual_report_info_post_data['propertiesName'] = "query_xzxk"
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/nbServlet.json?nbEnter=true',data=self.info.enterprise_annual_report_info_post_data)
		# print page
		ths = [u'序号', u'许可文件编号', u'许可文件名称', u'有效期自', u'有效期至', u'许可机关', u'许可内容']
		tds = []
		if page != "":
			self.info.result_json['ent_pub_administrative_license'] = self.parser.get_result_json_for_classic_dict_info(json.loads(page), ths=ths, tds=tds)
			# print self.info.result_json

	# 知识产权出质登记信息
	def get_intellectual_property_rights_pledge_registration_info(self, *args, **kwargs):
		self.info.enterprise_annual_report_info_post_data['propertiesName'] = "query_zscq"
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/nbServlet.json?nbEnter=true',data=self.info.enterprise_annual_report_info_post_data)
		# print page
		ths = [u'序号', u'出质商标注册号', u'商标名称', u'类别', u'出质人名称', u'质权人名称', u'质权登记期限', u'变更情况']
		tds = []
		if page != "":
			self.info.result_json['ent_pub_knowledge_property'] = self.parser.get_result_json_for_classic_dict_info(json.loads(page), ths=ths, tds=tds)
			# print self.info.result_json
	# 行政处罚信息
	def get_administrative_punishment_info(self, *args, **kwargs):
		self.info.enterprise_annual_report_info_post_data['propertiesName'] = "query_xzcf"
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/nbServlet.json?nbEnter=true',data=self.info.enterprise_annual_report_info_post_data)
		# print page
		ths = [u'序号', u'行政处罚决定书文号', u'违法行为类型', u'行政处罚内容', u'作出行政处罚决定机关名称', u'作出行政处罚决定日期 ', u'详情']
		tds = []
		if page != "":
			self.info.result_json['ent_pub_administration_sanction'] = self.parser.get_result_json_for_classic_dict_info(json.loads(page), ths=ths, tds=tds)
			# print self.info.result_json

	# 运行逻辑
	def run(self, *args, **kwargs):
		self.get_corporate_annual_reports_info()
		self.get_shareholder_contribution_info()
		self.get_equity_change_info()
		self.get_administrative_licensing_info()
		self.get_intellectual_property_rights_pledge_registration_info()
		self.get_administrative_punishment_info()
		pass
		
# 爬取其他部门公示信息类
class OtherDepartmentsPubliction(object):
	def __init__(self, info=None, crawler=None, parser=None, *args, **kwargs):
		self.info = info
		self.crawler = crawler
		self.parser = parser
	# 行政许可信息
	def get_administrative_licensing_info(self, *args, **kwargs):
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/manyCommonFnQueryServlet.json?query_xingzhengxuke=true', 
													data=self.info.other_administrative_licensing_info_past_data)
		# print page
		ths = [u'序号', u'行政文件编号', u'许可文件名称', u'有效期自', u'有效期至', u'许可机关', u'许可内容', u'登记状态', u'项目名称', u'详情']
		tds = []
		self.info.result_json['other_dept_pub_administration_license'] = self.parser.get_result_json_for_classic_dict_info(json.loads(page).get('items'), ths=ths, tds=tds)
		# print self.info.result_json
	# 行政处罚信息
	def get_administrative_punishment_info(self, *args, **kwargs):
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/manyCommonFnQueryServlet.json?query_xingzhengchufa=true', 
													data=self.info.other_administrative_licensing_info_past_data)
		# print page
		ths = [u'序号', u'处罚决定书文号', u'违法行为类型', u'处罚种类', u'处罚事由', u'处罚机关', u'处罚决定书签发日期', u'登记状态']
		tds = []
		self.info.result_json['other_dept_pub_administration_sanction'] = self.parser.get_result_json_for_classic_dict_info(json.loads(page).get('items'), ths=ths, tds=tds)
		# print self.info.result_json
	def get_major_tax_list_info(self, *args, **kwargs):
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/manyCommonFnQueryServlet.json?majorTaxList=true', 
													data=self.info.other_administrative_licensing_info_past_data)
		# print page
		ths = [u'序号', u'案件性质', u'主要违法事实', u'实施检查的单位', u'详情']
		tds = []
		self.info.result_json = self.parser.get_result_json_for_classic_dict_info(json.loads(page).get('items'), ths=ths, tds=tds)
		# print self.info.result_json
	# 运行逻辑
	def run(self, *args, **kwargs):
		self.get_administrative_licensing_info()
		self.get_administrative_punishment_info()
		pass
		
# 爬取司法协助公示信息类
class JudicialAssistancePubliction(object):
	def __init__(self, info=None, crawler=None, parser=None, *args, **kwargs):
		self.info = info
		self.crawler = crawler
		self.parser = parser
	# 股权冻结信息
	def get_equity_freeze_info(self, *args, **kwargs):
		self.info.industrial_change_info_post_data['propertiesName']="gqdjList"
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/commonServlet.json?commonEnter=true', 
													data=self.info.industrial_change_info_post_data)
		# print page
		ths = [u'序号', u'被执行人', u'股权数额', u'执行法院', u'协助公示通知书文号', u'状态', u'详情']
		tds = []
		self.info.result_json['judical_assist_pub_equity_freeze'] = self.parser.get_result_json_for_classic_dict_info(json.loads(page).get('items'), ths=ths, tds=tds)
		# print self.info.result_json

	# 股东变更信息
	def get_shareholders_change_info(self, *args, **kwargs):
		self.info.industrial_change_info_post_data['propertiesName']="gdbgList"
		page = self.crawler.crawl_page_by_url_post('http://www.jsgsj.gov.cn:58888/ecipplatform/commonServlet.json?commonEnter=true', 
													data=self.info.industrial_change_info_post_data)
		# print page
		ths = [u'序号', u'被执行人', u'股权数额', u'受让人', u'执行法院', u'详情']
		tds = []
		self.info.result_json['judical_assist_pub_shareholder_modify'] = self.parser.get_result_json_for_classic_dict_info(json.loads(page).get('items'), ths=ths, tds=tds)
		# print self.info.result_json

	# 运行逻辑
	def run(self, *args, **kwargs):
		self.get_equity_freeze_info()
		self.get_shareholders_change_info()
		pass

# 省份的爬取类
class JiangsuCrawler(object):
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
		start_time = time.time()
		self.crack = CrackCheckcode(info=self.info, crawler=self.crawler)
		is_valid = self.crack.run(ent_number)
		if not is_valid:
			print 'error,the register is not valid...........'
			return
		end_time = time.time()
		print '-------------------------crack_spend_time:%s--------------' % (end_time - start_time)
		for item_page in BeautifulSoup(self.info.after_crack_checkcode_page, 'html.parser').find_all('a'):
			# print item_page
			print self.info.ent_number
			self.info.result_json = {}
			start_time = time.time()
			self.crack.parse_post_check_page(item_page)
			industrial = IndustrialPubliction(self.info, self.crawler, self.parser)
			industrial.run()
			enterprise = EnterprisePubliction(self.info, self.crawler, self.parser)
			enterprise.run()
			other = OtherDepartmentsPubliction(self.info, self.crawler, self.parser)
			other.run()
			judical = JudicialAssistancePubliction(self.info, self.crawler, self.parser)
			judical.run()
			end_time = time.time()
			print '--------------------------crawler_spend_time:%s' % (end_time - start_time)
			print {self.info.ent_number: self.info.result_json}
			self.info.result_json_list.append( {self.info.ent_number: self.info.result_json})

		return self.info.result_json_list

			# self.json_dump_to_file('jiangsu.json', {self.info.ent_number: self.info.result_json})
		

class TestJiangsuCrawler(unittest.TestCase):
	def __init__(self):
		pass
	def setUp(self):
		self.info = InitInfo()
		self.crawler = MyCrawler(info=self.info)
		self.parser = MyParser(info=self.info, crawler=self.crawler)

	def test_checkcode(self):
		self.crack = CrackCheckcode(info=self.info, crawler=self.crawler)
		is_valid = self.crack.run(ent_number)
		self.assertTrue(is_valid)
	def test_crawler_register_num(self):
		crawler = JiangsuCrawler('./enterprise_crawler/jiangsu.json')
		ent_list = [u'320100000149869']
		for ent_number in ent_list:
			result = crawler.run(ent_number=ent_number)
			self.assertType
	def test_crawler_key(self):
		crawler = JiangsuCrawler('./enterprise_crawler/jiangsu.json')
		ent_list = [u'创业投资中心']
		for ent_number in ent_list:
			crawler.run(ent_number=ent_number)


if __name__ == '__main__':

	if DEBUG:
		unittest.main()

	crawler = JiangsuCrawler('./enterprise_crawler/jiangsu.json')
	ent_list = [u'320100000149869'] #, u'320106000236597', '320125000170935']
	for ent_number in ent_list:
		crawler.run(ent_number=ent_number)