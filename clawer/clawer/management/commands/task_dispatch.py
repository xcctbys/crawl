# coding=utf-8


from optparse import make_option

from django.core.management.base import BaseCommand

from html5helper.utils import wrapper_raven
from clawer.models import Clawer, ClawerTask, RealTimeMonitor
from clawer.utils import DownloadQueue, download_clawer_task



def run():
    clawers = Clawer.objects.filter(status=Clawer.STATUS_ON).all()
    monitor = RealTimeMonitor()
    download_queue = DownloadQueue()

    for clawer in clawers:
        clawer_settting = clawer.cached_settings()
        queue_name = clawer_settting.prior_to_queue_name()

        # clawer_tasks = ClawerTask.objects.filter(clawer_id=clawer.id, status=ClawerTask.STATUS_LIVE).order_by("id")[:clawer_settting.dispatch]
        # 不按照id排序
        clawer_tasks = ClawerTask.objects.filter(clawer_id=clawer.id, status=ClawerTask.STATUS_LIVE)[:clawer_settting.dispatch]

        for item in clawer_tasks:
            if not download_queue.enqueue(queue_name, download_clawer_task, args=[item, clawer_settting]):
                break
            item.status = ClawerTask.STATUS_PROCESS
            item.save()
            #trace it
            monitor.trace_task_status(item)

        print "clawer is %d, job count %d, queue name %s" % (clawer.id, len(download_queue.jobs), queue_name)

    return download_queue


def empty_all():
    download_queue = DownloadQueue()

    download_queue.queue.empty()
    download_queue.urgency_queue.empty()
    download_queue.foreign_queue.empty()


class Command(BaseCommand):
    args = ""
    help = "Dispatch clawer task"
    option_list = BaseCommand.option_list + (
        make_option('--empty',
            dest='empty',
            action="store_true",
            help='empty all'
        ),
    )

    @wrapper_raven
    def handle(self, *args, **options):
        if options["empty"]:
            empty_all()
            return

        run()
