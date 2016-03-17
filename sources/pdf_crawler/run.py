#!/usr/bin/env python
#!encoding=utf-8
import os
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
if PDF_CRAWLER_SETTINGS and PDF_CRAWLER_SETTINGS.find('settings_pro') >= 0:
    import settings_pro as settings
else:
    import settings


def config_logging():
    settings.logger = logging.getLogger('pdf_crawler')
    settings.logger.setLevel(settings.log_level)
    fh = logging.FileHandler(settings.log_file)
    fh.setLevel(settings.log_level)
    ch = logging.StreamHandler()
    ch.setLevel(settings.log_level)

    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(pathname)s:%(lineno)d:: %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    settings.logger.addHandler(fh)
    settings.logger.addHandler(ch)

max_crawl_time = 0
reqst = requests.Session()
reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})


def get_json(url, yesterday):
	json_restore_dir = '%s%s.json.gz' % (settings.json_list_dir,yesterday)
	resp = reqst.get(url)
	if resp.status_code == 200:
		with open(json_restore_dir, 'wb') as f:
			f.write(resp.content)
	g = gzip.GzipFile(mode='rb', fileobj=open(json_restore_dir, 'rb'))
	open(json_restore_dir[:-3], 'wb').write(g.read())
	pass

def get_json_file(yesterday):
	abs_yesterday_json_file = os.path.join(settings.json_list_dir, yesterday) + '.json'
	if not os.path.exists(abs_yesterday_json_file):
		resp = reqst.get('%s/%s/%s/%s/%s' % (settings.host, settings.ID, yesterday[:4], yesterday[4:6], yesterday[6:]))
		if resp.status_code == 200:
			m = re.search(r'(\d+.json.gz)', resp.content)
			if m:
				get_json('%s/%s/%s/%s/%s/%s' % (settings.host, settings.ID, yesterday[:4], yesterday[4:6], yesterday[6:], m.group(1)), yesterday)
			else:
				print '-------error-------re.search----'
				# settings.logger.warn('-------error-------re.search----')
		else:
			print '---------error----------reqst.get------'
			# settings.logger.warn('---------error----------reqst.get------')

def get_pdf(save_path, list_dict):

	pdf_restore_dir = '%s/%s/%s/%s' % (settings.pdf_restore_dir, save_path[:4],save_path[4:6],save_path[6:])
	if not os.path.exists(pdf_restore_dir):
		CrawlerUtils.make_dir(pdf_restore_dir)

	for item in list_dict:
		pdf_url = item['pdf_url']
		count = 0
		while count <10:
			resp = reqst.get(pdf_url)
			if resp.status_code == 200 and resp.content:
				with open(os.path.join(pdf_restore_dir, pdf_url.rsplit('/')[-1]), 'wb') as f:
					f.write(resp.content)
				break
			else:
				count += 1
				if count == 10:
					print '%s,get-error' % pdf_url
					# settings.logger.info('%s,get-error' % pdf_url)
				continue

if __name__ == '__main__':

	config_logging()
	yesterday = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y%m%d')
	# yesterday = '20160118'
	get_json_file(yesterday)
	max_crawl_time = int(sys.argv[1])
	if len(sys.argv) >= 3 and sys.argv[2] == 'all':
		pass
	else:
		if len(sys.argv) >= 3:
			need_json_file = sys.argv[2:]
		else:
			need_json_file = [yesterday]

		for json_file_item in need_json_file:
			abs_json_path = os.path.join(settings.json_list_dir, json_file_item) + '.json'
			if not os.path.exists(abs_json_path):
				get_json_file(json_file_item)
				# print '-----------error------------'
			if not os.path.exists(abs_json_path):
				print '--------error--nothave--%s-' % abs_json_path
				# settings.logger.info('--------error--nothave--%s-' % abs_json_path)
				continue
			f = open(abs_json_path, 'r')
			for line in f.readlines():
				# print type(json.loads(line)['list'])
				process = multiprocessing.Process(target=get_pdf, args=( json_file_item, json.loads(line)['list']))
				process.daemon = True
				process.start()
				process.join(max_crawl_time)
				print 'child process exit'
				# settings.logger.info('child process exit')
			f.close()
			need_dict = {}
			for pdf_item in os.listdir('%s/%s/%s/%s/' % (settings.pdf_restore_dir, json_file_item[:4], json_file_item[4:6], json_file_item[6:])):
				# print pdf_item
				if pdf_item.split('.')[1] == 'pdf':
					need_dict['http://rmfygg.court.gov.cn/psca/lgnot/bulletin/download/'+pdf_item] = '%s/%s/%s/%s/%s' % (os.path.abspath(os.curdir), json_file_item[:4], json_file_item[4:6], json_file_item[6:], pdf_item)
					# print pdf_item
			CrawlerUtils.json_dump_to_file('%s/%s/%s/%s/%s%s' % (settings.pdf_restore_dir, json_file_item[:4], json_file_item[4:6], json_file_item[6:], json_file_item, '_pdf.json'), need_dict)
			# need_dict = {}



