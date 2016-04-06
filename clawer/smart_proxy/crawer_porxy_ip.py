#coding:utf8
from plugins import *
from models import ProxyIp

class Crawer(object):
    def __init__(self):
        self.proxyip = None
        pass

    def do_with(self, func):
        #每个插件返回的是代理IP地址加端口号的列表
        try:
            address = func.run()
        except Error as e:
            #logging.write() #对于出现错误，写入错误日志中。
            pass
        #对每项进行检测并放入mysql中
        for item in address:
            # if test_ok(item):
            #     add_data(item)
            self.proxyip = ProxyIp('ip_port':item)

    def run(self):
        #得到有多少个爬虫，多少个插件。
        proxy_list = os.listdir(os.path.join(os.getcwd(), plugins)).pop('__init__.py')
        for item in porxy_list:
            self.do_with(item)
if __name__ == '__main__':
    crawer = Crawer()
    crawer.run()
