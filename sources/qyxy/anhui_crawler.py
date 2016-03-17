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
import importlib

ENT_CRAWLER_SETTINGS = os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS:
    settings = importlib.import_module(ENT_CRAWLER_SETTINGS)
else:
    import settings

class AnhuiCrawler(object):
	#html数据的存储路径
	html_restore_path = settings.html_restore_path + '/anhui/'
	#验证码图片的存储路径
    	ckcode_image_path = settings.json_restore_path + '/anhui/ckcode.jpg'
    	#write_file_mutex = threading.Lock()
	def __init__(self, json_restore_path):
		self.id = None
		self.json_restore_path = json_restore_path
		self.ckcode_image_path = settings.json_restore_path + '/anhui/ckcode.jpg'
		self.reqst = requests.Session()
		self.reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})
		self.mydict = {'eareName':'http://www.ahcredit.gov.cn',
				'search':'http://www.ahcredit.gov.cn/search.jspx',
				'searchList':'http://www.ahcredit.gov.cn/searchList.jspx',
				'validateCode':'http://www.ahcredit.gov.cn/validateCode.jspx?type=0&id=0.5074288535327053',
				'QueryInvList':'http://www.ahcredit.gov.cn/QueryInvList.jspx?',
				'queryInvDetailAction':'http://www.ahcredit.gov.cn/queryInvDetailAction.jspx?'}

		self.mysearchdict = {'businessPublicity':'http://www.ahcredit.gov.cn/businessPublicity.jspx?',
				'enterprisePublicity':'http://www.ahcredit.gov.cn/enterprisePublicity.jspx?',
				'otherDepartment':'http://www.ahcredit.gov.cn/otherDepartment.jspx?',
				'justiceAssistance':'http://www.ahcredit.gov.cn/justiceAssistance.jspx?'}
		self.jsp_one_dict = {u'基本信息':None, u'变更信息':'/QueryAltList.jspx?',u'主要人员信息':'/QueryMemList.jspx?', \
				u'分支机构信息':'/QueryChildList.jspx?',u'清算信息':None,u'动产抵押登记信息':None,\
				u'股权出质登记信息':None,u'行政处罚信息':None,u'经营异常信息':None,\
				u'严重违法信息':None,u'抽查检查信息':None,u'股东（发起人）信息':'/QueryInvList.jspx?'}

		self.one_dict = {u'基本信息':'ind_comm_pub_reg_basic',
				u'股东信息':'ind_comm_pub_reg_shareholder',
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
				u'股权变更信息':'ent_pub_equity_change',
				u'行政许可信息':'ent_pub_administration_license',
				u'知识产权出资登记':'ent_pub_knowledge_property',
				u'知识产权出质登记信息':'ent_pub_knowledge_property',
				u'行政处罚信息':'ent_pub_administration_sanction'}
		self.three_dict = {u'行政许可信息':'other_dept_pub_administration_license',
				u'行政处罚信息':'other_dept_pub_administration_sanction'}
		self.four_dict = {u'股权冻结信息':'judical_assist_pub_equity_freeze',
				u'司法股权冻结信息':'judical_assist_pub_equity_freeze',
				u'股东变更信息':'judical_assist_pub_shareholder_modify'}
		self.result_json_dict = {}

	def get_check_num(self):
		resp = self.reqst.get(self.mydict['search'], timeout = 120)
		if resp.status_code != 200:
			return None
		resp = self.reqst.get(self.mydict['validateCode'], timeout = 120)
		if resp.status_code != 200:
			return None
		with open(self.ckcode_image_path, 'wb') as f:
			f.write(resp.content)
		from CaptchaRecognition import CaptchaRecognition
		#code_cracker = CaptchaRecognition('qinghai')
		code_cracker = CaptchaRecognition('qinghai')
		#code_cracker = CaptchaRecognition('guangdong')
		ck_code = code_cracker.predict_result(self.ckcode_image_path)
		if not ck_code is None:
			return ck_code[1]
		else:
			return None

	def get_id_num(self, findCode):
		count = 0
		while count < 20:
			check_num = self.get_check_num()
			print check_num
			if check_num is None:
				count += 1
				continue
			data = {'name':findCode,'verifyCode':check_num}
			resp = self.reqst.post(self.mydict['search'],data=data, timeout = 120)
			if resp.status_code != 200:
				print 'error...(get_id_num)'
				continue
			if resp.content.find('true')>=0:
				temp={'checkNo':check_num,'entName':findCode}
				resp = self.reqst.post(self.mydict['searchList'],data=temp, timeout = 120)
				if resp.status_code != 200:
					print 'error...post'
					count += 1
					continue
				soup = BeautifulSoup(resp.content)
				divs = soup.find(class_='list')
				if divs == None:continue
				mainId = divs.ul.li.a['href'][divs.ul.li.a['href'].find('id=')+3:]
				break
		return mainId

	def get_tables(self, url):
		resp = self.reqst.get(url, timeout = 120)
		if resp.status_code == 200:
			tables = BeautifulSoup(resp.content).find_all('table')
			return [table for table in tables] #if (table.find_all('th') or table.find_all('a')) ]
	def get_one_to_one_dict(self, allths, alltds):
		one_to_one_dict = {}
		for key, value in zip(allths, alltds):
			one_to_one_dict[key] = value
		return one_to_one_dict

	def test_print_table(self, tables):
		for table in tables:
			print table
	def test_print_all_ths_tds(self, allths, alltds):
		for th in allths:
			print th
		for td in alltds:
			print td
	def test_print_all_dict(self, mydict):
		for key,value in mydict.items():
			print key,':',value

	def do_with_specially(self, mydict, head, table_specially):
		#print len(table_specially)
		# for table in table_specially:
		# 	print table
		ths = table_specially.find_all('th')
		tds = table_specially.find_all('td')
		# for th in ths[1:4]+ths[6:]:
		# 	print th.get_text().strip()
		# for td in tds:
		# 	print td.get_text().strip() if td.get_text() else None
		#print ths[0]

		# print [th.get_text().strip() for th in (ths[1:4]+ths[6:])]
		# print [td.get_text().strip() if td.get_text() else None for td in tds]
		# 已修改—--by蔡丹红 2016.1.31
		# allths = [th.get_text().strip() for th in (ths[1:4]+ths[6:])]
		# alltds = [td.get_text().strip() if td.get_text() else None for td in tds]

		allths = [th.get_text().strip() for th in ths[1:4]]
		alltds = [td.get_text().strip() if td.get_text() else None for td in tds[0:3]]
		list1 = self.get_one_to_one_dict(allths, alltds)

		allths = [th.get_text().strip() for th in ths[6:]]
		alltds = [td.get_text().strip() if td.get_text() else None for td in tds[3:]]
		list2 = self.get_one_to_one_dict(allths, alltds)

		detail = []
		detail.append(list2)

		table_dict = {}
		table_dict[u'list'] = detail

		table_dict.update(list1)

		return {u"投资人及出资信息": [table_dict]}
		#self.test_print_all_ths_tds(allths, alltds)
		# return self.get_one_to_one_dict(allths, alltds)

	def do_with_hasnext(self, mydict, head, table_head, table_next):
		#print 'do_with_hasnext',head
		#if head == u'股东（发起人）信息' or head == u'股东信息':
		if head in [u'股东（发起人）信息' , u'股东信息']:
			#print head
			templist = []
			ths = table_head.find_all('th')[1:]
			#print [th.get_text() for th in ths]
			allths = [th.get_text() for th in ths]
			allths.append(u'详情')
			a_count = len(table_next.find_all('a'))
			#print a_count
			for i in range(1, a_count+1):
				tempresp = self.reqst.get(self.mydict['QueryInvList']+'pno='+str(i)+'&mainId='+self.id)
				if tempresp.status_code == 200:
					tempsoup = BeautifulSoup(tempresp.content)
					for tr in tempsoup.find_all('tr'):
						#print [td.get_text().strip() if td.get_text()  else None for td in tr.find_all('td')]
						details = []
						for td in tr.find_all('td'):
							if td.find('a'):
								#print self.mydict['eareName'] + td.a['onclick'][13:-2]
								temp = self.reqst.get( self.mydict['eareName'] + td.a['onclick'][13:-2], timeout = 120)
								if temp.status_code == 200:
									detail_soup = BeautifulSoup(temp.content)
									specially_dict = self.do_with_specially(mydict, head, detail_soup.find_all('table')[0])
								else:
									print 'error...temp'
							else:
								details.append(td.get_text().strip() if td.get_text() else None)
						#print len(details), details, specially_dict
						details.append(specially_dict)
						templist.append(self.get_one_to_one_dict(allths, details))
			
				else :
					print 'error...tempurl'
			self.result_json_dict[mydict[head]] = templist
		# elif head == u'企业年报':
		# 	pass
		else:
			ths = table_head.find_all('th')[1:]
			#print [th.get_text() for th in ths]
			templist = []
			allths = [th.get_text() for th in ths]
			a_count = len(table_next.find('a'))
			#print a_count
			for i in range(1, a_count+1):
				try:
					tempresp = self.reqst.get(self.mydict['eareName'] + self.jsp_one_dict[head] + 'pno='+str(i) + '&mainId='+self.id, timeout = 120)
				except TypeError:
					break
				if tempresp.status_code == 200:
					tempsoup = BeautifulSoup(tempresp.content)
					for tr in tempsoup.find_all('tr'):
						#print [td.get_text().strip() if td.get_text() else None for td in tr.find_all('td')]
						alltds = [td.get_text().strip() if td.get_text() else None for td in tr.find_all('td')]
						if head==u'主要人员信息':
							alltds_two = alltds[int(len(alltds)/2):]+alltds[:int(len(alltds)/2)]
							#self.test_print_all_ths_tds(allths, alltds_two)
							templist.append(self.get_one_to_one_dict(allths, alltds_two))
						#self.test_print_all_ths_tds(allths, alltds)
						templist.append(self.get_one_to_one_dict(allths, alltds))
			self.result_json_dict[mydict[head]] = templist

	def do_with_nonext(self, mydict, head, table_head, table_content):

		if head in [u'股东（发起人）信息' , u'股东信息']:
			#print head
			templist = []
			ths = table_head.find_all('th')[1:]
			#print [th.get_text() for th in ths]
			allths = [th.get_text() for th in ths]
			allths.append(u'详情')
			a_count = len(table_content.find_all('tr'))
			#print a_count
			for tr in table_content.find_all('tr'):
				#print [td.get_text().strip() if td.get_text()  else None for td in tr.find_all('td')]
				details = []
				for td in tr.find_all('td'):
					if td.find('a'):
						#print self.mydict['eareName'] + td.a['onclick'][13:-2]
						temp = self.reqst.get( self.mydict['eareName'] + td.a['onclick'][13:-2], timeout = 120)
						if temp.status_code == 200:
							detail_soup = BeautifulSoup(temp.content)
							specially_dict = self.do_with_specially(mydict, head, detail_soup.find_all('table')[0])
						else:
							print 'error...temp'
					else:
						details.append(td.get_text().strip() if td.get_text() else None)
				#print len(details), details, specially_dict
				details.append(specially_dict)
				templist.append(self.get_one_to_one_dict(allths, details))
			self.result_json_dict[mydict[head]] = templist
		else:
			#print 'do_with_nonext', head
			tds = table_head.find_all('td')
			ths = table_head.find_all('th')[1:]
			#print len(tds), len(ths)
			if len(tds)>0:
				# print [th.get_text().strip() for th in ths]
				# print [td.get_text().strip()  if td.get_text() else None for td in tds]
				allths = [th.get_text().strip() for th in ths]
				alltds = [td.get_text().strip()  if td.get_text() else None for td in tds]
				#self.test_print_all_ths_tds(allths, alltds)
				self.result_json_dict[mydict[head]] = self.get_one_to_one_dict(allths, alltds)
			else:
				#print [th.get_text().strip() for th in ths]
				allths = [th.get_text().strip() for th in ths]
				content_tds = table_content.find_all('td')
				if len(content_tds) == 0:
					#print [None for th in ths]
					alltds = [None for th in ths]
				else:
					#print [td.get_text().strip() if td.get_text() else None for td in table_content.find_all('td')]
					alltds = [td.get_text().strip() if td.get_text() else None for td in table_content.find_all('td')]
				#self.test_print_all_ths_tds(allths, alltds)
				#print head
				#print mydict[head]
				
				self.result_json_dict[mydict[head]] = self.get_one_to_one_dict(allths, alltds)
				

	def get_json_one(self, mydict, tables):
		count_table = len(tables)
		for i,table in enumerate(tables):
			try:
				if table.tr.th.get_text().split('\n')[0].strip() in [u'基本信息', u'变更信息',u'主要人员信息',u'分支机构信息',\
									u'清算信息',u'动产抵押登记信息',u'股权出质登记信息',u'行政处罚信息',\
									u'经营异常信息',u'严重违法信息',u'抽查检查信息',u'股东（发起人）信息', u'股东信息' ]:
					if i !=0 and i+2 < count_table and len(tables[i+2].find_all('a'))>1:
						#print i,'have next',
						# print tables[i]
						# print tables[i+2]
						self.do_with_hasnext(mydict, table.tr.th.get_text().split('\n')[0].strip(), tables[i], tables[i+2])
					elif  i+1<count_table:
						#print i,'no next'
						self.do_with_nonext(mydict, table.tr.th.get_text().split('\n')[0].strip(), tables[i], tables[i+1])

			except AttributeError:
				pass
	def help_enter_get_dict(self, tables):
		needdict = {}
		for i, table in enumerate(tables):
			if i==0:
				allth = [th.get_text() for th in table.find_all('th')][1:]
			else:
				allth = [th.get_text() for th in table.find_all('th')[:-1]]
			alltd = [td.get_text().strip() if td.get_text() else None for td in table.find_all('td')]

			key = allth.pop(0)
			tempvalue = []
			x = 0
			y = x + len(allth)
			#print '---------------------%d-------------------------------%d' % (len(allth), len(alltd))
			while y <= len(alltd):
				tempdict = {}
				for keys, values in zip(allth[1:],alltd[x:y]):
					tempdict[keys] = values
				x = y
				y = x + len(allth)
				tempvalue.append(tempdict)

			needdict[key] = tempvalue
			# print 'allth:',len(allth),'alltd:',len(alltd)
			# for th in allth:
			# 	print th.strip()
			# for td in alltd:
			# 	print td

		return needdict

	def do_with_enter(self, mydict, head, table_enter):
		#print head
		#print table_enter
		templist = []
		trs = table_enter.find_all('tr')
		#print [th.get_text() for th in trs[1].find_all('th')]
		allths = [th.get_text() for th in trs[1].find_all('th')]
		for tr in trs[2:]:
			#print [self.help_enter_get_dict(self.get_tables(self.mydict['eareName'] + td.a['href'])) if td.find('a') else td.get_text() for td in tr.find_all('td')]
			alltds = [self.help_enter_get_dict(self.get_tables(self.mydict['eareName'] + td.a['href'])) if td.find('a') else td.get_text() for td in tr.find_all('td')]
			templist.append(self.get_one_to_one_dict(allths, alltds))
		self.result_json_dict[mydict[head]] = templist
		return templist
				

	def get_json_two(self, mydict, tables):
		tables = [table for table in tables if len(table.find_all('div'))==0 and len(table.find_all('script'))==0]
		count_table = len(tables)
		#print count_table
		# for table in tables:
		# 	print table
		for i, table in enumerate(tables):
			ths = table.find_all('th')
			#print len(ths)
			if len(ths) >0:
				if ths[0].get_text().strip() == u'企业年报':
					#print 'one',ths[0].get_text().strip()
					self.do_with_enter(mydict, ths[0].get_text().strip(), table)
				elif ths[0].get_text().strip() in  [u'行政许可信息', u'股权变更信息']:
					#print 'two',ths[0].get_text().strip()
					self.do_with_nonext(mydict, ths[0].get_text().strip(), table, tables[i+1])
				elif ths[0].get_text().strip() in [ u'知识产权出质登记信息', \
			 				u'股东（发起人）及出资信息', u'行政处罚信息']:
					#print 'three',ths[0].get_text().strip()
					self.do_with_nonext(mydict, ths[0].get_text().strip(), table, tables[i+1])
			# if len(table.find_all('th'))>0 and table.find_all('th')[0] == u'企业年报':
			# 	print 'one',table.find_all('th')[0]
			# 	pass
			# elif len(table.find_all('th'))>0 and table.find_all('th')[0] == u'行政许可信息':
			# 	print 'two',table.find_all('th')[0]
			# 	pass
			# elif len(table.find_all('th'))>0 and table.find_all('th')[0] == u'股权变更信息':
			# 	print 'three',table.find_all('th')[0]
			# 	pass
			# elif len(table.find_all('th'))>0 and table.find_all('th')[0] in [u'变更信息', u'知识产权出质登记信息',\
			# 							 u'股东（发起人）及出资信息', u'行政处罚信息']:
			# 	print 'four',table.find_all('th')[0]
		pass
	def get_json_three(self, mydict, tables):
		count_table = len(tables)
		for i,table in enumerate(tables):
			try:
				if table.tr.th.get_text().split('\n')[0].strip() in [u'行政许可信息', u'行政处罚信息' ]:
					if i !=0 and i+2 < count_table and len(tables[i+2].find_all('a'))>1:
						#print i,'have next'
						self.do_with_hasnext(mydict, table.tr.th.get_text().split('\n')[0].strip(), tables[i], tables[i+2])
					elif  i+1<count_table:
						#print i,'no next'
						self.do_with_nonext(mydict, table.tr.th.get_text().split('\n')[0].strip(), tables[i], tables[i+1])
			except AttributeError:
				pass
		pass
	def get_json_four(self, mydict, tables):
		self.do_with_nonext(mydict, tables[0].find_all('th')[0].get_text().strip(), tables[0], tables[1])
		pass

	def run(self, findCode):

		self.ent_number = str(findCode)
		#对每个企业都指定一个html的存储目录
		self.html_restore_path = self.html_restore_path + self.ent_number + '/'
		if settings.save_html and not os.path.exists(self.html_restore_path):
			CrawlerUtils.make_dir(self.html_restore_path)

		self.id = self.get_id_num(findCode)
		print self.id
		self.result_json_dict = {}
		#self.result_json_dict[findCode] = {}
		tableone = self.get_tables(self.mysearchdict['businessPublicity'] + 'id=' +self.id)
		self.get_json_one(self.one_dict, tableone)
		tabletwo = self.get_tables(self.mysearchdict['enterprisePublicity'] + 'id=' +self.id)
		self.get_json_two(self.two_dict, tabletwo)
		tablethree = self.get_tables(self.mysearchdict['otherDepartment'] + 'id=' +self.id)
		self.get_json_three(self.three_dict, tablethree)
		tablefour = self.get_tables(self.mysearchdict['justiceAssistance'] + 'id=' +self.id)
		self.get_json_four(self.four_dict, tablefour)

		#self.write_file_mutex.acquire()
		print {self.ent_number: self.result_json_dict}
		CrawlerUtils.json_dump_to_file(self.json_restore_path, {self.ent_number: self.result_json_dict})
		#self.write_file_mutex.release()

if __name__ == '__main__':
	anhui = AnhuiCrawler('./enterprise_crawler/anhui.json')
	# anhui.run('450100000128441')
	f = open('enterprise_list/anhui.txt', 'r')
	for line in f.readlines():
		print line.split(',')[2].strip()
		anhui.run(str(line.split(',')[2]).strip())
	f.close()
# anhui.run('340000000006066')
# anhui.run('340313000002482')
# anhui.run('340000000018072')
# anhui.run('341521000013920')
