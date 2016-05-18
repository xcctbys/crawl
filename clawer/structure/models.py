# -*- coding: utf-8 -*-

import json
import datetime

#from storage.models import Job
from collector.models import Job
from collector.models import CrawlerTask, CrawlerDownloadData
from mongoengine import (Document,
                              IntField,
                              StringField,
                              ReferenceField,
                              DateTimeField)

class StructureTask(Document):
    (STATUS_LIVE, STATUS_DISPATCH, STATUS_PROCESS, STATUS_ANALYSIS_FAIL, STATUS_ANALYSIS_SUCCESS, STATUS_EXTRACT_FAIL, STATUS_EXTRACT_SUCCESS) = range(1, 8)
    STATUS_CHOICES = (
        (STATUS_LIVE, u"新增"),
        (STATUS_DISPATCH, u'分发中'),
        (STATUS_PROCESS, u"进行中"),
        (STATUS_ANALYSIS_FAIL, u"分析失败"),
        (STATUS_ANALYSIS_SUCCESS, u"分析成功"),
        (STATUS_EXTRACT_FAIL, u"导出失败"),
        (STATUS_EXTRACT_SUCCESS, u"导出成功"),
    )
    job = ReferenceField(Job,  reverse_delete_rule=CASCADE)
    status = IntField(default=STATUS_LIVE, choices=STATUS_CHOICES)
    update_date = DateTimeField(default=datetime.datetime.now)
    retry_times = IntField(default=0)


class Parser(Document):
    parser_id = IntField()
    python_script = StringField()

class Extracter(Document):
    extracter_id = IntField()
    extracter_config = StringField()

class StructureConfig(Document):
    job = ReferenceField(Job)
    parser = ReferenceField(Parser)
    extracter = ReferenceField(Extracter)
     
class CrawlerAnalyzedData(Document):
    crawler_task = ReferenceField(CrawlerTask)
    update_date = DateTimeField(default=datetime.datetime.now())
    analyzed_data = StringField()
    retry_times = IntField(default = 0)

class ExtracterInfo(StructureTask):
    extract_task = ReferenceField(StructureTask)
