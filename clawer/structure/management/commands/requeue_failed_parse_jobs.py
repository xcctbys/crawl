import rq
from django.conf import settings
from structure.structure import Consts, StructureGenerator, parser_func
from html5helper.utils import wrapper_raven
from django.core.management.base import BaseCommand
from structure.models import CrawlerAnalyzedData
from collector.models import CrawlerTask, CrawlerDownloadData
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

def refresh_failed_jobs():
	count = 0
	failed_tasks = CrawlerTask.objects(status = 6)
	print "% d crawlertasks failed parsing now" % len(failed_tasks)
	for failed_task in failed_tasks:
		failed_task.update(status = 5)
		count += 1
	print "Refresh % d failed crawlertasks (Which failed for over max retry times)" % count
	logging.info("Refresh % d failed crawlertasks (Which failed for over max retry times)" % count)

def requeue_failed_jobs():
	structure_generator = StructureGenerator()
	failed_tasks = CrawlerTask.objects(status = 6)
	
	if failed_tasks == None:
		logging.info("No failed parse jobs at this time")
		print "No failed parse jobs at this time"
	else:
		print "Current number of failed parse jobs: %d" % len(failed_tasks)
	count = 0
	deleted_data_count = 0
	for failed_task in failed_tasks:
		failed_data = CrawlerAnalyzedData.objects(crawler_task = failed_task).first()
		if failed_data.retry_times >= 3:
			failed_data.delete()
			deleted_data_count += 1
		else:
			failed_job_source_data = structure_generator.get_task_source_data(failed_task)
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
				logging.error("Cannot requeue parse job because the queue: %s is full" % q.name)
				print "Cannot requeue parse job because the queue: %s is full" % q.name
				return None
			else:
				q.enqueue_call(func = parser_func, args = [failed_job_source_data])
				failed_data_retry_times = failed_data.retry_times + 1
				failed_data.update(retry_times = failed_data_retry_times)
            		count += 1
            		failed_task.update(status = 5)
	print "%d failed parse jobs requeued successfully!" %count
	if deleted_data_count > 0:
		print "Delete % d data from crawlertasks which failed for over max retry times" % deleted_data_count

def run():
	print "Requeuing failed jobs..."
	requeue_failed_jobs()

class Command(BaseCommand):
    # @wrapper_raven
    def handle(self, *args, **options):
        run()