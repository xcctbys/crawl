# Statement of Goals

开发人员使用URIGenerator调URIFilter,  输入 URI_List, 返回URI_list_unique

# Functional Description

## 功能

### 输入
- URIGenerator产生的URI _list。

### 输出
- URI_list_unique

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
    ###先在本地redis进行 set array[i] =1 操作，然后定期写回##
    
    
  
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

            URI_list_unique = URIFilter(uri_list)

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
def URIFilterfd():    
        import os
          //进程1     
        try:
                if os.fork() > 0:
                        os._exit(0)
        except OSError, error:
                print 'fork #1 failed: %d (%s)' % (error.errno, error.strerror)
            os._exit(1)
    
        //分离进程
        os.chdir('/')
        os.setsid()
        os.umask(0)
    
             URIFilter() 
        
def URIFilter():
    
        {
    
          ...//去重器实现
        }
if __name__ == '__main__':
    
        URIFilter()



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

#### 调用
```
  URIFilter_list = FilterAPI (filter_typeid,URI_list, access_token = princetechs)

```

#### URL
- ##### **读取settings 配置**
```
eg： http://princetechs.com:8000/cr-clawr/uri_filter/api/uri_filter
```

####  格式

   **JSON**

####  HTTP请求方式

 **POST**
 
 
#### SDK 调用api 处理 ：
     
```
 api = FilterAPIClient(filter_typeid,URI_list, access_token = princetechs)
 put URI_list in  request body
 send request
 connect  to  remote   URIFilter server
 get data  by  POST

```
 
####  出错处理
 
 - API调用异常，抛出`error_code`


 
# Directory 代码目录结构
# Database 数据库
- Mongodb 
- Redis

  
# Test 测试

   输入                                                                                                输出
去重类型`filter_typeid` 和 元素类型不限的list                             筛选后的list

   