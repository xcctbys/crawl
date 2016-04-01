# Statement of Goals 目标描述

* 从网页抓取代理ip入库保存并为开发员提供获取代理IP的接口

# Functional Description 功能说明

## 1. 获取代理ip并整理入库
- 输入：源代码
- 输出: 数据库
- 逻辑流程
	
		ip_list = crawer.run() #获取代理ip列表。[(ip:port,province), ...]
		for each in ip_list:  #测试有效性并整理入库。
			if test_OK(each):
				insert_into_database((ip:port,province))
			
- 利用单进程在测试代理ip的速度有点慢。
- 源网页结构如果出错，得调整源代码。
	
## 2. 为开发人员提供获取代理ip接口
- 输入：
- 返回：[‘ip:port’, ...]
- 逻辑流程
		
		class Proxy(object):  #面向对象
			def __init__(self):
				pass
			def get_proxy(num=5, province=None): #接口
				proxy_ip = ProxyIp() #实例ORM对象
				proxy_list = proxy_ip.object.filter(province=Nonu, is_valid=True) #过滤代理 ip 地址。
				return [item.ip_port for item in proxy_list][:num] #返回指定数量，默认为5.
			

- 响应速度快
- 如果返回为False([],None),需要重新调用（不传参）
- 每次需要获取的列表长度不应太长。用户检测返回的列表是否为空列表。


# User Interface 用户界面





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
plugins/: 包，装载个各插件，即对应抓取有IP代理网址的各个爬虫。每个爬虫对网页进行分析，返回[(ip,port,province),...]。
</pre>

## Object Description 对象描述
###  数据库表设计
	
	id				:	1						# int, key, 自增
	ip_port			:	'127.0.0.1:8080'		# char, unique, ip:port
	province		:	('Beijing',1)			# enumerate, 省份名称
	is_valid		:	True					# Bool, 是否有效
	create_datetime	:	'2016-03-30 15:44:03'	# datatime, 添加时间
	update_datetime:	''						# datetime, 更新时间

	


### 数据库存储策略

* 存入：在ip代理网页分析时，获取得到的 ip:port, province, is_valid.如果没有province,则设置为'other'.
* 读取：调用提供的 `get_proxy` 接口，获得代理ip列表，用多进程，或者使用单进程只运行一个代理，如果出错，则换取另外一个进行爬取。
* 清理：根据标志字段及时间字段，轮询对数据库的每一条代理进行测试，并改变is_valid字段，根据配置文件设置存储的最大代理ip数量,并控制数据此数量。


# Internel 内部实现

### mysql ORM设计
Define class `ProxyIp`
	
	# models.py
	class ProxyIp(BaseModel):
		ip_port = models.charField(max_length=20, unique=True)
		province = models.CharField(max_length=20)
		is_valid = models.BooleanField()
		creade_datetime = models.DateTimeField(auto_now_add=True)
		update_datetime = models.DateTimeField(auto_now=True)
		
		def __unicode__(self):
			return self.ip_port
###  抓取及轮询实现
	
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
    		for item in porxy_list:
    			self.do_with(item)
    if __name__ == '__main__':
    	crawer = Crawer()
    	crawer.run()
 
`Round data` #轮询数据库 api 封装，使得时刻更新数据库里数据。

	def change_valid(id):
		proxy = ProxyIp.object.filter(id=id) #得到对应id的代理。
		proxy = {'http':'http://'+proxy}
		try:
			resp = reqst.get(url, proxies=proxy)
		except:
			update_data(id, flag=False) #更新，置为不可用。
			return False
		if resp.status_code == 200:
			return True
		update_data(id, falg=False)
		return False
	total_count = ProxyIp.object.all().count() #获得数据库里数量
	#pool.map(test_OK, range(1, total_count))
	for id in range(1, total_count):
		change_vaild(id)
	
###  对外提供的调用接口
#### 云爬虫调用接口
实现 `get_proxy` data # 接口，返回 [ip:port,...]

<pre>
### api.py

from models import ProxyIp
calss Proxy(object):
	def __init__(self):
		self.proxy_ip = ProxyIp()
		
	def get_proxy(num=5, province=None):
		if province:
			ip_list = self.proxy_ip.object.filter(province=province, flag=True)
		else:
			ip_list = self.proxy_ip.object.filter(flag=True)
		if len(ip_list) < num:
			temp_list = self.proxy_ip.object.filter(province='other', flag=True)
			ip_list.extend(temp_list)
		result_list = []
		for item in ip_list:
			result_list.append('%s%s' % (item.ip, item.port))
		if len(reslut_list) <= num:
			return result_list
		else:
			return reslut_list[:num]
</pre>
		

	
#### url api 调用接口
`urls.py` # 实现用户 url api 接口实现

	urls = patterns("start_proxy", 
    url(r"^show_ip/$", "show_ip"),	。
   	)
 `views.py` 
 
 	from . proxy import *
	from api import Proxy

	def show_ip(requests):
		num = requests.GET.get('num')
		province = requests.GET.get('province')
		proxy = Proxy()
		json_ip = dict(zip(range(1,num), proxy.get_proxy()))
    	return render('html', 'json_ip':json_ip)


# Test 测试

## 代码实现
<pre>
#####test_proxy.py 伪代码如下。

import unittest

class TestProxy(unittest.TestCase):
	def setUp(self):
		pass
	def test_api(self):
		pass #测试接口
	def tearDown(self):
		pass
</pre>

- 环境相关
- 
		django 1.8.2
		json
		mysql-python
- 输入:django-admin manage.py test tests/test_proxy.TestProxy.test_api
- 期望输出: 返回代理ip列表。

#布署运行
### 获取代理ip
* 使用 crontab 定时运行crawer_ip_proxy.py脚本调用抓取代理IP并测试后入库 。
* 使用 crontab 定时运行轮询脚本清理 数据库表的数据，也可以根据 timestamp 字段及 flag 字段定时删除无效数据。

### 使用代理ip
* example use `get_proxy` 开发人员使用获取代理ip接口

		from api import Proxy
		porxy = Porxy()
		proxy_list = proxy.get_proxy(5,'Beijing') #['ip:port', ...]

* example use url  使用url获取json格式的代理ip
	
		input: ‘http://.../show_ip?province=Beijing&num=5'
		output: {'id_1':'127.0.0.1:8080', ...}
- 参考文档: <https://www.toptal.com/freelance/why-design-documents-matter>

