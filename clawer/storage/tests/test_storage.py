#encoding=utf-8
import json
import os
import datetime
import logging

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as DjangoUser, Group
from django.conf import settings
from storage.models import Job


class TestJob(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.user = DjangoUser.objects.create_user(username="xxx", password="xxx")

    def tearDown(self):
        TestCase.tearDown(self)
        self.user.delete()
        
    def test_create(self):
        job = Job.objects.create(name="hello", creator=self.user, info="go")
        self.assertGreater(job.id, 0)
        
        job.delete()
        
    def test_as_json(self):
        job = Job.objects.create(name="hello", creator=self.user, info="go")
        data = job.as_json()
        self.assertIsNotNone(data)
        
        job.delete()
