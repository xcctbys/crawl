"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from captcha.models import Captcha
import json


class TestViews(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.client = Client()
        
    def test_index(self):
        captcha = Captcha.objects.create(url="http://www.baidu.com", category=2, image_hash="sss")
        url = reverse("captcha.views.index")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        captcha.delete()
        
    def test_make_label(self):
        url = reverse("captcha.views.make_label")
        captcha = Captcha.objects.create(url="http://www.baidu.com", category=2, image_hash="sss")
        
        resp = self.client.post(url, {"captcha_id":captcha.id, "label":"kkk"})
        self.assertEqual(resp.status_code, 200)
        
        result = json.loads(resp.content)
        self.assertEqual(result["is_ok"], True)
        
        captcha.delete()
        
    def test_labeled(self):
        captcha = Captcha.objects.create(url="http://www.baidu.com", category=2, image_hash="sss", label_count=4)
        url = reverse("captcha.views.labeled")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        captcha.delete()
        
    def test_all_labeled(self):
        captcha = Captcha.objects.create(url="http://www.baidu.com", category=2, image_hash="sss", label_count=4)
        url = reverse("captcha.views.all_labeled")
        resp = self.client.get(url, {"category":2})
        self.assertEqual(resp.status_code, 200)
        captcha.delete()
