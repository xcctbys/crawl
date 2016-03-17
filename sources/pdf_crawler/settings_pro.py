#!/usr/bin/env python
#coding=utf-8
import logging

log_level = logging.WARN
log_file = '/data/pdf_crawler/result_pdf/crawler.log'
logger = None

pdf_restore_dir = '/data/pdf_crawler/result_pdf'
json_list_dir = '/data/pdf_crawler/json_list/'

host = 'http://clawer.princetechs.com:8080/media/clawer_result'
ID = '29'