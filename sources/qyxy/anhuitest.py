#!/usr/bin/env python
#encoding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import re
import os,os.path
from bs4 import BeautifulSoup

class Anhui(object):
	def __init__(self):
		self.reqst = requests.Session()
		self.reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

	def crack_checkcode(self):
		resp = self.reqst.get('http://www.ahcredit.gov.cn/search.jspx')
		if resp.status_code != 200:
			return None
		resp = self.reqst.get('http://www.ahcredit.gov.cn/validateCode.jspx?type=0&id=0.5074288535327053')
		if resp.status_code != 200:
			return None
		with open('s.jpg', 'wb') as f:
			f.write(resp.content)
		from CaptchaRecognition import CaptchaRecognition
		code_cracker = CaptchaRecognition('qinghai')
		ck_code = code_cracker.predict_result('s.jpg')
		return ck_code

	def crawl_check_page(self):
		count = 0
		while count < 3:
			ckcode = self.crack_checkcode()[1]
			print ckcode
			data = {'name':'340000000002071','verifyCode':ckcode}
			resp = self.reqst.post('http://www.ahcredit.gov.cn/search.jspx',data=data)
			if resp.status_code != 200:
				print 'error...(crawl_check_page)'
				continue
			if resp.content.find('true')>=0:
				temp={'checkNo':ckcode,'entName':'340000000002071'}
				resp = self.reqst.post('http://www.ahcredit.gov.cn/searchList.jspx',data=temp)
				if resp.status_code != 200:
					print 'error...post'
					count += 1
					continue
				soup = BeautifulSoup(resp.content,'html5lib')
				divs = soup.find(class_='list')
				if divs == None:continue
				print divs.ul.li.a['href']
				resp = self.reqst.get('http://www.ahcredit.gov.cn'+ divs.ul.li.a['href'])
				mainId = divs.ul.li.a['href'][divs.ul.li.a['href'].find('id=')+3:]
				if resp.status_code == 200:
					soup = BeautifulSoup(resp.content,'html5lib')
					#soup = BeautifulSoup(resp.content,'lxml')
					mydict={temp['entName']:None}
					tables = soup.find_all('table')
					print len(tables)
					# print len(soup.find_all('div'))
					# for i, divs in enumerate(soup.body.find_all('div')[8:]):
					# 	print '.............',i,'................'
					# 	print divs
					# 	print '\n\n\n\n\n----------\n\n\n\n\n'
					for trs in tables[0].find_all('tr'):
						if trs.td:
							for ths in trs.find_all('th'):
								if ths.get_text():
									print ths.get_text().strip()
							for tds in trs.find_all('td'):
								if tds.get_text():
									print tds.get_text().strip()

					print  tables[1].tr.find('th').get_text().split('\n')[0]
					for ths in tables[1].find_all('th', attrs={'width':'20%'}):
						print ths.string	
					QueryInvList = 'http://www.ahcredit.gov.cn/QueryInvList.jspx?'
					Host = 'http://www.ahcredit.gov.cn'
					for i in range(1, len(tables[3].find_all('a'))+1):
						tempurl =  QueryInvList + 'pno=' + str(i) + '&mainId='+mainId
						resp = self.reqst.get(tempurl)
						if resp.status_code == 200:
							tempsoup = BeautifulSoup(resp.content)
							for trs in tempsoup.find_all('tr'):
								for tds in trs.find_all('td'):
									if tds.find('a'):
										detail_resp = self.reqst.get(Host + tds.a['onclick'][13:-2])
										if detail_resp.status_code == 200:
											detailsoup = BeautifulSoup(detail_resp.content)
											detail_table = detailsoup.find('table')
											detailths = detail_table.find_all('th')
											detailths_yes = detailths[1:4] + detailths[6:]
											for ths in detailths_yes:
												print ths.get_text()
											print '\n'
											detailtds = detail_table.find_all('td')
											#detailtds_yes = detailtds[1:4] + detailtds[6:]
											for tds in detailtds:
												print tds.get_text()
											
									if tds.string:
										print tds.string.strip()

					for ths in tables[4].find_all('th'):
						print ths.get_text()
					for trs in tables[5].find_all('tr'):
						for tds in trs.find_all('td'):
							print tds.get_text()

					for ths in tables[6].find_all('th')[1:4]:
						print ths.string
					QueryMemList = 'http://www.ahcredit.gov.cn/QueryMemList.jspx?'
					for i in range(1, len(tables[8].find_all('a'))+1):
						tempurl =  QueryMemList + 'pno=' + str(i) + '&mainId='+mainId
						resp = self.reqst.get(tempurl)
						if resp.status_code == 200:
							tempsoup = BeautifulSoup(resp.content)
							for tds in tempsoup.find_all('td'):
								print tds.string

					for ths in tables[9].find_all('th')[1:5]:
						print ths.string
					QueryChildList = 'http://www.ahcredit.gov.cn/QueryChildList.jspx?'
					for i in range(1, len(tables[11].find_all('a'))+1):
						tempurl =  QueryChildList + 'pno=' + str(i) + '&mainId='+mainId
						resp = self.reqst.get(tempurl)
						if resp.status_code == 200:
							tempsoup = BeautifulSoup(resp.content)
							for tds in tempsoup.find_all('td'):
								print tds.string
					
					for trs in tables[12].find_all('tr')[1:]:
						print trs.th.string + ':' + trs.td.string

					for ths in tables[16].find_all('th')[1:]:
						print ths.string
					for trs in tables[17].find_all('tr'):
						for tds in trs.find_all('td'):
							print tds.string

					for ths in tables[13].find_all('th')[1:]:
						print ths.string
					QueryPledgeList = 'http://www.ahcredit.gov.cn/QueryPledgeList.jspx?'
					for i in range(1, len(tables[15].find_all('a'))+1):
						tempurl =  QueryPledgeList + 'pno=' + str(i) + '&mainId='+mainId
						resp = self.reqst.get(tempurl)
						if resp.status_code == 200:
							tempsoup = BeautifulSoup(resp.content)
							for tds in tempsoup.find_all('td'):
								print tds.string


					for ths in tables[22].find_all('th')[1:]:
						print ''.join(ths.get_text())
					for trs in tables[23].find_all('tr'):
						for tds in trs.find_all('td'):
							print tds.string

					for ths in tables[18].find_all('th')[1:]:
						print ths.string
					for trs in tables[19].find_all('tr'):
						for tds in trs.find_all('td'):
							print tds.string

					for ths in tables[20].find_all('th')[1:]:
						print ths.string
					for trs in tables[21].find_all('tr'):
						for tds in trs.find_all('td'):
							print tds.string

					for ths in tables[24].find_all('th')[1:]:
						print ths.string
					for trs in tables[25].find_all('tr'):
						for tds in trs.find_all('td'):
							print tds.string

					

					table1 = soup.find(class_='detailsList')
					f = open('table1.txt', 'w')
					for index, tr in enumerate(table1.find_all('tr')):
						if index==0:continue
						for th,td in zip(tr.find_all('th'),tr.find_all('td')):
							print >> f,th.get_text().strip(),td.get_text().strip()
					f.close()
					f = open('table2.txt', 'w')
					table2 = soup.find('table',attrs={'cellspacing':"0","cellpadding":"0",'class':"detailsList",'id':"touziren"})
					print type(table2)
					table2 = table2.find_all('th',attrs={'width':"20%",'style':"text-align:center;"})
					for item in table2:
						print >>f,item.get_text()
					preitem = None
					for i in range(1,10):
						resp = self.reqst.get('http://www.ahcredit.gov.cn/QueryInvList.jspx?pno=' + str(i) +'&mainId=4EF6A3BF5498AAA4AEEEB80A05878626')
						if preitem == resp.content:
							print i
							break
						preitem = resp.content
						soup = BeautifulSoup(resp.content,'html5lib')
						table2 = soup.find_all('td')
						for item in table2:
							if item.a:
								urlid = item.a['onclick'][item.a['onclick'].find('window.open')+13:-2]
								#print 'http://www.ahcredit.gov.cn'+urlid
								#print item.get_text().strip()
								resp = self.reqst.get('http://www.ahcredit.gov.cn'+urlid)
								tempsoup = BeautifulSoup(resp.content,'html5lib')
								tabeldetail = tempsoup.find('table',attrs={'cellpadding':"0" ,'cellspacing':"0", 'class':"detailsList" })
								ths = tabeldetail.find_all('th')
								tds = tabeldetail.find_all('tr')
								# for th in ths:
								# 	print th.get_text().strip()
								# for td in tds:
								# 	print td.get_text().strip()
							else :
								pass
								#print item.get_text().strip()
						return True
					else :
						print 'error...if'
						count += 1
						continue
			return False

anhui = Anhui()
anhui.crawl_check_page()