# coding=utf-8


from django.core.management.base import BaseCommand
from django.conf import settings
# from django.core.management import call_command
from html5helper.utils import wrapper_raven

from collector.utils_generator import CrawlerCronTab


class Command(BaseCommand):

    help =" This command is used to dispatch generator from cron.f."

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.cron = CrawlerCronTab(filename = settings.CRON_FILE)

    # @wrapper_raven
    def handle(self, *args, **options):
        self.cron.task_generator_run()
        print "After run !Expected output from generator dispatch"
