# 目标描述

开发人员通过直接读入用户手工输入的URI数组、导入的包含URI的CSV或者TXT文件、Python或者Shell的脚本文件，通过处理，直接将包含特定的URI的JSON文件输出到MongoDB数据库中。


# 功能说明

##  数据预处理

### 输入
- 用户手工输入的URI： 字符串类型，单条字符串长度不得超过 8000个字符，输入来自网页text标签，数量没有要求。
- 导入文件： CSV文件或者TXT文件，内容包括URI，输入来自网页的导入，每次仅能输入单个文件。
- 导入脚本：Python或者Shell脚本， 脚本输入为 ？？？，输出为标准输出stdout， 输入来自网页的导入，每次仅能输入单个文件。
- 配置信息：字符串类型，单条字符串长度不得超过 8000个字符 按照"协议://域名/路径/文件?参数=参数值"， 输入来自网页text标签，每次输入一条信息，每次一个配置文件。

### 输出
- MongoDB数据库	
- 错误日志	
- 失败日志
		
### 流程(伪代码)
Master读入配置信息包括URI文件或者URI生成脚本等。若为URI文件，则逐一进行合法性校验，去重校验，保存进入MongoDB中；若为URI生成器脚本，连通其他信息（如crontab信息）保存进MongoDB中。

```
def data_preprocess( *args, **kwargs):
	# 读入配置信息包括URI文件或者URI生成脚本等
	load_input_files
	# 对读入类型进行校验
	validate_files
	if file is script:
		save file with settings to uri_genenrator_collection
	else:
		uri_lists = read file
		for uri in lists:
			validate uri
			dereplicate uri
			save uri in mongodb
	return None
```

### 失败处理

- 手工输入单条URI超过约束，将异常URI保存到错误日志中，并给出提示。
- 合法性校验失败后，将失败结果记录到错误日志中，继续处理。
- 去重校验检查出重复结果后，将重复结果记录到错误日志中，不保存并继续处理。
- 单条URI保存失败，将此条URI保存进失败日志中。并在保存后统一提示。
- URI脚本保存失败，将此文件保存进失败日志中，并在保存后给出提示。
- 输入数据不在要求范围内，直接报错。

### 前提条件

- 已经将输入进行格式类型校验。
- MongoDB数据库表已经建立。

### 限制条件

- 此函数运行在Master服务器上。



##  URI生成器调度

### 输入
- URI生成器任务标志， 可以为MongoDB的ObjectID对象$_id。

### 输出
- RQ 队列	
- 错误日志	
- 失败日志
		
### 流程(伪代码)
Master从MongoDB的URI生成器Collection中获取_id为$_id的文档，定义URI下载队列，将URI生成器函数，作为参数压入URI任务下载队列中，并返回URI下载队列对象。

```
def dispatch_uri($_id, *args, **kwargs):
	uri_object = uri_generator_mongodb.get_document_filter({_id : $_id})
	download_uri_queue = DownloadURIQueue()
	# 获取此文档的父job的优先级
	priority = uri_generator_mongodb.get_job_priority({_id : $_id})
	# priority includes (very high, high, medium, low)
	# 根据优先级插入
	if priority == 'very high':
		download_queue.enqueue('high', download_uri_task, args=[item, *args, **kwargs, at_front=True])
	else priority in (high, medium, low):
		download_queue.enqueue( priority , download_uri_task, args=[item, *args, **kwargs])
	update uri_object status
	return download_queue
```

rq 队列定义样例:

```
# rq的命名规则可以根据优先级来 high, medium, low,
# rq.enqueue()的option: timeout, result_ttl, at_front等
q = Queue('low', connection=redis_conn)
q.enqueue_call(func=count_words_at_url,
               args=('http://nvie.com',),
               timeout=30)
```

### 失败处理

- 若$_id不在URI生成器的Collection中，保存此信息到错误日志中，并给出提示。
- 若入队列没有成功，则将错误消息写入失败日志中。

### 前提条件

- 服务器将命令写入定时任务crontab中。
- URI任务生成器函数已经声明，比如 def download_uri_task(uri_generator_id).(等接口定义好了再修改)
- URI任务下载队列函数或对象已经定义，比如 class DownloadURIQueue()

### 限制条件

- 此函数运行在Master服务器上
- 建立起redis数据库


##  URI生成

### 输入
- URI生成器Collection的文档。 
- 其他配置信息（到时候在定）

### 输出
- None
		
### 流程(伪代码)

```
def download_uri_task(uri_generator_doc, other_settings):
	# 将任务生成器脚本代码即uri_generator_doc.docs保存到本地
	uri_generator_doc.write_code(local_path)
	# 创建新文件用于保存脚本执行输出的URI
	create new file to save uris producted by script
	# 开启子进程执行刚保存的代码并等待退出
	fork subprocess to run new script and wait it to quit
	URI_lists = get  uris from new file
	for uri in URI_lists:
		try:
			if not 判断uri在redis缓存中
				insert uri into URI Collection
			else:
		except Exception :
			Update error log
	Update uri_generat_log
	delete the new file
	return True
```


### 失败处理

- 如果子进程执行失败，则将失败信息写入到错误日志中，并返回False。
- 若在讲uri插入到 collection中出错，则将错误信息写入到错误日志中，并继续执行。

### 前提条件

- Slave 启动rq worker，并从URI生成rq队列取得工作任务。 

### 限制条件

- 此函数运行在Slave服务器上。
- 此函数运行时间不得多于5 min (到底多少？)



# 数据库设计

mongodb当中的数据库定义。

## Job
```
from mongoengine import *


class Job(Document):
    (STATUS_ON, STATUS_OFF) = range(1, 3)
    STATUS_CHOICES = (
        (STATUS_ON, u"启用"),
        (STATUS_OFF, u"下线"),
    )
    name = StringField(max_length=128)
    info = StringField(max_length=1024)
    customer = StringField(max_length=128, null=True)
    status = IntField(default=STATUS_ON, choices=STATUS_CHOICES)
    add_datetime = DateTimeField(default= datetime.datetime.now())
```
## CrawlerTask

```
class CrawlerTask(Document):
	(STATUS_LIVE, STATUS_PROCESS, STATUS_FAIL, STATUS_SUCCESS, STATUS_ANALYSIS_FAIL, STATUS_ANALYSIS_SUCCESS) = range(1, 7)
    STATUS_CHOICES = (
        (STATUS_LIVE, u"新增"),
        (STATUS_PROCESS, u"进行中"),
        (STATUS_FAIL, u"下载失败"),
        (STATUS_SUCCESS, u"下载成功"),
        (STATUS_ANALYSIS_FAIL, u"分析失败"),
        (STATUS_ANALYSIS_SUCCESS, u"分析成功"),
    )
    job = ReferenceField(Job,  reverse_delete_rule=CASCADE)
    task_generator = ReferenceField(CrawlerTaskGenerator, null=True)
    uri = StringField(max_length=1024)
    cookie = StringField(max_length=1024,  null=True)
    args = StringField(max_length=1024, null=True)
    status = IntField(default=STATUS_LIVE, choices=STATUS_CHOICES)
    store = StringField(max_length=512, blank=True, null=True)
    add_datetime = DateTimeField(default=datetime.datetime.now())

```


## CrawlerTaskGenerator

```

class CrawlerTaskGenerator(Document):
    (STATUS_ALPHA, STATUS_BETA, STATUS_PRODUCT, STATUS_ON, STATUS_OFF, STATUS_TEST_FAIL) = range(1, 7)
    STATUS_CHOICES = (
        (STATUS_ALPHA, u"alpha"),
        (STATUS_BETA, u"beta"),
        (STATUS_PRODUCT, u"production"),
        (STATUS_ON, u"启用"),
        (STATUS_OFF, u"下线"),
        (STATUS_TEST_FAIL, u"测试失败"),
    )
    job = ReferenceField(Job)
    code = StringField()  #python code
    cron = StringField(max_length=128)
    status = IntField(default=STATUS_ALPHA, choices=STATUS_CHOICES)
    add_datetime = DateTimeField(default=datetime.datetime.now())
```
## CrawlerGeneratorLog

```

class GrawlerGeneratorLog(Document):
    (STATUS_FAIL, STATUS_SUCCESS) = range(1, 3)
    STATUS_CHOICES = (
        (STATUS_FAIL, u"失败"),
        (STATUS_SUCCESS, u"成功"),
    )
    job = ReferenceField(Job, reverse_delete_rule=CASCADE)
    task_generator = ReferenceField(CrawlerTaskGenerator)
    status = IntField(default=0, choices=STATUS_CHOICES)
    failed_reason = StringField(max_length=10240, null=True, blank=True)
    content_bytes = IntField(default=0)
    spend_msecs = IntField(default=0) #unit is microsecond
    hostname = StringField(null=True, blank=True, max_length=16)
    add_datetime = DateTimeField(default=datetime.datetime.now())
```

## CrawlerUriLog
``` 

class CrawlerUriLog(Document):
    (STATUS_FAIL, STATUS_SUCCESS) = range(1, 3)
    STATUS_CHOICES = (
        (STATUS_FAIL, u"失败"),
        (STATUS_SUCCESS, u"成功"),
    )
    job = ReferenceField(Job,  reverse_delete_rule=CASCADE)
    task_generator = ReferenceField(CrawlerTaskGenerator, null= True)
    status = IntField(default=0, choices=STATUS_CHOICES)
    failed_reason = StringField(max_length=10240, null=True)
    content_bytes = IntField(default=0)
    spend_msecs = IntField(default=0) #unit is microsecond
    hostname = StringField(null=True, max_length=16)
    add_datetime = DateTimeField(default=datetime.datetime.now())
```

# 接口
## 接口1
- 接口说明：	
此接口是Master服务器调用，用于将传入的文件和配置信息进行校验后 存储进入MongoDB中。
	
- 调用方式	

```
	def data_preprocess(files, settings, *args, **kwargs):
		return None
```
 
## 接口2
- 接口说明	
	Master从MongoDB的CrawlerTaskGenerator中获取_id为$_id的文档，定义URI下载队列DownloadQueue，将URI生成器函数，文档作为参数压入URI任务下载队列中，并返回URI下载队列对象。
- 调用方式

```
def dispatch_uri($_id, *args, **kwargs):
	return DownloadQueue()
```

## 接口3
- 接口说明	
	Slave从URI任务生成器队列中获取任务，执行URI生成器脚本并将输出的URI结果保存进MongoDB中。
- 调用方式

```
def download_uri_task(uri_generator_doc, *args, **kwargs):
	return None
```

# 测试计划
正确性测试，容错性测试，数据库测试

 
TestCase | 测试功能 | 输入	| 预期输出
------------ | ------------------------ | --------------------------- 
1 |数据预处理 | 仅包含URI的CSV或TXT文件 | MongoDB数据库中CrawlerTask中存入文件中的URI内容。
2 | 数据预处理 | Python文件或者Shell脚本 | MongoDB数据库中CrawlerTaskGenerator中存入输入文件内容



## Testcase 1	                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        

- 测试功能	
数据预处理

- 输入	
	
仅包含URI的CSV或TXT文件
- 期望输出

MongoDB数据库中CrawlerTask中存入内容。

## Testcase 2	                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        

- 测试功能	
数据预处理

- 输入	
	
Python文件或者Shell脚本 
- 期望输出

MongoDB数据库中CrawlerTaskGenerator中存入输入文件内容




# Other

- 参考文档: <https://www.toptal.com/freelance/why-design-documents-matter>

