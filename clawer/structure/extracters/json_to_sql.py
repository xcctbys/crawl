#coding:utf8

import json
import types
import sys
import os

class JsonToSql(object):
    def __init__(self):
        self.config_dic = {}    #记录配置文件json解析后的字典
        self.mapping = {}       #记录self.config_dic中的映射关系
        self.tmp_dic = {}       #记录所需要的逻辑外键
        self.table_name = ''    #记录所需要的数据库表名
        self.id = ''            #记录公司的唯一标识id
        self.data_sql = None    #保持需要插入数据库的数据的sql文件

    def parser_json(self, config):
        """
        解析json文件，生成字典
        :param config: json文件源
        :return:解析后生成的字典
        """
        config_json = open(config,'r+')
        try:
            dict_json = json.loads(config_json.read())
        except:
            print 'json error'
        config_json.close()
        return  dict_json


    def get_json_source(self):
        self.data_source = self.config_dic['database']['source_file']['filename']

    def create_source_db(self):
        source_db = self.config_dic['database']['source_db']
        
    def create_destination_db(self):
        destination_db = self.config_dic['database']['destination_db']

    def get_mapping(self):
        self.mapping = self.config_dic['mapping']
    
    def create_commond(self):
        db_info = self.config_dic['database']['destination_db']
        comm = '%s -u %s -p%s -h %s -P %s -f < ' % (db_info['dbtype'],db_info['username'],db_info['password'],db_info['host'],db_info['port'])
        return comm

    def create_table_sql(self, table_file):
        """
        根据配置文件中，table的信息，创建数据库，创建表
        生成table.sql
        :return:
        """
        tables_info = self.config_dic['table']
        db_name = self.config_dic['database']['destination_db']['dbname']
        # 文件名需要动态
        table_sql = open(table_file, 'w')
        database_sql = 'DROP DATABASE IF EXISTS %s;\nCREATE DATABASE %s;\nUSE %s;\n' % (db_name, db_name, db_name)
        table_sql.write(database_sql.encode('utf8'))
        sql = ''
        for t_name in tables_info:
            table = tables_info[t_name]
            sql = 'CREATE TABLE %s ( ' % (t_name)
            for field in table:
                sql += field['dest_field'] + ' ' + field['datatype']
                if field['option']:
                    sql += ' ' + (field['option'])
                sql += ','
            sql = sql[0:len(sql)-1]
            sql += ');\n\n'
            table_sql.write(sql.encode('utf8'))
        table_sql.close()

    def create_data_sql(self, data, table_path, associated_field_path):
        """
        生成需要插入的数据源（insert.sql）
        :param data: 公司信息记录的json
        :param table_path: 查询数据的路径
        :param associated_field_path: 外键的路径
        :return: 无
        """
        source_json = open(data, 'r+')  #guangxi.json数据源需要改成动态获取
        for line in source_json:
            source = json.loads(line)
            # 获取许可证号，待改进
            #for k in source.keys():
            self.id = source.keys()[0]
            #查询数据
            self.get_data(source.values()[0], table_path, associated_field_path)
            #print "result over",
        source_json.close()

    def get_data(self, source, path, associated_field_path):
        """
        由create_data_sql调用，遍历数据源，获取所需数据，及其各个层次外键
        :param source:公司信息记录的json
        :param path:查询数据的路径
        :param associated_field_path:外键的路径
        :return: 无
        """
        if len(path) == 0:
            if isinstance(source, types.ListType) and len(source) > 0:
                for i in range(len(source)):
                    self.parser_data(source[i])
            elif isinstance(source, types.DictionaryType):
                self.parser_data(source)
            elif len(source) == 0:
                pass
            else:
                print 'warning: unknown data source'
            return

        if associated_field_path[0]:
            if isinstance(source, types.ListType):
                self.tmp_dic[associated_field_path[0]] = source[0][associated_field_path[0]]
                #print source[0][associated_field_path[0]]
            else:
                self.tmp_dic[associated_field_path[0]] = source[associated_field_path[0]]
                #print source[associated_field_path[0]]

        try:
            self.get_data(source[path[0]], path[1:], associated_field_path[1:])
        except TypeError:
            for i in range(len(source)):
                try:
                    self.get_data(source[i], path, associated_field_path)
                except IndexError:
                    self.get_data(source[i], [], associated_field_path)
        except KeyError:
            print 'warning: the company has not these info'
        #except IndexError:
            #self.get_data(source[path[0]], [], associated_field_path[1:])
            #self.record_associated(source, associated_field_path)

    def parser_data(self, source):
        """
        由 create_data_sql->get_data->parser_data 调用
        对找到的数据进行解析（从字典到数据）
        :param source: 通过查询，找到的用户所需数据
        :return: 无
        """
        #print "start ******"
        if len(source) == 0:
            return

        self.tmp_dic[u'主键'] = self.id
        merged_dict = source.copy()
        merged_dict.update(self.tmp_dic)
        field = []       #记录字段的英文名
        values = []      #记录字段的数据

        #for k in merged_dict.keys():
            #print k

        for k in self.mapping[self.table_name]['dest_field'].keys():
            field.append(self.mapping[self.table_name]['dest_field'][k])
            try:
                values.append(merged_dict[k])
            except KeyError:
                values.append('')    #源数据中没有要找的信息，用空串占位
        values = ["'%s'" % i for i in values]
        sql = 'INSERT INTO %s (%s) VALUES(%s); \n' % (self.table_name, ', '.join(field), ', '.join(values))

        self.data_sql.write(sql.encode('utf8'))
        #print "end ******"
        return

    def test_table(self, extracter_conf, export_file):
        """
        生成创建表的sql文件
        :param extracter_conf: 配置文件
        :param export_file: 输出的sql文件
        :return: 无
        """
        print 'hi, spider!'
        self.config_dic = extracter_conf
        self.get_mapping()
        self.create_table_sql(export_file)
        pass

    def test_get_data(self, extracter_conf, data, export_file):
        """
        生成数据sql文件，用于向关系数据库中导入数据
        :param extracter_conf: 配置文件
        :param data: 源文件
        :param export_file: 输入的sql文件
        :return: 无
        """
        print 'hi, spider!'
        self.config_dic = extracter_conf
        self.get_mapping()
        self.data_sql = open(export_file, 'w')
        use_database = 'use %s;\n' % self.config_dic['database']['destination_db']['dbname']
        self.data_sql.write(use_database)
        for k in self.mapping.keys():
            self.table_name = self.mapping[k]['dest_table']
            path = self.mapping[k]['source_path']
            associated_field_path = self.mapping[k]['associated_field_source_path']
            self.create_data_sql(data, path, associated_field_path)
            self.tmp_dic.clear()
        self.data_sql.close()
        print 'over'

    def test_daoru(self, sql_file):
        result = self.create_commond()+sql_file
        tmp = os.popen(result).readlines()
        print tmp
        pass

if __name__ == '__main__':
    json_to_sql = JsonToSql()
    json_to_sql.test_get_data('gs_table_conf.json', 'guangxi.json', './my_insert.sql')
    json_to_sql.test_table('gs_table_conf.json', './my_table.sql')
    json_to_sql.test_daoru('./my_table.sql')

