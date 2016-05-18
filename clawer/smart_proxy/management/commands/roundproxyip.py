#coding:utf8
import sys
# sys.path.append('/Users/princetechs3/Documents/pyenv/cr-clawer/clawer/')

from django.core.management.base import BaseCommand 
# from smart_proxy.round_proxy_ip import RoundProxy
import smart_proxy.round_proxy_ip as rounds

class Command(BaseCommand):
    def handle(self, *args, **options):
        # rounds = RoundProxy()
        rounds.run()         