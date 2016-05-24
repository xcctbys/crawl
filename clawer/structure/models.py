# -*- coding: utf-8 -*-
import django.utils
import json
import datetime
from django.db import models
#from storage.models import Job
from storage.models import Job as JobMySQL
from collector.models import Job as JobMongoDB
from collector.models import CrawlerTask, CrawlerDownloadData
from mongoengine import (Document,
                              IntField,
                              StringField,
                              ReferenceField,
                              BooleanField,
                              DateTimeField)

class Parser(models.Model):
     parser_id = models.CharField(unique = True, max_length = 100)
     python_script = models.TextField()
     update_date = models.DateField(django.utils.timezone.now())

     class Meta:
          db_table = "parser"

class StructureConfig(models.Model):
     job_copy_id = models.CharField(unique = True, max_length = 100)
     job = models.OneToOneField(
          JobMySQL,
          on_delete = models.CASCADE)

     parser = models.OneToOneField(
          Parser,
          on_delete = models.CASCADE)

     update_date = models.DateField(django.utils.timezone.now())

     class  Meta:
          db_table = "structure_config"

class CrawlerAnalyzedData(Document):
     crawler_task = ReferenceField(CrawlerTask)
     update_date = DateTimeField(default=datetime.datetime.now())
     analyzed_data = StringField()
     retry_times = IntField(default = 0)
     meta = {"db_alias": "structure"}

class Extracter(Document):
    extracter_id = IntField()
    extracter_config = StringField()

class ExtracterStructureConfig(Document):
    job = ReferenceField(JobMongoDB)
    extracter = ReferenceField(Extracter)

class CrawlerExtracterInfo(Document):
    extract_task = ReferenceField(CrawlerTask)
    update_date = DateTimeField(default=datetime.datetime.now())
    extracted_status = BooleanField(default=False)
    retry_times = IntField(default = 0)
