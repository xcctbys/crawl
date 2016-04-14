# Statement of Goals

开发人员输入由URIGenerator等产生的URI _list,返回去重后的URI _list _unique。




# Functional Description

## 功能
-避免爬虫重复爬取,浪费资源,将相同的URI进行过滤，同时支持其它数据类型去重。
### 输入
- URIGenerator产生的URI _list。

### 输出
- URI _list _unique

### 流程（伪代码）

```
URI_list_unique   =  URIFilter(URI_list)  
  #URIGenerator 传入URI_list，调用URIFilter
  
  
URIFilter( )内部
   for  URI in URI_list
        #md5 加密
        m = hashlib.md5()    
	    m.update('URI’)
        psw = m.hexdigest()
```
- eg:
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
    #先在本地redis进行 set array[i] =1 操作，然后定期写回##
    read   wback_bitmap_cycle   from  settings
    when   time  =  wback_time
    update  bit-map  in   mongodb



    
  
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

-  失败处理
   
   布隆过滤器有一定误报率（false positive rate），可以严格防止漏报（false negative）。通过控制bit－map的大小和hash函数的个数，可以将误报率控制在0.01%以下。
   
   
   
- 限制条件
  
  Bloom Filter 允许插入和查询，不允许删除（需要删除时要用改进的Counting Bloom Filter,同时用于bit－map需要原来4倍空间大小，可保证溢出率逼近0）。
  
  

# User Interface

## 调用方式

         from crawlerfilter.api  import  FilterAPI
         URIFilter_list = FilterAPI (filter_typeid,URI_list, access_token = princetechs)

###  example:

- Input : 
```
uri_list= [ https://www.baidu.com/，...http://www.2cto.com，... https://www.baidu.com/ ...] 
          //与千万或上亿条历史数据对比后去重
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
Django 开启 守护进程运行服务
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
  def isContaions(self, value):   /
       if value == None:   
           return False   
       ret = True   
     for f in self.hashFunc:   
           loc = f.hash(value)   
           ret = ret & self.bitset[loc]   
       return ret   

```

## SDK 使用
   
     
    **URIGenerator  ----> URIFilter SDK------> URIFilter Server**
 
#### 参数

-  `filter_typeid`
-  `URI_list`

#### 开发者调用
```
  from crawlerfilter.api  import  FilterAPI
  URIFilter_list = FilterAPI (filter_typeid,URI_list, access_token = princetechs)

```

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
 api = FilterAPIClient(filter_typeid,URI_list, access_token = 'princetechs')
 json.dumps (URI_list)
 put URI_list in  request body
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

  URI_list = {[www.baidu.com ,  www.princetechs.com, ....,]}

  URL_listencode = urllib.urlencode(URI_list)

  URI_listencode =json.dumps(URI_listencode)

  //传递json

  requrl = ${url} //从settings中得到request  url

  res = urllib2.Request(url = requrl,data =URI_listencode)

  print       res
```
   

    

**Server**:

     
```
if request.method == "POST":

     // 可进行校验if self.check_auth(access_token):
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
    bitmap_type = StringField(max_length=128)
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

```
def deploy():  // ' 定义一个部署任务 ', run远程操作
fab deploy
```


```
from datetime import datetime
from fabric.api import  *  // import  fabric.api 中run,local, sudo ,env,roles,cd ,put

env.user = 'root'
env.hosts = ['${主机host}] //user@ip:port',] ，ssh要用到的参数

env.password = ' 9527'
def setting_urifilter():
   commit  settings in local
def update_urifilter_setting_remote():
      with cd('~/cr-clawer/uri_filter'):   #cd进入目录
      run('ls -l | wc -l')  #远程操作用run
def update():
    setting_urifilter()
    update_urifilter_setting_remote()



def bitmap_init():
    bitmap = "/home/admin/cr-clawer/uri_filter/bitmap"
    if files.exists(bitmap) is False:
        sudo("mkdir %s )

    with cd("mkdir"):
        sudo(“creat bitmap”)


def bitmap_update():
    with cd("/home/admin/cr-clawer/uri_filter/bitmap"):
      ")
         sudo(“read bitmap_new”)

def urifilter_down():
    if files.exists(urifilter) is False:
        sudo("mkdir %s )
    with cd("/home/admin/cr-clawer/uri_filter/urifilter"):
        sudo("git pull")
        sudo("urifilter init")


def urifilter_start():
    with cd("/home/admin/cr-clawer/uri_filter/urifilter"):
        sudo("chmod ")
        sudo("service urifilter start")


def urifilter_stop():
     with cd("/home/admin/cr-clawer/uri_filter/urifilter"):
        sudo("chmod ")
        sudo("service urifilter stop")


```

#### install system environment
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

  
# Test 测试

| 输入|                                                                      |输出|
|-----------------------------------------------------------|---------------------------------------------|
|去重类型`filter_typeid` 和 元素类型不限的list           |                  筛选后的list|

   
