#coding:utf8
import os
import os.path
import django.conf
# from plugins import *
from plugins.xici import XiciProxy, HaoProxy, KuaiProxy, IPCNProxy, SixProxy, YouProxy, NovaProxy, Ip84Proxy
from models import ProxyIp
import smart_proxy.round_proxy_ip as check

proxy_list = [XiciProxy, SixProxy, YouProxy, NovaProxy, Ip84Proxy, IPCNProxy] # HaoProxy, KuaiProxy 目前不可用
proxy_list2=  [IPCNProxy]

class Crawler(object):
	def __init__(self):
		self.proxyip = None
		pass

	def do_with(self, func):
		#每个插件返回的是代理IP地址加端口号的列表
		try:
			address = func.run()
			if not address:
				address = []
			# valid = 0
			# notvalid = 0
			for item in address:
				try:
					if check.check_is_valid(item[0]):
						print item, '✓ valid'
						# valid += 1
						self.proxyip = ProxyIp(ip_port=item[0], province=item[1], is_valid=True) #放入mysql中
						self.proxyip.save()
					else:
						print item, '✗ not valid'
						# notvalid += 1
				except KeyboardInterrupt:
					return
				except:
					pass
			# print 'valid:    ', valid
			# print 'notvalid: ', notvalid
			# print 'valid rate: ', float(valid)/(valid + notvalid)
		except KeyboardInterrupt:
			return
		except Exception as e:
			# print 'error in do_with',e
			pass

	def run(self):
		#得到有多少个爬虫，多少个插件。
		for item in proxy_list:
		#for item in proxy_list2:
                        # print 'item:----', item
			self.do_with(item())
if __name__ == '__main__':
	os.environ["DJANGO_SETTINGS_MODULE"] = "crawler.settings"
	django.setup()
	crawler = Crawler()
	crawler.run()
