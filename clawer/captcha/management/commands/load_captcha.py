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
from captcha.models import Captcha, Category
import traceback






class DownloadCaptcha(object):
    def __init__(self, url, category, count=300):
        self.url = url
        self.count = count
        self.category = category
        self.save_dir = os.path.join(settings.CAPTCHA_STORE, "%d" % self.category)
        if os.path.exists(self.save_dir) is False:
            os.makedirs(self.save_dir, 0775)
        
    def download(self):
        finished = Captcha.objects.filter(category=self.category).count()
        if finished > self.count:
            return 
        
        for i in range(0, self.count - finished):
            r = requests.get(self.url, timeout=60)
            if r.status_code != 200:
                logging.warn("request %s failed, status code %d", self.url, r.status_code)
                continue
            
            image_hash = hashlib.md5(r.content).hexdigest()
            path = os.path.join(self.save_dir, image_hash)
            if os.path.exists(path):
                logging.warn("%d: %s exists", i, image_hash)
                continue
            
            with open(path, "w") as f:
                f.write(r.content)
                
            captcha = Captcha.objects.create(url=self.url, category=self.category, image_hash=image_hash)
            logging.debug("Download %d, image id %s, captcha id %d, category %d", i, image_hash, captcha.id, self.category)
        
        
    

class Command(BaseCommand):
    args = ""
    help = "Obtain all captcha."
    
    def __init__(self):
        self.categories = Category.objects.all()
    
    @wrapper_raven
    def handle(self, *args, **options):
        pool = multiprocessing.Pool(processes=2)
        pool.map(run, self.categories)
        

def run(category):
    if not category.url:
        return -1
    
    downloader = DownloadCaptcha(category.url, category.id, category.max_number)
    try:
        downloader.download()
    except:
        logging.warn("failed to download category %d: %s", downloader.category, traceback.format_exc(10))
        
    return downloader.category
    