#encoding=utf-8
from mongoengine import *
import datetime
import os
import logging
import traceback
import json
import redis
import codecs

from django.contrib.auth.models import User as DjangoUser
from django.conf import settings
from django.core.cache import cache

from clawer.utils import Download, UrlCache, DownloadQueue
from html5helper import redis_cluster


class Job(Document):
    (STATUS_ON, STATUS_OFF) = range(1, 3)
    STATUS_CHOICES = (
        (STATUS_ON, u"启用"),
        (STATUS_OFF, u"下线"),
    )
    name = StringField(max_length=128)
    status = IntField(default=STATUS_ON, choices=STATUS_CHOICES)
    add_datetime = DateTimeField(default= datetime.datetime.now())

class CrawlerTaskGenerator(Document):
    """ collection of generator scripts """
    (STATUS_ALPHA, STATUS_BETA, STATUS_PRODUCT, STATUS_ON, STATUS_OFF, STATUS_TEST_FAIL) = range(1, 7)
    STATUS_CHOICES = (
        (STATUS_ALPHA, u"alpha"),
        (STATUS_BETA, u"beta"),
        (STATUS_PRODUCT, u"production"),
        (STATUS_ON, u"启用"),
        (STATUS_OFF, u"下线"),
        (STATUS_TEST_FAIL, u"测试失败"),
    )
    job = ReferenceField(Job)
    code = StringField()  #python code
    cron = StringField(max_length=128)
    status = IntField(default=STATUS_ALPHA, choices=STATUS_CHOICES)
    add_datetime = DateTimeField(default=datetime.datetime.now())

class CrawlerTask(Document):
    """ collecton of uri  """
    (STATUS_LIVE, STATUS_PROCESS, STATUS_FAIL, STATUS_SUCCESS, STATUS_ANALYSIS_FAIL, STATUS_ANALYSIS_SUCCESS) = range(1, 7)
    STATUS_CHOICES = (
        (STATUS_LIVE, u"新增"),
        (STATUS_PROCESS, u"进行中"),
        (STATUS_FAIL, u"下载失败"),
        (STATUS_SUCCESS, u"下载成功"),
        (STATUS_ANALYSIS_FAIL, u"分析失败"),
        (STATUS_ANALYSIS_SUCCESS, u"分析成功"),
    )
    job = ReferenceField(Job,  reverse_delete_rule=CASCADE)
    task_generator = ReferenceField(CrawlerTaskGenerator, null=True)
    uri = StringField(max_length=1024)
    args = StringField(max_length=2048, null=True) # 存储cookie， header等信息
    status = IntField(default=STATUS_LIVE, choices=STATUS_CHOICES)
    from_host = StringField(max_length=128, blank=True, null=True)# 从哪台主机生成
    add_datetime = DateTimeField(default=datetime.datetime.now())


class GrawlerGeneratorLog(Document):
    """log : execution results of generator scripts  """
    (STATUS_FAIL, STATUS_SUCCESS) = range(1, 3)
    STATUS_CHOICES = (
        (STATUS_FAIL, u"失败"),
        (STATUS_SUCCESS, u"成功"),
    )
    job = ReferenceField(Job, reverse_delete_rule=CASCADE)
    task_generator = ReferenceField(CrawlerTaskGenerator)
    status = IntField(default=0, choices=STATUS_CHOICES)
    failed_reason = StringField(max_length=10240, null=True, blank=True)
    content_bytes = IntField(default=0)
    spend_msecs = IntField(default=0) #unit is microsecond
    hostname = StringField(null=True, blank=True, max_length=16)
    add_datetime = DateTimeField(default=datetime.datetime.now())

class GrawlerGeneratorCronLog(Document):
    """ log: execution results of crontab command """
    (STATUS_FAIL, STATUS_SUCCESS) = range(1, 3)
    STATUS_CHOICES = (
        (STATUS_FAIL, u"失败"),
        (STATUS_SUCCESS, u"成功"),
    )
    job = ReferenceField(Job, reverse_delete_rule=CASCADE)
    status = IntField(default=0, choices=STATUS_CHOICES)
    cron = StringField(max_length=128)
    failed_reason = StringField(max_length=10240, null=True, blank=True)
    spend_msecs = IntField(default=0) #unit is microsecond
    add_datetime = DateTimeField(default=datetime.datetime.now())

class CrawlerGeneratorErrorLog(Document):
    job = ReferenceField(Job,  reverse_delete_rule=CASCADE)
    failed_reason = StringField(max_length=10240, null=True)
    content_bytes = IntField(default=0)
    hostname = StringField(null=True, max_length=16)
    add_datetime = DateTimeField(default=datetime.datetime.now())

class CrawlerGeneratorAlertLog(Document):
    job = ReferenceField(Job,  reverse_delete_rule=CASCADE)
    type = StringField(max_length=128)
    reason = StringField(max_length=10240, null=True)
    content_bytes = IntField(default=0)
    hostname = StringField(null=True, max_length=16)
    add_datetime = DateTimeField(default=datetime.datetime.now())

