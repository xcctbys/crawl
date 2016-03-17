# coding=utf-8

from django.core.management.base import BaseCommand

from html5helper.utils import wrapper_raven
from captcha.models import Category

    

class Command(BaseCommand):
    args = ""
    help = "Obtain all captcha."
    
    def __init__(self):
        self.urls = Category.full_choices
    
    @wrapper_raven
    def handle(self, *args, **options):
        for item in Category.full_choices:
            Category.objects.create(id=item[0], name=item[1], url=item[2], max_number=item[3])
        
    