# coding:utf-8

import json
import types

config_json = open('gs_table_conf.json', 'r+')
config_dic = json.loads(config_json.read())
config_json.close()

tables_info = config_dic['table']



def get_data(source, path, associated_field_path):
    #print path
    if len(path) == 0:
        #print source
        parser_data(source)
        '''
        data_sql = open('./data.sql', 'a')
        data_sql.write(str(source))
        data_sql.close()
        '''
        return
    try:
        #print source
        get_data(source[path[0]], path[1:], associated_field_path[1:])
        if associated_field_path[0]:
            tmp_dic[associated_field_path[0]] = source[associated_field_path[0]]
    except TypeError:
        for i in range(len(source)):
            try:
                #print source
                get_data(source[i][path[0]], path[1:], associated_field_path[1:])
                if associated_field_path[0]:
                    tmp_dic[associated_field_path[0]] = source[i][associated_field_path[0]]
            except IndexError:
                get_data(source[i][path[0]], [], associated_field_path[1:])
                if associated_field_path[0]:
                    tmp_dic[associated_field_path[0]] = source[i][associated_field_path[0]]
            except KeyError:
               print "There are not these info."
               pass
    except IndexError:
            get_data(source[path[0]], [], associated_field_path)
            if associated_field_path[0]:
                tmp_dic[associated_field_path[0]] = source[associated_field_path[0]]

def create_data_sql(source_file, table_path, associated_field_path):
    source_json = open('guangxi.json', 'r+')
    for line in source_json:
        source = json.loads(line)
        get_data(source.values()[0], table_path, associated_field_path)
        #print source.values()[0]

         #get_data(source.values(), table_path)
        print "result over",
        # result = source.values()[0]
        for k in source.keys():
            print k
        print '\n'
    # source_dic = json.loads(source_json.read())
    source_json.close()

def parser_data(source):
    try:
        print tmp_dic
        for k in source.keys():
            #print table_name, '\n'
            #print k, source[k]
            pass
    except AttributeError:
        for i in range(len(source)):
            parser_data(source[i])
#create_data_sql('guangxi.json')

tmp_dic = {}
mapping = config_dic['mapping']
for k in mapping.keys():
    table_name = mapping[k]['name']
    path = mapping[k]['path']
    associated_field_path = mapping[k]['associated_field_path']
    create_data_sql('guangxi.json', path, associated_field_path)