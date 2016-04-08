#coding:utf8

import os
import sys
print os.getcwd()
# sys.path.append('/Users/princetechs3/Documents/pyenv/cr-clawer/clawer/')
sys.path.append(os.getcwd())

from django.test import TestCase
# from ..crawer_proxy_ip import Crawer
from smart_proxy.models import ProxyIp
from smart_proxy.crawer_proxy_ip import Crawer
from smart_proxy.api import Proxy

class ProxyTests(TestCase):
	def test_print(self):
		print 'hello'

	def test_crawer(self):
		crawer = Crawer()
		crawer.run()
		pass

	def test_api(self):
		proxy = Proxy()
		print proxy.get_proxy()
		print proxy.get_proxy(is_valid=False)

