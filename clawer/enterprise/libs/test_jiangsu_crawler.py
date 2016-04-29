#encoding=utf-8
import os
import sys
sys.path.append('/Users/princetechs3/Documents/pyenv/cr-clawer/clawer')
import re
import codecs
import json
import time
import random
import settings
import threading
import requests
import logging
from enterprise.libs.CaptchaRecognition import CaptchaRecognition

# 初始化信息类
class InitInfo(object):
	def __init__(self, *args, **kwargs):
		"""江苏工商公示信息网页爬虫初始化函数
		Args:
			json_restore_path: json文件的存储路径，所有江苏的企业，应该写入同一个文件，因此在多线程爬取时设置相同的路径。同时，
			 需要在写入文件的时候加锁
		Returns:
		"""
		#html数据的存储路径
		self.html_restore_path = settings.json_restore_path + '/jiangsu/'
		# 验证码图片的存储路径
		self.ckcode_image_path = settings.json_restore_path + '/jiangsu/ckcode.jpg'
		self.code_cracker = CaptchaRecognition('jiangsu')
		#多线程爬取时往最后的json文件中写时的加锁保护
		

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

		# self.proxies = Proxies().get_proxies()
		self.proxies = []
		# self.json_restore_path = json_restore_path
		self.corp_org = ''
		self.corp_id = ''
		self.corp_seq_id = ''
		self.common_enter_post_data = {}
		self.ci_enter_post_data = {}
		self.nb_enter_post_data = {}
		self.post_info = {
			'ind_comm_pub_reg_basic': {'url_type': 'ci_enter', 'post_type': 'ci_enter', 'specificQuery': 'basicInfo'},
			'ind_comm_pub_reg_shareholder': {'url_type': 'ci_enter', 'post_type': 'ci_enter_with_recordline', 'specificQuery': 'investmentInfor'},
			'ind_comm_pub_reg_modify': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'biangeng'},
			'ind_comm_pub_arch_key_persons': {'url_type': 'ci_enter', 'post_type': 'ci_enter_with_recordline', 'specificQuery': 'personnelInformation'},
			'ind_comm_pub_arch_branch': {'url_type': 'ci_enter', 'post_type': 'ci_enter_with_recordline', 'specificQuery': 'branchOfficeInfor'},
			#'ind_comm_pub_arch_liquadition': {'url_type': 'ci_enter', 'post_type': 'common_enter', 'specificQuery': 'qsfzr'},
			'ind_comm_pub_movable_property_reg': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'dongchan'},
			'ind_comm_pub_equity_ownership_reg': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'guquanchuzhi'},
			'ind_comm_pub_administration_sanction': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'chufa'},
			'ind_comm_pub_business_exception': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'abnormalInfor'},
			#'ind_comm_pub_serious_violate_law': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'xxx'},
			'ind_comm_pub_spot_check': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'checkup'},

			'ind_comm_pub_reg_shareholder_detail': {'url_type': 'ci_detail', 'post_type': 'ci_detail', 'specificQuery': 'investorInfor'},

			'ent_pub_annual_report': {'url_type': 'nb_enter', 'post_type': 'nb_enter', 'propertiesName': 'query_report_list'},
			'annual_report_detail': {'url_type': 'nb_enter', 'post_type': 'nb_enter'},
			'ent_pub_shareholder_capital_contribution': {'url_type': 'nb_enter', 'post_type': 'nb_enter', 'propertiesName': 'query_tzcz'},
			'ent_pub_administrative_license': {'url_type': 'nb_enter', 'post_type': 'nb_enter', 'propertiesName': 'query_xzxk'},
			'ent_pub_knowledge_property': {'url_type': 'nb_enter', 'post_type': 'nb_enter', 'propertiesName': 'query_zscq'},
			'ent_pub_administration_sanction': {'url_type': 'nb_enter', 'post_type': 'nb_enter', 'propertiesName': 'query_xzcf'},

			'other_dept_pub_administration_license': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'xingzheng'},
			'other_dept_pub_administration_sanction': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'xingzhengchufa'},

			'judical_assist_pub_equity_freeze': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'gqdjList'},
			'judical_assist_pub_shareholder_modify': {'url_type': 'common_enter', 'post_type': 'common_enter', 'propertiesName': 'gdbgList'}
		}

# 破解验证码类
class CrackCheckcode(object):
	def __init__(self, info=None, *args, **kwargs):
		self.info = info
		pass
	def crack_checkcode(self, *args, **kwargs):
		"""破解验证码
		:return 破解后的验证码
		"""
		resp = self.crawl_page_by_url(self.info.urls['get_checkcode'])
		if not resp :
			logging.error('Failed, exception occured when getting checkcode')
			return ('', '')
		time.sleep(random.uniform(2, 4))

		self.info.write_file_mutex.acquire()
		ckcode = ('', '')
		with open(self.info.ckcode_image_path, 'wb') as f:
			f.write(resp)
		try:
			ckcode = self.code_cracker.predict_result(self.ckcode_image_path)
		except Exception as e:
			logging.error('exception occured when crack checkcode')
			ckcode = ('', '')
		finally:
			pass
		self.info.write_file_mutex.release()
		return ckcode
		
	def crawl_check_page(self, *args, **kwargs):
		"""爬取验证码页面，包括下载验证码图片以及破解验证码
		:return true or false
		"""
		print self.info.urls['official_site']
		resp = self.crawl_page_by_url(self.info.urls['official_site'])
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
			data = {'name': self.ent_number, 'verifyCode': ckcode[1]}
			resp = self.crawl_page_by_url_post(self.info.urls['post_checkcode'], data=data)

			if resp.find("onclick") >= 0 and self.parse_post_check_page(resp):
				return True
			else:
				logging.error("crawl post check page failed! count number = %d\n"%(count))
			time.sleep(random.uniform(5, 8))
		return False
	
	def parse_post_check_page(self, page):
		"""解析提交验证码之后的页面，提取所需要的信息，比如corp id等
		Args:
			page: 提交验证码之后的页面
		"""
		m = re.search(r'onclick=\\\"\w+\(\'([\w\./]+)\',\'(\w*)\',\'(\w*)\',\'(\w*)\',\'(\w*)\',\'(\w*)\',\'(\w*)\'\)', page)
		if m:
			self.corp_org = m.group(2)
			self.corp_id = m.group(3)
			self.corp_seq_id = m.group(4)
			self.common_enter_post_data = {
				'showRecordLine': '1',
				'specificQuery': 'commonQuery',
				'propertiesName': '',
				'corp_org': self.corp_org,
				'corp_id': self.corp_id,
				'pageNo': '1',
				'pageSize': '5'
			}
			self.ci_enter_post_data = {
				'org': self.corp_org,
				'id': self.corp_id,
				'seq_id': self.corp_seq_id,
				'specificQuery': ''
			}
			self.ci_enter_with_record_line_post_data = {
				'CORP_ORG': self.corp_org,
				'CORP_ID': self.corp_id,
				'CORP_SEQ_ID': self.corp_seq_id,
				'specificQuery': '',
				'pageNo': '1',
				'pageSize': '5',
				'showRecordLine': '1'
			}
			self.ci_detail_post_data = {
				'ORG': self.corp_org,
				'ID': '',
				'CORP_ORG': self.corp_org,
				'CORP_ID': self.corp_id,
				'SEQ_ID': '',
				'REG_NO': self.ent_number,
				'specificQuery': ''
			}
			self.nb_enter_post_data = {
				'ID': '',
				'REG_NO': self.ent_number,
				'showRecordLine': '0',
				'specificQuery': 'gs_pb',
				'propertiesName': '',
				'pageNo': '1',
				'pageSize': '5',
				'ADMIT_MAIN': '08'
			}
			return True
		return False
	def run(self, ent_number=None, *args, **kwargs):
		self.ent_number = ent_number
		if not self.crawl_check_page():
			logging.error('crack check code failed, stop to crawl enterprise %s' % self.ent_number)
		time.sleep(random.uniform(5, 10))

# 自己的爬取类，继承爬取类
class MyCrawler(Crawler):
	def __init__(self, *args, **kwargs):
		self.write_file_mutex = threading.Lock()
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
			resp = self.info.reqst.get(url, proxies= self.info.proxies)
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
	def __init__(self, *args, **kwargs):
		pass

# 爬取工商公示信息类
class IndustrialPubliction(object):
	def __init__(self, *args, **kwargs):
		pass
	# 登记信息
	def get_regirster_info(self, *args, **kwargs):
		pass
	# 备案信息
	def get_record_info(self, *args, **kwargs):
		pass
	# 动产抵押登记信息
	def get_movable_property_register_info(self, *args, **kwargs):
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
		self.get_regirster_info()
		print 'hello'
		pass

# 爬取企业公示信息类
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
		
# 爬取其他部门公示信息类
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
		
# 爬取司法协助公示信息类
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

# 省份的爬取类
class JiangsuCrawler(object):
	"""江苏工商公示信息网页爬虫
	"""
	def __init__(self, json_restore_path= None, *args, **kwargs):
		self.info = InitInfo()
		self.crack = CrackCheckcode(info=self.info)
		pass
	def run(self, ent_number=None, *args, **kwargs):
		self.crack.run(ent_number)

class TestJiangsuCrawler(unittest.Test):
	pass

if __name__ == '__main__':
	crawler = JiangsuCrawler('./enterprise_crawler/jiangsu.json')
	crawler.run(ent_number='320000000000192')
