# 目标描述

根据 企业名称及所在省份号，爬取 全国企业信息公示系统 32个省份的工商数据。利用下载器下载并提取有效json格式数据，保存至mongodb。


##### 目标说明
- 能够直接在全国企业信息系统里`只直接输入企业名称`进行数据下载，从而实现`模糊查询`
- 能够存储某些企业的`首页网址`，下次直接访问该网址获得更新数据，从而`跳过验证码识别`。
- 能够配置某些省份`使不使用代理`,从而`防止ip被封`。

# 过程与功能说明

##  数据下载

### 输入
- uri=enterprise://省份/企业名称/注册号。（在浩格云信上找不到注册号的以**********号代替）

### 输出
- {'注册号':{json data}} >> mongodb source CrawlerDownloadData
- 日志 >> mongodb log CrawlerDownloadLog

#### 前提条件
- 根据客户提供的 企业名称号 到 浩格云信等平台上找到注册号。并将 省份，企业名称，注册号 存入mysql,注册号没有找到的以 ******** 代替。以便让生成器生成类似 `enterprise://省份/企业名称/注册号`格式的uri让下载器下载。
		
### 流程(伪代码)

- 检测是否有注册号(数字)

```
	if register_no == '***':
		cls.run('name') #使用模糊查询 
	else:
		cls.run('registrations_digit')
```

- 检测能否跳过验证码

```
	def download_by_registration(registrations_digit)
		uri_args = get_uri_arg_from_db_by_registration_or_enterprise_name(registrations_digit) # 数据库里是否有 企业首页 的uri.args,{}.
		if valid_uri(uri+uri.args): #如果能够直接访问，则进入爬取，跳过验证码
			download_data()
		else:
			download_data_start_with_Captcha()
```

- 使用代理ip

```

		from smart_proxy.api import Proxy, UseProxy

		useproxy = UseProxy()
		is_use_proxy = useproxy.get_province_is_use_proxy(province='beijing') # True or False
		if not is_use_proxy:
			# 北京不使用代理
			self.proxies = []
		else:
			# 北京省份想使用代理
			proxy = Proxy()
			proxy_list = proxy.get_proxy(5,'Beijing') #['ip:port', ...]
```
	
- 前提条件：将需要使用代理的省份存放在数据库。

- 各省份下载说明及代码规范
	- 初始化变量
	- 破解验证码，拿取相关信息
	- 根据相关信息，爬取工商公示信息
	- 根据相关信息，爬取企业公示信息
	- 根据相关信息，爬取其他部门公示信息
	- 根据相关信息，爬取司法协助部门公示信息
	- 数据存储与日志存储
	
<pre>
# 初始化信息
class InitInfo(object):
	def __init__(self, *args, **kwargs):
		pass
# 破解验证码类
class CrackCheckcode(object):
	pass
# 自己的爬取类，继承爬取类
class MyCrawler(Crawler):
	def __init__(self, *args, **kwargs):
		useproxy = UseProxy()
		is_use_proxy = useproxy.get_province_is_use_proxy(province='beijing') # True or False
		if not is_use_proxy:
			# 北京不使用代理
			self.proxies = []
		else:
			# 北京省份想使用代理
			proxy = Proxy()
			proxy_list = proxy.get_proxy(5,'Beijing') #['ip:port', ...]
		self.reqst = requests.Session()
	def crawl_page_by_url(self, url):
		"""根据url直接爬取页面
		"""
		pass
	def crawl_page_by_url_post(self, url, data):
		""" 根据url和post数据爬取页面
		"""
		pass
# 自己的解析类，继承解析类
class MyParser(Parser):
	def __init__(self, *args, **kwargs):
		pass
# 工商公示信息
class IndustrialPubliction(object):
	def __init__(self, *args, **kwargs):
		pass
	# 登记信息
	def get_regirster_info(self, *args, **kwargs):
		pass
	# 备案信息
	def get_record_info(self, *args, **kwargs):
		pass
	# 动产抵押登记信息
	def get_movable_property_register_info(self, *args, **kwargs):
		pass
	# 股权出质登记信息
	def get_stock_equity_pledge_info(self, *args, **kwargs):
		pass
	# 行政处罚信息
	def get_administrative_penalty_info(self, *args, **kwargs):
		pass
	# 经营异常信息
	def get_abnormal_operation_info(self, *args, **kwargs):
		pass
	# 严重违法信息
	def get_serious_illegal_info(self, *args, **kwargs):
		pass
	# 抽查检查信息
	def get_spot_check_info(self, *args, **kwargs):
		pass
	# 运行逻辑
	def run(self, *args, **kwargs):
		pass

# 企业公示信息
class EnterprisePubliction(object):
	def __init__(self, *args, **kwargs):
		pass
	# 企业年报
	def get_corporate_annual_reports_info(self, *args, **kwargs):
		pass
	# 股东及出资信息
	def get_shareholder_contribution_info(self, *args, **kwargs):
		pass
	# 股权变更信息
	def get_equity_change_info(self, *args, **kwargs):
		pass
	# 行政许可信息
	def get_administrative_licensing_info(self, *args, **kwargs):
		pass
	# 知识产权出质登记信息
	def get_intellectual_property_rights_pledge_registration_info(self, *args, **kwargs):
		pass
	# 行政处罚信息
	def get_administrative_punishment_info(self, *args, **kwargs):
		pass
	# 运行逻辑
	def run(self, *args, **kwargs):
		pass
		
# 其他部门公示信息
class OtherDepartmentsPubliction(object):
	def __init__(self, *args, **kwargs):
		pass
	# 行政许可信息
	def get_administrative_licensing_info(self, *args, **kwargs):
		pass
	# 行政处罚信息
	def get_administrative_punishment_info(self, *args, **kwargs):
		pass
	# 运行逻辑
	def run(self, *args, **kwargs):
		pass
		
# 司法协助公示信息
class JudicialAssistancePubliction(object):
	def __init__(self, *args, **kwargs):
		pass
	# 股权冻结信息
	def get_equity_freeze_info(self, *args, **kwargs):
		pass
	# 股东变更信息
	def get_shareholders_change_info(self, *args, **kwargs):
		pass
	# 运行逻辑
	def run(self, *args, **kwargs):
		pass
				
</pre>

# 数据库设计

# 测试计划
## Testcase	非常重要                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        

							                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        








 

