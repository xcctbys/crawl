#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import json
import pymongo


def analyze_logs():
    analyzed_report = {}
    log_db = connect(database='log')
    source_db = connect(database='source')
    total = log_db.crawler_download_log.count({})
    for log in log_db.crawler_download_log.find({}):
        task_id = log[u'task']
        task_uri = source_db.crawler_task.find_one({"_id": task_id})['uri']
        province, company_name, _ = analyze_uri(task_uri)
        reason = log[u'failed_reason']
        if reason in analyzed_report:
            analyzed_report[reason].append(province)
        else:
            analyzed_report[reason] = [province]
    return total, analyzed_report


def connect(database='default'):
    client = pymongo.MongoClient("mongodb://clawer:plkjplkj@dds-wz9a828f745eac341.mongodb.rds.aliyuncs.com:3717,dds-wz9a828f745eac342.mongodb.rds.aliyuncs.com:3717/{0}?replicaSet=mgset-1160325".format(database))
    return client[database]


def analyze_uri(uri):
    l = uri.split('/')
    province = l[3]
    company_name = l[4]
    registered_no = l[5]
    return (province, company_name, registered_no)


if __name__ == '__main__':
    # 最多打印前多少类错误
    MAX_ERROR_LENGTH = 10
    # 最多打印出现该类错误公司次数
    MAX_COMPANY_LENGTH = 31
    total, analyzed_report = analyze_logs()
    sorted_reasons = sorted(analyzed_report, key=lambda k: len(analyzed_report[k]), reverse=True)
    print "总共下载失败{0}次".format(total)
    for reason in sorted_reasons[0:MAX_ERROR_LENGTH]:
        company_names = analyzed_report[reason]
        company_names2 = set(company_names)
        print "#########################"
        print "#########################"
        print "-------------------------"
        print "{0}, 共计{1}次".format(reason, len(company_names))
        print "-------------------------"
        for company_name in company_names2:
            print company_name.encode("utf8")