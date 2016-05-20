#coding:utf8

import json
import types
import sys

class JsonToSql(object):
    def __init__(self):
        self.config_dic = {}
        self.data_source = []
        self.mapping = {}
        self.tmp_dic = {}
        self.table_name = ''
        self.id = ''

    def parser_json(self, config):
        config_json = open(config,'r+')
        self.config_dic = json.loads(config_json.read())
        config_json.close()

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
        comm = '%s -u %s -p%s -h %s -P %s -f' % (db_info['dbtype'],db_info['username'],db_info['password'],db_info['host'],db_info['port'])

    def create_table_sql(self):
        """
        根据配置文件中，table的信息，创建数据库，创建表
        生成table.sql
        :return:
        """
        tables_info = self.config_dic['table']
        sql = ''
        # 文件名需要动态
        table_sql = open('./table_sql.sql', 'w')
        for t_name in tables_info:
            table = tables_info[t_name]
            sql = 'CREATE TABLE %s ( ' % (t_name)
            for field in table:
                sql += field['field'] + ' ' + field['datatype']
                if field['option']:
                    sql += ' ' + (field['option'])
                sql += ','
            sql = sql[0:len(sql)-1]
            sql += ')\n\n'
            table_sql.write(sql.encode('utf8'))
        table_sql.close()

    def create_data_sql(self, source_file, table_path, associated_field_path):
        """
        生成需要插入的数据源（insert.sql）
        :param source_file: 公司信息记录的json
        :param table_path: 查询数据的路径
        :param associated_field_path: 外键的路径
        :return: 无
        """
        source_json = open('guangxi.json', 'r+')  #guangxi.json数据源需要改成动态获取
        for line in source_json:
            source = json.loads(line)
            # 获取许可证号，待改进
            for k in source.keys():
                self.id = k
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
            if type(source) == types.ListType and len(source) > 0:
                for i in range(len(source)):
                    self.parser_data(source[i])
            elif type(source) == types.DictionaryType:
                self.parser_data(source)
            else:
                #print 'error',source, 'endinnnnnnnnnnnnnnnnnnnnnnnng'
                pass
            return

        if associated_field_path[0]:
            if type(source) == types.ListType:
                self.tmp_dic[associated_field_path[0]] = source[0][associated_field_path[0]]
                #print source[0][associated_field_path[0]]
            else:
                self.tmp_dic[associated_field_path[0]] = source[associated_field_path[0]]
                #print source[associated_field_path[0]]

        try:
            self.get_data(source[path[0]], path[1:], associated_field_path[1:])
            #self.record_associated(source, associated_field_path)
        except TypeError:
            for i in range(len(source)):
                try:
                    self.get_data(source[i], path, associated_field_path)
                    #self.record_associated(source[i], associated_field_path)
                except IndexError:
                    self.get_data(source[i], [], associated_field_path[1:])
                    #self.record_associated(source[i], associated_field_path)
                except KeyError:
                    #需要写日志
                    #print 'source-eeeee:', source[i]
                    #print "source[i]", source[i]
                    #print "path[0]:", path[0]
                    #print  "associated_field_path:", associated_field_path
                    #print sys.exc_info()[0], sys.exc_info()[1]
                    #print "There are not these info."
                    pass
        except IndexError:
            self.get_data(source[path[0]], [], associated_field_path[1:])
            #self.record_associated(source, associated_field_path)

    def parser_data(self, source):
        """
        由 create_data_sql->get_data->parser_data 调用
        对找到的数据进行解析（从字典到数据）
        :param source: 通过查询，找到的用户所需数据
        :return: 无
        """
        #data_sql = open('./insert_data.sql', 'w')
        #print "start ******"
        #print source
        #print self.tmp_dic
        if len(source) == 0:
            return

        self.tmp_dic['register_num'] = self.id
        merged_dict = source.copy()
        merged_dict.update(self.tmp_dic)
        print "id ", self.id
        print "table name: ", self.table_name
        for k in self.mapping[self.table_name]['dest_field'].keys():
            try:
                print k, self.mapping[self.table_name]['dest_field'][k], merged_dict[k]
            except KeyError:
                print '\n字段设置错误，请检查配置文件'
        #print merged_dict
        #print "end ******"
        pass
        '''
        try:
            merged_dict = source.copy()
            merged_dict.update(self.tmp_dic)
        except AttributeError:
            for i in range(len(source)):
                self.parser_data(source[i])
            return
        print self.table_name
        print self.id
        for k in merged_dict.keys():
            print k, source[k], 'asdfdsafasf'
            # data_sql.write("%s %s \n" % (k.encode('utf8'), source[k].encode('utf8')))
        #print self.tmp_dic
        #print self.table_name
        #print self.id
        #data_sql.close()
        '''
    def record_associated(self, source, associated_field_path):
        """
        由 create_data_sql->get_data->record_associated 调用
        获取当前层中的外键
        :param source: 查找数据中当前层的数据
        :param associated_field_path: 外键路径
        :return: 空
        """
        if associated_field_path[0]:
            try:
                self.tmp_dic[associated_field_path[0]] = source[associated_field_path[0]]
                print self.tmp_dic
            except KeyError:
                #print "source: ", source
                print "associated_field_path: ", associated_field_path
                # print "there isn't associated field"
                pass
            except IndexError:
                #print "config error"
                pass
        return

    def test_table(self):
        print 'hi, spider!'
        self.parser_json('gs_table_conf.json')
        self.get_mapping()
        self.create_table_sql()
        '''
        for k in self.mapping.keys():
            self.table_name = self.mapping[k]['dest_table']
            path = self.mapping[k]['source_path']
            associated_field_path = self.mapping[k]['associated_field_path']
            self.create_data_sql('guangxi.json', path, associated_field_path)
            self.tmp_dic.clear()
        '''
        pass

    def run(self):
        print 'hi, spider!'
        self.parser_json('gs_table_conf.json')
        self.get_mapping()
        for k in self.mapping.keys():
            self.table_name = self.mapping[k]['dest_table']
            path = self.mapping[k]['source_path']
            associated_field_path = self.mapping[k]['associated_field_source_path']
            self.create_data_sql('guangxi.json', path, associated_field_path)
            self.tmp_dic.clear()
        pass
'''
config_json = open('gs_table_conf.json', 'r+')
config_dic = json.loads(config_json.read())
config_json.close()

tables_info = config_dic['table']
'''

if __name__ == '__main__':
    json_to_sql = JsonToSql()
    json_to_sql.run()
    #json_to_sql.test_table()

