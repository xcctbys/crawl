# coding=utf-8

import os
import requests
import logging
import hashlib
import multiprocessing
import sys

from django.core.management.base import BaseCommand
from django.conf import settings

from html5helper.utils import wrapper_raven
from enterprise.models import Enterprise







class Command(BaseCommand):
    args = ""
    help = "Remove multiple enterprise"
    
    def __init__(self):
        pass
    
    @wrapper_raven
    def handle(self, *args, **options):
        self._remove_multiple()
    
    def _remove_multiple(self):
        step = 1000
        offset = 0
        multiple = 0
        
        while True:
            enterprises = Enterprise.objects.all()[offset:offset+step]
            if len(enterprises) <= 0:
                break
            offset += step
            for item in enterprises:
                qs = Enterprise.objects.filter(register_no=item.register_no).exclude(id=item.id)
                if qs.count() > 0:
                    qs.delete()
                    multiple += 1
                    
        print "Remove multiple %d" % multiple
                    
        
        