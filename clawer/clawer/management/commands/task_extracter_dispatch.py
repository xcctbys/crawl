# coding=utf-8
from django.core.management.base import BaseCommand
from html5helper.utils import wrapper_raven
from structure.structure import ExtracterGenerator, ExecutionTasks


def run():
    extractergenerator = ExtracterGenerator()
    extracter_task_queues = extractergenerator.assign_tasks()
    return extracter_task_queues


class Command(BaseCommand):
    args = ""
    help = "Dispatch Extracter Task"

    #@wrapper_raven
    def handle(self, *args, **options):
        run()
