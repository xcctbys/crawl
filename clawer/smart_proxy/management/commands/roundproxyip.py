#coding:utf8
from django.core.management.base import BaseCommand,commandError    
from round_proxy_ip import RoundProxy

class Command(BaseCommand):
    def handle(self, *args, **options):
        rounds = RoundProxy()
        rounds.run()         