#encoding=utf-8
from mongoengine import *
import datetime
import os
import logging
import traceback
import json
import redis
import codecs
from django.db import models
from django.contrib.auth.models import User as DjangoUser
from django.conf import settings
from django.core.cache import cache

from clawer.utils import Download, UrlCache, DownloadQueue
from html5helper import redis_cluster


# Create your models here.



'''
class FilterBitMap(Document):
    (STATUS_ON, STATUS_OFF) = range(1, 3)
    STATUS_CHOICES = (
        (STATUS_ON, u"启用"),
        (STATUS_OFF, u"弃用"),
     )
    bitmap_array = IntArray(bits_size)  # IntArray  需要实现
    bitmap_type= StringField(max_length=128)
    creat_datetime = DateTimeField(default= datetime.datetime.now())
    meta = {"db_alias": "source"}



class URIFilterErrorLog(Document):
        failed_reason = StringField(max_length=10240, null=True)
        filtertype_id = IntField(default=0)
        err_datetime = DateTimeField(default=datetime.datetime.now())
        meta = {"db_alias": "log"}

'''
