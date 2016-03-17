#coding=utf-8
""" test fields
"""

from django.utils import unittest
from html5helper import fields

class TestCharField(unittest.TestCase):
    def test_init(self):
        input = fields.CharField()
        self.assertIsNotNone(input)
        
        
class TestTextField(unittest.TestCase):
    def test_init(self):
        textarea = fields.TextField(rows= 5, placeholder="gggg")
        self.assertIsNotNone(textarea)
        
    
class TestPasswordField(unittest.TestCase):
    def test_init(self):
        ctrl = fields.PasswordField(placeholder="gggg")
        self.assertIsNotNone(ctrl)
        

class TestIntegerField(unittest.TestCase):
    def test_init(self):
        ctrl = fields.IntegerField(placeholder="gggg")
        self.assertIsNotNone(ctrl)


class TestMarkdownField(unittest.TestCase):
    def test_init(self):
        ctrl = fields.MarkdownField()
        self.assertIsNotNone(ctrl)


class TestChoiceField(unittest.TestCase):
    def test_init(self):
        ctrl = fields.ChoiceField(choices=((0, "1"), (1, "2")))
        self.assertIsNotNone(ctrl)