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
import importlib

ENT_CRAWLER_SETTINGS = os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS:
    settings = importlib.import_module(ENT_CRAWLER_SETTINGS)
else:
    import settings

class SichuanCrawler(object):
	#html数据的存储路径
	html_restore_path = settings.html_restore_path + '/sichuan/'
	ckcode_image_path = settings.json_restore_path + '/sichuan/ckcode.jpg'
    	#write_file_mutex = threading.Lock()
	def __init__(self, json_restore_path):
		self.pripid = None
		self.cur_time = str(int(time.time()*1000))
		self.reqst = requests.Session()
		self.json_restore_path = json_restore_path
		self.ckcode_image_path = settings.json_restore_path + '/sichuan/ckcode.jpg'
		self.result_json_dict = {}
		self.reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

		self.mydict = {'eareName':'http://www.ahcredit.gov.cn',
				'search':'http://gsxt.scaic.gov.cn/ztxy.do?method=index&random=',
				'searchList':'http://gsxt.scaic.gov.cn/ztxy.do?method=list&djjg=&random=',
				'validateCode':'http://gsxt.scaic.gov.cn/ztxy.do?method=createYzm'}
	
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
		print self.mydict['search']+self.cur_time
		resp = self.reqst.get(self.mydict['search']+self.cur_time, timeout = 180)
		if resp.status_code != 200:
			print resp.status_code
			return None
		#print BeautifulSoup(resp.content).prettify
		resp = self.reqst.get(self.mydict['validateCode']+'&dt=%s&random=%s' % (self.cur_time, self.cur_time), timeout = 180)
		if resp.status_code != 200:
			print 'no validateCode'
			return None
		with open(self.ckcode_image_path, 'wb') as f:
			f.write(resp.content)
		from CaptchaRecognition import CaptchaRecognition
		code_cracker = CaptchaRecognition('sichuan')
		ck_code = code_cracker.predict_result(self.ckcode_image_path)
		if ck_code is None:
			return None
		else:
			return ck_code[1]

		

	def get_id_num(self, findCode):
		count = 0
		while count < 20:
			yzm = self.get_check_num()
			if yzm is None:
				count += 1
				continue
			print self.cur_time
			data = {'currentPageNo':'1', 'yzm':yzm, 'cxym':"cxlist", 'maent.entname':findCode}
			resp = self.reqst.post(self.mydict['searchList']+self.cur_time, data=data, timeout = 180)
			print resp.status_code
			divs = BeautifulSoup(resp.content).find_all('div', attrs={"style":"width:950px; padding:25px 20px 0px; overflow: hidden;float: left;"})
			#print divs[0]
			try:
				onclick = divs[0].ul.li.a['onclick']
				print onclick
				m = re.search(r"openView\(\'(\w+?)\'", onclick)
				if m:
					return m.group(1) 
			except:
				print count
				print '*'*100
				pass
			count += 1

		pass
	def get_re_list_from_content(self, content):
		
		pass

	def help_dcdy_get_dict(self, method, maent_pripid, maent_xh, random):
		data = {'method':method, 'maent.pripid':maent_pripid, 'maent.xh':maent_xh, 'random':random}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data = data, timeout = 180)
		needdict = {}
		for table in BeautifulSoup(resp.content).find_all('table'):
			dcdy_head, dcdy_allths, dcdy_alltds = self.get_head_ths_tds(table)
			needdict[dcdy_head] = self.get_one_to_one_dict(dcdy_allths, dcdy_alltds)
		return needdict

	def help_enter_get_dict(self, method, maent_pripid, year, random):
		data = {'method':method, 'maent.pripid':maent_pripid, 'maent.nd':year, 'random':random}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		#print resp.status_code
		#print BeautifulSoup(resp.content).prettify
		needdict = {}
		for i, table in enumerate(BeautifulSoup(resp.content).find_all('table')):
			enter_head, enter_allths, enter_alltds = self.get_head_ths_tds(table)
			if i == 0:
				enter_head = enter_allths[0]
				enter_allths = enter_allths[1:]
			if enter_head == u'股东及出资信息':
				enter_allths = [u'股东', u'认缴出资额（万元）', u'认缴出资时间', u'认缴出资方式', u'实缴出资额（万元）', u'出资时间', u'出资方式']
			#self.test_print_all_ths_tds(enter_head, enter_allths, enter_alltds)
			needdict[enter_head] = self.get_one_to_one_dict(enter_allths, enter_alltds)
			if enter_head == u'企业基本信息' or enter_head == u'企业资产状况信息':
				needdict[enter_head] = self.get_one_to_one_dict(enter_allths, enter_alltds)[0]
		return needdict



	def help_detail_get_dict(self, method, maent_xh, maent_pripid, random):
		data = {'method':method, 'maent.xh':maent_xh, 'maent.pripid':maent_pripid, 'random':random}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		# print resp.status_code
		# print BeautifulSoup(resp.content).prettify
		for table in BeautifulSoup(resp.content).find_all('table'):
			if table.find_all('th') and table.find_all('th')[0].get_text().strip() == u'股东及出资信息':
				#print table
				detail_head, detail_allths, detail_alltds = self.get_head_ths_tds(table)
				# self.test_print_all_ths_tds(detail_head, detail_allths, detail_alltds)
				tempdict = {}
				for key, value in zip(detail_allths[:3], detail_alltds[:3]):
					tempdict[key] = value
				onelist_dict = {}
				for key, value in zip(detail_allths[3:], detail_alltds[3:]):
					onelist_dict[key] = value
				tempdict['list'] = [onelist_dict]
				return {u'股东及出资信息':[tempdict]}
				break
		# else:
		# 	print 'i'*100
		
	def get_head_ths_tds(self, table):
		print table
		try:
			head = table.find_all('th')[0].get_text().strip().split('\n')[0].strip()
		except:
			head = None
			pass
		allths = [th.get_text().strip() for th in table.find_all('th')[1:] if th.get_text()]
		for i, th in enumerate(allths):
			if th[:2] == '<<':
				allths = allths[:i]
				break
		alltds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]
		if head == u'变更信息' or head == u'修改记录':
			alltds = []
			for td in table.find_all('td'):
				if td.get_text():
					if len(td.find_all('span'))>1:
						alltds.append(td.find_all('span')[1].get_text().strip().split('\n')[0].strip())
					else:
						alltds.append(td.get_text().strip())
				else:
					alltds.append(None)

		if head == u'主要人员信息':
			allths = allths[:int(len(allths)/2)]
		if head == u'股东及出资信息':
			allths = allths[:3]+allths[5:]
		if head == u'股东信息':
			alltds = []
			for td in table.find_all('td'):
				if td.find('a'):
					onclick = td.a['onclick']
					m = re.search(r"showRyxx\(\'(\w+?)\',\'(\w+?)\'\)", onclick)
					if m:
						maent_xh = m.group(1)
						maent_pripid = m.group(2)
						#print 'maent_xh',':', maent_xh,'maent_pripid',':',maent_pripid
						#print self.help_detail_get_dict('tzrCzxxDetial',maent_xh, maent_pripid, self.cur_time)
						alltds.append(self.help_detail_get_dict('tzrCzxxDetial',maent_xh, maent_pripid, self.cur_time))
				elif td.get_text():
					alltds.append(td.get_text().strip())
				else:
					alltds.append(None)
		if head == u'企业年报':
			alltds = []
			for td in table.find_all('td'):
				if td.find('a'):
					onclick = td.a['onclick']
					m = re.search(r'doNdbg\(\'(\w+)\'\)',onclick)
					if m:
						alltds.append(td.get_text().strip())
						alltds.append(self.help_enter_get_dict('ndbgDetail', self.pripid, m.group(1), self.cur_time))
				elif td.get_text():
					alltds.append(td.get_text().strip())
				else:
					alltds.append(None)
			allths.insert(2, u'详情')
		if head == u'动产抵押登记信息':
			alltds = []
			for td in table.find_all('td'):
				if td.find('a'):
					onclick = td.a['onclick']
					m = re.search(r'doDcdyDetail\(\'(\w+?)\'\)', onclick)
					if m:
						alltds.append(self.help_dcdy_get_dict('dcdyDetail', self.pripid, m.group(1), self.cur_time))
				elif td.get_text():
					alltds.append(td.get_text().strip())
				else:
					alltds.append(None)
		# if len(alltds) == 0:
		# 	alltds = [None for th in allths]
		return head, allths, alltds

	def get_one_to_one_dict(self, allths, alltds):
		if len(allths) == len(alltds):
			one_to_one_dict = {}
			for key, value in zip(allths, alltds):
				one_to_one_dict[key] = value
			return [one_to_one_dict]
		else:
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
	def get_table_by_head(self, tables, head_item):
		for table in tables:
			if table.find_all('th'):
				temp_head = table.find_all('th')[0].get_text().strip().split('\n')[0].strip()
				#print 'temp_head', temp_head, 'head_item', head_item
				if temp_head == head_item:
					return table
		# else:
		# 	print 'no'*10
		pass

	def get_json_one(self, mydict, tables, *param):
		#self.test_print_table(tables)
		for head_item in param:
			#print '----'*10, head_item
			table = self.get_table_by_head(tables, head_item)
			if table:
				head, allths, alltds = self.get_head_ths_tds(table)
				#self.test_print_all_ths_tds(head, allths, alltds)
				self.result_json_dict [mydict[head]] = self.get_one_to_one_dict(allths, alltds)
		pass			
	def get_json_two(self, mydict, tables):
		#self.test_print_table(tables)
		for head_item in param:
			#print '----'*10, head_item
			table = self.get_table_by_head(tables, head_item)
			if table:
				head, allths, alltds = self.get_head_ths_tds(table)
				#self.test_print_all_ths_tds(head, allths, alltds)
				self.result_json_dict [mydict[head]] = self.get_one_to_one_dict(allths, alltds)
		
		pass
	def get_json_three(self, mydict, tables):
		#self.test_print_table(tables)
		for head_item in param:
			#print '----'*10, head_item
			table = self.get_table_by_head(tables, head_item)
			if table:
				head, allths, alltds = self.get_head_ths_tds(table)
				#self.test_print_all_ths_tds(head, allths, alltds)
				self.result_json_dict [mydict[head]] = self.get_one_to_one_dict(allths, alltds)
		
		pass
	def get_json_four(self, mydict, tables):
		#self.test_print_table(tables)
		for head_item in param:
			#print '----'*10, head_item
			table = self.get_table_by_head(tables, head_item)
			if table:
				head, allths, alltds = self.get_head_ths_tds(table)
				#self.test_print_all_ths_tds(head, allths, alltds)
				self.result_json_dict [mydict[head]] = self.get_one_to_one_dict(allths, alltds)
		pass

	def run(self, findCode):

		self.ent_number = str(findCode)
		#对每个企业都指定一个html的存储目录
		self.html_restore_path = self.html_restore_path + self.ent_number + '/'
		if settings.save_html and not os.path.exists(self.html_restore_path):
			CrawlerUtils.make_dir(self.html_restore_path)

		self.pripid = self.get_id_num(findCode)
		print findCode, self.pripid
		self.result_json_dict = {}

		data = {'method':'qyInfo', 'maent.pripid':self.pripid, 'czmk':'czmk1', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		# print BeautifulSoup(resp.content).prettify
		self.get_json_one(self.one_dict, BeautifulSoup(resp.content).find_all('table'), u'基本信息', u'股东信息', u'变更信息')

		data = {'method':'baInfo', 'maent.pripid':self.pripid, 'czmk':'czmk2', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		self.get_json_one(self.one_dict, BeautifulSoup(resp.content).find_all('table'), u'主要人员信息', u'分支机构信息', u'清算信息')

		data = {'method':'dcdyInfo', 'maent.pripid':self.pripid, 'czmk':'czmk4', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout =120)
		self.get_json_one(self.one_dict, BeautifulSoup(resp.content).find_all('table'), u'动产抵押登记信息')

		data = {'method':'gqczxxInfo', 'maent.pripid':self.pripid, 'czmk':'czmk4', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		self.get_json_one(self.one_dict, BeautifulSoup(resp.content).find_all('table'), u'股权出质登记信息')

		data = {'method':'jyycInfo', 'maent.pripid':self.pripid, 'czmk':'czmk6', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		self.get_json_one(self.one_dict, BeautifulSoup(resp.content).find_all('table'), u'经营异常信息')

		data = {'method':'yzwfInfo', 'maent.pripid':self.pripid, 'czmk':'czmk14', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		self.get_json_one(self.one_dict, BeautifulSoup(resp.content).find_all('table'), u'严重违法信息')

		data = {'method':'cfInfo', 'maent.pripid':self.pripid, 'czmk':'czmk3', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		self.get_json_one(self.one_dict, BeautifulSoup(resp.content).find_all('table'), u'行政处罚信息')

		data = {'method':'ccjcInfo', 'maent.pripid':self.pripid, 'czmk':'czmk7', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		self.get_json_one(self.one_dict, BeautifulSoup(resp.content).find_all('table'), u'抽查检查信息')




		data = {'method':'qygsInfo', 'maent.pripid':self.pripid, 'czmk':'czmk8', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		self.get_json_one(self.two_dict, BeautifulSoup(resp.content).find_all('table'), u'企业年报')

		data = {'method':'qygsForTzrxxInfo', 'maent.pripid':self.pripid, 'czmk':'czmk12', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		self.get_json_one(self.two_dict, BeautifulSoup(resp.content).find_all('table'), u'股东及出资信息', u'变更信息')

		data = {'method':'cqygsForTzrbgxxInfo', 'maent.pripid':self.pripid, 'czmk':'czmk15', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		self.get_json_one(self.two_dict, BeautifulSoup(resp.content).find_all('table'), u'股权变更信息')

		data = {'method':'qygsForXzxkInfo', 'maent.pripid':self.pripid, 'czmk':'czmk10', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		self.get_json_one(self.two_dict, BeautifulSoup(resp.content).find_all('table'), u'行政许可信息')

		data = {'method':'qygsForZzcqInfo', 'maent.pripid':self.pripid, 'czmk':'czmk11', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		self.get_json_one(self.two_dict, BeautifulSoup(resp.content).find_all('table'), u'知识产权出质登记信息')

		data = {'method':'qygsForXzcfInfo', 'maent.pripid':self.pripid, 'czmk':'czmk13', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		self.get_json_one(self.two_dict, BeautifulSoup(resp.content).find_all('table'), u'行政处罚信息')



		data = {'method':'qtgsInfo', 'maent.pripid':self.pripid, 'czmk':'czmk9', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		self.get_json_one(self.three_dict, BeautifulSoup(resp.content).find_all('table'), u'行政许可信息')

		data = {'method':'qtgsForCfInfo', 'maent.pripid':self.pripid, 'czmk':'czmk16', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		self.get_json_one(self.three_dict, BeautifulSoup(resp.content).find_all('table'), u'行政处罚信息')




		data = {'method':'sfgsInfo', 'maent.pripid':self.pripid, 'czmk':'czmk17', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		self.get_json_one(self.four_dict, BeautifulSoup(resp.content).find_all('table'), u'司法股权冻结信息')

		data = {'method':'sfgsbgInfo', 'maent.pripid':self.pripid, 'czmk':'czmk18', 'random':self.cur_time}
		resp = self.reqst.post('http://gsxt.scaic.gov.cn/ztxy.do', data=data, timeout = 180)
		self.get_json_one(self.four_dict, BeautifulSoup(resp.content).find_all('table'), u'司法股东变更登记信息')

		self.result_json_dict['ind_comm_pub_reg_basic'] = self.result_json_dict['ind_comm_pub_reg_basic'][0]
		if 'ind_comm_pub_arch_liquidation' in self.result_json_dict.keys() and len(self.result_json_dict['ind_comm_pub_arch_liquidation']) > 0:
			self.result_json_dict['ind_comm_pub_arch_liquidation'] = self.result_json_dict['ind_comm_pub_arch_liquidation'][0]
		CrawlerUtils.json_dump_to_file(self.json_restore_path, {self.ent_number: self.result_json_dict})

if __name__ == '__main__':
	sichuan = SichuanCrawler('./enterprise_crawler/sichuan.json')
	sichuan.run('510181000035008')
	# sichuan.run('511000000000753')
	# sichuan.run('510300000004462')
	# f = open('enterprise_list/sichuan.txt', 'r')
	# for line in f.readlines():
	# 	print line.split(',')[2].strip()
	# 	sichuan.run(str(line.split(',')[2]).strip())
	# f.close()