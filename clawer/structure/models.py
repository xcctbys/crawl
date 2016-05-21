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
                              BooleanField,
                              DateTimeField)


class Parser(Document):
    parser_id = IntField()
    python_script = StringField()

class Extracter(Document):
    extracter_id = IntField()
    extracter_config = StringField()

class StructureConfig(Document):
    job = ReferenceField(Job)
    parser = ReferenceField(Parser)

class ExtracterStructureConfig(Document):
    job = ReferenceField(Job)
    extracter = ReferenceField(Extracter)

     
class CrawlerAnalyzedData(Document):
    crawler_task = ReferenceField(CrawlerTask)
    update_date = DateTimeField(default=datetime.datetime.now())
    analyzed_data = StringField()
    retry_times = IntField(default = 0)

class CrawlerExtracterInfo(Document):
    extract_task = ReferenceField(CrawlerTask)
    update_date = DateTimeField(default=datetime.datetime.now())
    extracted_status = BooleanField(default=False)
    retry_times = IntField(default = 0)
