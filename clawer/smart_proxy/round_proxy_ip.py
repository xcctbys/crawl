#coding:utf8
import os
import sys
sys.path.append(os.getcwd())
print os.getcwd()
from smart_proxy.models import ProxyIp
import requests
from clawer import settings
from multiprocessing.dummy import Pool
# import settings

# class RoundProxy(object):
#     def __init__(self):
#         self.reqst = requests.Session()
#         self.reqst.headers.update({'Accept': 'text/html, application/xhtml+xml, */*',
#                     'Accept-Encoding': 'gzip, deflate',
#                     'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
#                     'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})
#     def change_valid(self, id):
#         one_ip = ProxyIp.objects.get(id=id) #得到对应id的代理。
#         proxy = {'http':'http://'+ one_ip.ip_port}
#         # print id, proxy
#         try:
#             resp = self.reqst.get('http://www.baidu.com', proxies=proxy)
#         except:
#             # update_data(id, flag=False) #更新，置为不可用。
#             if one_ip.is_valid is False:
#                 return False
#             one_ip.is_valid = False
#             one_ip.save()
#             print 'no'
#             return False
#         if resp.status_code == 200:
#             if one_ip.is_valid is True:
#                 return True
#             one_ip.is_valid = True
#             one_ip.save()
#             print 'yes'
#             return True
#         # update_data(id, falg=False)
#         if one_ip.is_valid is False:
#             return False
#         one_ip.is_valid = False
#         one_ip.save()
#         return False
#     def run(self):
#         total_count = ProxyIp.objects.all().count() #获得数据库里数量
#         print total_count

#         pool = Pool(processes=4)
#         pool.map(self.change_valid, range(1, total_count))
#         pool.close()
#         pool.join()
#         # for id in range(1, total_count):
#         #     self.change_valid(id)
#         if total_count > settings.MAX_PROXY_NUM: #settings.MAX_PROXY_NUM:
#             num = total_count - settings.MAX_PROXY_NUM
#             ProxyIp.objects.filter(is_valid=False).order_by(creade_datetime)[:num].delete()
#             # delete_data(setting.MAX_PROXY_NUM - total_count)#删除多余无效数据
#             pass



reqst = requests.Session()
reqst.headers.update({'Accept': 'text/html, application/xhtml+xml, */*',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})
def change_valid(id):
    one_ip = ProxyIp.objects.get(id=id) #得到对应id的代理。
    proxy = {'http':'http://'+ one_ip.ip_port}
    print id, proxy
    try:
        resp = reqst.get('http://www.baidu.com', proxies=proxy)
    except:
        # update_data(id, flag=False) #更新，置为不可用。
        if one_ip.is_valid is False:
            return False
        one_ip.is_valid = False
        one_ip.save()
        print 'no'
        return False
    if resp.status_code == 200:
        if one_ip.is_valid is True:
            return True
        one_ip.is_valid = True
        one_ip.save()
        print 'yes'
        return True
    # update_data(id, falg=False)
    if one_ip.is_valid is False:
        return False
    one_ip.is_valid = False
    one_ip.save()
    return False

def run():
    total_count = ProxyIp.objects.all().count() #获得数据库里数量
    print total_count

    pool = Pool(processes=4)
    pool.map(change_valid, range(1, total_count))
    pool.close()
    pool.join()

    # for id in range(1, total_count):
    #     change_valid(id)
    if total_count > settings.MAX_PROXY_NUM: #settings.MAX_PROXY_NUM:
        num = total_count - settings.MAX_PROXY_NUM
        ProxyIp.objects.filter(is_valid=False).order_by(creade_datetime)[:num].delete()
        # delete_data(setting.MAX_PROXY_NUM - total_count)#删除多余无效数据
        pass