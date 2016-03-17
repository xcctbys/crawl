# coding=utf-8
""" run every hour
"""

import os
import datetime
import gzip

from django.core.management.base import BaseCommand
from django.conf import settings

from html5helper.utils import wrapper_raven
from clawer.models import Clawer, ClawerAnalysisLog
from django.utils.encoding import smart_str



def run():
    pre_hour = datetime.datetime.now() - datetime.timedelta(minutes=60)
    start = pre_hour.replace(minute=0, second=1)
    end = pre_hour.replace(minute=59, second=59)
    
    clawers = Clawer.objects.filter(status=Clawer.STATUS_ON)
    for item in clawers:
        merge_clawer(item, start, end)
        
    return True


def merge_clawer(clawer, start, end):
    analysis_logs = ClawerAnalysisLog.objects.filter(clawer=clawer, add_datetime__range=(start, end), status=ClawerAnalysisLog.STATUS_SUCCESS)
    if len(analysis_logs) <= 0:
        return
    
    path = save_path(clawer, start)
    with gzip.open(path, "wb") as f:
        print "clawer id %d, count is %d" % (clawer.id, len(analysis_logs))
        for item in analysis_logs:
            f.write(smart_str(item.result.strip()))
            f.write("\n")
        

def save_path(clawer, dt):
    path = os.path.join(settings.CLAWER_RESULT, "%d/%s/%s.json.gz" % (clawer.id, dt.strftime("%Y/%m/%d"), dt.strftime("%H")))
    parent = os.path.dirname(path)
    if os.path.exists(parent) is False:
        os.makedirs(parent, 0775)
    return path
        

class Command(BaseCommand):
    args = ""
    help = "Merge Analysis Result. Always merge previous hour"
    
    @wrapper_raven
    def handle(self, *args, **options):
        run()