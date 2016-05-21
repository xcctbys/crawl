# Statement of Goals 目标描述

方便开发和运营人员解析源数据，从配置文件（json格式）中提取一些特定字段创建数据库，并根据配置文件中的映射关系从特定的源数据文件（json格式）提取数据存储到目标数据库。

# Functional Description 功能说明

- 根据配置文件（config.json） 生成sql语句,并创建数据库，创建表结构，创建数据映射
- 根据配置文件中的映射关系，从数据源中提取数据，生成sql语句，存储数据

## 功能 读取 conf_json，生成sql语句

### 输入
- 配置文件（config.json）

### 输出
- sql语句
- 生成数据库
- 创建错误日志

###逻辑流程（用伪代码写下）

```
class JsonToSql(object):
    """根据配置文件，生成对应的sql语句，并将sql导入mysql中
    """

    config_dic = {}
    data_source = []
    
    def parser_json(self,config):
    """解析配置文件
    """
        config_json = open(config,'r+')
        self.config_dic = json.loads(config_json.read())
        config_json.close()

    def get_data_source(self):
        self.data_source = self.config_dic['database']['source_file']['filename']

    def get_source_db(self):
        source_db = self.config_dic['database']['source_db']
        
    def get_destination_db(self):
        destination_db = self.config_dic['database']['destination_db']

    def get_mapping(self):
        mapping = self.config_dic['mapping']
    
    def create_commond(self):
        db_info = self.config_dic['db_info']['destination_db']
        comm = '%s -u %s -p%s -h %s -P %s -f' % (db_info['dbtype'],db_info['username'],db_info['password'],db_info['host'],db_info['port'])

    def create_table_sql(self):
    """从配置文件中获得信息，生成创建表结构的sql语句
    """
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
    """从源json数据中得到数据，生成更新表记录的sql语句
    """
        pass

    def run(self,config):
    """创建表结构，创建插入数据，导入数据库
    """
        parser_json(config)
        create_commond()
        create_table_sql()
        create_data_sql()
        pass
```

    
###性能
###有哪些失败可能，失败后如何处理

问题:
1.创建数据库失败
2.插入数据失败
处理：
记录日志


# User Interface 用户界面

## 登陆界面


## 编程接口

- 调用方式
config = './config.json'
json_to_sql = JsonToSql()
json_to_sql.run(config)

- 输入
conf.json
- 输出
create_table.sql
data.sql
创建数据库并插入数据
- 例子
```
config = './gs_table_conf.json'
json_to_sql = JsonToSql()
json_to_sql.run(config)
```
输出结果：
```
文件：
create_table.sql
data.sql

mysql> show tables;
+---------------------------+
| Tables_in_test            |
+---------------------------+
| 投资其他公司               |
| 股东出资状况               |
| ent_pub_ent_annual_report |
| guaranty                  |
| ind_comm_pub_arch_branch  |
| invest_other_company      |
| test                      |
+---------------------------+

```


# Other

- 参考文档: <https://www.toptal.com/freelance/why-design-documents-matter>
