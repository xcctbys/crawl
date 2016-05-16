# coding:utf-8

import json
import types

config_json = open('gs_table_conf.json', 'r+')
config_dic = json.loads(config_json.read())
config_json.close()

tables_info = config_dic['table']

# print config_dic['mapping']

def get_data(source, para):
    try:
        pass
        # print para[0]
    except:
        pass
    if para is None:
        print source,"\nover"
        return

    if type(source) is types.ListType:
        for i in range(len(source)):
            # print para[0],para[1]
            try:
                get_data(source[i][para[0]], para[1:])
            except:
                get_data(source[i][para[0]], None)
    elif type(source) is types.DictionaryType:
        try:
            get_data(source[para[0]], para[1:])
        except:
            get_data(source[para[0]], None)
    else:
        print "Error"
        return



source_json = open('guangxi.json', 'r+')
for line in source_json:
    source = json.loads(line)
    para = ["ent_pub_ent_annual_report", "详情", "企业资产状况"]
    get_data(source.values(), para)
    print "result over",
    # result = source.values()[0]
    for k in source.keys():
        print k
    print '\n'
# source_dic = json.loads(source_json.read())
source_json.close()

