#!/usr/bin/env python
#coding=utf-8
import logging

log_level = logging.WARN
log_file = '/data/clawer_result/bankrupt/crawler.log'
logger = None

pdf_restore_dir = '/data/clawer_result/bankrupt/pdf'
json_restore_dir = '/data/clawer_result/bankrupt/json'

#host = 'http://clawer.princetechs.com:8080/media/clawer_result'
host = 'http://10.100.90.51:8080/media/clawer_result'
ID = '3'