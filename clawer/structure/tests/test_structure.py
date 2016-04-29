# -*- coding: utf-8 -*-
import unittest
from django.test import TestCase
#import commands
# from django.test.client import Client
# from django.core.urlresolvers import reverse
# from django.contrib.auth.models import User as DjangoUser, Group
# from django.conf import settings
# from storage.models import Job
from collector.models import CrawlerTask
from structure.structure import (StructureGenerator,
                                 ParserGenerator,
                                 ExtracterGenerator,
                                 ExecutionTasks,
                                 insert_test_data)


class TestStructureGenerator(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        structuregenerator = StructureGenerator()

    def tearDown(self):
        TestCase.tearDown(self)

    def test_filter_downloaded_tasks(self):
        count = CrawlerTask.objects.count()
        if count == 0:
            insert_test_data()
        else:
            downloaded_tasks = structureconfig.filter_downloaded_tasks()
        self.assertGreater(len(downloaded_tasks), 0)
        for task in downloaded_tasks:
            self.assertEqual(task.status, 5)

    def test_filter_parsed_tasks(self):
        count = CrawlerTask.objects.count()
        if count == 0:
            insert_test_data()
        else:
            parsed_tasks = structureconfig.filter_parsed_tasks()
        self.assertGreater(len(parsed_tasks), 0)
        for task in parsed_tasks:
            self.assertEqual(task.status, 7)

    def test_get_job_priority(self, job):
        pass

    def test_get_job_source_data(self, job):
        pass


class TestParserGenerator(TestCase):
    def test_assign_tasks(self):
        pass

    def test_assign_task(self):
        pass

    def test_get_parser(self):
        pass

    def test_is_duplicates(self):
        pass


class TestExtracterGenerator(TestCase):
    def test_assign_tasks(self):
        pass

    def test_assign_task(self):
        pass

    def test_get_extracter(self):
        pass

    def test_if_not_exist_create_db_schema(self):
        pass

    def test_extract_fields(self):
        pass

    def test_get_extracter_db_config(self):
        pass


class TestExecutionTasks(TestCase):
    def test_exec_task(self):
        pass
