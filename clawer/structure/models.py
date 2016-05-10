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
     crawlertask = ReferenceField(CrawlerTask)
     parser = ReferenceField(Parser)
     db_xml = StringField()
     
class CrawlerAnalyzedData(Document):
     uri = StringField(max_length =8000)
     job = ReferenceField(Job)
     update_date = DateTimeField(default=datetime.datetime.now())
     analyzed_data = StringField()

class ParseJobInfo(Document):
     rq_parse_job_id = StringField()#把生成解析任务时的RQ job.id结构化，这样job失败一定次数后利用触发函数在数据库中找到StructureConfig中的CrawlerTask并改变其标志位为解析失败
     crawlerdownloaddata = ReferenceField(CrawlerDownloadData)  