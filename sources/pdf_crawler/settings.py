#!/usr/bin/env python
#coding=utf-8
import logging
log_level = logging.WARN
log_file = './result_pdf/crawler.log'
logger = None
pdf_restore_dir = './result_pdf' #所有PDF的根目录，生成的PDF会以/year/month/day/all_pdf 的形式存储在该目录下
json_list_dir = './json_list/' #程序首先得从url地址下载昨天的.json.gz文件，并以20160120.json的文件格式放置在该目录下
host = 'http://clawer.princetechs.com:8080/media/clawer_result' #下载json.gz文件所对应url的前部分
ID = '29' #下载json.gz文件所对应url的ID部分,加上一个日期就可以完全的构造出事个 url