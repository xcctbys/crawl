# coding=utf-8

import traceback
import os
import sys
import time
from optparse import make_option
import threading
import socket
import random

from django.core.management.base import BaseCommand

from html5helper.utils import wrapper_raven
from clawer.models import Clawer, ClawerTask, ClawerDownloadLog

from clawer.utils import AnalysisClawerTask


EXIT_TIMER = None
WORK_THREAD = None


def run(runtime, thread_count):
    time.sleep(random.randint(1, 30))
    
    EXIT_TIMER = threading.Timer(runtime, force_exit)
    EXIT_TIMER.start()
    
    WORK_THREAD = threading.Thread(target=do_run)
    WORK_THREAD.start()
    WORK_THREAD.join(runtime)
        
    return True


def force_exit():
    os._exit(1)


def do_run():
    clawers = Clawer.objects.filter(status=Clawer.STATUS_ON).all()
    total_job_count = 0
    file_not_found = 0
    
    for clawer in clawers:
        analysis = clawer.runing_analysis()
        if not analysis:
            continue
        path = analysis.product_path()
        analysis.write_code(path)
        
        job_count = 0
        clawer_setting = clawer.cached_settings()
        clawer_tasks = ClawerTask.objects.filter(clawer_id=clawer.id, status=ClawerTask.STATUS_SUCCESS).order_by("id")[:clawer_setting.analysis]
        for item in clawer_tasks:
            try:
                if os.path.exists(item.store) is False:
                    file_not_found += 1
                    handle_not_found(item)
                    continue
                
                analysis_clawer_task = AnalysisClawerTask(clawer, item)
                analysis_clawer_task.analysis()
                
                job_count += 1
            except: 
                print traceback.format_exc(10)   
                
        print "clawer is %d, job count is %d" % (clawer.id, job_count)
        total_job_count += job_count
    
    print "total job count is %d, file not found %d" % (total_job_count, file_not_found)
    return total_job_count


def handle_not_found(clawer_task):
    try:
        download_log = ClawerDownloadLog.objects.filter(task=clawer_task, status=ClawerDownloadLog.STATUS_SUCCESS).order_by("-id")[0]
    except:
        download_log = None
        print traceback.format_exc(10)
        print "not found clawer task %d 's download log" % clawer_task.id
        
    if not download_log:
        return
    
    if download_log.hostname == socket.gethostname():
        clawer_task.status = ClawerTask.STATUS_LIVE
        clawer_task.save()


class Command(BaseCommand):
    args = ""
    help = "Analysis clawer download page"
    option_list = BaseCommand.option_list + (
        make_option('--run',
            dest='run',
            default=300,
            help='Run seconds'
        ),
        make_option('--thread',
            dest='thread',
            default=2,
            help='Run threads'
        ),
    )
    
    @wrapper_raven
    def handle(self, *args, **options):
        run(int(options["run"]), int(options["thread"]))
