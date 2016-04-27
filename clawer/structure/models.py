# -*- coding: utf-8 -*-

import json
import datetime

from storage.models import Job
from collector.models import CrawlerTask, CrawlerDownloadData
from mongoengine import (Document,
                         IntField,
                         StringField,
                         ReferenceField,)


class Parser(Document):
     parser_id = IntField()
     python_script = StringField()


class StructureConfig(Document):
     job = ReferenceField(Job)
     parser = ReferenceField(Parser)
     db_xml = StringField()
     
class CrawlerAnalyzedData(Document):
     uri = StringField(max_length =8000)
     job = ReferenceField(Job)
     update_date = DateTimeField(default=datetime.datetime.now())
     analyzed_data = StringField()