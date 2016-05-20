import rq
from django.conf import settings
from structure.structure import Consts, StructureGenerator, StructureConfig, ExtracterGenerator
from html5helper.utils import wrapper_raven
from django.core.management.base import BaseCommand
from structure.models import CrawlerAnalyzedData CrawlerExtracterInfo
from collector.models import CrawlerTask
from mongoengine import *
import logging
import redis

try:
    redis_url = settings.STRUCTURE_REDIS
except:
    redis_url = None

connection = redis.Redis.from_url(redis_url) if redis_url else redis.Redis()
too_high_queue = rq.Queue(Consts.QUEUE_PRIORITY_TOO_HIGH, connection = connection)
high_queue = rq.Queue(Consts.QUEUE_PRIORITY_HIGH, connection = connection)
normal_queue = rq.Queue(Consts.QUEUE_PRIORITY_NORMAL, connection = connection)
low_queue = rq.Queue(Consts.QUEUE_PRIORITY_LOW, connection = connection)

def requeue_failed_jobs():
	structure_generator = StructureGenerator()
	failed_tasks = CrawlerTask.objects(status = 8)
	
	if failed_tasks == None:
		logging.info("No failed extract jobs at this time")
		print "No failed extract jobs at this time"
	else:
		print "Current number of failed extract jobs: %d" % len(failed_tasks)
	count = 0

	for failed_task in failed_tasks:
		failed_data = CrawlerExtracterInfo.objects(crawler_task = failed_task).first()
		if failed_data.retry_times >= 3:
			pass
		else:
			failed_job_data = structure_generator.get_task_analyzed_data(failed_task)
                        structureconfig = StructureConfig.objects(job=data.crawler_task.job).first()
                        failed_job_conf = structureconfig.extracter.extracter_config
			failed_job_priority = structure_generator.get_task_priority(failed_task)
			q = None
			if failed_job_priority == Consts.QUEUE_PRIORITY_TOO_HIGH:
				q = too_high_queue
			elif failed_job_priority == Consts.QUEUE_PRIORITY_HIGH:
				q = high_queue
			elif failed_job_priority == Consts.QUEUE_PRIORITY_NORMAL:
				q = normal_queue
			elif failed_job_priority == Consts.QUEUE_PRIORITY_LOW:
				q = low_queue
			else:
				q = low_queue
			if (q.count + 1) > Consts.QUEUE_MAX_LENGTH:
				logging.error("Cannot requeue extract job because the queue: %s is full" % q.name)
				print "Cannot requeue extract job because the queue: %s is full" % q.name
				return None
			else:
				q.enqueue_call(func = ExtracterGenerator.extracter, args = [failed_job_conf, failed_job_data])
				failed_data_retry_times = failed_data.retry_times + 1
				failed_data.update(retry_times = failed_data_retry_times)
            		count += 1
            		failed_task.update(status = 7)
	print "%d failed extract jobs requeued successfully!" %count

def run():
	print "Requeuing failed jobs..."
	requeue_failed_jobs()

class Command(BaseCommand):
    # @wrapper_raven
    def handle(self, *args, **options):
        run()
