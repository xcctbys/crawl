#coding:utf8
import sys
import os
# sys.path.append(os.getcwd())
# sys.path.append('/Users/princetechs3/Documents/pyenv/cr-clawer/clawer/')

from django.core.management.base import BaseCommand
from smart_proxy.utils.get_ip_into_my import *

class Command(BaseCommand):
	def handle(self, *args, **options):
        test =PaidProxy(num=100,sortby= 'time',protocol= 'http')
        ip_list = test.get_ipproxy()
        read = PutIntoMy()
        read.readLines(ip_list)




