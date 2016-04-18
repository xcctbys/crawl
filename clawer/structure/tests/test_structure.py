# -*- coding: utf-8 -*-

from django.test import TestCase
# from django.test.client import Client
# from django.core.urlresolvers import reverse
# from django.contrib.auth.models import User as DjangoUser, Group
# from django.conf import settings
# from storage.models import Job
from structure.structure import (StructureGenerator,
                                 ParserGenerator,
                                 ExtracterGenerator,
                                 ExecutionTasks,)


class TestStructureGenerator(TestCase):
    def test_filter_downloaded_jobs(self):
        pass

    def test_filter_parsed_jobs(self):
        pass

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
