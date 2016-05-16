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


class Parser(Document):
     parser_id = IntField()
     python_script = StringField()

class StructureConfig(Document):
     job = ReferenceField(Job)
     parser = ReferenceField(Parser)
     db_xml = StringField()
     
class CrawlerAnalyzedData(Document):
     crawler_task = ReferenceField(CrawlerTask)
     update_date = DateTimeField(default=datetime.datetime.now())
     analyzed_data = StringField()
     retry_times = IntField(default = 0)