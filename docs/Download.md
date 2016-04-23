# 目标描述

根据用户提供的下载器及生成器生成的url，利用rq实现分布式系统进行数据下载并存储。

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
- 无

### 输出
- rq
- 错误日志
- 警告日志

### 目标说明
- job优先级与根据主机进行分发
- 2G内存大约可以维持rq队列的数量。
	- 1024 \*1024 \* 2 / 250 = 8000 条（250=str(40)+function(120)+list(72+16)）
- 200万条/天 的数据。达到目标需要每5分钟分发多少条
	- 2000000/(24*60/5) = 7000 条
- 测试rq 入队列 7000 条需要的时间，及top监控内存状态
	- queue_lens: 7000     use_time: 9.0135269165
	- MemRegions: 82496 total, 2783M resident, 111M private, 2488 shared
	- 结论：分发时 入队所需要的时间不是很长，从mongobd里获取所需要的时间(查询1000万条数据,能够达到平均 50毫秒)，以及slaver消化的时间很长(4个bash,近10分钟)
	
### 实现策略说明
- 可以按照job优先级，(TODO:或者 主机号 进行分发。都是利用 rq 队列）。简单思路：配置设备较优的机器rq启动顺序为 rq worker high mid low
- 可以设置一次内总的分发数量，并设置单个job的分发数量。
- 用多进程进行任务分发。
- 使用回收机制。（并且设有最大回收次数）
- 有错误及警告日志。
	
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



### 流程(伪代码)
- 定义4个全局优先级队列 
- 设置多进程执行的超时时间，及超时处理方法 `dispatch_download`
- 从集合CrawlerTask中find本次job状态为启用的,并根据优先级或者主机排序，得到最大的分发数量`dispatch_use_pool`
- 多进程对每个job,根据单个job最大的分发数量，依照优先级进行rq队列的入队，`q_down_super.enqueue`
- 日志记录

```
q_down_low = Queue('down_low', connection=redis_conn)
q_down_mid = Queue('down_mid', connection=redis_conn)
q_down_high = Queue('down_high', connection=redis_conn)
q_down_super = Queue('down_super', connection=redis_conn)

def dispatch_use_pool(item)
	prioirity = item.get('priority')
	dispatch = db.DownloadSetting.findOne({'job':item.get('job')}).get('dispatch')
	max_download_times = db.DownloadSetting.findOne({'job':item.get('job')}).get('max_retry_times')
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

#####也可以只使用单进程。
def dispatch_download(*args, **kwargs):
	#设置超时时间
	timer = threading.Timer(300, force_exit)
    timer.start()
    #从集合中获取新增的，优先级较高的任务。
	if setting_by_priority:
		download_object = db.Job.find({'status:Job.STATUS_ON'}).sort({$Job.priority, -1})[:settings.MAX_TOTAL_DISPATCH_COUNT_ONCE]
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

### 前提条件
- settings.py 中设置了分发数量等

```
	 MAX_TOTAL_DISPATCH_COUNT_ONCE = 7000 #设置一次分发的数量
	 DISPATCH_USE_POOL_TIMEOUT = 300  #设置在分发过程中使用多进程的时间限制
	 DISPATCH_BY_PRIORITY = True or False #设置是只按优先级分发
	DISPATCH_BY_HOSTNAME = True or False  #设置是只按主机分发
	 Q_DOWN_SUPER_LEN = 1000 #设置优先级队列的长度，防止队列无限增长并控制内存消耗。
	 Q_DOWN_HIGH_LEN = 1000
	 Q_DOWN_MID_LEN = 2000
	 Q_DOWN_LOW_LEN = 3000
	 CODE_PATH = '/Users/princetechs3/my_code' # 配置下载器 code(python or shell)的保存路径
	 OPEN_CRAWLER_FAILED_ONLY = False and True #是否一直分发失败的任务
```
- 想着数据库已经建立

```
	Job
	CrawlerDownload
	CrawlerDownloadSetting
	...
```
### 限制条件
- 每次分发的数量不宜过大，保持在 5000-10000
- 超时时间 可以根据实际情况进行调整，设置时间暂定为 5 分钟
- 队列的长度不宜过大，每个队列的长度不宜超过 2000（估算），可以根据实际情况进行调整。

### 如何执行
- master执行分发器进行任务分发

```
  #for nginx
  */5    *    *    *    * cd /home/webapps/cr-clawer/confs/cr;./bg_cmd.sh dispatch
```
- slaver 从队列中取数据，并执行。（确保下载程序 与 salver 机器执行脚本在同一目录之下）

```
 rq worker q_down_super q_down_high q_down_mid q_down_low
 # 尽可能将它单独写成一个脚本
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
class Download(object):
	def __init__(self, task, crawler_download, crawler_download_setting):
	    self.content = None #保存下载下来的数据
		...
		pass
	def download(self):
		if self.task.uri.find('enterprise://') != -1:
			download_with_enterprise() #封装公商
			return
        if not self.crawler_download.types.is_support:
        	write_crawlerdownloadlog()
        	self.task.status == STATUS_FAIL # 这条url任务失败了。
        	return
		if self.tasl.type.language is 'python' 
			try:
				# use exec
				save python code to path
				sys.path.append(path)
				import name_module
				self.content = name_module.run(uri = self.uri)
				CrawlerDownloadData() # 将下载下来的数据下载并保存
				CrawlerDownloadLog(SUCCESS) #将下载成功日志保存
				self.task.status == STATUS_SUCCESS #下载这条url成功了。
			except Exception as e:
				CrawlerDownloadLog(FAIL) #将下载失败日志保存
				self.task.status == STATUS_FAIL # 这条url任务失败了。
		elif self.type is 'shell' :
			try:
				# use commands.getstatusoutput('sh %s %s' (filename, self.task.uri))
				save shell code to path
				result = commands.getstatusoutput('sh name.sh')
				self.content = result[1]
				... # 写日志
			except Exception as e:
				... # 写日志
		elif self.types is 'curl' :
			try:
				result = commands.getstatusoutput('%s %s' % (types, self.uri))
				self.content = result[1]
				... # 写日志
			except Exception as e:
				... # 写日志
		else:
			try:
				settings by crawler_download_settings # 通过下载设置器及 task 里的 args 对Session进行配置
				r = requests.get(self.url, headers=self.headers, proxies=self.proxies)
				self.content = r.text
				... # 写日志
			except Exception as e:
				... # 写日志
```	


```
def force_exit(download_timeout, task):
	pgid = os.getpgid(0)
	# 改变这个任务的状态为下载失败
	self.task.status == CrawlerTask.STATUS_FAIL
	CrawlerDownloadLog(FAIL) #将下载失败日志保存
	os.killpg(pgid, 9)
	os._exit(1)
	
def download_clawer_task():
	try:
		crawler_download = CrawlerDownload.objects(job=task.job)[0]
		crawler_download_setting = CrawlerDownloadSetting.objects(job=task.job)[0]
	except Exception as e:
		CrawlerDownloadLog(FAIL) #将下载失败日志保存
		self.task.status == STATUS_FAIL # 这条url任务失败了。
	down = Download(task, crawler_download, crawler_download_setting)
	#设置定时器，如果在指定时间内没有完成，则退出。
	timer = threading.Timer(crawler_download_setting.download_timeout, force_exit, [crawler_download_setting.download_timeout, task])
	timer.start()
	down.download()
	timer.cancel()
```

```
rq worker down_super down_high down_mid down_low
```


### 前提条件

- Slave 启动rq worker，并从URI生成rq队列取得工作任务。 

### 限制条件

- 此函数运行在Slave服务器上。
- 此函数运行时间不得多于5 min (到底多少？)



# 数据库设计
mysql数据库定义(能够引用mongodb?)
## CrawlerDownloadSetting
- 生产者：用户新增一个job时，设置 下载器配置 时产生。
- 消费者：下载程序

```
class CrawlerDownloadSetting(model.Models):
    job = ForeignKey(Job)
    dispatch_num = models.IntegerField(u"每次分发下载任务数", default=100)
    max_retry_times = IntegerField(default=0)
    proxy = models.TextField(blank=True, null=True)
    cookie = models.TextField(blank=True, null=True)
    prior = models.IntegerField(default=PRIOR_NORMAL)
    last_update_datetime = models.DateTimeField(auto_now_add=True, auto_now=True)
    add_datetime = models.DateTimeField(auto_now_add=True)
```

mongodb当中的数据库定义。
## CrawlerDownloadSetting（冗余mysql）
```
class CrawlerDownloadSetting(Document):
    job = ReferenceField(Job)
    dispatch_num = IntField(default=100)
    max_retry_times = IntField(default=0)
    proxy = StringField()
    cookie = StringField()
    download_timeout = IntField(default=120)
    last_update_datetime = DateTimeField(default=datetime.datetime.now())
    add_datetime = DateTimeField(default=datetime.datetime.now())
    meta = {"db_alias": "source"}
```
## CrawlerDownloadType

- 生产者：由管理员产生，配置布暑该平台支持的下载器语言
- 消费者：用户设置下载器时，types字段引用，

```
class CrawlerDownloadType(Document):
    language = StringField()
    is_support = BooleanField(default=True)
    add_datetime = DateTimeField(default=datetime.datetime.now())
    meta = {"db_alias": "source"} # 默认连接的数据库
```
## CrawlerDownload
- 生产者：由用户新增一个job时，设置下载器产生。
- 消费者：下载程序

```
class CrawlerDownload(Document):
    (STATUS_ON, STATUS_OFF) = range(0, 2)
    STATUS_CHOICES = (
        (STATUS_ON, u"启用"),
        (STATUS_OFF, u"下线")
    )
    job = ReferenceField(Job)
    # job = StringField()
    code = StringField()  # code
    types = ReferenceField(CrawlerDownloadType)
    status = IntField(default=0, choices=STATUS_CHOICES)
    add_datetime = DateTimeField(default=datetime.datetime.now())
    meta = {"db_alias": "source"} # 默认连接的数据库
```


## CrawlerDownloadData
- 生产者：下载程序
- 消费者：分析器

```
class CrawlerDownloadData(Document):
    job = ReferenceField(Job)
    downloader = ReferenceField(CrawlerDownload)
    crawlertask = ReferenceField(CrawlerTask)
    requests_headers = StringField()
    response_headers = StringField()
    requests_body = StringField()
    response_body = StringField()
    hostname = StringField()
    remote_ip = StringField()
    add_datetime = DateTimeField(default=datetime.datetime.now())
    meta = {"db_alias": "source"} # 默认连接的数据库
```

## CrawlerDispatchAlertLog
- 生产者：该日志由下载器在分发工作时队列满等警告产生
- 消费者：用户及管理员查看

```
class CrawlerDispatchAlertLog(Document):
    (ALTER, SUCCESS, FAILED) = range(1,4)
    ALTER_TYPES = (
        (ALTER, u'警告'),
        (SUCCESS, u'分发成功'),
        (FAILED, u'分发失败')
    )
    job = ReferenceField(Job,  reverse_delete_rule=CASCADE)
    types = IntField(choices=ALTER_TYPES, default=1)
    reason = StringField(max_length=10240, required=True)
    content_bytes = IntField(default=0)
    hostname = StringField(required=True, max_length=32)
    add_datetime = DateTimeField(default=datetime.datetime.now())
    meta = {"db_alias": "log"} # 默认连接的数据库
```

## CrawlerDownloadLog
- 生产者： 下载程序
- 消费者： 用户及管理员查看


```
class CrawlerDownloadLog(Document):
    (STATUS_FAIL, STATUS_SUCCESS) = range(1, 3)
    STATUS_CHOICES = (
        (STATUS_FAIL, u"失败"),
        (STATUS_SUCCESS, u"成功"),
    )
    job = ReferenceField(Job)
    # job = StringField(max_length=10240, required=True)
    task = ReferenceField(CrawlerTask)
    status = IntField(default=0, choices=STATUS_CHOICES)
    requests_size = IntField()
    response_size = IntField()
    failed_reason = StringField(max_length=10240, required=False)
    downloads_hostname = StringField(required=True, max_length=32)
    spend_time = IntField(default=0) #unit is microsecond
    add_datetime = DateTimeField(auto_now=True)
    meta = {"db_alias": "log"} # 默认连接的数据库
```

# 测试计划
正确性测试，容错性测试，数据库测试

## start
开启以下服务
- mongod   #mongodb 服务端
- sudo mysql.server start  #mysql 服务端
- redis-server #redis 服务端

## Testcase	                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
下载器及下载器设置入库
添加一个 job,crawlerdownload, crawlerdownloadtype, crawlerdownload,CrawlerTaskGenerator,CrawlerDownloadSetting。

```
		onetype = CrawlerDownloadType(language='python', is_support=True)
        onetype.save()
        job1 = Job(name='1', info='2', customer='ddd', priority=-1)
        job1.save()
        ctg1 = CrawlerTaskGenerator(job=job1, code='echo hello1', cron='* * * * *')
        ctg1.save()
        ct1 = CrawlerTask(job=job1, task_generator=ctg1, uri='http://www.baidu.com', args='i', from_host='1')
        ct1.save()
        codestr1 = open('/Users/princetechs3/my_code/code1.py','r').read()
        cd1 =CrawlerDownload(job=job1, code=codestr1, types=onetype)
        cd1.save()
        cds1 =CrawlerDownloadSetting(job=job1, proxy='122', cookie='22', dispatch_num=50)
        cds1.save()
```
可以在 test_downloaders 里找到。利用下面语句可以插入 4个job到mongodb

	python manage.py test collector.tests.test_downloader.TestMongodb.test_insert_4_jobs
在 mongodb 的source 数据库，有各个集合

	use source #使用source 数据库
	show collections #查看有哪些集合（表）
		crawler_download
		crawler_download_setting
		crawler_download_type
		crawler_task
		crawler_task_generator
		job
	db.job.find().pretty() #想看job集合有哪些文档(行)
		#会出现4个job
	###在此，log 数据库还会有任何的 集合，开始分发。			
## Testcase
分发测试

如果想要清空 rq 队列，可以先执行如下命令

		redis-cli
		flushall
		exit
输入：

		python manage.py downloader_dispatch #开如分发
输出：

		rq info  #查看任务进入的rq优先级队列。(每一个job有一个优先级)
		
		use log #使用 log数据库
		db.crawler_dispatch_alert_log.find().pretty() #可以查看对应的 任务分发状态（types）及其他
		
## TestCase
下载测试
输入：
	
	cd ~/cr-clawer/confs/dev ###进行目录，该目录下有 run_local.sh 脚本
	./run_local.sh rq_down  #启动连接 rq 队列，并自动开如下载
输出：
	
	rq info #查看任务队列，会被 slave 机器消费。
	
	use source
	show collections
		crawler_download_data #下载数据 在该集合中，可以查看其中字段
	use log
	show collections
		crawler_download_log #下载	日志在该集合中，有表示该下载的 成功，失败情况等。

## 公商数据
	
	还没有存入数据库
	但可以执行，数据格式与以前一致
		
							                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        








 

