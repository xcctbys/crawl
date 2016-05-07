# coding=utf-8
from optparse import make_option
from django.core.management.base import BaseCommand
from html5helper.utils import wrapper_raven
from collector.models import Job, CrawlerTask, CrawlerDownloadSetting, CrawlerDispatchAlertLog
from django.conf import settings
from collector.util_downloader import download_clawer_task
import redis
import rq
import threading
import datetime
import time
import socket
import os
import sys
from multiprocessing import Pool

try:
	redis_url = settings.URL_REDIS
except:
	redis_url = None

redis_conn = redis.Redis.from_url(redis_url) if redis_url else redis.Redis()
from mongoengine import connect

q_down_super = rq.Queue('down_super', connection=redis_conn)
q_down_low = rq.Queue('down_low', connection=redis_conn)
q_down_mid = rq.Queue('down_mid', connection=redis_conn)
q_down_high = rq.Queue('down_high', connection=redis_conn)

class SentryClient(object):
	def __init__(self):
		self.client = None
		if hasattr(settings, 'RAVEN_CONFIG'):
			self.client = raven.Client(dsn=settings.RAVEN_CONFIG["dsn"])
		
	def capture(self):
		if not self.client:
			return
		self.client.captureException()

def write_dispatch_success_log(job, reason):
	print reason
	cdal = CrawlerDispatchAlertLog(job=job, types=2, reason=reason, hostname=str(socket.gethostname()))
	cdal.content_bytes = sys.getsizeof(cdal)
	cdal.save()
	pass
def write_dispatch_failed_log(job, reason):
	print reason
	cdal = CrawlerDispatchAlertLog(job=job, types=3, reason=reason, hostname=str(socket.gethostname()))
	cdal.content_bytes = sys.getsizeof(cdal)
	cdal.save()
	pass
def write_dispatch_error_log(job, reason):
	print reason
	cdal = CrawlerDispatchAlertLog(job=job, types=3, reason=reason, hostname=str(socket.gethostname()))
	cdal.content_bytes = sys.getsizeof(cdal)
	cdal.save()
	pass
def write_dispatch_alter_log(job, reason):
	print reason
	cdal = CrawlerDispatchAlertLog(job=job, types=1, reason=reason, hostname=str(socket.gethostname()))
	cdal.content_bytes = sys.getsizeof(cdal)
	cdal.save()
	pass


def dispatch_use_pool(task):
	try:
		dispatch_num = CrawlerDownloadSetting.objects(job=task.job)[0].dispatch_num
		if dispatch_num == 0:
			write_dispatch_alter_log(job=task.job, reason='dispatch_num is 0')
			return
		# print type(dispatch_num), dispatch_num
		max_retry_times = CrawlerDownloadSetting.objects(job=task.job)[0].max_retry_times
		if settings.OPEN_CRAWLER_FAILED_ONLY:
			down_tasks = CrawlerTask.objects(status=CrawlerTask.STATUS_FAIL)[:dispatch_num]
		else:
			if datetime.datetime.now().minute >= 56:
				#max_retry_times <= max_retry_times
				down_tasks = CrawlerTask.objects(status=CrawlerTask.STATUS_FAIL, retry_times__lte=max_retry_times)[:dispatch_num]
			else:
				down_tasks = CrawlerTask.objects(status=CrawlerTask.STATUS_LIVE)[:dispatch_num]
			if len(down_tasks)==0:
				# write_dispatch_alter_log(job=task.job, reason='get down_tasks len is 0')
				return
	except Exception as e:
		write_dispatch_error_log(job=task.job, reason=str(e))
		# sentry = SentryClient()
		# sentry.capture()
		return

	for task in down_tasks:
		priority = task.job.priority
		try:
			if priority == -1:
				if len(q_down_super) >= settings.Q_DOWN_SUPER_LEN:
					write_dispatch_alter_log(job=task.job, reason='q_down_super lens get maxlen')
					continue
				q_down_super.enqueue(download_clawer_task, args=[task] )
			elif priority == 0:
				if len(q_down_high) >= settings.Q_DOWN_HIGH_LEN:
					write_dispatch_alter_log(job=task.job, reason='q_down_high lens get maxlen')
					continue
				q_down_high.enqueue(download_clawer_task, args=[task], at_front=True)
			elif priority == 1:
				if len(q_down_high) >= settings.Q_DOWN_HIGH_LEN:
					write_dispatch_alter_log(job=task.job, reason='q_down_high lens get maxlen')
					continue
				q_down_high.enqueue(download_clawer_task, args=[task], at_front=False)
			elif priority == 2:
				if len(q_down_mid) >= settings.Q_DOWN_MID_LEN:
					write_dispatch_alter_log(job=task.job, reason='q_down_mid lens get maxlen')
					continue
				q_down_mid.enqueue(download_clawer_task, args=[task], at_front=True)
			elif priority == 3:
				if len(q_down_mid) >= settings.Q_DOWN_MID_LEN:
					write_dispatch_alter_log(job=task.job, reason='q_down_mid lens get maxlen')
					continue
				q_down_mid.enqueue(download_clawer_task, args=[task], at_front=False)
			elif priority == 4:
				if len(q_down_low) >= settings.Q_DOWN_LOW_LEN:
					write_dispatch_alter_log(job=task.job, reason='q_down_low lens get maxlen')
					continue
				q_down_low.enqueue(download_clawer_task, args=[task], at_front=True)
			elif priority == 5:
				if len(q_down_low) >= settings.Q_DOWN_LOW_LEN:
					write_dispatch_alter_log(job=task.job, reason='q_down_low lens get maxlen')
					continue
				q_down_low.enqueue(download_clawer_task, args=[task], at_front=False)
			task.status = CrawlerTask.STATUS_DISPATCH
			task.save()
			# write_success_dispatch_log()
			write_dispatch_success_log(job=task.job, reason='success')
		except Exception as e:
			# write_fail_dispatch_log()
			write_dispatch_failed_log(job=task.job, reason=str(e))


def force_exit():
	pgid = os.getpgid(0)
	if pool is not None:
		pool.terminate()
	os.killpg(pgid, 9)
	os._exit(1)


def run():
	# timer = threading.Timer(settings.DISPATCH_USE_POOL_TIMEOUT, force_exit)
	# timer.start()
	print 'begin'
	if settings.DISPATCH_BY_PRIORITY:
		total = 0
		pool = Pool()
		jobs = Job.objects(status=Job.STATUS_ON).order_by('+priority')
		for job in jobs:
			# print 'priority:',job.priority
			count = CrawlerTask.objects(job=job).count()
			if count == 0:
				continue
			total += count
			# print 'total:', total
			if total > settings.MAX_TOTAL_DISPATCH_COUNT_ONCE:
				break
			tasks = CrawlerTask.objects(job=job)
			for task in tasks:
				dispatch_use_pool(task)
			# pool.map(dispatch_use_pool, tasks)
			# pool.close()
			# pool.join()
		# tasks = CrawlerTask.objects(status=CrawlerTask.STATUS_LIVE).order_by('job.priority')[:settings.MAX_TOTAL_DISPATCH_COUNT_ONCE]
	elif settings.DISPATCH_BY_HOSTNAME:
		#TODO:按照主机进行分发
		pass
	


def empty_all():
	pass


class Command(BaseCommand):
	args = ""
	help = "Dispatch clawer task"

	# @wrapper_raven
	def handle(self, *args, **options):
		run()
