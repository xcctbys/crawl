# coding:utf8

import json
import os
import types


class JsonToSql(object):
    """
    根据导出层配置文件，提取源数据生成sql语句，并将结果导入到mysql中
    """

    def __init__(self):
        self.config_dic = {}  # 记录配置文件json解析后的字典
        self.mapping = {}  # 记录self.config_dic中的映射关系
        self.fk_dic = {}  # 记录所需要的逻辑外键
        self.table_name = ''  # 记录所需要的数据库表名
        self.key = ''  # 记录公司的唯一标识key
        self.data_file = None  # 保存需要插入数据库的数据的sql文件

    def parse_json(self, config):
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

    def get_mapping(self):
        self.mapping = self.config_dic['mapping']

    def create_command(self):
        db_info = self.config_dic['database']['destination_db']
        comm = '-u %s -p%s -h %s -P %s -f' % (db_info['username'], db_info['password'], db_info['host'],
                                              db_info['port'])
        return comm

    def create_table_sql(self, table_file):
        """
        根据配置文件中，table的信息，创建表
        :param table_file: 存放表结构的sql文件
        :return: 无
        """
        tables_info = self.config_dic['table']
        db_name = self.config_dic['database']['destination_db']['dbname']
        with open(table_file, 'w') as table_sql:
            database_sql = 'USE %s;\n' % db_name
            table_sql.write(database_sql.encode('utf8'))
            sql = ''
            for t_name in tables_info:  # 获得每张表结构信息
                table = tables_info[t_name]
                field_dict = {}
                for field in table:  # 获取单张表的字段信息
                    value = '%s %s' % (field['datatype'], field['option'])
                    field_dict[field['dest_field']] = value

                sql = 'CREATE TABLE %s (' % t_name
                for k, v in field_dict.items():  # 生成sql语句
                    sql += '%s %s,' % (k, v)
                sql = sql[0:len(sql) - 1] + ');\n\n'
                table_sql.write(sql.encode('utf8'))

    def create_data_sql(self, data, table_path, associated_field_path):
        """
        生成需要插入的sql语句
        :param data: 数据源（dictionary）
        :param table_path: 查询数据的路径（list）
        :param associated_field_path: 外键的路径（list）
        :return: 数据源value为空返回False
        """
        self.key = data.keys()[0]
        if not data[self.key]:
            return False

        self.get_data(data.values()[0], table_path, associated_field_path)
        return True

    def get_data(self, source, path, associated_field_path):
        """
        由create_data_sql调用，遍历数据源，获取所需数据，及其各个层次外键
        :param source:源数据信息记录（dictionary）
        :param path:查询数据的路径（list）
        :param associated_field_path:外键的路径（list）
        :return: 空
        """
        if not source:
            return None

        if not path:  # 查询路径为空时，开始解析数据
            if isinstance(source, types.ListType) and len(source) > 0:
                for i in range(len(source)):
                    self.parse_data(source[i])
            elif isinstance(source, types.DictionaryType):
                self.parse_data(source)
            else:
                print 'warning: unknown data source'
            return None

        if associated_field_path[0]:  # 若外键路径存在，则记录
            if isinstance(source, types.ListType):
                self.fk_dic[associated_field_path[0]] = source[0][associated_field_path[0]]
            else:
                self.fk_dic[associated_field_path[0]] = source[associated_field_path[0]]

        try:
            self.get_data(source[path[0]], path[1:], associated_field_path[1:])
        except TypeError:
            for i in range(len(source)):
                self.get_data(source[i], path, associated_field_path)
        except KeyError:
            print 'warning: the company has not these info'

    def parse_data(self, source):
        """
        由 create_data_sql->get_data->parse_data 调用
        对找到的数据进行解析（从字典到数据）
        :param source: 通过查询，找到所需数据（dictionary）
        :return: 空
        """
        if not source:
            return None

        self.fk_dic[u'主键'] = self.key
        merged_dict = source.copy()
        merged_dict.update(self.fk_dic)  # 合并找到的数据与最外层主id
        field = []  # 记录字段的英文名
        values = []  # 记录字段的数据

        # 根据mapping中设置的中英文映射关系，得到key（即所需要的字段）, value（即所对应的数据库字段名）
        # 根据所得到的key，从merged_dict中找到相应的value（即数据库中对应字段的值）
        # 拼接两个对应的value得到sql语句
        for k in self.mapping[self.table_name]['dest_field'].keys():
            mapping_field_value = self.mapping[self.table_name]['dest_field'][k]
            try:
                # 以下代码用于解决配置文件字段多对一关系
                # 如果field中已经存在该字段，且merged_dict[k]存在，那就改变对应的values[index]的值为merged_dict[k]
                index = field.index(mapping_field_value)
                if not values[index] and k in merged_dict.keys():
                    values[index] = merged_dict[k]
                continue
            except ValueError:
                field.append(mapping_field_value)

            try:
                values.append(merged_dict[k])
            except KeyError:
                values.append('')  # 源数据中没有要找的信息，用空串占位

        values = ["'%s'" % i for i in values]
        sql = 'INSERT INTO %s (%s) VALUE(%s); \n' % (self.table_name, ', '.join(field), ', '.join(values))

        self.data_file.write(sql.encode('utf8'))
        return None

    def run_generate_db_sql(self, extracter_conf, export_file):
        """
        生成创建表的sql文件
        :param extracter_conf: 导出层配置（dictionary）
        :param export_file: 输出的sql文件
        :return: True/False
        """
        if not extracter_conf or not export_file:
            return False
        self.config_dic = extracter_conf
        self.get_mapping()
        self.create_table_sql(export_file)
        return True

    def run_generate_data_sql(self, extracter_conf, data, export_file):
        """
        生成数据sql文件，用于向关系数据库中导入数据
        :param extracter_conf: 导出层配置(dictionary)
        :param data: 数据源 (dictionary)
        :param export_file: 输入的sql文件
        :return: 任意一个参数为空或源数据不是字典类型，返回False
        """
        if not extracter_conf or not data or not export_file:
            return False
        if not isinstance(data, types.DictionaryType):
            return False
        self.config_dic = extracter_conf
        self.get_mapping()
        self.data_file = open(export_file, 'w')
        use_database = 'use %s;\n' % self.config_dic['database']['destination_db']['dbname']
        self.data_file.write(use_database)
        for k in self.mapping.keys():
            self.table_name = self.mapping[k]['dest_table']
            path = self.mapping[k]['source_path']
            associated_field_path = self.mapping[k]['associated_field_source_path']
            self.create_data_sql(data, path, associated_field_path)
            self.fk_dic.clear()
        self.data_file.close()
        return True

    def run_restore_db(self, sql_file):
        """
        将sql文件导入到mysql数据库中
        :param sql_file：文件路径
        """
        result = 'mysql %s < %s' % (self.create_command(), sql_file)
        os.popen(result)

    def run_backup_db(self, sql_file):
        """
        将sql文件导入到mysql数据库中
        :param sql_file：文件路径
        """
        result = 'mysqldump %s > %s' % (self.create_command(), sql_file)
        os.popen(result)


if __name__ == '__main__':
    json_to_sql = JsonToSql()
    json_to_sql.run_generate_data_sql('gs_table_conf.json', 'guangxi.json', '/tmp/my_insert.sql')
    json_to_sql.run_generate_db_sql('gs_table_conf.json', '/tmp/my_table.sql')
    json_to_sql.run_restore_db('./my_table.sql')
