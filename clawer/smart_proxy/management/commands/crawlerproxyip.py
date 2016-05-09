#coding:utf8
import sys
import os
# sys.path.append(os.getcwd())
# sys.path.append('/Users/princetechs3/Documents/pyenv/cr-clawer/clawer/')

from django.core.management.base import BaseCommand
from smart_proxy.crawler_proxy_ip import Crawler

class Command(BaseCommand):
	def handle(self, *args, **options):         
		crawler = Crawler()
		crawler.run()