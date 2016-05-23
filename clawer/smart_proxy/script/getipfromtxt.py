# -*- coding: utf-8 -*-¬
import os¬
import mysql.connector
import time
#中证配置
config = {
  'user': 'plkj',
  'password': 'Password2016',
  'host': 'csciwlpc.mysql.rds.aliyuncs.com',
  'database': 'csciwlpc',
  'raise_on_warnings': True,
}
cnx = mysql.connector.connect(**config)
class ReadFile:
    def readLines(self):
        f = open("/root/ipproxy.txt", "r",1)
        i=0
        list=[]
        for line in f:
            #strs = line.split("\t")
            strs=line.replace('\r',"")
            timestamp=time.time()
            tup_time=time.localtime(timestamp)
            format_time=time.strftime("%Y-%m-%d %H:%M:%S",tup_time)
            print strs
            #if len(strs) != 5:
               #continue¬


            data=(strs.replace("\n",""),'OTHER', '1',format_time,format_time)
            list.append(data)
            print list
            cursor=cnx.cursor()
            sql = "insert into smart_proxy_proxyip(ip_port,province,is_valid,create_datetime,update_datetime) values(%s,%s,%s,%s,%s)"
            if i>10:
                cursor.executemany(sql,list)
                cnx.commit()
                print("插入")
                i=0
                list=[]
            i=i+1
        if i>0:
            cursor.executemany(sql,list)
            cnx.commit()
        cnx.close()
        f.close()
        print("ok")
    def listFiles(self):
        d = os.listdir("/root")
        return d

············
if __name__ == "__main__":
    readFile = ReadFile()
    readFile.readLines()
getiptxt.py