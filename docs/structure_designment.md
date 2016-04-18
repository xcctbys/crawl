# 目标

方便开发和运营人员解析源数据，从中提取一些特定字段的数据存储到目标数据库。

# 设计思路

结构化层主要分为解析层和导出层。

解析层是对爬取的源数据做初次解析，解析为JSON格式的数据并存储到Mongo数据库。

解析层采用Master/Slave结构，Master即任务生产者，负责找出已经完成下载的Job并为其生成解析任务分发到不同RQ队列里，Slave即任务的消费者，负责依次从对应优先级的RQ队列中依次获取任务（即特定的解析任务）并执行。

导出层是对解析层生成的JSON数据进行二次解析，该层主要完成两件事情，第一，动态创建关系型数据库表的（如Mysql），第二，特定字段的提取并存储到上文创建的数据库表中。

导出层同样采用Master/Slave结构，Master即任务生产者，负责找出已经完成初次解析的Job并为其生成导出任务分发到不同的RQ队列里，Slave即任务的消费者，负责依次从对应优先级的RQ队列中获取导出任务并执行。

# 功能

## 生产解析任务（In master）

从数据库过滤需要解析的job，读取该job的解析器配置并选择对应的解析器(HTML，JSON，PDF，OCR)生成一个解析任务，根据任务的优先级分配到不同优先级的队列。

### 输入

无

### 输出

日志文件

### ORM

```python
class StructureConfigs(Document):

    job = ReferenceField(Job)
    plugin_id = IntField()


class StructerPlugins(Document):

    (DEFAULT, HTML, JSON, PDF, OCR) = range(1, 6)
    CHOICES = (
        (DEFAULT, u"DEFAULT"),
        (HTML, u"HTML"),
        (JSON, u"JSON"),
        (PDF, u"PDF"),
        (OCR, u"OCR"),
    )
    uri = StringField(max_length=1024, null=True)
    type = IntField(default=DEFAULT, null=True)
    python_script = TextField()
```

### 逻辑流程

```python
assign_tasks():
    jobs = filter_downloaded_jobs():
    for job in jobs:
        conf = _get_structure_conf_by_id(job.id)
        structer = _get_structer_by_id(conf.plugin_id)
        priority = _get_job_priobrity_by_id(job.id)
        data = _get_source_data(job.id)
        if not is_duplicates(data):
          try:
              _assign_task(priority, structer, data)
          except:
              _error_log()
        else:
            _log(duplicates)


_assign_task(proiority='low', structer=lambda:None, data=data):
    q = get_queue(proiority)
    q.enqueue(structer, data)


_get_structer_by_id(plugin_id):
    script = StructerPlugins.objecs.filter(id=plugin_id)
    absolute_path = local_save(script)

    def structer(absolute_path):
        from subprocess import call
        call(["python {0}".format(script)])

    return structer
```


## 消费解析任务（In Slave）

根据服务器cpu数启动相同数量的worker，每个worker依次从网络队列中读取对应优先级的任务，执行完成后循环前一步直到队列中任务为空。

### 输入

无

### 输出

- 数据库
- 日志文件

### 逻辑流程

```python
import sys
from rq import Connection, Worker


with Connection():
    qs = sys.argv[1:] or ['default']

    w = Worker(qs)
    w.work()
```


## 生产导出任务（In Master）

1. 生成Mysql数据表
2. 从解析的JSON数据中提取特定字段的数据，并做中英文映射，其中映射关系需要运营人员配置，最终存入指定数据库中。

- 输入: job_id
- 输出: None
- 逻辑流程

        @handle_error
        create_mysql_schema(job_id):
            conf = read_mongo(job_id)
            tables = parse(conf)
            for table in tables:
                insert(table)

        @handle_error
        extract_fields_to_mysql(job_id):
            source = read_mongo(job_id)
            target = extract_fields(source)
            write_mysql(target)
            write_log(succeed)

## 消费解析任务（In Slave）


## 去重器

判断要结构化的源数据是否已经存在，若存在根据配置文件检测是否要更新，需要更新返回False否则返回True；若不存在返回True。True表示源数据已经结构化，False表示源数据未结构化。

### 输入

源数据

### 输出

True | False

### 逻辑流程

```python
is_duplicates(data):
    exist = is_exist(data)  # 防重器
    if not exist:
        if check_update():  # 防重器
            return True
        else:
            return False
    else:
        return True
```

# User Interface 用户界面

## 登陆界面

## 编程接口

- 调用方式
- 输入
- 输出
- 例子


# Internel 内部实现

## Directory 代码目录结构

    λ ~/Projects/cr-clawer/clawer/structure/ dev* tree
    .
    ├── __init__.py
    ├── admin.py
    ├── migrations
    │   └── __init__.py
    ├── models.py
    ├── tests
    │   └── __init__.py
    └── views.py

    2 directories, 6 files

## Database 数据库


# Test 测试

## Testcase 1

- 依赖
- 输入
- 期望输出


# Other

- 参考文档: <https://www.toptal.com/freelance/why-design-documents-matter>

