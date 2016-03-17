#!/usr/bin/env python
#!encoding=utf-8
import os
import os.path
import sys
import raven
import gzip
import random
import time
import datetime
import stat

import logging
import Queue
import threading
import multiprocessing
import settings
import json
import requests
import re
from crawler import CrawlerUtils

PDF_CRAWLER_SETTINGS=os.getenv('PDF_CRAWLER_SETTINGS')
if PDF_CRAWLER_SETTINGS == 'settings_pro':
    import settings_pro as settings
elif PDF_CRAWLER_SETTINGS == 'settings_all':
    import settings_all as settings
else:
    import settings

max_crawl_time = 0
reqst = requests.Session()
reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

def get_need_down_json_file_name(url):
	count = 0
	resp = None
	while count<5:
		try:
			resp = reqst.get(url)
		except:
			count += 1
			continue
		if resp.content == 200:
			break
		else:
			count += 1
			continue
	if resp is None or resp.status_code != 200:
		return None
	else:
		m = re.search(r'(\d+.json.gz)', resp.content)
		if m:
			return m.group(1)
		else:
			return None

def get_data_json_file(abs_yesterday_json_url, abs_json_restore_dir, json_gz_file_name):
	abs_json_restore_path = '%s/%s' % (abs_json_restore_dir, json_gz_file_name)
	# print 'abs_json_restore_path:', abs_json_restore_path
	count = 0
	resp = None
	while count<10:
		try:
			resp = reqst.get(abs_yesterday_json_url)
		except:
			count += 1
			continue
		if resp.status_code == 200 and resp.content:
			with open(abs_json_restore_path, 'wb') as f:
				f.write(resp.content)
			return True
			break
		else:
			count += 1
			continue
	if resp is None:
		return False
	else:
		return True

def get_pdfs_from_data_json(abs_pdf_restore_dir, json_file_name):
	f = open(json_file_name, 'r')
	for line in f.readlines():
		list_dict = json.loads(line)['list']
		for i, item in enumerate(list_dict):
			# print i,'---------'
			# print item
			pdf_url = item['pdf_url']
			count = 0
			resp = None
			while count<10:
				resp = reqst.get(pdf_url)
				if resp.status_code == 200 and resp.content:
					with open('%s/%s' % (abs_pdf_restore_dir, pdf_url.rsplit('/')[-1]), 'wb') as f:
						f.write(resp.content)
					break
				else:
					count += 1
					if count == 10:
						print '%s, get_error_pdf' % pdf_url
					continue
			if count != 10:
				list_dict[i]['abs_path'] = '%s/%s' % (abs_pdf_restore_dir, pdf_url.rsplit('/')[-1])
		# print list_dict
		CrawlerUtils.json_dump_to_file('%s%s%s' %(json_file_name[:-5], '_insert', json_file_name[-5:]), {'list':list_dict})
	f.close()


def down_yesterday_pdf(yesterday):
	yesterday = yesterday
	abs_yesterday_json_url = '%s/%s/%s/%s/%s' % (settings.host, settings.ID, yesterday[:4], yesterday[4:6], yesterday[6:])
	# print 'abs_yesterday_json_url:', abs_yesterday_json_url
	need_down_json_file_name = get_need_down_json_file_name(abs_yesterday_json_url)
	if need_down_json_file_name is None:
		print '-error__from_%s____no_data' % abs_yesterday_json_url
		return
	else:
		abs_yesterday_json_url = '%s/%s' % (abs_yesterday_json_url, need_down_json_file_name)
		# print 'abs_yesterday_json_url:',abs_yesterday_json_url
		abs_json_restore_dir = '%s/%s/%s/%s' % (settings.json_restore_dir, yesterday[:4], yesterday[4:6], yesterday[6:])
		if not os.path.exists(abs_json_restore_dir):
			CrawlerUtils.make_dir(abs_json_restore_dir)
		abs_pdf_restore_dir = '%s/%s/%s/%s' % (settings.pdf_restore_dir, yesterday[:4], yesterday[4:6], yesterday[6:])
		if not os.path.exists(abs_pdf_restore_dir):
			CrawlerUtils.make_dir(abs_pdf_restore_dir)
		# print 'abs_json_restore_dir:', abs_json_restore_dir
		get_json_file_OK = get_data_json_file(abs_yesterday_json_url, abs_json_restore_dir, need_down_json_file_name)
		if get_json_file_OK is False:
			print '-error--nodata_from_%s%s' % (abs_json_restore_dir, need_down_json_file_name)
			return
		else:
			abs_yesterday_json_gz_file_name = '%s/%s' %(abs_json_restore_dir, need_down_json_file_name)
			abs_yesterday_json_file_name = '%s/%s%s' %(abs_json_restore_dir, yesterday, '.json')
			# print 'abs_yesterday_json_file_name:',abs_yesterday_json_file_name
			# print 'abs_yesterday_json_gz_file_name:', abs_yesterday_json_gz_file_name
			g = gzip.GzipFile(mode='rb', fileobj=open(abs_yesterday_json_gz_file_name, 'rb'))
			open(abs_yesterday_json_file_name, 'wb').write(g.read())
			if os.path.isfile(abs_yesterday_json_gz_file_name):
				os.remove(abs_yesterday_json_gz_file_name)
			get_pdfs_from_data_json(abs_pdf_restore_dir, abs_yesterday_json_file_name)
	pass

def down_argv_pdf(some_days):
	for item in some_days:
		down_yesterday_pdf(item)

if __name__ == '__main__':
	
	max_crawl_time = int(sys.argv[1])
	if len(sys.argv) == 2:
		yesterday = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y%m%d')
		down_yesterday_pdf(yesterday)
	else:
		down_argv_pdf(sys.argv[2:])