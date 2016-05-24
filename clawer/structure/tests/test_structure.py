# -*- coding: utf-8 -*-
import unittest
from django.test import TestCase
from mongoengine import *
import random
import os
import django.utils
#import commands
# from django.test.client import Client
# from django.core.urlresolvers import reverse
# from django.contrib.auth.models import User as DjangoUser, Group
from django.conf import settings
from structure.models import Parser, StructureConfig, CrawlerAnalyzedData
# from django.conf import settings
from structure.models import Parser, StructureConfig, CrawlerAnalyzedData, Extracter, CrawlerExtracterInfo
from collector.utils_generator import DataPreprocess
from collector.models import Job as JobMongoDB
from storage.models import Job as JobMySQL
from collector.models import (CrawlerTask,
                                 CrawlerDownloadData,
                                 CrawlerDownloadType,
                                 CrawlerDownload,
                                 CrawlerDownloadSetting,
                                 CrawlerTaskGenerator)
from structure.structure import (StructureGenerator,
                                 ParserGenerator,
                                 QueueGenerator,
                                 ExtracterGenerator,
                                 ExecutionTasks,
                                 insert_test_data,
                                 empty_test_data,
                                 parser_func,
                                 Consts)
#Vertical Test
def insert_job(name, text, parser_text, settings):
    # name = "enterprise"
    prior = random.randint(-1, 5)
    #Downloader
    onetype = CrawlerDownloadType(language = 'other', is_support= True)
    onetype.save()
    #Job
    job_mongodb = JobMongoDB(name = name, info = "", priority = prior)
    job_mongodb.save()
    job_mysql = JobMySQL(name = name, info = "", priority = prior)
    job_mysql.save()
    #Generator
    script = """import json\nprint json.dumps({'uri':"http://www.baidu.com"})"""
    cron = "* * * * *"
    code_type = CrawlerTaskGenerator.TYPE_PYTHON
    schemes = ['http', 'https']
    generator = CrawlerTaskGenerator(job = job_mongodb, code = script, code_type = code_type, schemes = schemes, cron = cron)
    generator.save()
    #Downloader
    cds1 = CrawlerDownloadSetting(job = job_mongodb, proxy = '122', cookie = '22', dispatch_num = 50)
    cds1.save()
    cd1 = CrawlerDownload(job = job_mongodb, code = 'codestr2', types = onetype)
    cd1.save()
    #Generator
    dp = DataPreprocess(job_mongodb.id)
    dp.save(text = text, settings = settings)
    #Structure
    parser = Parser(
        parser_id = name,
        python_script = parser_text,
        update_date = django.utils.timezone.now())
    parser.save()
    structureconfig = StructureConfig(
        job_copy_id = job_mongodb.id,
        job = job_mysql,
        parser = parser,
        update_date = django.utils.timezone.now())
    structureconfig.save()

#Unittest
class TestStructureGenerator(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.test_structuregenerator = StructureGenerator()
        self.test_count = CrawlerTask.objects.count()
        if self.test_count == 0:
            empty_test_data()
            insert_test_data()
        else:
            pass
        self.test_crawlertasks = CrawlerTask.objects()

    def tearDown(self):
        TestCase.tearDown(self)

    def test_filter_downloaded_tasks(self):
        test_downloaded_tasks = self.test_structuregenerator.filter_downloaded_tasks()
        self.assertGreater(len(test_downloaded_tasks), 0)
        for test_downloaded_task in test_downloaded_tasks:
            self.assertEqual(test_downloaded_task.status, 5)

    def test_filter_parsed_tasks(self):
        test_parsed_tasks = self.test_structuregenerator.filter_parsed_tasks()
        self.assertGreater(len(test_parsed_tasks), 0)
        for test_parsed_task in test_parsed_tasks:
            self.assertEqual(test_parsed_task.status, 7)

    def test_get_task_priority(self):
        for test_crawlertask in self.test_crawlertasks:
            test_priority = self.test_structuregenerator.get_task_priority(test_crawlertask)
            self.assertIn(test_priority, (Consts.QUEUE_PRIORITY_TOO_HIGH,
                Consts.QUEUE_PRIORITY_HIGH,
                Consts.QUEUE_PRIORITY_NORMAL,
                Consts.QUEUE_PRIORITY_LOW))

    def test_get_task_source_data(self):
        for test_crawlertask in self.test_crawlertasks:
            test_job_source_data = self.test_structuregenerator.get_task_source_data(test_crawlertask)
            self.assertIsInstance(test_job_source_data, CrawlerDownloadData)

class TestParserGenerator(TestCase):
    
    def setUp(self):
        TestCase.setUp(self)
        self.test_parsergenerator = ParserGenerator()
        self.test_count = CrawlerTask.objects.count()
        if self.test_count == 0:
            empty_test_data()
            insert_test_data()
        else:
            pass

    def tearDown(self):
        TestCase.tearDown(self)

    def test_get_parser(self):
        test_crawlertask = CrawlerTask.objects().first()
        test_rawparser = self.test_parsergenerator.get_parser(test_crawlertask)
        self.assertIsNotNone(test_rawparser)

    def test_is_duplicates(self):
        pass

    def test_assign_parse_task(self):
        test_crawlerdownloaddata = CrawlerDownloadData.objects().first()
        test_priority = test_crawlerdownloaddata.crawlertask.job.priority
        test_rawparser = self.test_parsergenerator.get_parser(test_crawlerdownloaddata.crawlertask)
        test_parse_job_id = self.test_parsergenerator.assign_parse_task(test_priority, test_rawparser, test_crawlerdownloaddata)
        self.assertIsNotNone(test_parse_job_id)
        test_parsejobinfo = ParseJobInfo.objects(rq_parse_job_id= test_parse_job_id).first()
        self.assertIsNotNone(test_parsejobinfo.crawlerdownloaddata)
        #Clean the saved object in MongoDB and job in RQ queues which are created for testing purpose
        for test_rq_queue in self.test_parsergenerator.queues:
            if test_rq_queue.name == test_priority:
                test_rq_queue.remove(test_parse_job_id)
                break
            else:
                pass
        test_parsejobinfo.delete()

    def test_assign_parse_tasks(self):
        test_rq_queues = self.test_parsergenerator.assign_parse_tasks()
        self.assertEqual(len(test_rq_queues), 4)
        for test_rq_queue in test_rq_queues:
            self.assertGreater(test_rq_queue.count, 0)
            test_rq_queue.empty()
        ParseJobInfo.drop_collection()

    def test_parser_function(self):
        test_crawlertask = CrawlerTask.objects().first()
        test_crawlerdownloaddata = CrawlerDownloadData.objects(crawlertask = test_crawlertask).first()
        test_rawparser = self.test_parsergenerator.get_parser(test_crawlertask)
        test_analyzed_data = parser_func(test_rawparser, test_crawlerdownloaddata)
        test_crawleranalyzeddata = CrawlerAnalyzedData.objects(Q(uri = test_crawlertask.uri) & Q(job = test_crawlertask.job)).first()
        self.assertIsNotNone(test_crawleranalyzeddata.analyzed_data)
        if self.assertEqual(test_crawlertask.status, 7):
            #Clean data
            test_crawlertask.update(status = random.choice(range(1,8)))
        else:
            pass
        test_crawleranalyzeddata.delete()

class TestQueueGenerator(TestCase):
    
    def setUp(self):
        TestCase.setUp(self)
        self.test_queuegenerator = QueueGenerator()

    def tearDown(self):
        TestCase.tearDown(self)

    def test_enqueue(self):
        test_priority = random.choice((Consts.QUEUE_PRIORITY_TOO_HIGH,
            Consts.QUEUE_PRIORITY_HIGH,
            Consts.QUEUE_PRIORITY_NORMAL,
            Consts.QUEUE_PRIORITY_LOW))
        def test_parser_func(self, data):
            pass
        test_crawlerdownloaddata = CrawlerDownloadData.objects().first()
        test_parse_job_id = self.test_queuegenerator.enqueue(test_priority, test_parser_func, args = [test_crawlerdownloaddata])
        self.assertIsNotNone(test_parse_job_id)
        for test_rq_queue in self.test_queuegenerator.rq_queues:
            if test_rq_queue.name == test_priority:
                test_rq_queue.remove(test_parse_job_id)
                break
            else:
                pass

class TestExtracterGenerator(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.test_extractergenerator = ExtracterGenerator()
        self.test_count = CrawlerTask.objects.count()

    def tearDown(self):
        TestCase.tearDown(self)

    def test_assign_extract_task(self):
        test_crawleranalyzeddata = CrawlerAnalyzedData.objects().first()
        test_priority = test_crawleranalyzeddata.crawler_task.job.priority
        test_extracter = self.test_extractergenerator.extracter
        test_extract_job_id = self.test_extractergenerator.assign_extract_task(test_priority, test.extracter, test_crawleranalyzeddata)
        test_assertIsNotNone(test_extract_job_id)

    def test_assign_extract_tasks(self):
        test_rq_queues = self.test_extractergenerator.assign_extract_tasks()
        self.assertEqual(len(test_rq_queues), 4)
        for test_rq_queue in test_rq_queues:
            self.assertGreater(test_rq_queue.count, 0)
            test_rq_queue.empty()
    
    def test_extract_function(self):
        test_crawlertask = CrawlerTask.objects().first()
        test_crawleranalyzeddata = CrawlerAnalyzedData.objects(crawler_task = test_crawlertask).first()
        test_extracter = self.test_extractergenerator.extracter(test_crawlertask)
        test_extracted_result = extracter(test_rawparser, test_crawlerdownloaddata)
        test_extractedinfo = CrawlerExtracterInfo.objects(job=test_crawlertask.job)
        self.assertTrue(test_extracted_result)
        
        if self.assertEqual(test_crawlertask.status, 9):
            #Clean data
            test_crawlertask.update(status=random.choice(range(1,10)))
        else:
            pass
        test_crawlerextracteddata.delete()

    def test_if_not_exist_create_db_schema(self):
        pass

    def test_extract_fields(self):
        pass


class TestExecutionTasks(TestCase):
    def test_exec_task(self):
        pass

    def test_retry_handler(self):
        pass
