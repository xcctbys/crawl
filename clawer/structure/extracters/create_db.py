# coding:utf-8

import json
import types

config_json = open('gs_table_conf.json', 'r+')
config_dic = json.loads(config_json.read())
config_json.close()

tables_info = config_dic['table']

sql = ''
for t_name in tables_info:
    sql += 'CREATE TABLE %s ( ' % (t_name)
    table = tables_info[t_name]
    for field in table:
        sql += field['field'] + ' ' + field['datatype']
        if field['option']:
            sql += ' ' + (field['option'])
        sql += ','
    sql = sql[0:len(sql) - 1]
    sql += ');\n\n'
    print type(sql)
    table_sql = open('./table_sql.sql', 'w')
    table_sql.write(sql.encode('utf8'))
    table_sql.close()
