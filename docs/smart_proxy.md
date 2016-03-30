# 云爬虫代理抓取模块实现设计方案
## 1.0 总体设计
* **本模块需要实现的功能如下：**
	* 实现抓取proxy代理IP爬虫插件化
	* 实现代理IP的本地存储
	* 实现单元测试与日志本地存储
* 布署运行

## 1.1 模块目录结构如下：
<pre>
├── logproxy.log			# 日志文件。
├── view.py					# 视图文件。
|-- models.py				# 模型文件。
|-- urls.py					# 控制文件。
├── province_use_proxy.ini	# 配置文件。
├── proxy_plugins			# 包，装载各个插件。
│   ├── __init__.py
│   └── xici.py
└── test_proxy.py			# 测试文件。
    
logproxy.log: 主要记录插件出现了错误，数据库操作出现的错误报警等信息。
view.py: 为该模块的视图文件，实现视图的展现。
models.py: 数据库模型的建立，及接口的定义。
urls.py: 控制文件，定义url与响应函数的映射。
province_use_proxy: 配置文件说明了哪些省份的爬虫需要使用IP代理。一行为一个省份的汉语拼音名。
test_proxy.py: 对各个功能进行单元测试。
proxy_plugins/: 包，装载个各插件，即对应抓取有IP代理网址的各个爬虫。每个爬虫对网页进行分析，返回[(ip,port,province),...]。
</pre>

## 1.2 数据库设计
### 1.2.0 数据库表设计
	
	id			:	1						# int, key, 自增
	ip			:	'127.0.0.1'				# char, ip地址
	port		:	'8080'					# char, 端口号
	province	:	'Beijing'				# char, 省份名称
	flag		:	True					# Bool, 是否有效
	timestamp	:	'2016-03-30 15:44:03'	# datatime, 添加时间
### 1.2.1 mysql ORM设计
Define class `ProxyIp`
	
	# models.py
	class ProxyIp(baseModel):
		ip = models.IPAddressField()
		port = models.IntegerField()
		province = models.CharField(max_length=20)
		flag = models.BooleanField()
		timestamp = models.DateTimeField(auto_now_add=True)
		
		def __unicode__(self):
			return '%s:%s' % (self.ip, self.port)
### 1.2.2 接口设计
`Add` data  # 接口，往数据库里添加数据。

	def add_data(**data):
		ip_proxy = ProxyIp(**data)
		ip_proxy.save()
example `Add data`
	
	add_data(ip='127.0.0.1',port=8080, province='Beijing', flag=True)
`Find` data # 接口，查找指定数据。

	def find_data(start=None, end=None, **data):
		ip_proxy = ProxyIp.objects.filter(**data)
		if start is None and end is None:
			return ip_proxy
		elif start is None:
			return ip_proxy[:end]
		elif end is None:
			return ip_proxy[start:]
		else:
			return ip_proxy[start:end]

example `Find data`

	find_data(id=1)
	find_data(1,2, flag=Flase)
	
`update` data # 接口，更新数据库某些数据。

	def update_data(id=None, **data2):
		ip_proxy = ProxyIp.objects.filter(**data1)
		ip_proxy.update(**data2)

example `update data`

	update_data(id=1, flag=0)
		
`Delete` data # 接口，删除数据库指定数据。
	
	def delete_data(start=None, end=None, **data):
		if start is None and end is None:
			instance = ProxyIp.objects.filter(**data)
		elif start is None:
			instance = ProxyIp.objects.filter(**data)[:end]
		elif end is None:
			instance = ProxyIp.objects.filter(**data)[start:]
		else:
			instance = ProxyIp.objects.filter(**data)[start:end]
		instance.delete()

example `Delete data`
	
	delete_data(end=10, flag=False)
 

`get_proxy` data # 接口，返回 [ip:port,...]

	def get_proxy(province=None):
		if province:
			ip_list = find_data(province=province, flag=True)
		else:
			ip_list = find_data(flag=True)
		if len(ip_list) < 5:
			temp_list = find_data(province='other', flag=True)
			ip_list.extend(temp_list)
		result_list = []
		for item in ip_list:
			result_list.append('%s%s' % (item.ip, item.port))
		return result_list
		
example `get_proxy`:

	self.proxy = {'http':'http://'+random.choice(get_proxy()), 'https':'https://'+random.choice(get_proxy())}

### 1.2.3 数据库存储策略
#### 输入：各个插件爬虫的源代码
#### 输出：可用的代理IP

* 存入：在ip代理网页分析时，获取得到的 http, port, province, flag.如果没有province,则设置为'other'.
* 读取：调用提供的 `get_proxy` 接口，获得代理ip列表，用多进程，或者使用单进程只运行一个代理，如果出错，则换取另外一个进行爬取。
* 清理：根据标志字段及时间字段，轮询对数据库的每一条代理进行测试，并改变flag字段，使得ProxyIp.id<=10000。
	

## 1.3 控制器设计 urls.py

	urls = patterns("start_proxy", 
    url(r"^begin/$", "main"),	# 开始生成代理到数据库
    url(r"^use_setting/$", 'use_settings'), #用户自定义使用哪些省份代理
    url(r'^add_plugins/$', 'add_plugins'),  #用户添加代理爬虫
    url(r"^show_data/$", "show_data"), #显示到页面有 多少代理
    url(r"^show_choice_data/$", "show_choice_data"), #显示到页面有多少过滤后的代理。
	)
## 1.4 视图设计 view.py

	from . proxy import *
	from multiprocessing import Pool
	from models import ProxyIp

	def do_with(func):
    	#每个插件返回的是代理IP地址加端口号的列表
    	try:
        	address = func.run()
    	except Error as e:
        	logging.write() #对于出现错误，写入错误日志中。
    	#对每项进行检测并放入redis中
    	for item in address:
        	if test_ok(item):
            	insert_mysql(item)
    
	def main():
    	#得到有多少个爬虫，多少个插件。
    	proxy_list = os.listdir(os.path.join(os.getcwd(), proxy)).pop('__init__.py')
    	#使用多进程爬取
    	pool = Pool(4)
    	pool.map(do_with, proxy_list)
    	pool.join()
    	pool.close()
    
    def use_setting():
    	read choices from html
    	write province_use_proxy file
    	generetor a dict in init
    	return the dict
    
    def add_plugins():
    	pass #添加文件到 proxy_plugins 文件目录下。
    	
    def add_data(**data):
		ip_proxy = ProxyIp(**data)
		ip_proxy.save()
		return None
		
	def show_data():
		pass # 展示数据库的可用代理ip列表。
	
	def show_choice_data(,province):
		pass #展示指定省份或者其他信息的代理ip列表。
		
## 1.5 单元测试

### 1.5.0 具体实现
<pre>
#####test_proxy.py 伪代码如下。

import unittest

class TestProxy(unittest.TestCase):
	def setUp(self):
		pass
	def test_get(self):
		pass #测试每个插件爬虫是否可以访问网页。
	def test_parse(self):
		pass #测试每个插件返回的列表是否格式正确。
	def test_valid(self):
		pass #测试ip地址的有效率
	def test_insert(self):
		pass #测试是否可以入库
	def tearDown(self):
		pass
</pre>
### 1.5.1 测试要求
* 都采用print的形式输出结果。
* 插入数据库操作时，在本地自己那一个数据库，字段设计请参见[数据库的设计](#jump)

## 1.6 布署运行
### 1.6.0 获取代理ip
* 使用 crontab 定时运行 view.py。在网页里则可以以某个触发事件运行 view.py。
* 使用 crontab 定时清理 数据库表的数据，也可以根据 timestamp 字段及 flag 字段定时删除无效数据。

### 1.6.1 使用代理ip
* 可以将要使用代理的省份汉语拼音写入该模块的配置文件中(privince_use_proxy).表示该些省份需要代理。
* 爬虫模块初始化时读取该文件，生成全局字典，{‘Beijing':1,'Anhui':0}.
* 爬虫模块各爬虫初始化 self.proxies = [] if dict['prov']==0 else get_proxies_from_db('prov').并在 get, post 请求后追回参数 self.reqst.get(url, param=param, `proxies=proxies` )

	