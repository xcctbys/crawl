# coding=utf-8


from django.core.management.base import BaseCommand
from django.conf import settings
# from django.core.management import call_command
from html5helper.utils import wrapper_raven

from collector.utils_generator import CrawlerCronTab
import time


class Command(BaseCommand):

    help =" This command is used to dispatch generator from cron.f."

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.cron = CrawlerCronTab(filename = settings.CRON_FILE)

    # @wrapper_raven
    def handle(self, *args, **options):
        print "Before run !Expected output from generator dispatch"
        start_time = time.time()
        self.cron.task_generator_run()
        end_time = time.time()
        print "Run time is %f s!"%(end_time - start_time)
