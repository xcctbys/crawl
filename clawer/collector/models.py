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
    (PRIOR_0, PRIOR_1, PRIOR_2, PRIOR_3, PRIOR_4, PRIOR_5, PRIOR_6) = range(-1, 6)
    PRIOR_CHOICES = (
        (PRIOR_0, u"-1"),
        (PRIOR_1, u"0"),
        (PRIOR_2, u"1"),
        (PRIOR_3, u"2"),
        (PRIOR_4, u"3"),
        (PRIOR_5, u"4"),
        (PRIOR_6, u"5"),
    )

    creator = StringField(max_length= 128)
    name = StringField(max_length=128)
    info = StringField(max_length=1024)
    customer = StringField(max_length=128, null = True)
    status = IntField(default=STATUS_ON, choices=STATUS_CHOICES)
    priority= IntField(default=PRIOR_6, choices= PRIOR_CHOICES)
    add_datetime = DateTimeField(default= datetime.datetime.now())
    meta = {"db_alias": "source"}



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
    (TYPE_PYTHON, TYPE_SHELL) = range(1, 3)
    TYPE_CHOICES = (
        (TYPE_PYTHON, u'Python'),
        (TYPE_PYTHON, u'Shell'),
    )
    job = ReferenceField(Job)
    code = StringField()  #python or shell code
    code_type =
    cron = StringField(max_length=128)
    status = IntField(default=STATUS_ALPHA, choices=STATUS_CHOICES)
    add_datetime = DateTimeField(default=datetime.datetime.now())
    meta = {"db_alias": "source"}

    def status_name(self):
        for item in self.STATUS_CHOICES:
            if item[0] == self.status:
                return item[1]
        return ""

    def code_dir(self):
        path = os.path.join(settings.MEDIA_ROOT, "codes")
        if os.path.exists(path) is False:
            os.makedirs(path, 0775)
        return path

    def alpha_path(self):
        return os.path.join(self.code_dir(), "%s_alpha.py" % str(self.job.id))

    def product_path(self):
        return os.path.join(self.code_dir(), "%s_product.py" % str(self.job.id))

    def write_code(self, path):
        with codecs.open(path, "w", "utf-8") as f:
            f.write(self.code)

class CrawlerTask(Document):
    (STATUS_LIVE, STATUS_DISPATCH, STATUS_PROCESS, STATUS_FAIL, STATUS_SUCCESS, STATUS_ANALYSIS_FAIL, STATUS_ANALYSIS_SUCCESS) = range(1, 8)
    STATUS_CHOICES = (
        (STATUS_LIVE, u"新增"),
        (STATUS_DISPATCH, u'分发中'),
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
    retry_times = IntField(default=0)
    meta = {"db_alias": "source"} # 默认连接的数据库

class CrawlerGeneratorLog(Document):
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

    meta = {"db_alias": "source"}

class CrawlerGeneratorCronLog(Document):
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

    meta = {"db_alias": "source"}

class CrawlerGeneratorErrorLog(Document):
    job = ReferenceField(Job,  reverse_delete_rule=CASCADE)
    failed_reason = StringField(max_length=10240, null=True)
    content_bytes = IntField(default=0)
    hostname = StringField(null=True, max_length=16)
    add_datetime = DateTimeField(default=datetime.datetime.now())

    meta = {"db_alias": "source"}

class CrawlerGeneratorAlertLog(Document):
    job = ReferenceField(Job,  reverse_delete_rule=CASCADE)
    type = StringField(max_length=128)
    reason = StringField(max_length=10240, null=True)
    content_bytes = IntField(default=0)
    hostname = StringField(null=True, max_length=16)
    add_datetime = DateTimeField(default=datetime.datetime.now())

    meta = {"db_alias": "source"}

