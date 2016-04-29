# Statement of Goals

开发人员调用去重器接口,输入由 URIGenerator 等产生的uri列表 ,`uri_list` ,返回去重后的 `uri_list_unique`。运维人员对去重器进行本地或远程部署.

# Functional Description

### URI及其它数据类型的去重。
### 输入
- URIGenerator产生的`uri_list`。
成员为uri的list
### 输出
- `uri_list_unique`
去重后的list.
### 流程（伪代码）

```
uri_list_unique   =  URIFilter(uri_list)
  #URIGenerator 传入URI_list，调用URIFilter
  
URIFilter( )内部
   for  uri in uri_list
        #md5 加密
        m = hashlib.md5()    
	    m.update('URI’)
        psw = m.hexdigest()
```
#### Example:
   uri = www.baidu.com
 
- md5 加密后：
```
      16位 大写	49545C5F7D247B3A  
```

  
  
- 去重过程

```  
def URIFilter():
    del_list = [ ]
    for  uri  in   uri_list   :
        if  isContaions(self, value) =  true   and    modifed_flag = false ：
            del_list .append (uri)
    url_list = url_list – del_list
    return  url_list_new 
  
```
  
  - 定时写回
  
```
    #先在本地redis进行 set array[i] =1 操作，然后每月1号0点0分定期写回##


    0 0 1 * *           /user/cr-clawer/uri_filter   update  bit-map  in   mongodb

  
```
  
  


#### 去重服务器初始化
  
  
- 初始化
   
```
     connect  to  mongodb
     if    bit-map  not  exist mongodb  
           read   settings
            creat   bit-map  in mongodb  //读取设置，新建bit-map
```

- START

```
  if  bit-map  not exist redis                          
     get bit –map  from  mongodb by id    //启动服务,下载bit-map
     put  bit –map in  redis     //redis用来做数据缓存
 If   bit –map  exist   redis            //redis中是否已经有bit-map
     Creat   uri_filter pd  //创建守护进程 ，开启服务

```

#### 失败处理
   
- 布隆过滤器有一定误报率（false positive rate），可以严格防止漏报（false negative）。通过控制bit－map的大小和hash函数的个数，可以将误报率控制在0.01%以下。
   
   
   





#### 限制条件

- Bloom Filter 允许插入和查询，不允许删除（需要删除时要用改进的Counting Bloom Filter,同时用于bit－map需要原来4倍空间大小，可保证溢出率逼近0）。



  
## 去重性能

   使用BloomFilter 实现防重器,时间复杂度O(1), 空间复杂度 O(1) ,远小于数据库索引查找 和 Hashtable等.误差率可控制在0.01%以下.占用内存与待去重uri条数成正比.

**Example:**

    设置uri数量规模n=1000000 ,控制误差率 p=0.01%, 可计算出
    m = 19170116.754734 bits = 2.28 mb
    100万条uri去重需要空间约2.38MB.
    m ∝ n , 即 1千万uri去重需要22.9mb (bit-map) ,1 亿uri 需要229 mb 位图(bit-map) .


# User Interface

## URI去重器
#### 用户配置
用户可以在project中的settings配置去重器参数.

`URI_NUM_SCALE`预计要去重的uri数量级和.
`ACCEPT_ERROR_RATE`能够接受的去重失误率.

#### 调用
```
   from crawlerfilter.api  import  FilterAPI
   uri_filter_list = FilterAPI (filter_typeid,uri_list, access_token = ``)

```
#### 传入参数
- `filter_typeid` 用int值标识要过滤数据类型,uri =1,ip =2(可扩展)
- `uri_list` 将多条uri以list形式传入
- `access_token`调用接口的token验证,可不传入


#### 输出
- `URIFilter_list` 去重后的 uri列表

#### 限制条件
`uri_list`的规模由用户决定,传入uri的条数会决定处理时间.每次传入1000条以内uri,处理时间在s(秒)级.


###  example:

- Input : 
```
filter_typeid = 1
uri_list= [ https://www.baidu.com/，...http://www.2cto.com，... https://www.baidu.com/ ...] 
          //与千万或上亿条历史数据对比后去重
access_token = ''
```
- Output:  

```
uri_list=[ https://www.baidu.com/，...http://www.2cto.com ...]
```

# Internel 内部实现

### Bloom Filter
- 利用BloomFilter原理 ,使用bit-map数据结构，URIFilter对照bit-map标志位进行去重。
- bit-map放置在mongodb中，可以借助 GridFS 来分片存储，服务器将bit-map拿到本地redis做数据缓存。


### URIFilter  server 守护进程
```
Django 开启守护进程运行服务
```


### 算法实现

#### hash


```
class SimpleHash():  
   def __init__(self, cap, seed):   
       self.cap = cap   
        self.seed = seed           
  def hash(self, value):   
     ret = 0   
        for i in range(len(value)):   
            ret += self.seed*ret + ord(value[i])   
        return (self.cap-1) & ret       

```



#### 布隆过滤器

```
class BloomFilter():   
        def __init__(self, BIT_SIZE=1<<m):   
        self.BIT_SIZE = 1 << m  
       self.seeds = [5, 7, 11, 13, 31, 37, 61，....]    //k个
       self.bitset = BitVector.BitVector(size=self.BIT_SIZE)   
       self.hashFunc = []   
        for i in range(len(self.seeds)):   
             self.hashFunc.append(SimpleHash(self.BIT_SIZE, self.seeds[i]))   
             print self.container_size  
         return  

```

#### 插入新URI

```
def insert(self, value):  
       for f in self.hashFunc:   
           loc = f.hash(value)   
           self.bitset[loc] = 1   

```


#### 是否包含URI

```
  def isContaions(self, value):
       if value == None:   
           return False   
       ret = True   
     for f in self.hashFunc:   
           loc = f.hash(value)   
           ret = ret & self.bitset[loc]   
       return ret   

```

## SDK 内部
   

**URIGenerator  ----> URIFilter SDK------> URIFilter Server**
 

#### URL
-  **读取settings 配置**
   得到远程服务器url,发送request  
```
eg： http://princetechs.com:8000/cr-clawr/uri_filter/api/uri_filter

```

####  格式

   **JSON**

####  HTTP请求方式

 **POST**
 
 
 
 #### SDK 调用api 处理 ：
     
```
 api = FilterAPIClient(filter_typeid,uri_list, access_token = 'princetechs')
 json.dumps (uri_list)
 put uri_list in  request body
 send request
 connect  to  remote   URIFilter server
 get data  by  POST

```
 
####  出错处理
 
 - API调用异常，抛出`error_code`



HTTPConnection.request(method,url[,body[,header]])

通过Http的POST请求 server-client 通信

####SDK与URIFilter  通信
  

**Client** :

  
```

  import urllib2

  uri_list = {[www.baidu.com ,  www.princetechs.com, ....,]}

  uri_listencode = urllib.urlencode(uri_list)

  uri_listencode =json.dumps(uri_listencode)

  //传递json

  requrl = ${url} //从settings中得到request  url

  res = urllib2.Request(url = requrl,data =uri_listencode)

  print       res
```
   

    

**Server**:

     
```
if request.method == "POST":
     #可加入校验if self.check_auth(access_token):
URIFilter() //调用去重
self.send_response('')
self.send_header('Content-Type', 'application/json')
ReturnHttpResponse(json.dumps(data),content_type='application/json')”

```
       


 

# Database 数据库
- Mongodb 
- Redis
## FilterBitMap
```
from mongoengine import *

class FilterBitMap(Document):
    (STATUS_ON, STATUS_OFF) = range(1, 3)
    STATUS_CHOICES = (
        (STATUS_ON, u"启用"),
        (STATUS_OFF, u"弃用"),
     )
    bitmap_array = IntArray(bits_size)
    bitmap_type= StringField(max_length=128)
    creat_datetime = DateTimeField(default= datetime.datetime.now())
```

## URIFilterErrorLog

```
class URIFilterErrorLog(Document):
        failed_reason = StringField(max_length=10240, null=True)
        filtertype_id = IntField(default=0)
        err_datetime = DateTimeField(default=datetime.datetime.now())


```

# Deploy 部署

### 利用fabric进行远程部署，SSH与远程主机通信
### **1-部署工具安装**
#### - SSH安装

- 首先确认SSH安装完成,重启SSH 服务.

#### 服务器设置
- 为 SSH 用户建立私钥和公钥。首先登录到需要建立密钥的账户下，注意要退出 root 用户（可用 su 命令切换到其它用户）
```　　
ssh-keygen
```　
- 将生成的 key 存放在默认目录下即可。过程中会提示输入 passphrase，用来给证书加个密码，提高安全性。如果此项留空，后面即可实现PuTTy 通过证书认证自动登录。
```　
ssh-keygen // 命令会生成两个密钥，首先我们需要将公钥改名留在服务器上：
cd ~/.ssh mv id_rsa.pub authorized_keys //将私钥 id_rsa 从服务器上复制出来，并删除掉服务器上的id_rsa文件。
```

#### 客户端设置

- 我们需要利用PuTTyGEN 这个工具,将 id_rsa 文件转化为PuTTy支持的格式.
点击 PuTTyGen 界面中的 `Load` 按钮，选择 `id_rsa` 文件，输入 `passphrase`（如果前面设置过）,然后点击 `Save PrivateKey`,生成这PuTTy 接受的私钥。
打开 PuTTy，在 Session 中输入服务器的IP地址，在 `Connection->SSH->Auth` 下点击 `Browse` 按钮，选择刚才生成好的私钥。回到`Connection`选项，在 `Auto-login username` 中输入证书所属的用户名。回到`Session` 选项卡，输入名字点 `Save` 保存下这个 `Session`。点击底部的 `Open` 应该就可以通过证书认证登录到服务器了。

- 如果有 passphrase 的话，登录过程中会要求输入 passphrase，否则可以直接登录到服务器上。


#### - fabric 安装
1.安装命令
```
pip install fabric
```
测试安装是否成功
python -c "from fabric.api import * ; print env.version"
显示出版本说明安装成功


2.创建连接（否则会报错提示“命令不存在”）
```
ln -s /usr/local/python2.7/bin/fab /usr/bin/fab
```



## **本地客户机终端部署URIFilter服务到远程服务器**


### 利用fab 命令 auto deploy


```
# fab -f deploy_filter.py  deploy_name   //在终端 execute 对应deploy_name的部署脚本
```
- `deploy_name` 表示要部署的服务名称
 例如 `urifilter_start` 去重器开启, `bitmap_update` 位图更新

#### **Example** :
```
fab -f deploy_filter.py bitmap_init   //在远程server 上初始化用于去重的 bitmap

```

### 用fabric deploy 任务


 脚本文件默认为fabfile.py
```
fab deploy_name //执行deploy脚本
``` 
文件名不为fabfile.py时需进行指定

```
mv fafile.py new_name.py //指定新自定义文件名

fab -f new_name deploy  //重命名后执行deploy脚本
```

定义一个部署任务
```
- def deploy():  //  `run`远程操作 ,`local` 执行本地操作
```

**Example** :
```
[root ]fab -f deploy_filter.py  update
 ...
[localhost] Executing task setting_urifilter //本地执行urifilter
[user@ip:port]Executing task update_urifilter_setting_remote // 更新远程服务器 urifilter settings

```
**Deploy脚本文件**



**初始导入及设置**
```

from datetime import datetime
from fabric.api import  *  // import  fabric.api 中run,local, sudo ,env,roles,cd ,put

env.user = 'root'
#ssh要用到的参数,远程主机ip和端口号
env.hosts = ['${主机host}] //user@ip:port',]
env.password = '  '//可以不使用明文配置,打通ssh即可

def setting_urifilter():  //设置本地urifilter
    commit  settings in local
def update_urifilter_setting_remote():
      with cd(${`uri_filter_setting_dir`}):   #cd进入目录
      run('commit settings in remote server')  //远程操作用run
def update():           //更新urifilter的settings
    setting_urifilter()
    update_urifilter_setting_remote()
```


**初始化bitmap**

```
#初始化用于去重的bitmap
def bitmap_init():
    bitmap = "${bitmap_dir}"
    if files.exists(bitmap) is False:
        sudo("mkdir %s )

    with cd("mkdir"):
        sudo(“creat bitmap”)

#更新bitmap
def bitmap_update():
    with cd("${bitmap_dir}"):
         sudo(“read bitmap_new”)
#get去重模块
def urifilter_get():
    if files.exists(urifilter) is False:
        sudo("mkdir %s )
    with cd("${urifilter_dir}"):
        sudo("git pull")
        sudo("bitmap_init")

```


**去重服务**

```
def urifilter_start()://去重开启
    with cd("${urifilter_dir}"):
        sudo("chmod ")
        sudo("service urifilter start")


def urifilter_stop()://去重关闭
     with cd("${urifilter_dir}"):
        sudo("chmod ")
        sudo("service urifilter stop")



def urifilter_restart()://去重重启
    with cd("${urifilter_dir}"):
        sudo("chmod ")
        sudo("service urifilter  restart")


```

**去重bitmap 定时写回**



```
def bitmap_wrback_start()://定时将bitmap写回mongodb
    print ("write back bitmap  server start")
    run( '${urifilter_dir}/write_back_bitmap.sh' )  //开启定时写回功能

  # 定时写回脚本write_back_bitmap.sh 内容

    0 0 1 * *  ${user_dir}/uri_filter/bitmap_update  //每月1号夜里0点执行bitmap写回


```


#### 安装 system environment
```
def install_settings():
    installer.install_settings()


def install_env():
    installer.install_env()


def install_django():
    installer.install_django()


def install_mongodb():
    installer.install_mongodb()

def install_redis():
    installer.install_redis()


```


# 代码目录树

```
uri_filter
├── __init__.py
├── api
│   ├── __init__.py
│   └── uri_filter.py
├── management
│   └── commands
│       ├── __init__.py
│       └── start_server.py
├── migrations
│   └── __init__.py
├── models.py
├── tests
│   ├── __init__.py
│   └── test_uri_filter.py
├── urls.py
├── utils
│   ├── __init__.py
│   ├── bloomfilter.py
│   ├── filter_utils.py
│   └── update.py
└── view.py


```


  
# Test 测试方案

| 输入            |                                                                      |          输出       |
|-----------------------------------------------------------|---------------------------------------------|
|去重类型`filter_typeid` (`int`类型)和 成员数据类型不限的list (列表)           |                   |筛选后的list  |
### 去重类型
- filter_typeid 对应参数可以为：
'uri_generator' ＃uri生成器去重
'uri_download'#uri下载器去重
'ip'#ip去重
'uri_parse'#uri解析去重

- list 为要去重的元素列表
  元素不限于uri，ip等
eg: ['www.baidu.com','www.hao.com','www.princetechs.com',.....'www.google.com']
    ['apple','fruit','orange',......'peanch','lemon']
    ['192.168.1.10','127.127.38.42'....'145.213.32.44']
    ['张','赵','李','王' .....'大海','月亮','星星']
 列表元素个数在1亿五千万条以内去重误差不大于0.01%
- 限制条件

  输入的格式为list,uri条数越多处理耗时越多,一般1000条左右uri处理用时在s(秒)级.

## 准备工作
#### 环境要求
- 项目requirement中所需基本环境
- redis3.0.7
- pyredis

### 开启redis服务
cd到redis安装目录下，
cd src
./redis-server &后台启动

### 检查是否启动成功
``` 
$ ps -ef | grep redis
```
看到redis服务和端口号即开启成功  
``` 
redis-server *:6379  
```
- 关闭  
在终端输入  
```
~  redis-cli shutdown  
```
- start  
```
cd到cr－clawer目录下  
在terminal下输入 python manage.py shell 进入环境  
 IN[0]:from uri_filter.api.api_uri_filter import *  
 IN[1]:from uri_filter.api.api_filter_timing import *  
＃uri_list可从txt文件中读入，每条uri之间以回车换行分割。  
 [IN]:from uri_filter.tests.test_uri_filter import*  
 [IN2]:file_path = "/tmp/filter_test.txt" ##自定义txt目录  
 [IN3]:uri_list = read_urilist_from_txt(file_path)
 [IN4]:uri_list_unique = bloom_filter_api('uri_generator', uri_list)
 [IN]: uri_list_timing = timing_filter_api('uri_parse',uri_list,expire)
 ```
