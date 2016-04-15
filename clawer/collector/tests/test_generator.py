#encoding=utf-8
import json
import os
import datetime
import logging
import unittest

# from django.test.client import Client
# from django.core.urlresolvers import reverse
# from django.contrib.auth.models import User as DjangoUser, Group

# from clawer.management.commands import task_generator_run, task_analysis, task_analysis_merge, task_dispatch
# from clawer.utils import UrlCache, Download, MonitorClawerHour
# from clawer.utils import DownloadClawerTask

from django.test import TestCase
from django.conf import settings
from collector.models import Job, CrawlerTask, CrawlerTaskGenerator, CrawlerGeneratorErrorLog, CrawlerGeneratorAlertLog, CrawlerGeneratorCronLog
# from mongoengine import *
from mongoengine.context_managers import switch_db
from collector.utils_generator import DataPreprocess, GeneratorDispatch, GeneratorQueue, GenerateCrawlerTask, SafeProcess
from redis import Redis
from rq import Queue
import subprocess

class TestMongodb(TestCase):
    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_job_save(self):
        # with switch_db(Job, 'source') as Job:
        job = Job(name='job')
        job.save()
        count = Job.objects(name='job').count()
        self.assertGreater(count, 0)
        # job.delete()

    def test_task_save(self):
        jobs = Job.objects(id='570ded84c3666e0541c9e8d9').first()
        task = CrawlerTask(uri='http://www.baidu.com')
        task.job=jobs
        task.save()
        result = CrawlerTask.objects.first()
        self.assertTrue(result)
        jobs.delete()

    def test_get_generator_with_job_id(self):
        job_id = '570f73f6c3666e0af4a9efad'
        generator_object =  CrawlerTaskGenerator.objects(job=job_id ,status = 4).first()
        self.assertTrue(generator_object)

    def test_job_find_by_name(self):
        job = Job.objects(name='job')
        self.assertGreater(len(job), 0)

    def test_job_find_by_id(self):
        job = Job.objects(id='570ded84c3666e0541c9e8d9')
        self.assertGreater(len(job), 0)

    def test_job_find_by_generator(self):
        generator = CrawlerTaskGenerator.objects.first()
        job = generator.job
        print job
        print job.id
        print job.priority
        self.assertEqual(job.id, '570f73f6c3666e0af4a9efad')

    def test_job_delete(self):
        job = Job.objects(name='job')
        job.delete()
        count = Job.objects(name='job').count()
        self.assertEqual(count, 0)

    def test_job_with_id(self):
        valid_id = "570ded84c3666e0541c9e8d9"
        invalid_id = "rfwearewrfaewrfaeawrarew"
        valid_job = Job.objects().with_id(valid_id)
        self.assertTrue(valid_job)
        try:
            invalid_job = Job.objects.with_id(invalid_id)
            self.assertTrue(invalid_job)
        except Exception as e:
            pass
    def test_generator_code_dir(self):
        generator = CrawlerTaskGenerator.objects.first()
        path = generator.code_dir()
        self.assertEqual(path, "/data/media/codes")

    def test_generator_product_path(self):
        generator = CrawlerTaskGenerator.objects.first()
        path = generator.product_path()
        self.assertTrue(path)

class TestPreprocess(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.job = Job(name='job')
        self.job.save()
        self.pre = DataPreprocess(job_id= self.job.id)

    def tearDown(self):
        TestCase.tearDown(self)
        self.job.delete()

    def test_read_from_string(self):
        inputs = """
        http://www.baidu.com
        https://www.baidu.com
        ftp://www.baidu.com
        ftps://www.baidu.com
        enterprise://baidu.com

        www.baidu.com
        baidu.com
        httd://baidu.com
        baidu.com,http://www.baidu.com
        http://www.baidu.com,http://baidu.com
        """
        uris = self.pre.read_from_strings(inputs, schemes=['enterprise'])
        print uris
        self.assertEqual(len(uris), 5)

    def test_save_text(self):
        inputs = """
        http://www.baidu.com
        """
        result = self.pre.save_text(inputs)

        self.assertTrue(result)
        result = CrawlerTask.objects.first()
        print result
        self.assertTrue(result)

    @unittest.skip("skipping read from file")
    def test_read_from_file(self):
        filename = "/Users/princetechs5/Documents/uri.csv"
        uris_string = ""
        with open(filename, 'r') as f:
            uris_string= f.read()
        self.assertTrue( uris_string)

    def test_read_from_file_and_not_save(self):
        filename = "/Users/princetechs5/Documents/uri.csv"
        uris_string = ""
        with open(filename, 'r') as f:
            uris_string= f.read()
        uris = self.pre.read_from_strings(uris_string, schemes=[])
        print uris
        self.assertListEqual( ['http://www.baidu.com', 'http://www.google.com'], uris)

    def test_save_script(self):
        script = """
            print json.dumps({'uri':"http://www.baidu.com"})
            """
        cron = "*/3 * * * *"
        result = self.pre.save_script(script, cron)
        self.assertTrue(result)

        count = CrawlerTaskGenerator.objects(code= script).count()
        self.assertGreater(count, 0)


    def test_save_with_text(self):
        inputs = """
        search://baidu.com

        www.baidu.com
        baidu.com
        httd://baidu.com
        """
        schemes= ['search']

        self.pre.save(text = inputs, settings={'schemes': schemes})
        uris = CrawlerTask.objects(uri = "search://baidu.com")
        self.assertEqual(len(uris), 1)
        for uri in uris:
            uri.delete()


    def test_save_with_script(self):
        script = """
            print json.dumps({'uri':"http://www.baidu.com"})
            """
        cron = "*/3 * * * *"

        self.pre.save(script= script, settings={'cron': cron})
        script_doc = CrawlerTaskGenerator.objects.first()
        self.assertTrue(script_doc)
        # script_doc.delete()

class TestDispatch(TestCase):
    """Test for GeneratorDispatch"""
    def setUp(self):
        TestCase.setUp(self)
        # self.job = Job(name='job')
        # self.job.save()
        # gd = GeneratorDispatch(job_id = self.job.id)
        self.gd = GeneratorDispatch(job_id = '570f73f6c3666e0af4a9efad')

    def tearDown(self):
        TestCase.tearDown(self)
        # self.job.delete()

    def test_get_generator_object(self):
        generator_object = self.gd.get_generator_object()
        print generator_object
        self.assertTrue(generator_object)
    def test_dispatch_uri(self):
        queue = self.gd.dispatch_uri()
        print queue
        self.assertTrue(queue)

class TestGenerateTask(TestCase):
    """ Test for GenerateCrawlerTask """
    def setUp(self):
        TestCase.setUp(self)
        # script = """
        #     print json.dumps({'uri':"http://www.baidu.com"})
        # """
        generator = CrawlerTaskGenerator.objects.first()
        self.gt = GenerateCrawlerTask(generator)

    def tearDown(self):
        TestCase.tearDown(self)


    def test_generate_task(self):
        result = self.gt.generate_task()
        self.assertTrue(result)

    def test_generate_task_failed(self):
        result = self.gt.generate_task_failed()
        self.assertTrue(result)

class TestSafeProcess(TestCase):
    """ Test for SafeProcess Class """
    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_popen(self):
        child1 = subprocess.Popen(["ls","-l"], stdout=subprocess.PIPE)
        child2 = subprocess.Popen(["wc"], stdin=child1.stdout,stdout=subprocess.PIPE)
        out = child2.communicate()
        print(out)
        self.assertTrue(out)

    def test_popen_python(self):
        path = "~/crawler/cr-clawer/clawer/clawer/media/codes/570f73f6c3666e0af4a9efad_product.py"
        out_path = "/tmp/task_generator_570f6bc5c3666e095ed99d90"
        out_f = open(out_path, "w")
        process = subprocess.Popen(['~/Documents/virtualenv/bin/python', path])
        self.assertTrue(process)

    def test_run(self):
        path = "/Users/princetechs5/crawler/cr-clawer/clawer/clawer/media/codes/570f73f6c3666e0af4a9efad_product.py"
        out_f = "/tmp/task_generator_570f6bc5c3666e095ed99d90"
        safe_process = SafeProcess(['~/Documents/virtualenv/bin/python', path], stdout=out_f, stderr=subprocess.PIPE)
        try:
            p = safe_process.run(1800)
        except OSError , e:
            print type(e)
            # safe_process.failed(e.child_traceback)
        except Exception, e:
            print type(e)
            # safe_process.failed(e)
        self.assertNotEqual(p,0)





