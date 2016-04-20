#encoding=utf-8

import datetime

from django.db import models
from django.contrib.auth.models import User as DjangoUser

from mongoengine import Document, EmbeddedDocument



class BaseModel(models.Model):

    class Meta:
        abstract = True
        ordering = ["-id"]

    def as_json(self):
        data = {}

        field_names = self._meta.get_all_field_names()
        for name in field_names:
            if hasattr(self, name) is False:
                continue
            field = getattr(self, name)

            if isinstance(field, datetime.datetime):
                data[name] = field.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(field, datetime.date):
                data[name] = field.strftime("%Y-%m-%d")
            elif field == None:
                data[name] = None
            else:
                data[name] = u"%s" % getattr(self, name)

        return data


    def _get_choice(self, choices, select_id):
        for item in choices:
            if item[0] == select_id:
                return item

        return None


class BaseDocument(Document):
    meta = {'abstract': True}


class BaseEmbeddedDocument(EmbeddedDocument):
    meta = {'abstract': True}


class Job(BaseModel):
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

    creator = models.ForeignKey(DjangoUser)
    name = models.CharField(max_length=128)
    info = models.CharField(max_length=1024)
    customer = models.CharField(max_length=128, blank=True, null=True)
    status = models.IntegerField(default=STATUS_ON, choices=STATUS_CHOICES)
    priority = models.IntegerField(default=PRIOR_6, choices=PRIOR_CHOICES)
    add_datetime = models.DateTimeField(auto_now_add=True)

