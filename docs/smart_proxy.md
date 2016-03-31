# Statement of Goals 目标描述

简单说明项目目标和目标用户。

* 实现网上代理IP的抓取并整理入库。
* 为云爬虫提供获取代理的接口调用。
* 为用户提供获取json格式代理的 url api 接口。

# Functional Description 功能说明

## 功能1
* 实现抓取proxy代理IP爬虫插件化
	- 输入：源代码
	- 输出: [(ip, port, province), ...]
* 实现代理IP的本地存储
	- 输入：[(ip, port, province), ...]
	- 输出：数据库存储
* 实现脚本轮询数据库，更新数据库代理ip的可用性
	- 输入：crontab 定时执行脚本
	- 输出：自动更新数据库 flag 字段
* 实现云爬虫获取代理 api 接口调用
	- 输入：api
	- 输出：[(ip,port), ...]
* 实现 url api 接口
	- 输入：url
	- 输出：{'id_1':'ip:port', 'id_2':'ip:port', ...}
* 实现单元测试
	- 输入：test example
	- 输出：test result
- 能做什么，多快能够完成
	- 用一个app 实现整个模块。计划1-2天内完成代码编写
- 有哪些失败可能，失败后如何处理
	- 在轮询时使用多进行，数据库更新可能会出现错误，可使用单线程。
- 有哪些限制


# User Interface 用户界面

## 登陆界面




## Directory 代码目录结构
<pre>
├── view.py					# 视图文件。
|-- models.py				# 模型文件。
|-- urls.py					# 控制文件。
├── plugins					# 包，装载各个插件。
│   ├── __init__.py
│   └── xici.py
└── tests
	|__test_proxy.py		# 测试文件。
    
view.py: 为该模块的视图文件，实现视图的展现。
models.py: 数据库模型的建立，及接口的定义。
urls.py: 控制文件，定义url与响应函数的映射。
test_proxy.py: 对各个功能进行单元测试。
proxy_plugins/: 包，装载个各插件，即对应抓取有IP代理网址的各个爬虫。每个爬虫对网页进行分析，返回[(ip,port,province),...]。
</pre>

## Object Description 对象描述
###  数据库表设计
	
	id				:	1						# int, key, 自增
	ip				:	'127.0.0.1'				# char, ip地址
	port			:	'8080'					# char, 端口号
	province		:	('Beijing',1)			# enumerate, 省份名称
	flag			:	True					# Bool, 是否有效
	create_datetime	:	'2016-03-30 15:44:03'	# datatime, 添加时间
	update_datetime:	''						# datetime, 更新时间

	


### 数据库存储策略

* 存入：在ip代理网页分析时，获取得到的 http, port, province, flag.如果没有province,则设置为'other'.
* 读取：调用提供的 `get_proxy` 接口，获得代理ip列表，用多进程，或者使用单进程只运行一个代理，如果出错，则换取另外一个进行爬取。
* 清理：根据标志字段及时间字段，轮询对数据库的每一条代理进行测试，并改变flag字段，使得ProxyIp.id<=1000。


# Internel 内部实现

### mysql ORM设计
Define class `ProxyIp`
	
	# models.py
	class ProxyIp(BaseModel):
		ip = models.IPAddressField()
		port = models.IntegerField()
		province = models.CharField(max_length=20)
		flag = models.BooleanField()
		creade_datetime = models.DateTimeField(auto_now_add=True)
		update_datetime = models.DateTimeField(auto_now=True)
		
		def __unicode__(self):
			return '%s:%s' % (self.ip, self.port)
###  内部调用api封装设计
`Add` data  # 添加数据api封装，往数据库里添加数据。

	def add_data(**data):
		ip_proxy = ProxyIp(**data)
		ip_proxy.save()
example `Add data`
	
	add_data(ip='127.0.0.1',port=8080, province='Beijing', flag=True)
`Find` data # 查找数据api封装，查找指定数据。

	def find_data_by_id(id):
		ip_proxy = ProxyIp.objects.filter(id=id)
		if ip_proxy:
			return '%s:%s' % (ip_proxy.ip, ip_proxy.port)
		

example `Find data`

	find_data(id=1)	
`update` data # 更新数据api封装，更新数据库某些数据。

	def update_data(id=None, **data2):
		ip_proxy = ProxyIp.objects.filter(id=id)
		ip_proxy.update(**data2)

example `update data`

	update_data(id=1, flag=0)
		
`Delete` data # 删除数据api封装，删除数据库指定数据。
	
	def delete_data(start=None, end=None, **data):
		if start is None and end is None:
			instance = ProxyIp.objects.filter(**data).order_by(create_datetime)
		elif start is None:
			instance = ProxyIp.objects.filter(**data)[:end]
		elif end is None:
			instance = ProxyIp.objects.filter(**data)[start:]
		else:
			instance = ProxyIp.objects.filter(**data)[start:end]
		instance.delete()

example `Delete data` #删除数据库数据api封装，使得数据库中数量不超过 1000 条。1000可在设置文件中设置
	
	count = ProxyIp.object.all().count() - setting.MAX_COUNT_IP_PROXY_NUM
	if count > 0:
		delete_data(end=count, flag=False)
	
`crawer_proxy_ip.py` # 实现插件化的代理ip抓取

	from . proxy import *
	from multiprocessing import Pool
	from models import ProxyIp
	
	class Crawer(object):
		def do_with(func):
    		#每个插件返回的是代理IP地址加端口号的列表
    		try:
        		address = func.run()
    		except Error as e:
        		logging.write() #对于出现错误，写入错误日志中。
    		#对每项进行检测并放入redis中
    		for item in address:
        		if test_ok(item):
            		add_data(item)
    
		def run():
    		#得到有多少个爬虫，多少个插件。
    		proxy_list = os.listdir(os.path.join(os.getcwd(), proxy)).pop('__init__.py')
    		#使用多进程爬取
    		pool = Pool(4)
    		pool.map(self.do_with, proxy_list)
    		pool.join()
    		pool.close()
    if __name__ == '__main__':
    	crawer = Crawer()
    	crawer.run()
 
`Round data` #轮询数据库 api 封装，使得时刻更新数据库里数据。

	def test_OK(id):
		proxy = find_data(id=id)
		proxy = {'http':'http://'+proxy}
		try:
			resp = reqst.get(url, proxies=proxy)
		except:
			update_data(id, flag=False)
			return False
		if resp.status_code == 200:
			return True
		update_data(id, falg=False)
		return False
	total_count = get_proxy_num()
	pool.map(test_OK, range(1, total_count))
	
###  对外提供的调用接口
#### 云爬虫调用接口
`get_proxy` data # 接口，返回 [ip:port,...]

	def get_proxy(num=5, province=None):
		if province:
			ip_list = find_data(province=province, flag=True)
		else:
			ip_list = find_data(flag=True)
		if len(ip_list) < num:
			temp_list = find_data(province='other', flag=True)
			ip_list.extend(temp_list)
		result_list = []
		for item in ip_list:
			result_list.append('%s%s' % (item.ip, item.port))
		if len(reslut_list) <= num:
			return result_list
		else:
			return reslut_list[:num]
		
example `get_proxy`:

	self.proxy = {'http':'http://'+random.choice(get_proxy()), 'https':'https://'+random.choice(get_proxy())}
#### url api 调用接口
`urls.py` # 实现用户 url api 接口实现

	urls = patterns("start_proxy", 
    url(r"^show_ip/$", "show_ip"),	。
   	)
 `views.py` 
 
 	from . proxy import *
	from multiprocessing import Pool
	from models import ProxyIp

	def show_ip(requests, num=5):
		json_ip = dict(zip(range(1,num), get_proxy()))
    	return render('html', 'json_ip':json_ip)


# Test 测试

## 代码实现
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
## Testcase 1


- 环境相关
	* 都采用print的形式输出结果。
	* 插入数据库操作时，在本地自己那一个数据库，字段设计请参见[数据库的设计](#jump)
- 输入:...
- 期望输出:...

#布署运行
### 获取代理ip
* 使用 crontab 定时运行crawer_ip_proxy.py脚本调用抓取代理IP并测试后入库 。
* 使用 crontab 定时运行轮询脚本清理 数据库表的数据，也可以根据 timestamp 字段及 flag 字段定时删除无效数据。

### 使用代理ip
* 可以将要使用代理的省份汉语拼音写入该模块的配置文件中(privince_use_proxy).表示该些省份需要代理。
* 爬虫模块初始化时读取该文件，生成全局字典，{‘Beijing':1,'Anhui':0}.
* 爬虫模块各爬虫初始化 self.proxies = [] if dict['prov']==0 else get_proxies_from_db('prov').并在 get, post 请求后追回参数 self.reqst.get(url, param=param, `proxies=proxies` )
* 用户可以在浏览器输入 url，会获得相应的 json 格式的代理ip响应
# Other

- 参考文档: <https://www.toptal.com/freelance/why-design-documents-matter>

