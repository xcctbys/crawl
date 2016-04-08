#coding:utf8
import sys
sys.path.append('/Users/princetechs3/Documents/pyenv/cr-clawer/clawer/')

from django.core.management.base import BaseCommand
from smart_proxy.crawer_proxy_ip import Crawer

class Command(BaseCommand):
    def handle(self, *args, **options):         
        crawer = Crawer()
        crawer.run()