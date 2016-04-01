# Statement of Goals 目标描述

程序通过直接读入用户手工输入的URI数组、导入的包含URI的CSV或者TXT文件、Python或者Shell的脚本文件，通过处理，直接将包含特定的URI的JSON文件输出到MongoDB数据库中。

# Functional Description 功能说明

##  保存配置
此函数运行在Master服务器上。

### 输入
- 用户手工输入的URI： 字符串类型，单条字符串长度不得超过 8000个字符，输入来自网页text标签，数量没有要求。
- 导入文件： CSV文件或者TXT文件，内容包括URI，输入来自网页的导入，每次仅能输入单个文件。
- 导入脚本：Python或者Shell脚本， 脚本输入为 ？？？，输出为标准输出stdout， 输入来自网页的导入，每次仅能输入单个文件。
- 配置信息：字符串类型，单条字符串长度不得超过 8000个字符 按照"协议://域名/路径/文件?参数=参数值"， 输入来自网页text标签，每次输入一条信息，每次一个配置文件。

### 输出
- MongoDB数据库	
- 错误日志	
- 失败日志
		
### 流程
Master读入配置信息包括URI文件或者URI生成脚本等。若为URI文件，则逐一进行合法性校验，去重校验，保存进入MongoDB中；若为URI生成器脚本，连通其他信息（如crontab信息）保存进MongoDB中。

### 失败处理

- 手工输入单条URI超过约束，将异常URI保存到错误日志中，并给出提示。
- 合法性校验失败后，将失败结果记录到错误日志中，继续处理。
- 去重校验检查出重复结果后，将重复结果记录到错误日志中，不保存并继续处理。
- 单条URI保存失败，将此条URI保存进失败日志中。并在保存后统一提示。
- URI脚本保存失败，将此文件保存进失败日志中，并在保存后给出提示。
- 输入数据不在要求范围内，直接报错。

### 前提条件

- 已经将输入进行格式类型校验。
- MongoDB数据库表已经建立。

### 限制条件

- None

##  URI生成器调度

### 输入
- URI生成器任务标志， 可以为MongoDB的ObjectID对象$_id。

### 输出
- RQ 队列	
- 错误日志	
- 失败日志
		
### 流程
Master从MongoDB的URI生成器Collection中获取_id为$_id的对象，定义URI下载队列，将URI生成器函数，对象作为参数压入URI任务下载队列中，并返回URI下载队列对象。

### 失败处理

- 若$_id不在URI生成器的Collection中，保存此信息到错误日志中，并给出提示。
- 若入队列没有成功，则将错误消息写入失败日志中。



### 前提条件

- 服务器将命令写入定时任务crontab中。
- URI任务生成器函数已经声明，比如 def download_uri_task(uri_generator_id).(等接口定义好了再修改)
- URI任务下载队列函数或对象已经定义，比如 class DownloadURIQueue()


### 限制条件

- 此函数运行在Master服务器上

##  URI生成

### 输入
- URI生成器任务标志， 可以为MongoDB的ObjectID对象$_id。

### 输出
- RQ 队列	
- 错误日志	
- 失败日志
		
### 流程
Master从MongoDB的URI生成器Collection中获取_id为$_id的对象，定义URI下载队列，将URI生成器函数，对象作为参数压入URI任务下载队列中，并返回URI下载队列对象。

### 失败处理

- 若$_id不在URI生成器的Collection中，保存此信息到错误日志中，并给出提示。
- 若入队列没有成功，则将错误消息写入失败日志中。



### 前提条件

- Slave节点加入到RQ 
- URI任务生成器函数已经声明，比如 def download_uri_task(uri_generator_id).(等接口定义好了再修改)
- URI任务下载队列函数或对象已经定义，比如 class DownloadURIQueue()


### 限制条件

- 此函数运行在Slave服务器上。




# User Interface 用户界面

## 登陆界面


# Internel 内部实现

## Directory 代码目录结构

## Object Description 对象描述


# Test 测试

## Testcase 1

- 环境相关
- 输入
- 期望输出


# Other

- 参考文档: <https://www.toptal.com/freelance/why-design-documents-matter>

