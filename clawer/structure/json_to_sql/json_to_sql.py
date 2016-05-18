#coding:utf-8

import json
import types

class JsonToSql(object):
    config_dic = {}
    data_source = []
    mapping = {}
    tmp_dic = {}
    table_name = ''
    id = ''

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
        db_info = self.config_dic['db_info']['destination_db']
        comm = '%s -u %s -p%s -h %s -P %s -f' % (db_info['dbtype'],db_info['username'],db_info['password'],db_info['host'],db_info['port'])

    def create_table_sql(self):
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
        source_json = open('guangxi.json', 'r+')  #guangxi.json数据源需要改成动态获取
        for line in source_json:
            source = json.loads(line)
            for k in source.keys():
                self.id = k
            self.get_data(source.values()[0], table_path, associated_field_path)
            #print "result over",

            #获取许可证号，待改进
            #for k in source.keys():
                #print k
            #print '\n'
        source_json.close()

    def get_data(self, source, path, associated_field_path):
        if len(path) == 0:
            self.parser_data(source)
            return
        try:
            self.get_data(source[path[0]], path[1:], associated_field_path)
            self.record_associated(source, associated_field_path)
        except TypeError:
            for i in range(len(source)):
                try:
                    self.get_data(source[i][path[0]], path[1:], associated_field_path)
                    self.record_associated(source[i], associated_field_path)
                except IndexError:
                    self.get_data(source[i][path[0]], [], associated_field_path)
                    self.record_associated(source[i], associated_field_path)
                except KeyError:
                    #需要写日志
                    #print "There are not these info."
                    pass
        except IndexError:
            self.get_data(source[path[0]], [], associated_field_path)
            self.record_associated(source, associated_field_path)

    def parser_data(self, source):
        try:
            data_sql = open('./insert_data.sql', 'w')
            #print self.mapping[self.table_name]['field']
            for k in self.mapping[self.table_name]['field'].keys():
                print k, source[k],self.mapping[self.table_name]['field'][k]
                #data_sql.write("%s %s \n" % (k.encode('utf8'), source[k].encode('utf8')))
            print self.tmp_dic
            print self.table_name
            print self.id
            print '\n'
            data_sql.close()
        except AttributeError:
            for i in range(len(source)):
                self.parser_data(source[i])

    def record_associated(self, source, associated_field_path):
        try:
            self.tmp_dic[associated_field_path[0]] = source[associated_field_path[0]]
            # print tmp_dic
        except KeyError:
            # print "there isn't associated field"
            pass
        except IndexError:
            # print "config error"
            pass

    def run(self):
        print 'hi, spider!'
        self.parser_json('gs_table_conf.json')
        self.get_mapping()
        #self.create_table_sql()

        for k in self.mapping.keys():
            self.table_name = self.mapping[k]['name']
            path = self.mapping[k]['path']
            associated_field_path = self.mapping[k]['associated_field_path']
            self.create_data_sql('guangxi.json', path, associated_field_path)
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

