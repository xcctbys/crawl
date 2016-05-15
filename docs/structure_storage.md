# Statement of Goals 目标描述

方便开发和运营人员解析源数据，从json中提取一些特定字段创建数据库并把特殊字段对应的数据存储到目标数据库。

# Functional Description 功能说明

- 根据 conf_json 生成sql语句,并创建数据库，创建表结构，创建数据映射
- 根据 source_json 和数据映射生成sql语句，存储数据

## 功能1 读取 conf_json，生成sql语句

### 输入
- conf_json

### 输出
- sql语句
- 日志

###逻辑流程（用伪代码写下）

```
class JsonToSql(object):
    """根据配置文件，生成对应的sql语句，并将sql导入mysql中
    """

    config_dic = {}
    json_source = []
    
    def parser_json(self,config):
    """解析配置文件
    """
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

    def run(self):
    """创建表结构，创建插入数据，导入数据库
    """
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
- 输入
- 输出
- 例子


# Internel 内部实现

## Directory 代码目录结构

## Database 数据库


# Test 测试

## Testcase 1

- 依赖
- 输入
- 期望输出


# Other

- 参考文档: <https://www.toptal.com/freelance/why-design-documents-matter>
