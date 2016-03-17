#!/usr/bin/env python
#encoding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import re
import os,os.path
from crawler import CrawlerUtils
from bs4 import BeautifulSoup
import time
import json
import importlib

ENT_CRAWLER_SETTINGS = os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS:
    settings = importlib.import_module(ENT_CRAWLER_SETTINGS)
else:
    import settings

class GuizhouCrawler(object):
	#html数据的存储路径
	html_restore_path = settings.html_restore_path + '/guizhou/'
	ckcode_image_path = settings.json_restore_path + '/guizhou/ckcode.jpg'
    	#write_file_mutex = threading.Lock()
	def __init__(self, json_restore_path):
		self.cur_time = str(int(time.time()*1000))
		self.nbxh = None
		self.reqst = requests.Session()
		self.json_restore_path = json_restore_path
		self.ckcode_image_path = settings.json_restore_path + '/guizhou/ckcode.jpg'
		self.result_json_dict = {}
		self.reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

		self.mydict = {'eareName':'http://www.ahcredit.gov.cn',
				'search':'http://gsxt.gzgs.gov.cn/',
				'searchList':'http://gsxt.gzgs.gov.cn/search!searchSczt.shtml',
				'validateCode':'http://gsxt.gzgs.gov.cn/search!generateCode.shtml?validTag=searchImageCode&'}
	
		self.one_dict = {u'基本信息':'ind_comm_pub_reg_basic',
				u'股东信息':'ind_comm_pub_reg_shareholder',
				u'发起人信息':'ind_comm_pub_reg_shareholder',
				u'股东（发起人）信息':'ind_comm_pub_reg_shareholder',
				u'变更信息':'ind_comm_pub_reg_modify',
				u'主要人员信息':'ind_comm_pub_arch_key_persons',
				u'分支机构信息':'ind_comm_pub_arch_branch',
				u'清算信息':'ind_comm_pub_arch_liquidation',
				u'动产抵押登记信息':'ind_comm_pub_movable_property_reg',
				u'股权出置登记信息':'ind_comm_pub_equity_ownership_reg',
				u'股权出质登记信息':'ind_comm_pub_equity_ownership_reg',
				u'行政处罚信息':'ind_comm_pub_administration_sanction',
				u'经营异常信息':'ind_comm_pub_business_exception',
				u'严重违法信息':'ind_comm_pub_serious_violate_law',
				u'抽查检查信息':'ind_comm_pub_spot_check'}

		self.two_dict = {u'企业年报':'ent_pub_ent_annual_report',
				u'企业投资人出资比例':'ent_pub_shareholder_capital_contribution',
				u'股东（发起人）及出资信息':'ent_pub_shareholder_capital_contribution',
				u'股东及出资信息（币种与注册资本一致）':'ent_pub_shareholder_capital_contribution',
				u'股东及出资信息':'ent_pub_shareholder_capital_contribution',
				u'股权变更信息':'ent_pub_equity_change',
				u'行政许可信息':'ent_pub_administration_license',
				u'知识产权出资登记':'ent_pub_knowledge_property',
				u'知识产权出质登记信息':'ent_pub_knowledge_property',
				u'行政处罚信息':'ent_pub_administration_sanction',
				u'变更信息':'ent_pub_shareholder_modify'}
		self.three_dict = {u'行政许可信息':'other_dept_pub_administration_license',
				u'行政处罚信息':'other_dept_pub_administration_sanction'}
		self.four_dict = {u'股权冻结信息':'judical_assist_pub_equity_freeze',
				u'司法股权冻结信息':'judical_assist_pub_equity_freeze',
				u'股东变更信息':'judical_assist_pub_shareholder_modify',
				u'司法股东变更登记信息':'judical_assist_pub_shareholder_modify'}
		self.result_json_dict = {}

	def get_check_num(self):
		# print self.mydict['search']
		resp = None
		search_count = 0
		while search_count<5:
			try:
				resp = self.reqst.get(self.mydict['search'])
			except:
				search_count += 1
				continue
			if resp.status_code == 200:
				break
			else:
				search_count += 1
				continue
		if resp.status_code != 200:
			print resp.status_code
			return None
		# print BeautifulSoup(resp.content).prettify
		validate_count = 0
		while validate_count<5:
			try:
				resp = self.reqst.get(self.mydict['validateCode']+self.cur_time)
			except:
				validate_count += 1
				continue
			if resp.status_code == 200:
				break
			else:
				validate_count += 1
				continue
		if resp.status_code != 200:
			print 'no validateCode'
			return None
		# print self.ckcode_image_path
		with open(self.ckcode_image_path, 'wb') as f:
			f.write(resp.content)
		from CaptchaRecognition import CaptchaRecognition
		code_cracker = CaptchaRecognition('guizhou')
		ck_code = code_cracker.predict_result(self.ckcode_image_path)

		# return ck_code[1]
		if not ck_code is None:
			return ck_code[1]
		else:
			return None

	def send_post_for_enter(self, host, nbxh, c, t, lsh):
		count = 0
		while count < 10:
			data = {'nbxh':nbxh, 'c':c, 't':t, 'lsh':lsh}
			try:
				resp = self.reqst.post(host, data=data)
			except:
				count +=1
				continue
			if resp.status_code == 200:
				return resp.content
			else:
				count += 1
				continue
	def get_dict_enter(self, allths, alltds, alltds_keys):
		alltds = json.loads(alltds)
		print alltds_keys
		if not alltds[u'data']:
			return []
		else:
			temp_alltds = []
			for item in alltds[u'data']:
				for key in alltds_keys:
					if item[key] is False or item[key]=='' or item[key] == None:
						temp_alltds.append(item[key])
					else: 
						temp_alltds.append(item[key].strip())
			return self.get_one_to_one_dict(allths, temp_alltds)

	def help_get_dict_form_enter(self, lsh):
		needdict={}
		result_dict = self.send_post_for_enter('http://gsxt.gzgs.gov.cn/nzgs/search!searchNbxx.shtml',self.nbxh, '0', '14', lsh)
		print result_dict
		value = self.get_dict_enter(allths = [u'注册号/统一社会信用代码', u'企业名称', u'企业联系电话', u'邮政编码', u'企业通信地址', u'企业电子邮箱', u'有限责任公司本年度是否发生股东股权转让', u'企业经营状态', u'是否有网站或网店', u'是否有投资信息或购买其他公司股权', u'从业人数'],
							alltds = result_dict,
							alltds_keys = [u'zch', u'qymc', u'lxdh', u'yzbm', u'dz', u'dzyx', u'sfzr', u'jyzt', u'sfww', u'sfdw', u'cyrs'],)
		needdict[u'企业基本信息'] = value[0]

		result_dict = self.send_post_for_enter('http://gsxt.gzgs.gov.cn/nzgs/search!searchNbxx.shtml',self.nbxh, '0', '15', lsh)
		value = self.get_dict_enter(allths = [u'类型', u'名称', u'网址'],
							alltds = result_dict,
							alltds_keys = [],)
		needdict[u'网站或网店信息'] = value

		result_dict = self.send_post_for_enter('http://gsxt.gzgs.gov.cn/nzgs/search!searchNbxx.shtml',self.nbxh, '0', '19', lsh)
		value = self.get_dict_enter(allths = [u'注册号/股东', u'认缴出资额（万元）', u'认缴出资时间', u'认缴出资方式', u'实缴出资额（万元）', u'出资时间', u'出资方式'],
							alltds = result_dict,
							alltds_keys = [u'tzr', u'rjcze', u'rjczrq', u'rjczfs', u'sjcze', u'sjczrq', u'sjczfs'])
		needdict[u'股东及出资信息'] = value
		
		result_dict = self.send_post_for_enter('http://gsxt.gzgs.gov.cn/nzgs/search!searchNbxx.shtml',self.nbxh, '0', '16', lsh)
		value = self.get_dict_enter(allths = [u'资产总额', u'所有者权益合计', u'销售总额', u'利润总额', u'销售总额中主营业务收入', u'净利润', u'纳税总额', u'负债总额'],
							alltds = result_dict,
							alltds_keys = [u'zcze', u'qyhj', u'xsze', u'lrze', u'zysr', u'lrze', u'nsze', u'fzze'])
		needdict[u'企业资产状况信息'] = value[0]

		result_dict = self.send_post_for_enter('http://gsxt.gzgs.gov.cn/nzgs/search!searchNbxx.shtml',self.nbxh, '0', '41', lsh)
		value = self.get_dict_enter(allths = [u'序号', u'修改事项', u'修改前', u'修改后', u'修改日期'],
							alltds = result_dict,
							alltds_keys = [u'rownum', u'bgsxmc', u'bgq', u'bgh', u'bgrq'])
		needdict[u'修改记录'] = value
		needdict[u'对外投资信息'] = []
		needdict[u'对外提供保证担保信息'] = []
		needdict[u'股权变更信息'] = []
		return needdict

	def get_id_num(self, findCode):
		count = 0
		while count < 20:
			# print self.cur_time
			yzm = self.get_check_num()
			print yzm
			if yzm is None:
				# print count,yzm
				count += 1
				continue
			data = {'q':findCode, 'validCode':yzm}
			first_count = 0
			resp = None
			while first_count<10:
				try:
					resp = self.reqst.post(self.mydict['searchList'], data=data)
				except:
					first_count += 1
					continue
				if resp.status_code == 200:
					break

			if resp.status_code == 200 :
				result_dict = json.loads(resp.content)
				# print result_dict
				if result_dict[u'successed'] == 'true' or result_dict[u'successed'] == True:
					print result_dict
					return result_dict[u'data'][0][u'nbxh']
					break
				else:
					count += 1
					continue
			else:
				count+=1
				continue
			# print resp.content
			break
			count += 1
		pass
	

	def get_one_to_one_dict(self, allths, alltds):
		# if len(allths) == len(alltds):
		# 	one_to_one_dict = {}
		# 	for key, value in zip(allths, alltds):
		# 		one_to_one_dict[key] = value
		# 	return one_to_one_dict
		# else:
		templist = []
		x = 0
		y = x + len(allths)
		#print '---------------------%d-------------------------------%d' % (len(allth), len(alltd))
		while y <= len(alltds):
			tempdict = {}
			for keys, values in zip(allths,alltds[x:y]):
				tempdict[keys] = values
			x = y
			y = x + len(allths)
			templist.append(tempdict)
		return templist

	def test_print_table(self, tables):
		for table in tables:
			print table
	def test_print_all_ths_tds(self, head, allths, alltds):
		print '--------------',head,'--------------'
		for th in allths:
			print th
		for td in alltds:
			print td

	def test_print_all_dict(self, mydict):
		for key,value in mydict.items():
			print key,':',value

	def get_json_one(self, allths, alltds, alltds_keys, head):
		alltds = json.loads(alltds)
		print alltds
		if not alltds[u'data']:
			self.result_json_dict[head] = []
		else:
			temp_alltds = []
			for item in alltds[u'data']:
				for key in alltds_keys:
					temp_alltds.append(item[key])
				if head == 'ind_comm_pub_reg_shareholder':
					temp_alltds.append(None)
			if head == u'ind_comm_pub_reg_basic' or head == u'ind_comm_pub_arch_liquidation':
				self.result_json_dict[head] = self.get_one_to_one_dict(allths, temp_alltds)[0]
			else:
				self.result_json_dict[head] = self.get_one_to_one_dict(allths, temp_alltds)


		pass			
	def get_json_two(self, allths, alltds, alltds_keys, head):
		alltds = json.loads(alltds)
		print alltds_keys
		if not alltds[u'data']:
			self.result_json_dict[head] = []
		else:
			temp_alltds = []
			for item in alltds[u'data']:
				for key in alltds_keys:
					if head == u'ent_pub_ent_annual_report' and key == 'lsh':
						if item[key] is False or item[key]=='' or item[key]==None:
							temp_alltds.append(None)
						else:
							temp_alltds.append( self.help_get_dict_form_enter(item[key]))
					elif head == u'ent_pub_administration_license' and key == 'lsh':
						if item[key] is False or item[key]=='' or item[key]==None:
							temp_alltds.append(None)
						else:
							temp_alltds.append( [])
					else:
						temp_alltds.append(item[key])
			self.result_json_dict[head] = self.get_one_to_one_dict(allths, temp_alltds)
		# if not alltds
		pass
	def get_json_three(self, allths, alltds, alltds_keys, head):
		alltds = json.loads(alltds)
		print alltds_keys
		if not alltds[u'data']:
			self.result_json_dict[head] = []
		else:
			temp_alltds = []
			for item in alltds[u'data']:
				for key in alltds_keys:
					temp_alltds.append(item[key])
			self.result_json_dict[head] = self.get_one_to_one_dict(allths, temp_alltds)
		pass
	def get_json_four(self, allths, alltds, alltds_keys, head):
		alltds = json.loads(alltds)
		print alltds_keys
		if not alltds[u'data']:
			self.result_json_dict[head] = []
		else:
			temp_alltds = []
			for item in alltds[u'data']:
				for key in alltds_keys:
					temp_alltds.append(item[key])
			self.result_json_dict[head] = self.get_one_to_one_dict(allths, temp_alltds)
		pass

	def send_post(self, host, nbxh, c, t):
		count = 0
		while count < 10:
			data = {'nbxh':nbxh, 'c':c, 't':t}
			try:
				resp = self.reqst.post(host, data=data)
			except:
				count +=1
				continue
			if resp.status_code == 200:
				return resp.content
			else:
				count += 1
				continue


	def run(self, findCode):

		self.ent_number = str(findCode)
		#对每个企业都指定一个html的存储目录
		self.html_restore_path = self.html_restore_path + self.ent_number + '/'
		if settings.save_html and not os.path.exists(self.html_restore_path):
			CrawlerUtils.make_dir(self.html_restore_path)

		nbxh = self.get_id_num(findCode)
		self.nbxh = nbxh

		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '5')
		print result_dict
		self.get_json_one(allths=[u'注册号/统一社会信用代码', u'名称', u'类型', u'法定代表人', u'注册资本', u'成立日期', u'住所', u'营业期限自', u'营业期限至', u'经营范围', u'登记机关', u'核准日期', u'登记状态'],
							alltds = result_dict,
							alltds_keys = [u'zch',u'qymc',u'qylxmc',u'fddbr',u'zczb',u'clrq',u'zs',u'yyrq1',u'yyrq2',u'jyfw',u'djjgmc',u'hzrq',u'mclxmc'],
							head = 'ind_comm_pub_reg_basic')
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '3')
		print result_dict
		self.get_json_one(allths = [u'变更事项', u'变更前内容', u'变更后内容', u'变更日期'],
							alltds = result_dict,
							alltds_keys = [u'bcsxmc',u'bcnr',u'bghnr', u'hzrq'],
							head = 'ind_comm_pub_reg_modify')
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '2', '3')
		print result_dict
		self.get_json_one(allths = [u'股东类型', u'股东', u'证照/证件类型', u'证照/证件号码', u'详情'],
							alltds = result_dict,
							alltds_keys = [u'tzrlxmc',u'czmc',u'zzlxmc', u'zzbh'],
							head = 'ind_comm_pub_reg_shareholder')
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '8')
		print result_dict
		self.get_json_one(allths = [u'序号', u'姓名', u'职务'],
							alltds = result_dict,
							alltds_keys = [u'rownum',u'xm',u'zwmc'],
							head = 'ind_comm_pub_arch_key_persons')
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '36')
		print result_dict
		self.get_json_one(allths = [u'清算负责人', u'清算组成员'],
							alltds = result_dict,
							alltds_keys = [],
							head = 'ind_comm_pub_arch_liquidation')
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '9')
		print result_dict
		self.get_json_one(allths = [u'序号', u'注册号/统一社会信用代码', u'名称', u'登记机关'],
							alltds = result_dict,
							alltds_keys = [u'rownum',u'fgszch',u'fgsmc', u'fgsdjjgmc'],
							head = 'ind_comm_pub_arch_branch')
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '25')
		print result_dict
		self.get_json_one(allths = [u'序号', u'登记编号', u'登记日期', u'登记机关', u'被担保债权数额', u'状态', u'公示日期', u'详情'],
							alltds = result_dict,
							alltds_keys = [],
							head = 'ind_comm_pub_movable_property_reg')
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '4')
		print result_dict
		self.get_json_one(allths = [u'序号', u'登记编号', u'出质人', u'证照/证件号码', u'出质股权数额', u'质权人', u'证照/证件号码', u'股权出质设立登记日期', u'状态', u'公示日期', u'变化情况'],
							alltds = result_dict,
							alltds_keys = [],
							head = 'ind_comm_pub_equity_ownership_reg')
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '1')
		print result_dict
		self.get_json_one(allths = [],
							alltds = result_dict,
							alltds_keys = [],
							head = 'ind_comm_pub_administration_sanction')
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '33')
		print result_dict
		self.get_json_one(allths = [],
							alltds = result_dict,
							alltds_keys = [],
							head = 'ind_comm_pub_business_exception')
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '34')
		print result_dict
		self.get_json_one(allths = [],
							alltds = result_dict,
							alltds_keys = [],
							head = 'ind_comm_pub_serious_violate_law')
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '35')
		print result_dict
		self.get_json_one(allths = [],
							alltds = result_dict,
							alltds_keys = [],
							head = 'ind_comm_pub_spot_check')


		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '13')
		print result_dict
		self.get_json_two(allths = [u'序号', u'详情', u'报送年度', u'发布日期'],
							alltds = result_dict,
							alltds_keys = [u'rownum', u'lsh', u'nd', u'rq'],
							head = 'ent_pub_ent_annual_report')
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '40')
		print result_dict
		self.get_json_two(allths = [u'股东', u'认缴额（万元）', u'实缴额（万元）', u'认缴出资方式', u'认缴出资额（万元）', u'认缴出资日期', u'认缴公示日期', u'实缴出资方式', u'实缴出资额（万元）', u'实缴出资日期', u'实缴公示日期'],
							alltds = result_dict,
							alltds_keys = [u'tzrmc', u'ljrje', u'ljsje', u'rjczfs', u'rjcze', u'rjczrq', u'rjgsrq', u'sjczfs', u'sjcze', u'sjczrq', u'sjgsrq'],
							head = 'ent_pub_shareholder_capital_contribution')
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '23')
		print result_dict
		self.get_json_two(allths = [u'序号', u'股东', u'变更前股权比例', u'变更后股权比例', u'股权变更日期', u'公示日期'],
							alltds = result_dict,
							alltds_keys = [],
							head = 'ent_pub_equity_change')
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '20')
		print result_dict
		self.get_json_two(allths = [u'序号', u'许可文件编号', u'许可文件名称', u'有效期自', u'有效期至', u'许可机关', u'许可内容', u'状态', u'公示日期', u'详情'],
							alltds = result_dict,
							alltds_keys = [u'rownum', u'xkwjbh', u'xkwjmc', u'ksyxqx', u'jsyxqx', u'xkjg', u'xknr', u'zt', u'gsrq', u'lsh'],
							head = 'ent_pub_administration_license')
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '21')
		print result_dict
		self.get_json_two(allths = [],
							alltds = result_dict,
							alltds_keys = [],
							head = 'ent_pub_knowledge_property')
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '22')
		print result_dict
		self.get_json_two(allths = [],
							alltds = result_dict,
							alltds_keys = [],
							head = 'ent_pub_shareholder_modify')


		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchOldData.shtml',nbxh, '0', '37')
		print result_dict
		self.get_json_three(allths = [u'序号', u'许可文件编号', u'许可文件名称', u'有效期自', u'有效期至', u'有效期', u'许可机关', u'许可内容', u'状态', u'详情'],
							alltds = result_dict,
							alltds_keys = [u'rownum', u'xkwjbh', u'xkwjmc', u'yxq1', u'yxq2', u'yxq', u'xkjg', u'xknr', u'zt', u'zt'],
							head = 'other_dept_pub_administration_license')
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchOldData.shtml',nbxh, '0', '38')
		print result_dict
		self.get_json_two(allths = [u'序号', u'行政处罚决定书文号', u'违法行为类型', u'行政处罚内容', u'作出行政处罚决定机关名称', u'作出行政处罚决定日期'],
							alltds = result_dict,
							alltds_keys = [],
							head = 'other_dept_pub_administration_sanction')



		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '49')
		print result_dict
		self.get_json_four(allths = [u'序号', u'被执行人', u'股权数额', u'执行法院', u'协助公示通知书文号', u'状态', u'详情'],
							alltds = result_dict,
							alltds_keys = [],
							head = 'judical_assist_pub_equity_freeze')
		result_dict = self.send_post('http://gsxt.gzgs.gov.cn/nzgs/search!searchData.shtml',nbxh, '0', '53')
		print result_dict
		self.get_json_four(allths = [u'序号', u'被执行人', u'股权数额', u'受让人', u'执行法院', u'详情'],
							alltds = result_dict,
							alltds_keys = [],
							head = 'judical_assist_pub_shareholder_modify')


		CrawlerUtils.json_dump_to_file(self.json_restore_path, {self.ent_number: self.result_json_dict})

if __name__ == '__main__':
	guizhou = GuizhouCrawler('./enterprise_crawler/guizhou.json')
	# guizhou.run('520300000040573')
	f = open('enterprise_list/guizhou.txt', 'r')
	for line in f.readlines():
		print line.split(',')[2].strip()
		guizhou.run(str(line.split(',')[2]).strip())
	f.close()