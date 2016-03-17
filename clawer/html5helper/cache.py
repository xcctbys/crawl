# coding=utf-8
"""High perforce cache system
"""

import datetime
import types

from django.core.cache import cache


class Cache(object):
    
    def __init__(self, label):
        self.label = label
        self.objs = {} # item value format is {"value":value, "expired_at":expired_at}
    
    def get(self, name):
        now = datetime.datetime.now()
        
        if name in self.objs and self.objs[name]["expired_at"] > now:
            return self.objs[name]["value"]
        
        value = cache.get(name)
        if not value:
            return None
        if not (isinstance(value, types.DictType) and "expired_at" in value and "value" in value):
            return None
        if value["expired_at"] > now:
            return None
        self.objs[name] = value
        return value["value"]
        
    def set(self, name, value, timeout=300):
        if timeout <= 0:
            self.delete(name)
            return
        self.objs[name] = self._pack_value(value, timeout)
        cache.set(name, self.objs[name], timeout)
        
    def delete(self, name):
        if name in self.objs:
            self.objs.pop(name)
        cache.delete(name)
        
    def _pack_value(self, value, timeout):
        expired_at = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        return {"value":value, "expired_at":expired_at}
        
    
default_cache = Cache(label="default")