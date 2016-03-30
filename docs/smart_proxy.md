# 云爬虫代理抓取模块实现设计方案
## 1.0 总体设计
* **本模块需要实现的功能如下：**
	* 实现抓取proxy代理IP爬虫插件化
	* 实现代理IP的本地存储（分布式存储）
	* 实现单元测试与日志本地存储
* 布署运行
 
## 1.1 实现porxy代理IP爬取插件化

### 1.1.0 目录结构如下：
<pre>
├── logproxy.log			# 日志文件。
├── main.py					# 主文件。
├── provinceuseproxy.ini	# 配置文件。
├── proxy					# 包，装载各个插件。
│   ├── __init__.py
│   └── xici.py
└── test_proxy.py			# 测试文件。
    
logproxy.log: 主要记录插件出现了错误，数据库操作出现的错误报警等信息。
main.py: 为该模块的主文件，利用多进程，实现插件的加载与运行，并有爬取及数据库入库日志记录与单元测试。
provinceuseproxy: 配置文件说明了哪些省份的爬虫需要使用IP代理。一行为一个省份的汉语拼音名。
test_proxy.py: 对各个功能进行单元测试。
proxy/: 包，装载个各插件，即对应抓取有IP代理网址的各个爬虫。每个爬虫对网页进行分析，返回[(ip,port,province),...]。
</pre>
### 1.1.1 具体实现
<pre>
#####main.py 伪代码如下

from . proxy import *
from multiprocessing import Pool

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
</pre>
<span id='jump'></span>
### 1.1.2 目前已经找到的IP代理网址
1. 好代理 ：[http://www.haodailiip.com/guonei](http://www.haodailiip.com/guonei)
2. 西刺代理：[http://www.xicidaili.com/nn/](http://www.xicidaili.com/nn/)
3. 快代理：[http://www.kuaidaili.com/free/](http://www.kuaidaili.com/free/)
4. 有代理：[http://www.youdaili.net/Daili/guonei/4296.html](http://www.youdaili.net/Daili/guonei/4296.html)
5. 66免费代理：[http://www.66ip.cn/](http://www.66ip.cn/)
6. IPCN：[http://proxy.ipcn.org/country/](http://proxy.ipcn.org/country/)
	
## 1.2 利用MYSQL实现代理IP存储
### 1.2.0 选用MYSQL的优势
* MySQL Cluster 是MySQL 适合于分布式计算环境的高实用、可拓展、高性能、高冗余版本，其研发设计的初衷就是要满足许多行业里的最严酷应用要求，这些应用中经常要求数据库运行的可靠性要达到99.999%。MySQL Cluster允许在无共享的系统中部署“内存中”数据库集群，通过无共享体系结构，系统能够使用廉价的硬件，而且对软硬件无特殊要求。此外，由于每个组件有自己的内存和磁盘，不存在单点故障。

### 1.2.1 集群配置(分布式)
* 详情参见：MySQL集群搭建详解 [http://database.51cto.com/art/201505/475376_all.htm](http://database.51cto.com/art/201505/475376_all.htm)

### 1.2.2 数据库的设计

<table>
	<caption>数据库设计表</caption>
	<tr>
		<th>id</th>
		<th>ip</th>
		<th>port</th>
		<th>province</th>
		<th>timestamp</th>
	</tr>
	<tr>
		<td>1</td>
		<td>127.0.0.1</td>
		<td>8080</td>
		<td>Beijing</td>
		<td>1459157035</td>
	</tr>
</table>
`设置province字段是为了让每个省份的爬虫尽量使用本省份的代理，以减少爬取时间。default='else',`  
`timestamp则为了实现定时删除过时数据。`

### 1.2.3 数据库存储策略

* 存入：在ip代理网页分析时，获取得到的 http, port, province.如果没有province,则设置为'else'.
* 读取：根据参数，利用SQL选取对应省份的 ip:port 多条，可用多进程，或者使用单进程只运行一个，如果出错，则换取另外一个进行爬取。
* 清理：根据时间字段，可利用mysql提供的触发器，或者利用crontab 定时清理过时数据，在清理数据前，也可以进行先备份。

## 1.3 单元测试

### 1.3.0 具体实现
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
### 1.3.1 测试要求
* 都采用print的形式输出结果。
* 插入数据库操作时，在本地自己那一个数据库，字段设计请参见[数据库的设计](#jump)

## 1.4 布署运行
### 1.4.0 获取代理ip
* 使用 crontab 定时运行 main.py。在网页里则可以以某个触发事件运行 main.py。
* 使用 crontab 定时清理 数据库表的数据，也可以根据 timestamp 字段设定触发器定时删除无效数据。

### 1.4.1 使用代理ip
* 可以将要使用代理的省份汉语拼音写入该模块的配置文件中(privinceuseproxy).表示该些省份需要代理。
* 爬虫模块初始化时读取该文件，生成全局字典，{‘Beijing':1,'Anhui':0}.
* 爬虫模块各爬虫初始化 self.proxies = [] if dict['prov']==0 else get_proxies_from_db('prov').并在 get, post 请求后追回参数 self.reqst.get(url, param=param, `proxies=proxies` )
