#coding:utf8

from django.core.management.base import BaseCommand,commandError
from crawer_proxy_ip import Crawer

class Command(BaseCommand):
    def handle(self, *args, **options):         
        crawer = Crawer()
        crawer.run()