#encoding=utf-8
import json
import os
import datetime
import logging
import unittest
import sys
from django.test import TestCase
from django.conf import settings
# from collector.models_download import CrawlerDownloadSetting, CrawlerDownloadType, CrawlerDownload
# from mongoengine import *
from redis import Redis
from rq import Queue
import commands
import subprocess
# from storage.models import Job
from collector.models import CrawlerDownloadType, CrawlerTask, Job, CrawlerTaskGenerator, CrawlerDownloadSetting, CrawlerDownload

class TestMongodb(TestCase):
	def setUp(self):
		TestCase.setUp(self)

	def tearDown(self):
		TestCase.tearDown(self)

	def insert_jobs(self):

		onetype = CrawlerDownloadType(language='python', is_support=True)
		onetype.save()

		job1 = Job(name='1', info='2', customer='ddd', priority=-1)
		job1.save()
		job2 = Job(name='2', priority=0)
		job2.save()
		job3 = Job(name='3', priority=2)
		job3.save()
		job4 = Job(name='4', priority=3)
		job4.save()

		ctg1 = CrawlerTaskGenerator(job=job1, code='echo hello1', cron='* * * * *')
		ctg1.save()
		ctg2 = CrawlerTaskGenerator(job=job2, code='echo hello2', cron='* * * * *')
		ctg2.save()
		ctg3 = CrawlerTaskGenerator(job=job3, code='echo hello3', cron='* * * * *')
		ctg3.save()
		ctg4 = CrawlerTaskGenerator(job=job4, code='echo hello4', cron='* * * * *')
		ctg4.save()

		CrawlerTask(job=job1, task_generator=ctg1, uri='http://www.baidu.com', args='i', from_host='1').save()
		CrawlerTask(job=job3, task_generator=ctg1, uri='http://www.fishc.com', args='l', from_host='1').save()
		CrawlerTask(job=job4, task_generator=ctg1, uri='https://xueqiu.com/', args='o', from_host='2').save()
		CrawlerTask(job=job2, task_generator=ctg1, uri='http://www.jb51.net/article/47957.htm', args='v', from_host='3').save()

		codestr1 = open('/Users/princetechs3/my_code/xuqiu.py','r').read()
		CrawlerDownload(job=job1, code=codestr1, types=onetype).save()
		CrawlerDownload(job=job2, code=codestr1, types=onetype).save()
		CrawlerDownload(job=job3, code=codestr1, types=onetype).save()
		CrawlerDownload(job=job4, code=codestr1, types=onetype).save()

		cdc1 =CrawlerDownloadSetting(job=job1, proxy='122', cookie='22', dispatch_num=50)
		cdc1.save()
		cdc2 = CrawlerDownloadSetting(job=job2, proxy='2', cookie='3', dispatch_num=60)
		cdc2.save()
		cdc3 = CrawlerDownloadSetting(job=job3, proxy='32', cookie='21', dispatch_num=70)
		cdc3.save()
		cdc4 = CrawlerDownloadSetting(job=job4, proxy='312', cookie='221', dispatch_num=100)
		cdc4.save()

		# jobs = Job.objects(status=Job.STATUS_ON).order_by('+priority')
		# for job in jobs:
		#     print job.priority


		# tasks = CrawlerTask.objects(status=CrawlerTask.STATUS_LIVE).order_by("+job.priority")[:settings.MAX_TOTAL_DISPATCH_COUNT_ONCE]
		# for task in tasks:
		#     print task.job.priority

	def delete_jobs(self):

		CrawlerDownloadType.objects.delete()
		Job.objects.delete()
		CrawlerTaskGenerator.objects.delete()
		CrawlerTask.objects.delete()
		CrawlerDownload.objects.delete()
		CrawlerDownloadSetting.objects.delete()

	def exec_command(self, commandstr):
		print commandstr
		sys.path.append('/Users/princetechs3/my_code')
		c = compile(commandstr, "", 'exec')
		exec c
		print result


	def test_get_task(self):
		self.delete_jobs()
		self.insert_jobs()
		self.assertEqual(CrawlerDownloadType.objects.count(), 1)
		self.assertEqual(Job.objects.count(), 4)
		self.assertEqual(CrawlerTaskGenerator.objects.count(), 4)
		self.assertEqual(CrawlerTask.objects.count(), 4)
		self.assertEqual(CrawlerDownload.objects.count(), 4)
		self.assertEqual(CrawlerDownloadSetting.objects.count(), 4)

		jobs = Job.objects(status=Job.STATUS_ON).order_by('+priority')
		self.assertTrue(jobs)
		for job in jobs:
			tasks = CrawlerTask.objects(job=job)
			self.assertTrue(tasks)

		self.delete_jobs()
		count = Job.objects.count()
		self.assertEqual(count, 0)



	def test_download(self):
		sys.path.append('/Users/princetechs3/my_code')

		onetype = CrawlerDownloadType(language='python')
		onetype.save()
		job1 = Job(name='1', info='2', customer='ddd', priority=-1)
		job1.save()
		ctg1 = CrawlerTaskGenerator(job=job1, code='echo hello1', cron='* * * * *')
		ctg1.save()
		ct1 = CrawlerTask(job=job1, task_generator=ctg1, uri='http://www.baidu.com', args='i', from_host='1')
		ct1.save()
		codestr1 = open('/Users/princetechs3/my_code/code1.py','r').read()
		cd1 =CrawlerDownload(job=job1, code=codestr1, types=onetype)
		cd1.save()
		cds1 =CrawlerDownloadSetting(job=job1, proxy='122', cookie='22', dispatch_num=50)
		cds1.save()

		job = Job.objects(status=Job.STATUS_ON)[0]
		self.assertTrue(job)
		task = CrawlerTask.objects(job=job)[0]
		self.assertTrue(task)

		cd = CrawlerDownload.objects(job=task.job)[0]
		self.assertTrue(cd)

		self.assertTrue(cd.code)
		with open('/Users/princetechs3/my_code/jobcode1.py', 'w') as f:
			f.write(cd.code)
		self.exec_command('import jobcode1;jobcode1.run(%s)' % "'http://www.baidu.com'")
		# print cd.code
		self.assertEqual(cd.types.language, 'python')
		print cd.types.language

	def test_curl(self):
		result = commands.getstatusoutput('curl http://www.baidu.com')
		print result

	def test_insert_python_job(self):
		onetype = CrawlerDownloadType(language='python', is_support=True)
		onetype.save()
		job1 = Job(name='1', info='2', customer='ddd', priority=-1)
		job1.save()
		ctg1 = CrawlerTaskGenerator(job=job1, code='echo hello1', cron='* * * * *')
		ctg1.save()
		ct1 = CrawlerTask(job=job1, task_generator=ctg1, uri='http://www.baidu.com', args='i', from_host='1')
		ct1.save()
		codestr1 = open('/Users/princetechs3/my_code/code1.py','r').read()
		cd1 =CrawlerDownload(job=job1, code=codestr1, types=onetype)
		cd1.save()
		cds1 =CrawlerDownloadSetting(job=job1, proxy='122', cookie='22', dispatch_num=50)
		cds1.save()

	def test_insert_shell_job(self):
		onetype = CrawlerDownloadType(language='shell', is_support=True)
		onetype.save()
		job1 = Job(name='1', info='2', customer='ddd', priority=-1)
		job1.save()
		ctg1 = CrawlerTaskGenerator(job=job1, code='echo hello1', cron='* * * * *')
		ctg1.save()
		ct1 = CrawlerTask(job=job1, task_generator=ctg1, uri='http://www.baidu.com', args='i', from_host='1')
		ct1.save()
		codestr2 = open('/Users/princetechs3/my_code/code2.sh','r').read()
		cd1 =CrawlerDownload(job=job1, code=codestr2, types=onetype)
		cd1.save()
		cds1 =CrawlerDownloadSetting(job=job1, proxy='122', cookie='22', dispatch_num=50)
		cds1.save()

	def test_insert_curl_job(self):
		onetype = CrawlerDownloadType(language='curl', is_support=True)
		onetype.save()
		job1 = Job(name='1', info='2', customer='ddd', priority=-1)
		job1.save()
		ctg1 = CrawlerTaskGenerator(job=job1, code='echo hello1', cron='* * * * *')
		ctg1.save()
		ct1 = CrawlerTask(job=job1, task_generator=ctg1, uri='http://www.fishc.com', args='i', from_host='1')
		ct1.save()
		# codestr2 = open('/Users/princetechs3/my_code/code2.sh','r').read()
		cd1 =CrawlerDownload(job=job1, code='codestr2', types=onetype)
		cd1.save()
		cds1 =CrawlerDownloadSetting(job=job1, proxy='122', cookie='22', dispatch_num=50)
		cds1.save()

	def test_insert_other_job(self):
		onetype = CrawlerDownloadType(language='other', is_support=True)
		onetype.save()
		job1 = Job(name='1', info='2', customer='ddd', priority=-1)
		job1.save()
		ctg1 = CrawlerTaskGenerator(job=job1, code='echo hello1', cron='* * * * *')
		ctg1.save()
		ct1 = CrawlerTask(job=job1, task_generator=ctg1, uri='http://www.fishc.com', args='i', from_host='1')
		ct1.save()
		# codestr2 = open('/Users/princetechs3/my_code/code2.sh','r').read()
		cd1 =CrawlerDownload(job=job1, code='codestr2', types=onetype)
		cd1.save()
		cds1 =CrawlerDownloadSetting(job=job1, proxy='122', cookie='22', dispatch_num=50)
		cds1.save()

	def test_get_max_dispatch(self):
		onetype = CrawlerDownloadType(language='other', is_support=True)
		onetype.save()
		job1 = Job(name='1', info='2', customer='ddd', priority=-1)
		job1.save()
		ctg1 = CrawlerTaskGenerator(job=job1, code='echo hello1', cron='* * * * *')
		ctg1.save()
		ct1 = CrawlerTask(job=job1, status=CrawlerTask.STATUS_FAIL, task_generator=ctg1, uri='http://www.fishc.com', args='i', from_host='1')
		ct1.save()
		# codestr2 = open('/Users/princetechs3/my_code/code2.sh','r').read()
		cd1 =CrawlerDownload(job=job1, code='codestr2', types=onetype)
		cd1.save()
		cds1 =CrawlerDownloadSetting(job=job1, proxy='122', cookie='22', dispatch_num=50)
		cds1.save()

		max_retry_times=1
		dispatch_num=1
		down_tasks = CrawlerTask.objects(status=CrawlerTask.STATUS_FAIL, retry_times__lte=max_retry_times)[:dispatch_num]
		self.assertTrue(down_tasks)

	def test_insert_4_jobs(self):
		self.test_insert_other_job()
		self.test_insert_curl_job()
		self.test_insert_shell_job()
		self.test_insert_python_job()

	def test_insert_enterprise_job(self):
		onetype = CrawlerDownloadType(language='other', is_support=True)
		onetype.save()
		job1 = Job(name='1', info='2', customer='ddd', priority=-1)
		job1.save()
		ctg1 = CrawlerTaskGenerator(job=job1, code='echo hello1', cron='* * * * *')
		ctg1.save()
		ct1 = CrawlerTask(job=job1, task_generator=ctg1, uri='enterprise://重庆/重庆理必易投资管理有限公司/500905004651063/', args='i', from_host='1')
		ct1.save()
		# codestr2 = open('/Users/princetechs3/my_code/code2.sh','r').read()
		cd1 =CrawlerDownload(job=job1, code='codestr2', types=onetype)
		cd1.save()
		cds1 =CrawlerDownloadSetting(job=job1, proxy='122', cookie='22', dispatch_num=50)
		cds1.save()
		pass








