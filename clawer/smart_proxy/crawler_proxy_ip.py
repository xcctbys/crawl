#coding:utf8
import os
import os.path
import django.conf
# from plugins import *
from plugins.xici import XiciProxy, HaoProxy, KuaiProxy, IPCNProxy, SixProxy, YouProxy, NovaProxy, Ip84Proxy
from models import ProxyIp
import smart_proxy.round_proxy_ip as check
from multiprocessing.dummy import Pool

proxy_list = [SixProxy(), YouProxy(), NovaProxy(), Ip84Proxy(), IPCNProxy()] # HaoProxy, KuaiProxy 目前不可用
proxy_list2=  [XiciProxy()]

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

                        # print 'item:----', item

	def run(self):
		pool = Pool()
		pool.map(self.do_with, proxy_list)
		pool.close()
		pool.join()


	def runfast(self):
		pool = Pool()
		pool.map(self.do_with, proxy_list2)
		pool.close()
		pool.join()

if __name__ == '__main__':
	os.environ["DJANGO_SETTINGS_MODULE"] = "crawler.settings"
	django.setup()
	crawler = Crawler()
	crawler.run()
