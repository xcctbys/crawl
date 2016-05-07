#coding:utf8
import os
import os.path
import django.conf
# from plugins import *
from plugins.xici import XiciProxy, HaoProxy, KuaiProxy, IPCNProxy, SixProxy, YouProxy, NovaProxy

from models import ProxyIp
import smart_proxy.round_proxy_ip as checkip

# proxy_list = [XiciProxy, HaoProxy, KuaiProxy, IPCNProxy, SixProxy, YouProxy]
proxy_list = [XiciProxy, KuaiProxy, IPCNProxy, SixProxy, YouProxy, NovaProxy]

class Crawer(object):
    def __init__(self):
        self.proxyip = None
        pass

    def do_with(self, func):
        #每个插件返回的是代理IP地址加端口号的列表
        try:
            address = func.run()
            if not address:
                address = []
            for item in address:
                # print item
                try:
                    if checkip.check_is_valid(item[0]):
                        print item
                        self.proxyip = ProxyIp(ip_port=item[0], province=item[1], is_valid=True) #放入mysql中
                        self.proxyip.save()
                except:
                    pass
        except KeyboardInterrupt as e:
            return

        except Exception as e:
            # print 'error in do_with',e
            pass

    def run(self):
        #得到有多少个爬虫，多少个插件。
        for item in proxy_list:
            # print 'item:----', item
            self.do_with(item())
if __name__ == '__main__':
    os.environ["DJANGO_SETTINGS_MODULE"] = "crawer.settings"
    django.setup()
    crawer = Crawer()
    crawer.run()
