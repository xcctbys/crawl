#coding:utf8
import os
import sys
sys.path.append(os.getcwd())
from django.test import TestCase
from smart_proxy.api import Proxy
# Create your tests here.

class SimpleTest(TestCase):

	def test_crawer(self):
		crawler = Crawler()
		crawler.run()
		pass

	def test_api(self):
		proxy = Proxy()
		print proxy.get_proxy()
		print proxy.get_proxy(is_valid=False)

