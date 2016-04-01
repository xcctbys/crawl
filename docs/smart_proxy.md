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
- 源网页结构如果出错，得有测试做好这方面的检测，并调整源代码。
	
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
- 每次需要获取的列表长度不应太长。在设置文件中可设置最大库存量。用户检测返回的列表是否为空列表。


# User Interface 用户界面





## Directory 代码目录结构
<pre>
├── view.py					# 视图文件。
|-- models.py				# 模型文件。
|-- urls.py					# 控制文件。
|—— api.py 					# 提供接口的文件。
|-- script/
|   |__ run.sh				# 运行命令的脚本。
|-- management/				# 实现让django 方法自动定期执行
|   |__ __init__.py
|   |__ commands/
|	     |__ __init__.py
|        |__ roundproxyip.py 	#manage.py roundproxyip 命令
|        |__ crawerproxyip.py  #manage.py crawerproxyip 命令
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
management/: 实现让django 方法自动定期执行
script/run.sh：安全运行django命令，实现代理ip抓取与轮询的定时执行。
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
	from models import ProxyIp
	
	class Crawer(object):
		def do_with(self, func):
    		#每个插件返回的是代理IP地址加端口号的列表
    		try:
        		address = func.run()
    		except Error as e:
        		logging.write() #对于出现错误，写入错误日志中。
    		#对每项进行检测并放入redis中
    		for item in address:
        		if test_ok(item):
            		add_data(item)
    
		def run(self):
    		#得到有多少个爬虫，多少个插件。
    		proxy_list = os.listdir(os.path.join(os.getcwd(), proxy)).pop('__init__.py')
    		for item in porxy_list:
    			self.do_with(item)
    if __name__ == '__main__':
    	crawer = Crawer()
    	crawer.run()
 
`Round data` #轮询数据库 api 封装，使得时刻更新数据库里数据。
<pre>
	####round_proxy_ip.py 
from models import ProxyIp
class RoundProxy(object):
	def change_valid(self, id):
		proxy = ProxyIp()
		one_ip = proxy.object.filter(id=id) #得到对应id的代理。
		one_ip = {'http':'http://'+ one_ip}
		try:
			resp = reqst.get(url, proxies=proxy)
		except:
			update_data(id, flag=False) #更新，置为不可用。
			return False
		if resp.status_code == 200:
			return True
		update_data(id, falg=False)
		return False
	def run(self):
		total_count = proxy.object.all().count() #获得数据库里数量
		#pool.map(test_OK, range(1, total_count))
		for id in range(1, total_count):
			self.change_vaild(id)
		if total_count > setting.MAX_PROXY_NUM:
			delete_data(setting.MAX_PROXY_NUM - total_count)#删除多余无效数据
</pre>
	
#### 云爬虫调用接口实现
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
		

	
#### url api 调用接口实现
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
	def test_valid(self):
		pass #测试抓取爬虫是否有效
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
- 输入：django-admin manage.py test tests/test_proxy.TestProxy.tes_valid
- 输出：返回未经检测有效性的代理ip,并且整个过程没有出现错误。
- 输入:django-admin manage.py test tests/test_proxy.TestProxy.test_api
- 期望输出: 返回代理ip列表['ip:port', ...]。

#布署运行
### 获取代理ip与检测代理ip
* 0.将app添加到项目目录中

* 1.首先把需要自动执行的django method写成django command

		#### crawerproxyip.py #抓取命令
		from django.core.management.base import BaseCommand,commandError
		from crawer_proxy_ip import Crawer           
		class Command(BaseCommand):
    		def handle(self, *args, **options):         
        		crawer = Crawer()
    			crawer.run()
        ### roundproxyip.py  #轮询命令
        from django.core.management.base import BaseCommand,commandError    
        from round_proxy_ip import RoundProxy       
		class Command(BaseCommand):
    		def handle(self, *args, **options):
    			rounds = RoundProxy()
    			rounds.run()         
        		
* 2.将自己定义的django command添加到用sh封装并使用cron服务实现定期执行

<pre>
WORKDIR=/home/webapps/cr-clawer/smart_proxy/ #指定哪个项目
PYTHON=/home/virtualenvs/dj18/bin/python #指定哪个python
function safe_run() #安全执行，加锁，设置时间，及运行django命令 python django-admin manage.py roundproxyip
{
    file="/tmp/structure_$1.lock"

    (
        flock -xn -w 10 200 || exit 1
        cd ${WORKDIR}; ${PYTHON} manage.py $*
    ) 200>${file}
}
time safe_run  $*
</pre> 
crontab -e
	
		*/20 * * * * cd /home/webapps/cr-clawer/smart_proxy/script/ run.sh crawerproxyip
		*/10 * * * * cd /home/webapps/cr-clawer/smart_proxy/script/ run.sh roundproxyip

	

### 使用代理ip
* example use `get_proxy` 开发人员使用获取代理ip接口

		from api import Proxy
		proxy = Proxy()
		proxy_list = proxy.get_proxy(5,'Beijing') #['ip:port', ...]

* example use url  使用url获取json格式的代理ip
	
		input: ‘http://.../show_ip?province=Beijing&num=5'
		output: {'id_1':'127.0.0.1:8080', ...}

## 已经找到有免费代理的网址
1. 好代理 ：[http://www.haodailiip.com/guonei](http://www.haodailiip.com/guonei)
2. 西刺代理：[http://www.xicidaili.com/nn/](http://www.xicidaili.com/nn/)
3. 快代理：[http://www.kuaidaili.com/free/](http://www.kuaidaili.com/free/)
4. 有代理：[http://www.youdaili.net/Daili/guonei/4296.html](http://www.youdaili.net/Daili/guonei/4296.html)
5. 66免费代理：[http://www.66ip.cn/](http://www.66ip.cn/)
6. IPCN：[http://proxy.ipcn.org/country/](http://proxy.ipcn.org/country/)


