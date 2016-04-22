# coding=utf-8


from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
# from django.utils.six import StringIO
from html5helper.utils import wrapper_raven

from collector.utils_generator import CrawlerCronTab


class Command(BaseCommand):

    help =" This command is used to install generator for all jobs."

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.cron = CrawlerCronTab(filename = settings.CRON_FILE)

    def add_arguments(self, parser):
        # # Positional arguments
        # parser.add_argument('poll_id', nargs='+', type=int)
        # # Named (optional) arguments
        # parser.add_argument('--delete',
        #     action='store_true',
        #     dest='delete',
        #     default=False,
        #     help='Delete poll instead of closing it')
        pass


    @wrapper_raven
    def handle(self, *args, **options):
        print "Expected output"
        self.cron.task_generator_install()
