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
4. 将解析过得任务存到本地，计算原始数据的hash值作为键，以及任务本身的一些数据全部存储。每次解析先查看数据库是否存在，如果配置时间策略等必须重新结构化，可以更新对应hash值得内容。
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

1. 动态生成数据库表结构
2. 从解析器结果（JSON数据）中提取字段并做中英文映射，最终存入目标数据库。

### 输入
无

### 输出
- 日志
- 数据库

### 逻辑流程

```
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
结构化层需要自定义的内容比较多，统一存到Mongo数据库中。需要为每个任务需要配置解析器、目标数据库、数据库表和字段、要提取的字段中英文映射。解析器是自定义的Python脚步，其中必须包含parse方法，参数为要解析的内容，返回解析后的JSON数据。最终解析器插件会同步到服务器本地文件目录`structure/parsers/`。

```
class Parser(Document):
    parser_id = IntField()
    python_script = TextField()


class StructureConfig(Document):
    task = ReferenceField(Job)
    parser = ReferenceField(Parser)
    db_xml = TextField()
    mappings = TextField()
```

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
│   └── __init__.py
├── models.py
├── parsers
├── structure.py
├── tests
│   ├── __init__.py
│   └── test_structure.py
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

