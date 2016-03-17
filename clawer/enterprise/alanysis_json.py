#!/usr/bin/env python
#coding:utf8

import json
import os, os.path
# from bs4 import BeautifulSoup
# import requests
import gzip
import MySQLdb
import codecs
import sys
import datetime

# import settings

json_url = r'/data/clawer_result/7/'
json_url2 = r'/data/clawer_result/7/2016/02/28/'
json_url3 = r'/data/clawer_result/7/2016/02/27/'
json_rul4 = r'/data/clawer_result/7/2016/03/01/'
abs_json_path = './abs_json_path/'
success_file_path = './success_file_path/'
fail_file_path = './fail_file_path/'
one_json_file = './one_json_file.json'
success_json_file = './success_json_file.json'
fail_json_file = './fail_json_file.json'
trans_dict = dict(
                [('10',u'总局'),
                ('11',u'北京'),
                ('12',u'天津'),
                ('13',u'河北'),
                ('14',u'山西'),
                ('15',u'内蒙古'),
                ('21',u'辽宁'),
                ('22',u'吉林'),
                ('23',u'黑龙江'),
                ('30',u'UnKnow'),
                ('31',u'上海'),
                ('32',u'江苏'),
                ('33',u'浙江'),
                ('34',u'安徽'),
                ('35',u'福建'),
                ('36',u'江西'),
                ('37',u'山东'),
                ('41',u'河南'),
                ('42',u'湖北'),
                ('43',u'湖南'),
                ('44',u'广东'),
                ('45',u'广西'),
                ('46',u'海南'),
                ('49',u'UnKnow'),
                ('40',u'UnKnow'),
                ('50',u'重庆'),
                ('51',u'四川'),
                ('52',u'贵州'),
                ('53',u'云南'),
                ('54',u'西藏'),
                ('61',u'陕西'),
                ('62',u'甘肃'),
                ('63',u'青海'),
                ('64',u'宁夏'),
                ('65',u'新疆'),
                ('71',u'台湾'),
                ('81',u'香港'),
                ('82',u'澳门'),])

db_total_dict = dict([('10',set()),
                ('11',set()),
                ('12',set()),
                ('13',set()),
                ('14',set()),
                ('15',set()),
                ('21',set()),
                ('22',set()),
                ('23',set()),
                ('30',set()),
                ('31',set()),
                ('32',set()),
                ('33',set()),
                ('34',set()),
                ('35',set()),
                ('36',set()),
                ('37',set()),
                ('41',set()),
                ('42',set()),
                ('43',set()),
                ('44',set()),
                ('45',set()),
                ('46',set()),
                ('49',set()),
                ('50',set()),
                ('51',set()),
                ('52',set()),
                ('53',set()),
                ('54',set()),
                ('61',set()),
                ('62',set()),
                ('63',set()),
                ('64',set()),
                ('65',set()),
                ('71',set()),
                ('81',set()),
                ('82',set()),
                ('40',set())])

success_dict = dict([('10',set()),
                ('11',set()),
                ('12',set()),
                ('13',set()),
                ('14',set()),
                ('15',set()),
                ('21',set()),
                ('22',set()),
                ('23',set()),
                ('31',set()),
                ('32',set()),
                ('33',set()),
                ('34',set()),
                ('35',set()),
                ('36',set()),
                ('37',set()),
                ('41',set()),
                ('42',set()),
                ('43',set()),
                ('44',set()),
                ('45',set()),
                ('46',set()),
                ('50',set()),
                ('51',set()),
                ('52',set()),
                ('53',set()),
                ('54',set()),
                ('61',set()),
                ('62',set()),
                ('63',set()),
                ('64',set()),
                ('65',set()),
                ('71',set()),
                ('81',set()),
                ('82',set()),
                ('30',set()),
                ('49',set()),
                ('40',set())])

fail_dict = dict([('10',set()),
                ('11',set()),
                ('12',set()),
                ('13',set()),
                ('14',set()),
                ('15',set()),
                ('21',set()),
                ('22',set()),
                ('23',set()),
                ('31',set()),
                ('32',set()),
                ('33',set()),
                ('34',set()),
                ('35',set()),
                ('36',set()),
                ('37',set()),
                ('41',set()),
                ('42',set()),
                ('43',set()),
                ('44',set()),
                ('45',set()),
                ('46',set()),
                ('50',set()),
                ('51',set()),
                ('52',set()),
                ('53',set()),
                ('54',set()),
                ('61',set()),
                ('62',set()),
                ('63',set()),
                ('64',set()),
                ('65',set()),
                ('71',set()),
                ('81',set()),
                ('82',set()),
                ('30',set()),
                ('49',set()),
                ('40',set())])

db_down_dict = dict([('10',set()),
                ('11',set()),
                ('12',set()),
                ('13',set()),
                ('14',set()),
                ('15',set()),
                ('21',set()),
                ('22',set()),
                ('23',set()),
                ('31',set()),
                ('32',set()),
                ('33',set()),
                ('34',set()),
                ('35',set()),
                ('36',set()),
                ('37',set()),
                ('41',set()),
                ('42',set()),
                ('43',set()),
                ('44',set()),
                ('45',set()),
                ('46',set()),
                ('50',set()),
                ('51',set()),
                ('52',set()),
                ('53',set()),
                ('54',set()),
                ('61',set()),
                ('62',set()),
                ('63',set()),
                ('64',set()),
                ('65',set()),
                ('71',set()),
                ('81',set()),
                ('82',set()),
                ('30',set()),
                ('49',set()),
                ('40',set())])

db_update_dict = dict([('10',set()),
                ('11',set()),
                ('12',set()),
                ('13',set()),
                ('14',set()),
                ('15',set()),
                ('21',set()),
                ('22',set()),
                ('23',set()),
                ('31',set()),
                ('32',set()),
                ('33',set()),
                ('34',set()),
                ('35',set()),
                ('36',set()),
                ('37',set()),
                ('41',set()),
                ('42',set()),
                ('43',set()),
                ('44',set()),
                ('45',set()),
                ('46',set()),
                ('50',set()),
                ('51',set()),
                ('52',set()),
                ('53',set()),
                ('54',set()),
                ('61',set()),
                ('62',set()),
                ('63',set()),
                ('64',set()),
                ('65',set()),
                ('71',set()),
                ('81',set()),
                ('82',set()),
                ('30',set()),
                ('49',set()),
                ('40',set())])

db_except_dict = dict([('10',set()),
                ('11',set()),
                ('12',set()),
                ('13',set()),
                ('14',set()),
                ('15',set()),
                ('21',set()),
                ('22',set()),
                ('23',set()),
                ('31',set()),
                ('32',set()),
                ('33',set()),
                ('34',set()),
                ('35',set()),
                ('36',set()),
                ('37',set()),
                ('41',set()),
                ('42',set()),
                ('43',set()),
                ('44',set()),
                ('45',set()),
                ('46',set()),
                ('50',set()),
                ('51',set()),
                ('52',set()),
                ('53',set()),
                ('54',set()),
                ('61',set()),
                ('62',set()),
                ('63',set()),
                ('64',set()),
                ('65',set()),
                ('71',set()),
                ('81',set()),
                ('82',set()),
                ('30',set()),
                ('49',set()),
                ('40',set())])
reason_dict = {}

# reqst = requests.Session()
# reqst.headers.update({'Accept': 'text/html, application/xhtml+xml, */*',
# 			'Accept-Encoding': 'gzip, deflate',
# 			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
# 			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

def dowload_json_by_days(url, one_json_file, f):
	# resp = None
	# # try:
	# resp = reqst.get(url)
	# for item in BeautifulSoup(resp.content).find_all('a')[1:]:
	# 	resp_gzip = reqst.get(''.join([url,item.get_text()]))
	# 	with open(abs_json_path+item.get_text(), 'wb') as f:
	# 		f.write(resp_gzip.content)
	# 	g = gzip.GzipFile(mode='rb', fileobj=open(abs_json_path+item.get_text(), 'rb'))
	# 	open(one_json_file, 'wb+').write(g.read())
		# print resp.status_code
	# except:
	# 	print 'error-get-reqst-%s' % json_url
    for item in os.listdir(url):
        path = os.path.join(url, item)
        g = None
        g = gzip.GzipFile(mode='rb', fileobj=open(path, 'rb'))
        f.write(g.read())
        f.flush()
        # f.close()


def dump_json_to_success_or_fail_file(abs_json_path, success_file_path, fail_file_path):
	success_file = open(success_file_path, 'w+')
	fail_file = open(fail_file_path, 'w+')
	with open(abs_json_path, 'rb') as f:
		for line in f.readlines():
			one_enter_dict = json.loads(line)
			for key, value in one_enter_dict.items():
				if key.isdigit() and key[:2]!='91':
					if one_enter_dict[key]:
						success_file.write(line)
						success_dict[key[:2]].add(key.strip())
					else:
						fail_file.write(line)
						fail_dict[key[:2]].add(key.strip())
	success_file.close()
	fail_file.close()
	pass

def get_total_dict_from_db():
	try:
		conn = MySQLdb.connect(host='10.100.80.50', user='cacti', passwd='cacti', db='clawer', port=3306)
		cur = conn.cursor()
		count = cur.execute('select register_no from enterprise_enterprise')
		results = cur.fetchall()
		for result in results:
			# print result
			if result[0] and result[0][:2] != '91':
				db_total_dict[result[0][:2]].add(result[0].strip())
                
		cur.close()
		conn.close()
	except MySQLdb.Error, e:
		print 'Mysql error %d:%s' %(e.args[0], e.args[1])

def get_down_dict_from_db():
	try:
		conn = MySQLdb.connect(host='10.100.80.50', user='cacti', passwd='cacti', db='enterprise', port=3306)
		cur = conn.cursor()
		count = cur.execute('select register_num from basic')
		results = cur.fetchall()
		for result in results:
			# print result
			if result[0] and result[0][:2] != '91':
				db_down_dict[result[0][:2]].add(result[0].strip())
                
		cur.close()
		conn.close()
	except MySQLdb.Error, e:
		print 'Mysql error %d:%s' %(e.args[0], e.args[1])

def get_update_dict_from_db(yesterday):
    try:
        conn = MySQLdb.connect(host='10.100.80.50', user='cacti', passwd='cacti', db='enterprise', port=3306)
        cur = conn.cursor()
        for days in yesterday:
            sql = 'select register_num from basic where timestamp like \"%s %%\" ' % days
            print sql
            count = cur.execute(sql)
            results = cur.fetchall()
            for result in results:
                # print result
                if result[0] and result[0][:2] != '91':
                    try:
                        db_update_dict[result[0][:2]].add(result[0].strip())
                    except KeyError as e:
                        pass
        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        print 'Mysql error %d:%s' %(e.args[0], e.args[1])

def get_except_dict_from_db(yesterday):
    count_except = 0
    count_clawer = 0
    try:
        conn = MySQLdb.connect(host='10.100.80.50', user='cacti', passwd='cacti', db='clawer', port=3306)
        cur = conn.cursor()
        for days in yesterday:
            sql = 'select t.uri from  clawer_clawertask as t, clawer_clawerdownloadlog as l where  t.id=l.task_id and l.status=1 and t.clawer_id=7 and  l.add_datetime like \"%s %%\"' % days
            sql2 = 'select t.uri from  clawer_clawertask as t, clawer_clawerdownloadlog as l where  t.id=l.task_id and l.status=2 and t.clawer_id=7 and  l.add_datetime like \"%s %%\"' % days
            print sql
            count_except += cur.execute(sql)
            # print count_except
            results = cur.fetchall()
            for result in results:
                num = result[0].strip().split('/')[-2]
                try:
                    db_except_dict[num[:2]].add(num.strip())
                except:
                    pass
            count_clawer += cur.execute(sql2)
        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        print 'Mysql error %d:%s' %(e.args[0], e.args[1])
    return count_except, count_clawer
    pass

def alanysis_data(count_except, count_clawer):
    total_enterprise_num = 0
    total_clawer_not_none = 0
    total_clawer_is_none = 0
    total_clawer_num = 0
    total_clawer_except_num = 0
    total_not_clawer_num = 0
    total_update_db_num = 0
    total_not_update_db_num = 0
    total_come_in_db_num = 0
    total_not_come_in_db_num = 0
    total_clawer_not_none_and_come_in_db_num = 0
    total_clawer_and_come_in_db_num = 0

    reportfile = codecs.open('report.csv', 'wb', 'utf8')
    reportfile.write('%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s' %  (u'代号', 
                                                                                                                u'省份', 
                                                                                                                u'总共', 
                                                                                                                u'爬取非空', 
                                                                                                                u'爬取为空', 
                                                                                                                u'共爬取', 
                                                                                                                u'爬取异常', 
                                                                                                                u'未爬取', 
                                                                                                                u'爬取率', 
                                                                                                                u'入库数', 
                                                                                                                u'未入库', 
                                                                                                                u'入库率', 
                                                                                                                u'库存量', 
                                                                                                                u'缺少量', 
                                                                                                                u'成功率', 
                                                                                                                u'爬取为非空并入库', 
                                                                                                                u'爬取并入库'))
    reportfile.write('\n')
    for key, value in db_total_dict.items():
        x = str( (len(success_dict[key]) + len(fail_dict[key])) / float(len(db_total_dict[key])+0.1) )[:4]
        y = str( len(db_update_dict[key]) / float( len(success_dict[key]) + len(fail_dict[key])+0.1) )[:4]
        z = str(len(db_down_dict[key]) / float(len(db_total_dict[key])+0.1)) [:4]
        reportfile.write( '%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s' % (key, \
                                                                                                                    trans_dict[key],\
                                                                                                                    len(db_total_dict[key]), \
                                                                                                                    len(success_dict[key]), \
                                                                                                                    len(fail_dict[key]), \
                                                                                                                    len(success_dict[key]) + len(fail_dict[key]),\
                                                                                                                    len(db_except_dict[key]),\
                                                                                                                    len(db_total_dict[key]) - len(db_except_dict[key]) - len(success_dict[key]) -len(fail_dict[key]),\
                                                                                                                    x, \
                                                                                                                    len(db_update_dict[key]),\
                                                                                                                    len(success_dict[key]) + len(fail_dict[key]) - len(db_update_dict[key]),\
                                                                                                                    y, \
                                                                                                                    len(db_down_dict[key]), \
                                                                                                                    len(db_total_dict[key]) - len(db_down_dict[key]), \
                                                                                                                    z, \
                                                                                                                    len( (db_down_dict[key] & success_dict[key]) ), \
                                                                                                                    len( (db_down_dict[key] & (success_dict[key] | fail_dict[key]))) )  )

        reportfile.write('\n')
        total_enterprise_num += len(db_total_dict[key])
        total_clawer_not_none += len(success_dict[key])
        total_clawer_is_none += len(fail_dict[key])
        total_clawer_num += (len(success_dict[key]) + len(fail_dict[key]))
        total_clawer_except_num += len(db_except_dict[key])
        total_not_clawer_num += (len(db_total_dict[key])-len(success_dict[key]))-len(fail_dict[key])-len(db_except_dict[key])
        total_update_db_num += len(db_update_dict[key])
        total_not_update_db_num += len(success_dict[key]) + len(fail_dict[key]) - len(db_update_dict[key])
        total_come_in_db_num += len(db_down_dict[key])
        total_not_come_in_db_num += len(db_total_dict[key]) - len(db_down_dict[key])
        total_clawer_not_none_and_come_in_db_num += len( (db_down_dict[key] & success_dict[key]) )
        total_clawer_and_come_in_db_num += len( (db_down_dict[key] & (success_dict[key] | fail_dict[key])))

    reportfile.write('\n')
    reportfile.write('%-15s,%-15s,%-15s,%-15s,%-15s,%s(%s),%s(%s),%s(%s),%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s,%-15s' % (u'总计', 
                                                                                                                len(db_total_dict.keys()), 
                                                                                                                total_enterprise_num, 
                                                                                                                total_clawer_not_none,
                                                                                                                total_clawer_is_none, 
                                                                                                                total_clawer_num, count_clawer,
                                                                                                                total_clawer_except_num, count_except,
                                                                                                                total_not_clawer_num, total_enterprise_num-count_clawer-count_except,
                                                                                                                u'未', 
                                                                                                                total_update_db_num,
                                                                                                                total_not_update_db_num,
                                                                                                                u'未',
                                                                                                                total_come_in_db_num, 
                                                                                                                total_not_come_in_db_num, 
                                                                                                                u'未',
                                                                                                                total_clawer_not_none_and_come_in_db_num, 
                                                                                                                total_clawer_and_come_in_db_num))

    reportfile.close()

    #get_no_clawer_csv()
    no_clawer_data_csv = codecs.open('no_clawer_data_csv.csv', 'wb')
    have_clawer_data_csv = codecs.open('have_clawer_data_csv.csv', 'wb')
    for key, value in db_total_dict.items():
        no_clawer_set = db_total_dict[key] - (success_dict[key] | fail_dict[key])
        have_clawer_set = success_dict[key]
        with open('/data/clawer_result/alanysis_7_json/all_data.txt', 'r') as f:
            for line in f.readlines():
                if line.split(',')[-1].strip() in no_clawer_set:
                    no_clawer_data_csv.write(line)
                        # no_clawer_data_csv.write('\n')
                if line.split(',')[-1].strip() in have_clawer_set:
                    have_clawer_data_csv.write(line)
                                    # have_clawer_data_csv.write('\n')
            # no_clawer_data_csv.write('\n')
            # have_clawer_data_csv.write('\n')
    no_clawer_data_csv.close()
    have_clawer_data_csv.close()

    no_come_in_db_data_csv = codecs.open('no_come_in_db_data_csv.csv', 'wb')
    have_come_in_db_data_csv = codecs.open('have_come_in_db_data_csv.csv', 'wb')
    for key, value in db_down_dict.items():
        no_come_in_db_set = (success_dict[key] | fail_dict[key]) - db_down_dict[key]
        have_come_in_db_set = db_down_dict[key]
        with open('/data/clawer_result/alanysis_7_json/all_data.txt', 'r') as f:
            for line in f.readlines():
                if line.split(',')[-1].strip() in no_come_in_db_set:
                    no_come_in_db_data_csv.write(line)
                        # no_come_in_db_data_csv.write('\n')
                if line.split(',')[-1].strip() in have_come_in_db_set:
                    have_come_in_db_data_csv.write(line)
                                    # have_come_in_db_data_csv.write('\n')
            # no_come_in_db_data_csv.write('\n')
            # have_come_in_db_data_csv.write('\n')
    no_come_in_db_data_csv.close()
    have_come_in_db_data_csv.close()

def json_dump_to_file(path, json_dict):
    write_type = 'wb'
    if os.path.exists(path):
        write_type = 'a'
    with codecs.open(path, write_type, 'utf-8') as f:
        f.write(json.dumps(json_dict, ensure_ascii=False)+'\n')

def alanysis_except(count_except):
    reason_dict = {}
    try:
        conn = MySQLdb.connect(host='10.100.80.50', user='cacti', passwd='cacti', db='clawer', port=3306)
        cur = conn.cursor()
        for days in yesterday:
            # sql = 'select t.uri from  clawer_clawertask as t, clawer_clawerdownloadlog as l where t.id=l.task_id and l.status=2 and t.clawer_id=7 and  l.add_datetime like \"%s %%\"' % days
            sql = 'select l.failed_reason, t.uri, l.add_datetime   from  clawer_clawertask as t, clawer_clawerdownloadlog as l where t.id=l.task_id and l.status=1 and t.clawer_id=7 and l.add_datetime like "%s %%"' % days
            count = cur.execute(sql)
            results = cur.fetchall()
            for result in results:
                num = result[1].strip().split('/')[-2]
                # print num
                if reason_dict.has_key(result[0].strip()) is True:
                    reason_dict[result[0].strip()].append(num)
                else:
                    reason_dict[result[0].strip()] = list()
                    reason_dict[result[0].strip()].append(num)
        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        print 'Mysql error %d:%s' %(e.args[0], e.args[1])
    for key, value in reason_dict.items():
        value.sort()
        try:
            count = len(value)
        except:
            count = 0.0
        bit = str((count+0.1) / float(count_except))[:4]
        json_dump_to_file('./reason.json', {key:value, 'count':count, 'bit':bit})
    pass

def make_dir(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if os.path.exists(path) and os.path.isdir(path):
            pass
        else:
            raise exc

if __name__ == '__main__':
    do_with_day = []
    lastname = []
    yesterday = str(datetime.date.today() - datetime.timedelta(days=1))
    for i in sys.argv[1:]:
        do_with_day.append(i)
        lastname.append(i[-2:])
    if not do_with_day:
        do_with_day.append(yesterday)
        lastname = [yesterday.split('-')[-1]]
    print do_with_day
    path_dir = os.path.join( os.path.join(os.getcwd(), '/'.join(yesterday.split('-')[:-1])), ''.join(lastname) )
    print path_dir
    make_dir(path_dir)
    os.chdir(path_dir)

    f = open(one_json_file, 'wb+')
    for day in do_with_day:
        # print os.path.join(json_url, '/'.join(day.split('-')))
        dowload_json_by_days(os.path.join(json_url, '/'.join(day.split('-'))), one_json_file, f)
    f.close()

    dump_json_to_success_or_fail_file(one_json_file, success_json_file, fail_json_file)
    get_down_dict_from_db()
    get_total_dict_from_db()

    if sys.argv[1:]:
        yesterday = list(sys.argv[1:])
    else:
        yesterday = [yesterday]
    get_update_dict_from_db(yesterday)
    count_except, count_clawer = get_except_dict_from_db(yesterday)

    alanysis_data(count_except, count_clawer)
    alanysis_except(count_except)

    
	
