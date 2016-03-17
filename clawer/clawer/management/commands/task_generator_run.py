# coding=utf-8

from django.core.management.base import BaseCommand

from html5helper.utils import wrapper_raven
from clawer.models import ClawerTaskGenerator
from clawer.utils import  GenerateClawerTask



def run(task_generator_id):
    task_generator = ClawerTaskGenerator.objects.get(id=task_generator_id)
    generate_clawer_task = GenerateClawerTask(task_generator)
    return generate_clawer_task.run()
    
                

class Command(BaseCommand):
    args = "task_generator_id"
    help = "Run task generator"
    
    @wrapper_raven
    def handle(self, *args, **options):
        task_generator_id = int(args[0])
        run(task_generator_id)