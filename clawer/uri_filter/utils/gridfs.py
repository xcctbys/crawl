#encoding=utf-8
from pymongo import Connection
from gridfs import *
from PIL import Image
from bson.objectid import ObjectId
import StringIO
import threading, time
from gridfs import *

'''
con = Connection("mongodb://admin:admin@127.0.0.1:27017")#用URI的方式建立数据库的链接,也有其他的方式进行授权
db = con['repository']#连接到具体的数据库
fs = gridfs.GridFS(db, 'bitmap')#连接到collection，不存在的话会进行创建
fs.put('data.txt')
ObjectId('50b8176989ee3209bccb0b54')#shell 返回文件在mongodb中的id，此时该数据库中会新建两个集合，images.chunk 和images.files
'''

class GFS:
    #定义connection and fs
    c = None
    db = None
    fs = None
    instance = None
    locker = threading.Lock()

    @staticmethod
    def _connect():
        if  not GFS.c:
            GFS.c = Connection( "mongodb://admin:admin@127.0.0.1:27017") # 建立mongodb的连接,管理员账号
            GFS.db = GFS.c['sources']  #连接到指定的数据库中
            GFS.fs = GridFS(GFS.db,  collection='bitmap') #连接到具体的collection中

    #初始化
    def __init__(self):
        print "__init__"
        GFS._connect()
        print "server info " + " * " * 40
        print GFS.c.server_info


    #获得单列对象
    @staticmethod
    def getInstance():
        GFS.locker.acquire()
        try:
            GFS.instance
            if not GFS.instance:
                GFS.instance = GFS()
            return GFS.instance
        finally:
            GFS.locker.release()


    #写入
    def put(self, name,  format="png",mime="image"):
        gf = None
        data = None
        try:
            data = StringIO.StringIO()
            name = "%s.%s" % (name,format)
            image = Image.open(name)
            image.save(data,format)
            #print "name is %s=======data is %s" % (name, data.getvalue())
            gf = GFS.fs.put(data.getvalue(), filename=name, format=format)
        except Exception as e:
            print "Exception ==>> %s " % e
        finally:
            GFS.c = None
            GFS._connect()

            return gf


    #获得data
    def get(self,id):
        gf = None
        try:
            gf  = GFS.fs.get(ObjectId(id))
            im = gf.read()                  #read the data in the GridFS
            dic = {}
            dic["chunk_size"] =  gf.chunk_size
            dic["metadata"] = gf.metadata
            dic["length"] = gf.length
            dic["upload_date"] = gf.upload_date
            dic["name"] = gf.name
            dic["content_type"] = gf.content_type
            dic["format"] = gf.format
            return (im , dic)
        except Exception,e:
            print e
            return (None,None)
        finally:
            if gf:
                gf.close()


    #将gridFS中的文件写入硬盘
    def write_2_disk(self, data, dic):
        name = "./get_%s" % dic['name']
        if name:
            output = open(name, 'wb')
            output.write(data)
            output.close()
            print "fetch image ok!"

    #获得文件列表
    def list(self):
        return GFS.fs.list()


    #删除文件
    def remove(self,name):
        GFS.fs.remove(name)

if __name__== '__main__':
    image_name= raw_input("input the image name>>")
    if image_name:
        gfs = GFS.getInstance()
        if gfs:
            image_id = gfs.put(image_name)
            print "==========Object id is %s  and it's type is %s==========" % (image_id , type(image_id))
            (data, dic) = gfs.get(ObjectId(image_id))
            gfs.write_2_disk(data, dic)
        else:
            pass