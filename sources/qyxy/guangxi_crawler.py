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

class GuangxiCrawler(object):
	#html数据的存储路径
	html_restore_path = settings.html_restore_path + '/guangxi/'
	ckcode_image_path = settings.json_restore_path + '/guangxi/ckcode.jpg'
    	#write_file_mutex = threading.Lock()
	def __init__(self, json_restore_path):
		# self.cur_time = str(int(time.time()*1000))
		self.id = None
		self.reqst = requests.Session()
		self.json_restore_path = json_restore_path
		self.ckcode_image_path = settings.json_restore_path + '/guangxi/ckcode.jpg'
		self.result_json_dict = {}
		self.reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

		self.mydict = {'eareName':'http://gxqyxygs.gov.cn',
				'search':'http://gxqyxygs.gov.cn/search.jspx',
				'searchList':'http://gxqyxygs.gov.cn/searchList.jspx',
				'validateCode':'http://gxqyxygs.gov.cn/validateCode.jspx?type=0&id=0.6145392225593206'}

		self.search_dict = {
				'eareName':'http://gxqyxygs.gov.cn',
				'search':'http://222.143.24.157/search.jspx',
				'validateCode':'http://222.143.24.157/validateCode.jspx?type=0&id=0.8720359673599201',
				'searchList':'http://222.143.24.157/searchList.jspx',
				'businessPublicity':'http://222.143.24.157/businessPublicity.jspx?',
				'enterprisePublicity':'http://222.143.24.157/enterprisePublicity.jspx?',
				'otherDepartment':'http://222.143.24.157/otherDepartment.jspx?',
				'justiceAssistance':'http://222.143.24.157/justiceAssistance.jspx?',
				'next_head':'http://gxqyxygs.gov.cn/Query'

		}
	
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
		print self.mydict['search']
		resp = self.reqst.get(self.mydict['search'], timeout = 120)
		if resp.status_code != 200:
			print resp.status_code
			return None
		# print BeautifulSoup(resp.content).prettify
		resp = self.reqst.get(self.mydict['validateCode'], timeout = 120)
		if resp.status_code != 200:
			print 'no validateCode'
			return None
		with open(self.ckcode_image_path, 'wb') as f:
			f.write(resp.content)
		from CaptchaRecognition import CaptchaRecognition
		code_cracker = CaptchaRecognition('guangxi')
		ck_code = code_cracker.predict_result(self.ckcode_image_path)
		if ck_code is None:
			return None
		else:
			return ck_code[1]

		

	def get_id_num(self, findCode):
		count = 0
		while count < 20:
			# print self.cur_time
			yzm = self.get_check_num()
			print yzm
			if yzm is None:
				count += 1
				continue
			data = {'checkNo':yzm, 'entName':findCode}
			resp = self.reqst.post(self.mydict['searchList'], data=data, timeout = 120)
			print resp.status_code
			# print BeautifulSoup(resp.content).prettify()
			if resp.status_code == 200:
				soup = BeautifulSoup(resp.content)
				div =  soup.find_all('div', attrs={'class':'list'})
				if not div:
					count += 1
					continue
				if div[0].find_all('a'):
					return div[0].find_all('a')[0]['href'].split('?')[1]
				else:
					count += 1
					continue
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
	def test_print_head_ths_tds(self, head, allths, alltds):
		print '-----', head, '-------'
		for th in allths:
			print th
		print '----th(%d)-----td(%d)-----' % (len(allths), len(alltds))
		for td in alltds:
			print td

	def test_print_all_dict(self, mydict):
		for key,value in mydict.items():
			print key,':',value
	def get_tables(self, url):
		resp = self.reqst.get(url, timeout = 120)
		if resp.status_code == 200:
			return BeautifulSoup(resp.content).find_all('table')
		else:
			return None
	def get_head_allths_alltds(self, table):
		if table.find_all('th'):
			head = table.find_all('th')[0].get_text().strip().split('\n')[0].strip()
		else:
			head = None
		allths = [th.get_text().strip() for th in table.find_all('th')[1:] if th.get_text()]
		alltds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]
		return head, allths, alltds
	def do_with_only_table(self, table):
		return self.get_head_allths_alltds(table)

	def get_dict_from_enter(self, tables):
		tempdict = {}
		for i, table in enumerate(tables):
			head = table.find_all('th')[0].get_text().strip()
			allths = [th.get_text().strip() for th in table.find_all('th')[1:] if th.get_text()]
			for index, th in enumerate(allths):
				if th[:2] == '<<':
					allths = allths[:index]
					break
			alltds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]
			if i==0:
				head = allths[0]
				allths = allths[1:]
			if not any(alltds):
				#alltds = [None for th in allths]
				alltds = []
			self.test_print_head_ths_tds(head, allths, alltds)
			if head == u'企业资产状况信息' or head == u'企业基本信息':
				tempdict[head] = self.get_one_to_one_dict(allths, alltds)[0]
				pass
			else:
				tempdict[head] = self.get_one_to_one_dict(allths, alltds)
		return tempdict

	def get_dict_from_gudong_detail(self, table):
		# allths = [th.get_text().strip() for th in table.find_all('th')[1:]]
		# allths = allths[:3]+allths[5:]
		# alltds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]
		allths = [th.get_text().strip() for th in table.find_all('th')]
		head = allths[0]
		alltds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]
		self.test_print_head_ths_tds(head, allths[1:], alltds)
		son_need_dict = {}
		for key, value in zip(allths[6:], alltds[3:]):
			son_need_dict[key] = value
		need_dict = {}
		for key, value in zip(allths[1:4], alltds[:3]):
			need_dict[key] = value
		need_dict['list'] = [son_need_dict]
		return {head:[need_dict]}
		# if len(alltds) == 0:
		# 	alltds = [None for th in allths]
		# return self.get_one_to_one_dict(allths, alltds)

	def get_dict_from_dongcan_detail(self, tables):
		tempdict = {}
		for i, table in enumerate(tables):

			if table.find_all('th') and not table.find_all('a'):
				head = table.find_all('th')[0].get_text().strip()
				print '----',head
				if head == u'动产抵押登记信息' or u'抵押权人概况' or u'被担保债权概况':
					allths = [th.get_text().strip() for th in table.find_all('th')[1:] if th.get_text()]
					alltds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]
				elif head == u'抵押物概况':
					allths = [th.get_text().strip() for th in table.find_all('th')[1:] if th.get_text()]
					alltds = [td.get_text().strip() if td.get_text() else None for td in tables[i+1].find_all('td')]
				# if len(alltds) == 0:
				# 	alltds = [None for th in allths]
				tempdict[head] = self.get_one_to_one_dict(allths, alltds)
		return tempdict

	def do_with_hasnext(self, table_th, table_a):
		head, allths = self.get_head_allths_alltds(table_th)[:2]
		alltds = []
		if head == u'主要人员信息':
			allths = allths[:int(len(allths)/2)]
		count_a = len(table_a)
		href = table_a.find_all('a')[0]['href']
		m = re.search(r'\(\"(\w+?)\",\d+\)', href)
		alltds = []
		if m:
			where = m.group(1).capitalize()
			alltds = []
			for i in range(1, count_a+1):
				urls = self.search_dict['next_head'] + where + 'List.jspx?pno=' + str(i) + '&mainId=' + self.id[3:]
				print urls
				resp = self.reqst.get(urls, timeout = 120)
				if resp.status_code == 200:
					next_table = self.get_tables(urls)[0]
					# next_table = BeautifulSoup(self.reqst.get(urls).content).find_all('table')[0]
					if head == u'股东（发起人）信息' or head == u'股东信息' or head == u'动产抵押登记信息':
						for td in next_table.find_all('td'):
							if td.find_all('a'):
								detail_href = td.a['onclick']
								first = detail_href.find('window.open')
								#print detail_href[first+13:-2]
								if head == u'股东（发起人）信息' or head == u'股东信息':
									alltds.append(self.get_dict_from_gudong_detail(self.get_tables(self.search_dict['eareName'] + detail_href[first+13:-2])[0]))
								elif head == u'动产抵押登记信息':
									alltds.append(self.get_dict_from_dongcan_detail(self.get_tables(self.search_dict['eareName'] + detail_href[first+13:-2])))
							elif td.get_text():
								alltds.append(td.get_text().strip())
							else:
								alltds.append(None)
					elif head == u'变更信息' or head == u'修改记录':
						for td in next_table.find_all('td'):
							if td.get_text():
								if len(td.find_all('span'))>1:
									alltds.append(td.find_all('span')[1].get_text().strip().split('\n')[0].strip())
								else:
									alltds.append(td.get_text().strip())
							else:
								alltds.append(None)
					else:
						if i == 1 and alltds:
							alltds = []
						else:
							alltds = alltds + [td.get_text().strip() if td.get_text() else None for td in next_table.find_all('td')]
				else:
					print 'get____error'
		else:
			print 'in hasnext no find search!'*3

		# if len(alltds) == 0:
		# 	alltds = [None for th in allths]
		self.test_print_head_ths_tds(head, allths, alltds)
		return head, allths, alltds
	def do_with_nonext(self, table_th, table_td):
		head, allths = self.get_head_allths_alltds(table_th)[:2]
		alltds = self.get_head_allths_alltds(table_td)[2]
		if head == u'主要人员信息':
			allths = allths[:int(len(allths)/2)]
		alltds = [td.get_text().strip() if td.get_text() else None for td in table_td.find_all('td')]
		if head == u'股东（发起人）信息' or head == u'动产抵押登记信息' or head == u'股东信息':
			alltds = []
			for td in table_td.find_all('td'):
				if td.find_all('a'):
					detail_href = td.a['onclick']
					first = detail_href.find('window.open')
					#print detail_href[first+13:-2]
					if head == u'股东（发起人）信息' or head == u'股东信息':
						alltds.append(self.get_dict_from_gudong_detail(self.get_tables(self.search_dict['eareName'] + detail_href[first+13:-2])[0]))
					elif head == u'动产抵押登记信息':
						alltds.append(self.get_dict_from_dongcan_detail(self.get_tables(self.search_dict['eareName'] + detail_href[first+13:-2])))
				elif td.get_text():
					alltds.append(td.get_text().strip())
				else:
					alltds.append(None)
		elif head == u'变更信息' or head == u'修改记录':
			alltds = []
			for td in table_td.find_all('td'):
				if td.get_text():
					if len(td.find_all('span'))>1:
						alltds.append(td.find_all('span')[1].get_text().strip().split('\n')[0].strip())
					else:
						alltds.append(td.get_text().strip())
				else:
					alltds.append(None)

		return head, allths, alltds

	def get_json_one(self, mydict, tables):
		count_table = len(tables)
		print count_table
		for i, table in enumerate(tables):
			# print table
			if table.find_all('th') and not table.find_all('a'):
				head = table.find_all('th')[0].get_text().split('\n')[0].strip()
				if i == 0 or head == u'清算信息':
					head, allths, alltds = self.do_with_only_table(table)
				elif i+2<count_table and len(tables[i+2].find_all('a'))>1:
					head, allths, alltds = self.do_with_hasnext(table, tables[i+2])
				elif i+1<count_table:
					head, allths, alltds = self.do_with_nonext(table, tables[i+1])
				self.test_print_head_ths_tds(head, allths, alltds)
				self.result_json_dict[mydict[head]] = self.get_one_to_one_dict(allths, alltds)
				if head == u'基本信息' or head == u'清算信息':
					self.result_json_dict[mydict[head]] = self.get_one_to_one_dict(allths, alltds)[0]

		pass			
	def get_json_two(self, mydict, tables):
		count_table = len(tables)
		print count_table
		#self.test_print_table(tables)
		for i, table in enumerate(tables):
			if table.find_all('th'):
				head = table.find_all('th')[0].get_text().split('\n')[0].strip()
				print head
				allths = [th.get_text().strip() for th in table.find_all('th')[1:] if th.get_text()]
				alltds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]
				if head == u'企业年报':
					alltds = []
					for td in table.find_all('td'):
						# detail_enter_port_dict = {}
						if td.get_text():
							if td.find('a'):
								alltds.append(td.get_text().strip())
								print 'a-----:', td.get_text().strip()
								get_count = 0
								enter_tables = None
								while get_count < 10:
									enter_tables = self.get_tables(self.search_dict['eareName'] + td.a['href'])
									if enter_tables is None:
										get_count += 1
										continue
									else: break
								if enter_tables:
									alltds.append( self.get_dict_from_enter(enter_tables ) )
								else:
									alltds.append( None)
								#alltds.append(None)
							else:
								alltds.append(td.get_text().strip())
						else:
							alltds.append(None)
						# alltds.append(detail_enter_port_dict)
					allths.insert(2,u'详情')
					self.test_print_head_ths_tds(head, allths, alltds)
					self.result_json_dict[mydict[head]] = self.get_one_to_one_dict(allths, alltds)
					pass
				elif head == u'行政许可信息' or head == u'股权变更信息':
					self.do_with_nonext(table, tables[i+1])
					pass
				elif head == u'股东及出资信息':
					allths = allths[:3]+allths[5:]
					print '******', head
					self.result_json_dict[mydict[head]] = self.get_one_to_one_dict(allths, alltds)
					pass
				else:
					self.do_with_nonext(table, tables[i+1])
					pass
		
		pass
	def get_json_three(self, mydict, tables):
		count_table = len(tables)
		print count_table
		for table in tables:
			if table.find_all('th') and not table.find_all('a'):
				head = table.find_all('th')[0].get_text().split('\n')[0].strip()
				print head
				allths = [th.get_text().strip() for th in table.find_all('th')[1:] if th.get_text()]
				alltds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]
				# if len(alltds) == 0:
				# 	alltds = [None for th in allths]
				self.test_print_head_ths_tds(head, allths, alltds)
				if head != '':
					self.result_json_dict[mydict[head]] = self.get_one_to_one_dict(allths, alltds)
		
		pass
	def get_json_four(self, mydict, tables):
		count_table = len(tables)
		print count_table
		for table in tables:
			if table.find_all('th') and not table.find_all('a'):
				head = table.find_all('th')[0].get_text().split('\n')[0].strip()
				print head
				allths = [th.get_text().strip() for th in table.find_all('th')[1:] if th.get_text()]
				alltds = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]
				# if len(alltds) == 0:
				# 	alltds = [None for th in allths]
				self.test_print_head_ths_tds(head, allths, alltds)
				if head != '':
					self.result_json_dict[mydict[head]] = self.get_one_to_one_dict(allths, alltds)
		pass

	def run(self, findCode):

		self.ent_number = str(findCode)
		#对每个企业都指定一个html的存储目录
		self.html_restore_path = self.html_restore_path + self.ent_number + '/'
		if settings.save_html and not os.path.exists(self.html_restore_path):
			CrawlerUtils.make_dir(self.html_restore_path)

		self.result_json_dict = {}
		self.id = self.get_id_num(findCode)
		print self.id
		resp = self.reqst.get('http://gxqyxygs.gov.cn/businessPublicity.jspx?' + self.id, timeout = 120)
		soup = BeautifulSoup(resp.content)
		self.get_json_one(self.one_dict, soup.find_all('table'))

		resp = self.reqst.get('http://gxqyxygs.gov.cn/enterprisePublicity.jspx?' + self.id, timeout = 120)
		soup = BeautifulSoup(resp.content)
		self.get_json_two(self.two_dict, soup.find_all('table'))

		resp = self.reqst.get('http://gxqyxygs.gov.cn/otherDepartment.jspx?' + self.id, timeout = 120)
		soup = BeautifulSoup(resp.content)
		self.get_json_three(self.three_dict, soup.find_all('table'))

		resp = self.reqst.get('http://gxqyxygs.gov.cn/justiceAssistance.jspx?' + self.id, timeout = 120)
		soup = BeautifulSoup(resp.content)
		self.get_json_four(self.four_dict, soup.find_all('table'))

		CrawlerUtils.json_dump_to_file(self.json_restore_path, {self.ent_number: self.result_json_dict})

if __name__ == '__main__':
	guangxi = GuangxiCrawler('./enterprise_crawler/guangxi.json')
	# guangxi.run('450200000016746')
	# guangxi.run('450000000000566')
	f = open('enterprise_list/guangxi.txt', 'r')
	for line in f.readlines():
		print line.split(',')[2].strip()
		guangxi.run(str(line.split(',')[2]).strip())
	f.close()