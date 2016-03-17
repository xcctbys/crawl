# -*- coding: UTF-8 -*-
from django.test import TestCase

from html5helper.cache import Cache, default_cache
        
# test cache
class TestCache(TestCase):
    def test_get(self):
        name = "aaaa"
        result = default_cache.get(name)
        self.assertEqual(result, None)
        
    def test_set(self):
        name = "aaaa"
        value = [2, 3]
        
        default_cache.set(name, value)
        self.assertEqual(default_cache.get(name), value)
        
        default_cache.set(name, value, timeout=0)
        self.assertEqual(default_cache.get(name), None)
        
    def test_delete(self):
        name = "aaaa"
        value = [2, 3]
        
        default_cache.set(name, value)
        default_cache.delete(name)
        self.assertEqual(default_cache.get(name), None)