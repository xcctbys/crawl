#coding:utf-8

'''
class ExtracterGenerator(StructureGenerator):
    def assign_tasks(self):
        tasks = self.filter_parsed_tasks()
        for task in tasks:
            priority = self.get_priority(task)
            db_conf = self.get_extracter_db_config(task)
            mappings = self.get_extracter_mappings(task)
            extracter = self.get_extracter(db_conf, mappings)
            try:
                self.assign_task(priority, extracter)
                logging.info("add task succeed")
            except:
                logging.error("assign task runtime error.")

    def assign_task(self,
                    priority=Consts.QUEUE_PRIORITY_NORMAL,
                    parser=lambda: None,
                    data=""):
        pass

    def get_extracter(self, db_conf, mappings):

        def extracter():
            try:
                self.if_not_exist_create_db_schema(db_conf)
                logging.info("create db schema succeed")
            except:
                logging.error("create db schema error")
            try:
                self.extract_fields(mappings)
                logging.info("extract fields succeed")
            except:
                logging.error("extract fields error")

        return extracter

    def if_not_exist_create_db_schema(self, conf):
        pass

    def extract_fields(self, mappings):
        pass

    def get_extracter_db_config(self):
        pass

'''

import json

class JsonToSql(object):
    config_dic = {}
    json_source = []
    
    def parser_json(self,config):
        config_json = open(config,'r+')
        config_dic = json.loads(config_json.read())
        config_json.close()

    def get_json_source(self):
        json_source = config_dic['database']['source_file']['filename']

    def create_source_db(self):
        source_db = self.config_dic['database']['source_db']
        
    def create_destination_db(self):
        destination_db = self.config_dic['database']['destination_db']

    def get_mapping(self):
        mapping = elf.config_dic['mapping']
    
    def create_commond(self):
        db_info = self.config_dic['db_info']['destination_db']
        comm = '%s -u %s -p%s -h %s -P %s -f' % (db_info['dbtype'],db_info['username'],db_info['password'],db_info['host'],db_info['port'])

    def create_table_sql(self):
        tables_info = self.config_dic['table']
        sql = ''
        for t_name in tables_info:
            table = tables_info[t_name]
            sql = 'CREATE TABLE %s ( ' % (t_name)
            for field in table:
                sql += field['field'] + ' ' + field['datatype']
                if field['option']:
                    sql += ' ' + (field['option'])
                sql +=  ','
            sql = sql[0:len(sql)-1]
            sql += ')\n\n'

        table_sql = open('./table_sql.sql','w')
        table_sql.write(sql.encode('utf8'))
        table_sql.close()
        
    def create_data_sql(self,source_json):
        pass


config_json = open('gs_table_conf.json','r+')
config_dic = json.loads(config_json.read())
config_json.close()

tables_info = config_dic['table']

#print config_dic['mapping']

source_json = open('guangxi.json','r+')
for line in source_json:
    source = json.loads(line)
    print source.values()[0]['ent_pub_ent_annual_report'][0][u'详情']
#source_dic = json.loads(source_json.read())
source_json.close()


'''
sql = ''
for t_name in tables_info:
    sql += 'CREATE TABLE %s ( ' % (t_name)
    table = tables_info[t_name]
    for field in table:
        sql += field['field'] + ' ' + field['datatype']
        if field['option']:
            sql += ' ' + (field['option'])
        sql +=  ','
    sql = sql[0:len(sql)-1]
    sql += ')\n\n'
    print type(sql)
    table_sql = open('./table_sql.sql','w')
    table_sql.write(sql.encode('utf8'))
    table_sql.close()
'''
