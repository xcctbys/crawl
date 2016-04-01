#encoding=utf-8
import json
import os

import pytest

from django.test.testcases import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as DjangoUser
from django.test.client import Client


from enterprise.utils import EnterpriseDownload
from enterprise.libs.guangdong_crawler import GuangdongClawer
from enterprise.models import Enterprise, Province




class TestGuangdong(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    @pytest.mark.timeout(15)
    def test_guangdong1(self):
        ent_num = "222400000001337"
        guangdong = GuangdongClawer()
        data = guangdong.run(ent_num)
        print data
        self.assertIsNotNone(data)

    @pytest.mark.timeout(15)
    def test_guangdong0(self):
        ent_num = "440301112088791"
        guangdong = GuangdongClawer()
        data = guangdong.run(ent_num)
        print data
        self.assertIsNotNone(data)
    
    @pytest.mark.timeout(15)
    def test_guangdong2(self):
        ent_num = "440000000035814"
        guangdong = GuangdongClawer()
        data = guangdong.run(ent_num)
        print data
        self.assertIsNotNone(data)

