#coding:utf8

import json
import types
import sys
import os


class JsonToSql(object):
    def __init__(self):
        self.config_dic = {}    #记录配置文件json解析后的字典
        self.mapping = {}    #记录self.config_dic中的映射关系
        self.tmp_dic = {}    #记录所需要的逻辑外键
        self.table_name = ''    #记录所需要的数据库表名
        self.id = ''    #记录公司的唯一标识id
        self.data_sql = None    #保持需要插入数据库的数据的sql文件

    def parser_json(self, config):
        """
        解析json文件，生成字典
        :param config: json文件源
        :return:解析后生成的字典
        """
        dict_json = None
        try:
            dict_json = json.loads(config)
        except Exception as e:
            print e
        return dict_json

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
        comm = '-u %s -p%s -h %s -P %s -f' % (db_info['username'], db_info['password'], db_info['host'],
                                              db_info['port'])
        return comm

    def create_table_sql(self, table_file):
        """
        根据配置文件中，table的信息，创建数据库，创建表
        生成table.sql
        :return:
        """
        tables_info = self.config_dic['table']
        db_name = self.config_dic['database']['destination_db']['dbname']
        table_sql = open(table_file, 'w')
        #database_sql = 'DROP DATABASE IF EXISTS %s;\nCREATE DATABASE %s;\nUSE %s;\n' % (db_name, db_name, db_name)
        database_sql = 'CREATE DATABASE %s;\nUSE %s;\n' % (db_name, db_name)
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
            sql = sql[0:len(sql) - 1]
            sql += ');\n\n'
            table_sql.write(sql.encode('utf8'))
        table_sql.close()

    def create_data_sql(self, data, table_path, associated_field_path):
        """
        生成需要插入的数据源（insert.sql）
        :param data: 公司信息记录的json
        :param table_path: 查询数据的路径
        :param associated_field_path: 外键的路径
        :return: 数据源value为None返回False
        """

        #*****************************换成字典****
        '''
        source = json.loads(data)
        self.id = source.keys()[0]        # 获取许可证号，待改进
        if not source[source.keys()[0]]:
            print source.keys()
            print 'key'
            print source[source.keys()[0]]
            return False
        '''
        self.id = data.keys()[0]
        if not data[self.id]:
            return False

        self.get_data(data.values()[0], table_path, associated_field_path)
        return True

    def get_data(self, source, path, associated_field_path):
        """
        由create_data_sql调用，遍历数据源，获取所需数据，及其各个层次外键
        :param source:公司信息记录的json
        :param path:查询数据的路径
        :param associated_field_path:外键的路径
        :return: 无
        """
        if not source:
            return

        if not path:
            if isinstance(source, types.ListType) and len(source) > 0:
                for i in range(len(source)):
                    self.parser_data(source[i])
            elif isinstance(source, types.DictionaryType):
                self.parser_data(source)
            else:
                print 'warning: unknown data source'
            return

        if associated_field_path[0]:
            if isinstance(source, types.ListType):
                self.tmp_dic[associated_field_path[0]] = source[0][associated_field_path[0]]
            else:
                self.tmp_dic[associated_field_path[0]] = source[associated_field_path[0]]

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

    def parser_data(self, source):
        """
        由 create_data_sql->get_data->parser_data 调用
        对找到的数据进行解析（从字典到数据）
        :param source: 通过查询，找到的用户所需数据
        :return: 无
        """
        if not source:
            return

        self.tmp_dic[u'主键'] = self.id
        merged_dict = source.copy()
        merged_dict.update(self.tmp_dic)
        field = []    #记录字段的英文名
        values = []    #记录字段的数据

        for k in self.mapping[self.table_name]['dest_field'].keys():
            field.append(self.mapping[self.table_name]['dest_field'][k])
            try:
                values.append(merged_dict[k])
            except KeyError:
                values.append('')    #源数据中没有要找的信息，用空串占位
        values = ["'%s'" % i for i in values]
        sql = 'INSERT INTO %s (%s) VALUE(%s); \n' % (self.table_name, ', '.join(field), ', '.join(values))

        self.data_sql.write(sql.encode('utf8'))
        return

    def test_table(self, extracter_conf, export_file):
        """
        生成创建表的sql文件
        :param extracter_conf: 配置
        :param export_file: 输出的sql文件
        :return: True/False
        """
        if not extracter_conf or not export_file:
            return False
        # self.config_dic = self.parser_json(extracter_conf)
        self.config_dic = extracter_conf
        self.get_mapping()
        self.create_table_sql(export_file)
        return True

    def test_get_data(self, extracter_conf, data, export_file):
        """
        生成数据sql文件，用于向关系数据库中导入数据
        :param extracter_conf: 配置文件
        :param data: 数据源 (dict)
        :param export_file: 输入的sql文件
        :return: True/False
        """

        #tmp = data.decode('utf8')
        #print type(tmp)
        #print tmp
        print 'start get data'
        if not extracter_conf or not data or not export_file:
            return False
        print 'get data dict'
        if not isinstance(data, types.DictionaryType):
            return False
        print 'config ok'
        # self.config_dic = self.parser_json(extracter_conf)
        self.config_dic = extracter_conf
        self.get_mapping()
        self.data_sql = open(export_file, 'w')
        use_database = 'use %s;\n' % self.config_dic['database']['destination_db']['dbname']
        self.data_sql.write(use_database)
        print 'confing........oooo'
        for k in self.mapping.keys():
            self.table_name = self.mapping[k]['dest_table']
            path = self.mapping[k]['source_path']
            associated_field_path = self.mapping[k]['associated_field_source_path']
            print 'create data sql'
            result = self.create_data_sql(data, path, associated_field_path)
            print 'over data sql'
            #if not result:
            #return False
            self.tmp_dic.clear()
        self.data_sql.close()
        print 'get data over'
        return True

    def test_restore(self, sql_file):
        result = 'mysql %s < %s' % (self.create_commond(), sql_file)
        os.popen(result)
        #tmp = os.popen(result).readlines()

    def test_backup(self, sql_file):
        result = 'mysqldump %s > %s' % (self.create_commond(), sql_file)
        os.popen(result)
        #tmp = os.popen(result).readlines()


if __name__ == '__main__':
    json_to_sql = JsonToSql()
    json_to_sql.test_get_data('gs_table_conf.json', 'guangxi.json', '/tmp/my_insert.sql')
    json_to_sql.test_table('gs_table_conf.json', '/tmp/my_table.sql')
    json_to_sql.test_restore('./my_table.sql')
