# coding:utf-8

import json
import types

config_json = open('gs_table_conf.json', 'r+')
config_dic = json.loads(config_json.read())
config_json.close()

tables_info = config_dic['table']

# print config_dic['mapping']

def get_data(source, path):
    if path == None:
        print source
        return
    try:
        print source
        get_data(source[path[0]], path[1:])
    except TypeError:
        for i in range(len(source)):
            try:
                #print source
                get_data(source[i][path[0]], path[1:])
            except IndexError:
                get_data(source[i][path[0]], None)
            except KeyError:
                print i, path[0]
    except IndexError:
            get_data(source[path[0]], None)

def create_data_sql(source_file):
    source_json = open('guangxi.json', 'r+')
    for line in source_json:
        source = json.loads(line)
        para = ["ent_pub_ent_annual_report", u"详情", u"企业资产状况"]
        get_data(source.values()[0],para)
        #print source.values()[0]

         #get_data(source.values(), para)
        print "result over",
        # result = source.values()[0]
        for k in source.keys():
            print k
        print '\n'
    # source_dic = json.loads(source_json.read())
    source_json.close()

create_data_sql('guangxi.json')
