#encoding=utf-8
import json
import os
from datetime import datetime
import logging
import unittest
from croniter import croniter

# from django.test.client import Client
# from django.core.urlresolvers import reverse
# from django.contrib.auth.models import User as DjangoUser, Group

# from clawer.management.commands import task_generator_run, task_analysis, task_analysis_merge, task_dispatch
# from clawer.utils import UrlCache, Download, MonitorClawerHour
# from clawer.utils import DownloadClawerTask

from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from django.utils.six import StringIO

from collector.models import Job, CrawlerTask, CrawlerTaskGenerator, CrawlerGeneratorLog, CrawlerGeneratorAlertLog, CrawlerGeneratorCronLog
# from mongoengine import *
from mongoengine.context_managers import switch_db
from collector.utils_generator import DataPreprocess, GeneratorDispatch, GeneratorQueue, GenerateCrawlerTask, SafeProcess, CrawlerCronTab
from collector.utils_generator import force_exit, exec_command
from collector.utils_cron import CronTab
from redis import Redis
from rq import Queue
import subprocess

class TestGeneratorInstall(TestCase):
    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_command(self):
        out = StringIO()
        call_command('task_generator_install', stdout=out)
        self.assertIn('Expected output', out.getvalue())


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
        job.delete()

    def test_task_save(self):
        jobs = Job.objects(id='570ded84c3666e0541c9e8d9').first()
        task = CrawlerTask(uri='http://www.baidu.com')
        task.job=jobs
        task.save()
        result = CrawlerTask.objects.first()
        self.assertTrue(result)
        task.delete()

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

    def test_task_delete_all(self):
        count = CrawlerTask.objects.delete()
        self.assertGreater(count, 0)

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
        script = """import json\nprint json.dumps({'uri':"http://www.baidu.com"})"""
        cron = "*/3 * * * *"

        self.pre.save(script= script, settings={'cron': cron})
        script_doc = CrawlerTaskGenerator.objects.first()
        self.assertTrue(script_doc)
        # script_doc.delete()

class TestDispatch(TestCase):
    """Test for GeneratorDispatch"""
    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)
        # self.job.delete()
    def test_job_is_found(self):
        gd = None
        try:
            gd = GeneratorDispatch(job_id = "570f73f6c3666e0af4a9efad")
        except KeyError, e:
            self.assertFalse(e)
        self.assertTrue(gd)

    def test_job_is_not_found(self):
        gd = None
        try:
            gd = GeneratorDispatch(job_id = "Not Found")
        except KeyError, e:
            self.assertTrue(e)
        self.assertFalse(gd)


    def test_get_generator_object(self):
        self.gd = GeneratorDispatch(job_id = '570f73f6c3666e0af4a9efad')
        generator_object = self.gd.get_generator_object()
        print generator_object
        self.assertTrue(generator_object)

    def test_dispatch_uri(self):
        self.gd = GeneratorDispatch(job_id = '570f73f6c3666e0af4a9efad')
        queue = self.gd.run()
        print queue
        self.assertTrue(queue)

class TestGenerateTask(TestCase):
    """ Test for GenerateCrawlerTask """
    def setUp(self):
        TestCase.setUp(self)
        # script = """import json\nprint json.dumps({'uri':"http://www.baidu.com"})"""
        # generator = CrawlerTaskGenerator.objects.first()
        # self.gt = GenerateCrawlerTask(generator)
        # task_count = CrawlerTask.objects().delete()
        # print "task count = %d" %(task_count)
        # log_count = CrawlerGeneratorLog.objects().delete()
        # print "generator log count = %d"%(log_count)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_settings_shell(self):
        SHELL = os.environ.get('SHELL', '/bin/bash')
        print SHELL
        tools = settings.__dict__.get('SHELL', settings.PYTHON)
        self.assertEqual(tools, settings.SHELL)

    def test_generate_task_shell(self):
        job = Job( name = 'shell', status= 1, priority =1)
        job.save()

        script = """#!/bin/bash\necho "{'uri':'http://www.shell.com'}"\n """
        cron = "* * * * *"
        generator = CrawlerTaskGenerator(job = job, code = script, cron = cron, code_type= CrawlerTaskGenerator.TYPE_SHELL, status= CrawlerTaskGenerator.STATUS_ON)
        generator.save()

        task_count = CrawlerTask.objects.delete()
        print "task count = %d" %(task_count)
        log_count = CrawlerGeneratorLog.objects().delete()
        print "generator log count = %d"%(log_count)

        gt = GenerateCrawlerTask(generator)
        result = gt.generate_task()
        generator.delete()
        job.delete()

        self.assertTrue(result)
        path = gt.out_path
        fd = open(path, 'r')
        contents = fd.read().strip()
        self.assertEqual(contents, """{'uri':'http://www.shell.com'}""")



    def test_generate_task_python(self):
        job = Job( name = 'python_script', status= 1, priority =1)
        job.save()

        script = """import json\nprint json.dumps({"uri":"http://www.baidu.com"})"""
        cron = "* * * * *"
        generator = CrawlerTaskGenerator(job = job, code = script, cron = cron, code_type= CrawlerTaskGenerator.TYPE_PYTHON, status= CrawlerTaskGenerator.STATUS_ON)
        generator.save()

        task_count = CrawlerTask.objects.delete()
        print "task count = %d" %(task_count)
        log_count = CrawlerGeneratorLog.objects().delete()
        print "generator log count = %d"%(log_count)

        gt = GenerateCrawlerTask(generator)
        result = gt.generate_task()
        generator.delete()
        job.delete()

        self.assertTrue(result)
        path = gt.out_path
        fd = open(path, 'r')
        contents = fd.read().strip()
        # key 与value 之间有个空格
        self.assertEqual(contents, """{"uri": "http://www.baidu.com"}""")


    def test_save_task(self):
        self.gt.save_task()
        count = CrawlerTask.objects(uri ='http://www.baidu.com').count()
        self.assertEqual(count, 1)

    def test_run_shell(self):
        job = Job( name = 'shell', status= 1, priority =1)
        job.save()

        script = """#!/bin/bash\necho "{'uri':'http://www.shell.com'}"\n """
        cron = "* * * * *"
        generator = CrawlerTaskGenerator(job = job, code = script, cron = cron, code_type= CrawlerTaskGenerator.TYPE_SHELL, status= CrawlerTaskGenerator.STATUS_ON)
        generator.save()

        task_count = CrawlerTask.objects.delete()
        print "task count = %d" %(task_count)
        log_count = CrawlerGeneratorLog.objects().delete()
        print "generator log count = %d"%(log_count)

        gt = GenerateCrawlerTask(generator)
        gt.run()

        self.assertFalse(os.path.exists(gt.out_path))
        count = CrawlerTask.objects(uri ='http://www.shell.com').count()
        generator.delete()
        job.delete()
        self.assertEqual(count, 1)

    def test_run_python(self):
        job = Job( name = 'python_script', status= 1, priority =1)
        job.save()

        script = """import json\nprint json.dumps({"uri":"http://www.baidu.com"})"""
        cron = "* * * * *"
        generator = CrawlerTaskGenerator(job = job, code = script, cron = cron, code_type= CrawlerTaskGenerator.TYPE_PYTHON, status= CrawlerTaskGenerator.STATUS_ON)
        generator.save()

        task_count = CrawlerTask.objects.delete()
        print "task count = %d" %(task_count)
        log_count = CrawlerGeneratorLog.objects().delete()
        print "generator log count = %d"%(log_count)

        gt = GenerateCrawlerTask(generator)
        gt.run()
        count = CrawlerTask.objects(uri ='http://www.baidu.com').count()

        generator.delete()
        job.delete()
        self.assertFalse(os.path.exists(gt.out_path))
        self.assertEqual(count, 1)


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
        """ path 的路径一定要写正确，不然会出大问题的 """
        path = "/Users/princetechs5/crawler/cr-clawer/clawer/clawer/media/codes/570f73f6c3666e0af4a9efad_product.py"
        out_path = "/tmp/task_generator_570f6bc5c3666e095ed99d90"
        out_f = open(out_path, "w")
        process = subprocess.Popen(['/Users/princetechs5/Documents/virtualenv/bin/python', path], stdout= out_f)
        self.assertTrue(process)

    def test_run(self):
        path = "/Users/princetechs5/crawler/cr-clawer/clawer/clawer/media/codes/570f73f6c3666e0af4a9efad_product.py"
        out_path = "/tmp/task_generator_570f6bc5c3666e095ed99d90"
        out_f = open(out_path, "w")
        safe_process = SafeProcess(['/Users/princetechs5/Documents/virtualenv/bin/python', path], stdout=out_f, stderr=subprocess.PIPE)
        p = -1
        try:
            p = safe_process.run(1800)
        except OSError , e:
            print type(e)
            # safe_process.failed(e.child_traceback)
        except Exception, e:
            print type(e)
            # safe_process.failed(e)
        err = p.stderr.read()
        print err
        status = safe_process.wait()
        # 进程的返回代码returncode
        self.assertEqual(status,0)

class TestCrawlerCron(TestCase):
    """ Test for Cron Class """
    def setUp(self):
        TestCase.setUp(self)
        # self.filename = '/tmp/output.tab'
        self.cron = CrawlerCronTab()
        """
        mongodb preparations:
            job:
            { "_id" : ObjectId("570f73f6c3666e0af4a9efad"), "name" : "job", "status" : 1, "add_datetime" : ISODate("2016-04-14T18:41:33.966Z"), "priority" : 1 }
            { "_id" : ObjectId("570ded84c3666e0541c9e8d8"), "name" : "cloud", "status" : 1, "add_datetime" : ISODate("2016-04-16T18:41:33.966Z"), "priority" : 4 }
            crawler_task_generator:
            { "_id" : ObjectId("570f6bc5c3666e095ed99d90"), "job" : ObjectId("570f73f6c3666e0af4a9efad"), "code" : "import json\nprint json.dumps({'uri':'http://www.baidu.com'})", "cron" : "*/3 * * * *", "status" : 4, "add_datetime" : ISODate("2016-04-14T18:06:33.978Z") }
            { "_id" : ObjectId("570f6bc5c3666e095ed99d92"), "job" : ObjectId("570ded84c3666e0541c9e8d8"), "code" : "import json\nprint json.dumps({'uri':'http://www.baidu.com'})", "cron" : "*/6 * * * *", "status" : 3, "add_datetime" : ISODate("2016-04-16T18:06:33.978Z") }

        """

        self.job = Job.objects(id= '570f73f6c3666e0af4a9efad').first()

    def tearDown(self):
        TestCase.tearDown(self)

    def test_insert_offline_job(self):
        job = Job(name='offline', status=Job.STATUS_OFF, priority=3)
        job.save()
        count =Job.objects(status = Job.STATUS_OFF).count()
        self.assertEqual(count, 1)
        job.delete()

    def test_file_not_exist(self):
        try:
            CrawlerCronTab('/tmp/NotExistFile.tab')
        except IOError, e:
            self.assertTrue(e)

    def test_save_code(self):
        generator =CrawlerTaskGenerator.objects(id ='570f6bc5c3666e095ed99d90').first()
        result = self.cron._test_save_code(generator)
        self.assertTrue(result)
        path = generator.product_path()
        try:
            with open(path, 'r') as f:
                content = f.read()
        except Exception, e:
            print "IOError"
        self.assertEqual(content, generator.code)


    def test_job_order_by_datetime(self):
        job = Job(name= 'jobs')
        job.save()
        job2 = Job.objects.order_by('-add_datetime').first()
        self.assertEqual(job2.name, job.name)
        job.delete()

    def test_install_crontab(self):
        generator =CrawlerTaskGenerator.objects(id ='570f6bc5c3666e095ed99d90').first()
        result = self.cron._test_install_crontab(generator)
        print result
        self.assertTrue(result)

    def test_crontab(self):
        generator =CrawlerTaskGenerator.objects(id ='570f6bc5c3666e095ed99d90').first()
        result = self.cron._test_crontab(generator)
        print result
        self.assertTrue(result)

    def test_task_generator_cron_comment(self):
        job = Job.objects(id ='570f73f6c3666e0af4a9efad').first()
        result = self.cron._task_generator_cron_comment(job)
        target = "job name:%s with id:%s"%('collector', '570f73f6c3666e0af4a9efad')
        self.assertEqual(result, target)

    def test_remove_offline_jobs(self):
        self.cron.remove_offline_jobs_from_crontab()
        job = Job.objects(status = Job.STATUS_OFF).first()
        comment = self.cron._task_generator_cron_comment(job)
        crons = self.cron.crontab.find_comment(comment)
        for cron in crons:
            self.assertFalse(cron)

    def test_update_online_jobs(self):
        # preparation
        script = """import json\nprint json.dumps({'uri':"http://www.baidu.com"})"""
        cron = "*/5 * * * *"
        generator = CrawlerTaskGenerator(job = self.job,code= script, cron = cron)
        generator.save()
        self.cron.update_online_jobs()

        generator2= CrawlerTaskGenerator.objects(job= self.job, status = CrawlerTaskGenerator.STATUS_ON).first()
        self.assertEqual(generator, generator2)

        generator2.delete()

    def test_save_cron_to_file(self):
        self.cron.crontab.new(command="/usr/bin/echo", comment="test")
        self.cron.save_cron_to_file()
        cron = CronTab()
        cron.read(self.filename)
        comment = "test"
        crons = cron.find_comment(comment)
        for cron in crons:
            self.assertTrue(cron)


    def test_task_generator_install(self):
        result = self.cron.task_generator_install()
        self.assertTrue(result)
        try:
            with open(self.filename, 'r') as f:
                content = f.read()
                print content
        except Exception , e:
            print "IOError"

        cron = CronTab()
        cron.read(self.filename)
        comment = self.cron._task_generator_cron_comment(self.job)
        crons = cron.find_comment(comment)
        for cron in crons:
            self.assertTrue(cron)

    def test_exec_command(self):
        command = "GeneratorDispatch('570f73f6c3666e0af4a9efad').run()"
        c = compile(command, "", 'exec')
        exec c

    def test_exec_and_save_current_crons(self):
        CrawlerGeneratorCronLog.objects().delete()
        self.cron.exec_and_save_current_crons()
        count = CrawlerGeneratorCronLog.objects.count()
        self.assertGreater(count, 0)

        # cron = CronTab()
        # cron.read(self.filename)
        # comment = self.cron._task_generator_cron_comment(self.job)
        # crons = cron.find_comment(comment)
        # for cron in crons:
        #     print cron.last_run
        #     self.assertTrue(cron)

    def test_croniter(self):
        base =  datetime(2010, 1, 25, 4, 46)
        # base = datetime.datetime.now()
        iters = croniter('*/5 * * * *', base)  # every 1 minites
        next = iters.get_next(datetime)
        # target = base + datetime.timedelta(minutes=1)
        target = '2010-01-25 04:50:00'
        self.assertEqual( str(next), target)

    def test_task_generator_run(self):
        result = self.cron.task_generator_run()
        self.assertTrue(result)

    def test_force_exit(self):
        CrawlerGeneratorAlertLog.objects.delete()
        print force_exit()

    def test_exec_command(self):
        cron = "*/6 * * * *"
        command ="GeneratorDispatch('570ded84c3666e0541c9e8d8').run()"
        comment = "job name:cloud with id:570ded84c3666e0541c9e8d8"
        CrawlerGeneratorCronLog.objects().delete()
        exec_command(command, comment, cron)
        count = CrawlerGeneratorCronLog.objects.count()
        self.assertGreater(count, 0)

