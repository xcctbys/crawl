# 目标描述

根据 企业名称及所在省份号，爬取 全国企业信息公示系统 32个省份的公商数据。利用下载器下载并提取有效json格式数据，保存至mongodb。


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
	if uri.rsplit('\')[-1].isdigit():
		download_by_registration('registrations_digit')
	else:
		download_by_enterprise_name('name') #使用模糊查询 
	```
- 检测能否跳过验证码

	```
	def download_by_registration(registrations_digit)
		uri = get_uri_from_db_by_registration_or_enterprise_name(registrations_digit) # 数据库里是否有 企业首页 的uri
		if valid_uri(uri): #如果能够直接访问，则进入爬取，跳过验证码
			download_data()
		else:
			download_data_start_with_Captcha()
	```
- 使用代理ip

	```
	from smart_proxy.api import Proxy
	def download_data(self):
		proxy = Proxy()
		if self.is_need_proxy(province):
			myproxy = proxy.get_proxy()
		else:
			myproxy = []
		self.reqst.get(url, proxy=proxy)
	```
	- 前提条件：将需要使用代理的省份存放在数据库，或者py文件里。


# 数据库设计

# 测试计划
## Testcase	非常重要                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        

							                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        








 

