# coding=utf-8

from django.core.management.base import BaseCommand

from html5helper.utils import wrapper_raven
from clawer.utils import MonitorClawerDay

                

class Command(BaseCommand):
    args = ""
    help = "Monitor clawer result hourly"
    
    @wrapper_raven
    def handle(self, *args, **options):
        monitor = MonitorClawerDay()
        monitor.monitor()
    
    