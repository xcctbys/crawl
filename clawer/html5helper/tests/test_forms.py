#coding=utf-8
""" test form
"""

from django.test import TestCase

from html5helper.forms import BasisForm


class TestBasisForm(TestCase):
    def test_init(self):
        form = BasisForm()
        self.assertIsNotNone(form)