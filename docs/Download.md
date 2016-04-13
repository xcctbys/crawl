# 目标描述

根据用户提供的下载器及生成器生成的url，利用分布式系统进行数据下载并存储。


# 过程与功能说明

##  Master将下载器入库

### 输入
- 下载器
- 配置信息(分发数量...)

### 输出
- MongoDB数据库	
- 错误日志	
		
### 流程(伪代码)
Master读入配置信息 与 下载器，进行校验及语法检测，标识该下载器的jobID,一同保存进入MongoDB对应表中；如果校验失败或者语法错误，不存入并且输出到错误日志。

```
def data_preprocess( *args, **kwargs):
	# 读入配置信息包括与生成脚本等
	load_input_files
	validate_settings
	validate_files_with_settings
	if file is valid:
		save file with settings to mongodb
	else:
		save log in mongodb
		report error
	return None
```

### 失败处理



### 前提条件

- MongoDB数据库表已经建立。

### 限制条件

- 此函数运行在Master服务器上。



## 下载器调度分发

### 输入
- dispatch_count
- url[:dispatched] in mongodb collection

### 输出
- rq
- 错误日志

### 相关说明
- 2G内存大约可以维持rq队列的数量。
	- 1024 \*1024 \* 2 / 250 = 8000 条（250=str(40)+function(120)+list(72+16)）
- 200万条/天 的数据。达到目标需要每5分钟分发多少条
	- 2000000/(24*60/5) = 7000 条
- 测试rq 入队列 7000 条需要的时间，及top监控内存状态
	- queue_lens: 7000     use_time: 9.0135269165
	- MemRegions: 82496 total, 2783M resident, 111M private, 2488 shared
	- 分发时 入队所需要的时间不是很长，从mongobd里获取所需要的时间，以及slaver消化的时间很长(4个bash,近10分钟)


### 流程(伪代码)

```
def dispatch_download(*args, **kwargs):

	#从集合中获取新增的，优先级较高的任务。
	download_object = db.Job.find({'status:Job.STATUS_ON'}).sort({$Job.priority, -1})[:max_total_dispatch_count_once]	
	download_queue = DownloadQueue()
	# priority includes range（-1，6)
	# 根据优先级插入
	for item in download_object:
		prioirity = item.get('priority')
		dispatch = db.DownloadSetting.findOne({'belog_job_id':item.get('belog_job_id')}).get('dispatch')
		max_download_times = db.DownloadSetting.findOne({'belog_job_id':item.get('belog_job_id')}).get('max_download_times')
		if priority == -1:
			down_tasks = db.ClawerTask.find({'status':'ClawerTask.STATUS_LIVE'})[:dispatch]
			sometimes = db.ClawerTask.find({'status':'ClawerTask.FAIL', 'download_times':{'$lt': max_download_times}})[:dispatch]
			for task in down_task:
				try:
					download_queue.enqueue(queue_name, download_clawer_task, args=[item.uri, item.jobs.id] )
				except:
					write_log
			update item.status == START
			update item.download_times += 1
		elif priority == -2:
			pass
		...
		
	return download_queue


```

download_clawer_task

```
def download_clawer_task():
	setting downloader
	try:
		downloader.download()
	except:
		fail_log
		sentry.except()
	success_log

```

rq 队列定义样例:

```
# rq的命名规则可以根据优先级来 high, medium, low,
# rq.enqueue()的option: timeout, result_ttl, at_front等
q = Queue('low', connection=redis_conn)
q.enqueue_call(func=count_words_at_url,
               args=('http://nvie.com',),
               timeout=30)
# 同时rq 队列是没有长度限制的。
```
执行分发器

```
  for root	
  */5    *    *    *    * cd /home/webapps/cr-clawer/confs/cr;./bg_cmd.sh dispatch
```

##  Slave下载数据

### 输入
- 无

### 输出
- 下载数据Mongodb, json	
- 错误日志	
- 下载日志
				
### 流程(伪代码)

```
connect rq
```


### 前提条件

- Slave 启动rq worker，并从URI生成rq队列取得工作任务。 

### 限制条件

- 此函数运行在Slave服务器上。
- 此函数运行时间不得多于5 min (到底多少？)



# 数据库设计

mongodb当中的数据库定义。
## DownloadTask

```
class DownloadTask(Document):
	(STATUS_FAIL, STATUS_SUCCESS) = range(1, 3)
   	 STATUS_CHOICES = (
        (STATUS_FAIL, u"失败"),
        (STATUS_SUCCESS, u"成功"),
    )
	belog_job_id = ReferenceField(Job)
    code = StringField()  #python code
    status = IntField()
    add_datetime = DateTimeField(default=datetime.datetime.now())
```

## DownloadData
```
class DownloadData(Document):
	belog_job_id = ReferenceField(Job)
	downloadtor_id = ReferenceField(DownloadTask)
	json_data = StringField()
	host_name = StringField()
```

## DownloadLog
```
class DownloadLog(Document):
    (STATUS_ON, STATUS_OFF) = range(1, 3)
     STATUS_CHOICES = (
		(STATUS_ON, u"启用"),
    	(STATUS_OFF, u"下线"),
    )
    belog_job_id = ReferenceField(Job)
    belog_task_id = ReferenceField(ClawerTask)
    status = IntField(default=0, choices=STATUS_CHOICES)
    failed_reason = StringField(max_length=10240, null=True, blank=True)
    hostname = models.CharField(null=True, blank=True, max_length=16)
    spend_time = IntField(default=0) #unit is microsecond
    add_datetime = DateTimeField(auto_now=True)
```
## DownloadSetting

```
class DownloadSetting(Document):
    (PRIOR_NORMAL, PRIOR_URGENCY, PRIOR_FOREIGN) = range(0, 3)
    PRIOR_CHOICES = (
        (PRIOR_NORMAL, "normal"),
        (PRIOR_URGENCY, "urgency"),
        (PRIOR_FOREIGN, "foreign"),
    )
    dispatch = IntField(u"每次分发下载任务数", default=100)
    download_code = TextField(blank=True, null=True)
    proxy = TextField(blank=True, null=True)
    cookie = TextField(blank=True, null=True)
    download_engine = StringField(max_length=16, default=Download.ENGINE_REQUESTS, choices=Download.ENGINE_CHOICES)
    download_js = TextField(blank=True, null=True)
    prior = IntField(default=PRIOR_NORMAL)
    last_update_datetime = DateTimeField(auto_now=True)
    report_mails = StringField(blank=True, null=True, max_length=256)
    add_datetime = DateTimeField(auto_now_add=True)

```


# 接口
## 接口1
- 接口说明：	
此接口是Master服务器调用，用于将传入的下载器进行校验后 存储进入MongoDB中。
	
- 调用方式	

```
	
```

# 测试计划
正确性测试，容错性测试，数据库测试

 

## Testcase 1	                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        



## Testcase 2	                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        








 

