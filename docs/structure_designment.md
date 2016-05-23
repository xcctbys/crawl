# 目标

方便开发和运营人员解析源数据，从中提取一些特定字段的数据存储到目标数据库。

# 设计思路

结构化层主要分为解析层和导出层。

解析层是对爬取的源数据做初次解析，解析为JSON格式的数据并存储到Mongo数据库。

解析层采用异步队列实现，通过crontab定时筛选已经完成下载的任务并为其生成解析任务分发到不同RQ队列里，worker负责依次从对应优先级的RQ队列中依次获取任务（即特定的解析任务）并执行。

导出层是对解析层生成的JSON数据进行二次解析，该层主要完成两件事情，第一，动态创建关系型数据库表的（如Mysql），第二，特定字段的提取并存储到上文创建的数据库表中。

导出层同样采用异步队列实现，通过crontab定时筛选已经完成初次解析的任务并为其生成导出任务分发到不同的RQ队列里，worker负责依次从对应优先级的RQ队列中获取导出任务并执行。

# Class

```
class Consts(object):
    """一些全局的常量
    """

    QUEUE_PRIORITY_TOO_HIGN = u"structure:higher"
    QUEUE_PRIORITY_HIGN = u"structure:high"
    QUEUE_PRIORITY_NORMAL = u"structure:normal"
    QUEUE_PRIORITY_LOW = u"structure:low"



class StructureGenerator(object):
    """结构化层通用生成器，提供一些通用的函数，暂时用于派生解析任务生成器和导出任务生成器
    """

    def filter_downloaded_tasks(self):
        pass

    def filter_parsed_tasks(self):
        pass

    def get_task_priority(self, task):
        pass

    def get_task_source_data(self, task):
        pass


class ParserGenerator(StructureGenerator):
    """解析任务生成器
    """

    pass


class ExtracterGenerator(StructureGenerator):
    """导出任务生成器
    """

    pass


class ExecutionTasks(object):
    """用于执行解析任务和导出任务
    """

    pass

```

# 功能

## 1. 生成解析任务（In master）

从数据库过滤需要解析的任务，读取该任务的解析器配置并选择对应的解析器(HTML，JSON，PDF，OCR)生成一个解析任务，根据任务的优先级分配到不同优先级的队列。

问题1： 如何查找已经下载完成的任务？
问题2： 如何设定解析器的接口？
问题3： 如何找到对应的解析器解析器函数？
问题4： 如何防止重复解析？
问题5： 如何限定RQ性能？

1. 筛选`collector.models.CrawlerTask`中`status`为`下载成功`的下载器任务
2. 解析器中必须包含`RawParser`类和其方法`parse`方法，该方法的参数为要解析的原始数据。
3. 在`1`中筛选出的下载器任务中可以找到其对应的`Job`，通过`Job`在结构化层配置数据库`StructureConfig`中找到对应`Job`的配置，在`StructureConfig`中可以在解析器数据库`Parser`中找到对应的Python脚本，将该脚本存储到本地`structure/parsers/`目录中以解析器`id`命名。每次查找解析器脚本时先从数据库同步到本地（防止数据库更新本地未更新的问题）。
4. 将解析过得任务存到数据库，计算原始数据的hash值作为键，以及任务本身的一些数据全部存储。每次解析先查看数据库是否存在，如果配置时间策略等必须重新结构化，可以更新对应hash值得内容。
5. 限制RQ队列的总长度，为每个任务设定超时时间。(可配置)

### 输入
无

### 输出
- 日志
- 数据库

### 逻辑流程

```
class ParserGenerator(StructureGenerator):
    def assign_tasks(self):
        tasks = self.filter_downloaded_tasks()
        for task in tasks:
            parser = self.get_parser(task)
            priority = self.get_priority(task)
            data = self.get_task_source_data(task)
            if not self.is_duplicates(data):
                try:
                    self.assign_task(priority, parser, data)
                    logging.info("add task succeed")
                except:
                    logging.error("assign task runtime error.")
            else:
                logging.error("duplicates")

    def assign_task(self,
                    priority=Consts.QUEUE_PRIORITY_NORMAL,
                    parser=lambda: None,
                    data=""):
        pass

    def get_parser(self, task):
        pass

    def is_duplicates(self, data):
        return False 
```

## 2. 生成导出任务（In Master）

从数据库过滤需要导出的task，读取该任务的导出器配置并生成对应的导出任务，根据任务的优先级分配到不同优先级的队列。

导出任务主要包含如下内容：

问题1. 如何动态生成数据库表结构并插入数据?    
问题2. 如何查找已经解析完成的任务？  
问题3. 如何找到对应的导出器的配置文件  
问题4. 导出任务的触发  
问题5. 容灾及错误处理  

1. 读取配置文件, 从解析器结果（JSON数据）中提取字段, 动态生成SQL建表语句和插入语句, 并做中英文映射，最终存入目标数据库。
2. 筛选`collector.models.CrawlerTask`中`status`为`解析成功`的解析器任务
3. 在筛选出的解析器任务中可以找到其对应的`Job`，通过`Job`在结构化层配置数据库`StructureConfig`中找到对应`Job`的配置，在`StructureConfig`中可以在导出器数据库`Extracter`中找到对应的 JSON 配置文件
4. 手动执行;  crontab定时执行
5. 用户编写了错误的配置文件;   导出失败的情况
### 输入
解析器解析后的JSON数据
导出器配置文件(数据表设置, mapping)

### 输出
- 关系数据库
- 日志

### 逻辑流程

```
class ExtracterGenerator(StructureGenerator):
    def assign_tasks(self):
        """分配所有任务"""
        pass

    def assign_task(self,
                    priority=Consts.QUEUE_PRIORITY_NORMAL,
                    parser=lambda: None,
                    data=""):
        pass

    def get_extracter(self, db_conf, mappings):
        """根据配置获得导出器"

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
        """导出相应字段"""
        pass

    def get_extracter_db_config(self):
        """获得数据库配置"""
        pass

```

## 3. 执行任务（In Slave）

根据服务器cpu数启动相同数量的worker，每个worker依次从网络队列中读取对应优先级的任务，执行完成后循环前一步直到队列中任务为空。

### 输入
无

### 输出

- 数据库
- 日志文件

### 逻辑流程

```
class ExecutionTasks(object):

    def exec_task(queue=Consts.QUEUE_PRIORITY_NORMAL):
        with Connection([queue]):
            w = Worker()
            w.work()
```

# 配置
结构化层需要自定义的内容比较多，统一存到Mongo数据库中。需要为每个任务需要配置解析器、目标数据库、数据库表和字段、要提取的字段中英文映射。
解析器是自定义的Python脚本，其中必须包含parse方法，参数为要解析的内容，返回解析后的JSON数据。最终解析器插件会同步到服务器本地文件目录`structure/parsers/`。  
导出器是固定的模块, 每个网站使用1个配置文件, 保存在MySQL, 每个配置文件, 根据源数据的结构, 按模板格式修改需自定义的部分, 包括"数据库设置", "映射设置", "数据表设置"三个部分
```
class Parser(Document):
    parser_id = IntField()
    python_script = TextField()

class Extracter(Document):
    extracter_id = IntField()
    extracter_conf = TextField()


class StructureConfig(Document):
    task = ReferenceField(Job)
    parser = ReferenceField(Parser)
    extracter = ReferenceField(Extracter)
    <!--db_xml = TextField()-->
    <!--mappings = TextField()-->

```


## 配置文件格式

```
{
    "database": {
        "source_db": {
            "dbtype": "原始数据库类型",
            "host": "源数据库地址",
            "port": "源数据库端口",
            "username": "源数据库用户名",
            "password":, "源数据库密码",
            "dbname": "源数据库名"
        },
        "destination_db": {
            "dbtype": "目标数据库类型",
            "host": "目标数据库地址",
            "port": "目标数据库端口",
            "username": "目标数据库用户",
            "password": "目标数据库密码",
            "dbname": "目标数据库库名"
        }
    },

    "mapping": {
        "表1": {
            "dest_table": "表1的英文名",
            "source_path": ["表1的表名在JSON源数据中的搜索路径"]
            "associated_field_source_path": ["关联字段在JSON源数据中的搜索路径"],
            "dest_field": {
                "关联字段": "关联字段英文名",
                "字段1": "字段1英文名",
                "字段2": "字段2英文名",
                "字段n": "字段n英文名"
            },
        "表2": {
            "dest_table": "表2英文名",
            "source_path": ["表2的表名在JSON源数据中的搜索路径"]
            "associated_field_source_path": ["关联字段在JSON源数据中的搜索路径"],
            "dest_field": {
                "关联字段": "关联字段英文名",
                "字段1": "字段1英文名",
                "字段2": "字段2英文名",
            },
        "表n": {
            "dest_table": "表n英文名",
            "source_path": ["表n的表名在JSON源数据中的搜索路径"]
            "associated_field_source_path": ["关联字段在JSON源数据中的搜索路径"],
            "dest_field": {
                "字段1": "字段1英文名",
                "字段2": "字段2英文名",
            }
    },

    "table": {
        "表1英文名": [
            {
                "dest_field": "关联字段英文名",
                "datatype": "数据类型",
                "option": "字段选项",
            },
			{
				"dest_field": "字段1英文名",
				"datatype": "数据类型",
				"option": "字段选项",
			},
			{
				"dest_field": "字段2英文名,
				"datatype": "数据类型",
				"option": "字段选项",
			},
			{
				"dest_field": "字段n英文名,
				"datatype": "数据类型",
				"option": "字段选项",
			}
		],
		"表2英文名": [
            {
                "dest_field": "关联字段英文名",
                "datatype": "数据类型",
                "option": "字段选项",
            },
			{
				"dest_field": "字段1英文名,
				"datatype": "数据类型",
				"option": "字段选项",
			},
			{
				"dest_field": "字段2英文名,
				"datatype": "数据类型",
				"option": "字段选项",
			}
		]
	}
}
```
### 关于database 部分
源数据库现只支持 MongoDB
目标数据库现只支持 MySQL
### 关于 mapping 部分: 
指定JSON源数据和关系数据库字段的映射关系和中英文表名的对应关系
- dest_table 自定义目标数据库表的英文名称
- source_path 表名在 JSON 源数据中的路径. 以列表形式呈现, 根据源数据的嵌套层次, 依次写入列表
- associated_field_source_path 关联字段的在 JSON 源数据中的路径. 
- dest_field 关系数据库表中字段的定义 
### 关于 table 部分:
- dest_field 为 mapping 中相应的目的数据库表的字段
- option 为字段的选项, 如设置主键, 默认值等
## 配置文件使用限制
1. 仅能用于建立基本表
2. associated_field_source_path 必须是 source_path 的子集
3. 每个表必须设置 associated_field_source_path, 如不必要则填为空串(如 [""])



# 部署
- crontab，在master服务器上定时更新解析生成器和导出生成器队列，最终会给出一个`python manage.py command`形式的命令
- 守护进程，在slave服务器上轮询查看对应优先级队列是否有任务，若有任务执行任务，若没有等待。

# User Interface 用户界面

## 登陆界面

## 编程接口

- 调用方式
- 输入
- 输出
- 例子


# Internel 内部实现

## Directory 代码目录结构

```
structure
├── __init__.py
├── admin.py
├── migrations
│   └── __init__.py
├── models.py
├── parsers
├── structure.py
├── tests
│   ├── __init__.py
│   └── test_structure.py
└── views.py
```

## Database 数据库


# Test 测试

## 单元测试

```
class TestStructureGenerator(TestCase):
    def test_filter_downloaded_tasks(self):
        pass

    def test_filter_parsed_tasks(self):
        pass

    def test_get_task_priority(self, task):
        pass

    def test_get_task_source_data(self, task):
        pass


class TestParserGenerator(TestCase):
    def test_assign_tasks(self):
        pass

    def test_assign_task(self):
        pass

    def test_get_parser(self):
        pass

    def test_is_duplicates(self):
        pass


class TestExtracterGenerator(TestCase):
    def test_assign_tasks(self):
        pass

    def test_assign_task(self):
        pass

    def test_get_extracter(self):
        pass

    def test_if_not_exist_create_db_schema(self):
        pass

    def test_extract_fields(self):
        pass

    def test_get_extracter_db_config(self):
        pass


class TestExecutionTasks(TestCase):
    def test_exec_task(self):
        pass
```
#测试方案
正确性测试，容错性测试，数据库测试

##测试环境
CentOS 7
开启以下服务：
service mariadb start
service memcached start
./redis-server
./mongod

##单模块测试添加数据
使用Django Shell:
	python manage.py shell
运行函数添加数据：
	from structure.structure import insert_test_data
	from structure.structure import empty_test_data
	empty_test_data()
	insert_test_data()
查看数据，打开mongodb：
	use source
	show tables #看到生成job，crawler_task, crawler_download和crawler_download_data
进入MySQL中查看生成的数据：
	mysql -u cacti -p
	#输入密码cacti
	show databases；
	use clawer;
	show tables;#其中可以看到生成的parser和structure_config两张表
	show columns from parser #或structure_config
	select parser_id from parser #选择某一列进行查看
单模块测试的数据就插入完成了。

##添加一个Job并为之配置下载器、生成器和解析器
使用Django Shell:
	python manage.py shell
输入指令：
	from structure.tests.test_structure import insert_job
	#该函数的参数表已经改成了（name, text, parser_text, settings）
	#test_insert_job_with_parser函数是重写insert_text_without_job函数，请参照子阳的文档先获取好text和settings参数
接下来获取其他参数：
	import os
	parser_file = open("~/Projects/cr-clawer/clawer/structure/parsers/template.py")#你的项目目录
	parser_text = parser_file.read()
	name = "test" #可随意取名字
运行函数生成job和生成下载解析器：
	insert_job(name, text, parser_text, settings)
##分发解析任务
输入指令：
	python manage.py task_parser_dispatch
输入：无
输出：生成四个RQ队列：structure：higher, structure:high, structure:normal, structure:low
队列中有任务，任务总数跟CrawlerTask中下载成功的总数一致,可以在MongoDB中通过以下指令验证
	use source
	db.crawler_task.find({status:5}).count()

##执行解析任务
输入指令：
	cd ~/cr-clawer/confs/dev
	./run_structure_local   #开启rq worker执行
输入：无
输出：开启worker执行指定队列名中的任务，成功则向MongoDB中写入解析结果，通过以下指令查看：
	use structure
	db.crawler_analyzed_data.find()
成功解析的CrawlerTask任务状态变为解析成功，通过以下指令查看：
	use source
	db.crawler_task.find({status:7})
解析失败的CrawlerTask任务状态变为解析失败，通过以下指令查看：
	use source
	db.crawler_task.find({status:6})

##重新分发失败任务
输入指令：
	python manage.py requeue_failed_parse_jobs
输入：无
输出：数据库中状态为解析失败且解析失败次数小于3的任务被重新分发到相应的RQ队列中，状态改为下载成功，通过以下指令查看：
	use source
	db.crawler_task.find({status:6})   #状态为解析失败的任务数量
	use default
	db.crawler_analyzed_data.find({retry_times:3})   #失败次数为3的任务数量
两数之差就应该时执行完本脚本后RQ队列中新增的任务数

##监控RQ队列
安装rq-dashboard:
	sudo pip install rq-dashboard
根据其提供的URL登陆浏览器即可通过图形化界面监控RQ队列及其任务
