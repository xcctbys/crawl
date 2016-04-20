from django.db import models

# Create your models here.

from mongoengine import *

class FilterBitMap(Document):
    (STATUS_ON, STATUS_OFF) = range(1, 3)
    STATUS_CHOICES = (
        (STATUS_ON, u"启用"),
        (STATUS_OFF, u"弃用"),
     )
    bitmap_array = IntArray(bits_size)
    bitmap_type= StringField(max_length=128)
    creat_datetime = DateTimeField(default= datetime.datetime.now())





class URIFilterErrorLog(Document):
        failed_reason = StringField(max_length=10240, null=True)
        filtertype_id = IntField(default=0)
        err_datetime = DateTimeField(default=datetime.datetime.now())