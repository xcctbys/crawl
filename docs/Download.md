# 目标描述

根据用户提供的下载器及生成器生成的url，利用分布式系统进行数据下载并存储。


# 过程与功能说明

##  Master将下载器及下载器设置入库

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
		return db.collections.findOne()
	else:
		save log in mongodb
		report error
	return None
```

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
- 警告日志

### 相关说明
- 2G内存大约可以维持rq队列的数量。
	- 1024 \*1024 \* 2 / 250 = 8000 条（250=str(40)+function(120)+list(72+16)）
- 200万条/天 的数据。达到目标需要每5分钟分发多少条
	- 2000000/(24*60/5) = 7000 条
- 测试rq 入队列 7000 条需要的时间，及top监控内存状态
	- queue_lens: 7000     use_time: 9.0135269165
	- MemRegions: 82496 total, 2783M resident, 111M private, 2488 shared
	- 分发时 入队所需要的时间不是很长，从mongobd里获取所需要的时间(查询1000万条数据,能够达到平均 50毫秒)，以及slaver消化的时间很长(4个bash,近10分钟)
	
将优先级分成-1, 0，1，2，3，4，5共7个优先级，-1, 为最高优先级，5为最低优先级；默认优先级为5。
共设4个优先级通道，队列头优先级高，队列尾优先级低。

down_super	
<===============< -1

down_high 	
0 <=============< 1

down_mid	
2 <=============< 3

down_low		
4 <=============< 5

启动worker按如下格式启动，workers将会顺序从给定的队列中无限循环读入jobs，而且会按照down_super down_high down_mid down_low顺序。

启动的worker的命令为：

```
rq worker down_super down_high down_mid down_low
```



### 流程(伪代码)
可以按照job优先级，或者 主机号 进行分发。（都是利用 rq 队列）。简单思路：配置设备较优的机器rq启动顺序为 rq worker high mid low （该启动顺序是否可以利用socket 或者。。让主机进行分发）
可以设置一次内总的分发数量，可以设置单个job的分发数量。
用多进程进行任务分发。
有回收机制。（并且设有最大回收次数）
有错误及警告日志。

```
q_down_low = Queue('down_low', connection=redis_conn)
q_down_mid = Queue('down_mid', connection=redis_conn)
q_down_high = Queue('down_high', connection=redis_conn)
q_down_super = Queue('down_super', connection=redis_conn)

def dispatch_use_pool(item)
	prioirity = item.get('priority')
	dispatch = db.DownloadSetting.findOne({'belog_job_id':item.get('belog_job_id')}).get('dispatch')
	max_download_times = db.DownloadSetting.findOne({'belog_job_id':item.get('belog_job_id')}).get('max_try_download_times')
	if priority == -1:
		if len(q_down_super) + dispatch > settings.QDOWNSUPERLEN:
			write_alter_log		
		down_tasks = db.ClawerTask.find({'status':'ClawerTask.STATUS_LIVE'})[:dispatch]
		sometimes = db.ClawerTask.find({'status':'ClawerTask.FAIL', 'download_times':{'$lt': max_download_times}})[:dispatch]
		if setting_by_hostname:
			down_task.sort({'$ClawerTask.host_name', -1})
		for task in down_task:
			try:
				q_down_super.enqueue(queue_name, download_clawer_task, args=[item.uri, item.jobs.id] )
				update time.status = STATUS_DISPATCH
				write_success_dispatch_log
			except:
				write_fail_dispatch_log
		update item.status == STATUS_START
		update item.download_times += 1
	elif priority == -2:
		pass
		...
	return


def dispatch_download(*args, **kwargs):
	#设置超时时间
	timer = threading.Timer(300, force_exit)
    timer.start()
    #从集合中获取新增的，优先级较高的任务。
	if setting_by_priority:
		download_object = db.Job.find({'status:Job.STATUS_ON'}).sort({$Job.priority, -1})[:settings.max_total_dispatch_count_once]
	elif setting_by_priority and setting_by_host:
		download_object = db.Job.find({'status:Job.STATUS_ON'}).sort({$Job.priority, -1})[:settings.max_total_dispatch_count_once]
		download_object = download_object.sort({'$Job.hostname', -1})
	else:
		download_object = db.Job.find({'status:Job.STATUS_ON'}).sort({$Job.hostname, -1})[:settings.max_total_dispatch_count_once]	
	download_queue = DownloadQueue()
	pool.map(dispatch_use_pool, download_object)
	pool.close()
	pool.join()
	return download_queue
	
	#退出函数	
def force_exit():
    pgid = os.getpgid(0)
    if pool is not None:
        pool.terminate()
    os.killpg(pgid, 9)
    os._exit(1)
```

download_clawer_task

```
def download_clawer_task():
	if download_type is python:
		setting downloader by cralwerdownloadsettings
	try:
		downloader.download()	
	except:
		fail_log
		sentry.except()
	else:
		try:
			import subprocess
			p = subprocess.Popen('ls', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			retval = p.wait()
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
q.enqueue(func=count_words_at_url,
               args=('http://nvie.com',))
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
- 下载数据Mongodb,
- 错误日志	
- 下载日志
				
### 流程(伪代码)

```
rq worker down_super down_high down_mid down_low
```


### 前提条件

- Slave 启动rq worker，并从URI生成rq队列取得工作任务。 

### 限制条件

- 此函数运行在Slave服务器上。
- 此函数运行时间不得多于5 min (到底多少？)



# 数据库设计

mongodb当中的数据库定义。
## CrawlerDownload

```
class CrawlerDownload(Document):
	 (STATUS_ON, STATUS_OFF) = range(1, 3)
     STATUS_CHOICES = (
		(STATUS_ON, u"启用"),
    	(STATUS_OFF, u"下线"),
    )
	job = ReferenceField(Job)
    code = StringField()  #python code
    status = IntField(default=0, choices=STATUS_CHOICES)
    add_datetime = DateTimeField(default=datetime.datetime.now())
    meta = {"db_alias": "source"} # 默认连接的数据库
```
## CrawlerDownloadSetting
```
class CrawlerDownloadSetting(Document):
    (PRIOR_NORMAL, PRIOR_URGENCY, PRIOR_FOREIGN) = range(0, 3)
    PRIOR_CHOICES = (
        (PRIOR_NORMAL, "normal"),
        (PRIOR_URGENCY, "urgency"),
        (PRIOR_FOREIGN, "foreign"),
    )
    (TYPE_PYTHON, TYPE_SHELL, TYPE_CURL, TYPE_WGET) = range(0, 4)
    TYPES_CHOICES = (
    	(TYPE_PYTHON, 'python'),
    	(TYPE_SHELL, 'shell'),
    	(TYPE_CRUL, 'curl'),
    	(TYPE_WGET, 'wget'),
    )
    job = ReferenceField(Job)
    dispatch = IntField(u"每次分发下载任务数", default=100)
    download_types = IntField(choices=TYPE_CHOICES, default=TYPE_PYTHON, null=False)
    download_code = TextField(blank=True, null=True)
    proxy = TextField(blank=True, null=True)
    cookie = TextField(blank=True, null=True)
    download_engine = StringField(max_length=16, default=Download.ENGINE_REQUESTS, choices=Download.ENGINE_CHOICES)
    download_js = TextField(blank=True, null=True)
    prior = IntField(choices=PRIOR_CHOICES, default=PRIOR_NORMAL)
    last_update_datetime = DateTimeField(auto_now=True)
    report_mails = StringField(blank=True, null=True, max_length=256)
    add_datetime = DateTimeField(auto_now_add=True)
	meta = {"db_alias": "source"} # 默认连接的数据库
```

## DownloadData
```
class DownloadData(Document):
	job = ReferenceField(Job)
	downloader = ReferenceField(CrawlerDownload)
	crawler_generator = ReferenceField(CrawlerTaskGenerator)
	origin_url = StringField()
	origin_data = StringField()
	requests_headers = StringField()
	response_headers = StringField()
	download_host_name = StringField()
	other_party_ip = StringField()
	add_datetime = DateTimeField(default=datetime.datetime.now())
	meta = {"db_alias": "source"} # 默认连接的数据库
```

## CrawlerDownloadLog
```
class CrawlerDownloadLog(Document):
    (STATUS_FAIL, STATUS_SUCCESS) = range(1, 3)
   	STATUS_CHOICES = (
        (STATUS_FAIL, u"失败"),
        (STATUS_SUCCESS, u"成功"),
    )
    job = ReferenceField(Job)
    belog_task_id = ReferenceField(ClawerTask)
    status = IntField(default=0, choices=STATUS_CHOICES)
    requests_size = IntField()
    response_size = IntField()
    failed_reason = StringField(max_length=10240, null=True, blank=True)
    download_host_name = StringField(null=True, blank=True, max_length=16)
    spend_time = IntField(default=0) #unit is microsecond
    add_datetime = DateTimeField(auto_now=True)
    meta = {"db_alias": "log"} # 默认连接的数据库
```

## CrawlerDownloadErrorLog
``` 
class CrawlerDownloadErrorLog(Document):
    job = ReferenceField(Job,  reverse_delete_rule=CASCADE)
    failed_reason = StringField(max_length=10240, null=True)
    content_bytes = IntField(default=0)
    hostname = StringField(null=True, max_length=16)
    add_datetime = DateTimeField(default=datetime.datetime.now())
    meta = {"db_alias": "log"} # 默认连接的数据库
```
## CrawlerDownloadAlertLog
``` 
class CrawlerDownloadAlertLog(Document):
    job = ReferenceField(Job,  reverse_delete_rule=CASCADE)
    type = StringField(max_length=128)
    reason = StringField(max_length=10240, null=True)
    content_bytes = IntField(default=0)
    hostname = StringField(null=True, max_length=16)
    add_datetime = DateTimeField(default=datetime.datetime.now())
    meta = {"db_alias": "log"} # 默认连接的数据库
```

# 测试计划
正确性测试，容错性测试，数据库测试

 

## Testcase 1	                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
下载器及下载器设置入库

	def test_data_preprocess():
		code, settings = readfile()
		try:
			valid_code
			valid_settings
		except:
			write fail_log
		write success_log
	tail log

## Testcase 2
分发测试
	
	def test_dispatch():
		try:
			conn db
		except:
			write error log
		try:
			db.collection.find({args})[:num_dispatch]
		except:
			write error log
		try:
			len(q_down_super)
			q_down_super.enqueue()
			...
		except:
			write log
		write log
				                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        








 

