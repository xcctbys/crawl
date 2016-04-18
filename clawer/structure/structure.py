# -*- coding: utf-8 -*-

import logging

from rq import Connection, Worker
from multiprocess import Pool
# from models import StructureConfig


class Consts(object):
    QUEUE_PRIORITY_TOO_HIGN = u"too hign"
    QUEUE_PRIORITY_HIGN = u"high"
    QUEUE_PRIORITY_NORMAL = u"normal"
    QUEUE_PRIORITY_LOW = u"low"


class StructureGenerator(object):

    def filter_downloaded_jobs(self):
        pass

    def filter_parsed_jobs(self):
        pass

    def get_job_priority(self, job):
        pass

    def get_job_source_data(self, job):
        pass


class ParserGenerator(StructureGenerator):
    def assign_tasks(self):
        jobs = self.filter_downloaded_jobs()
        for job in jobs:
            parser = self.get_parser(job)
            priority = self.get_priority(job)
            data = self.get_job_source_data(job)
            if not self.is_duplicates(data):
                try:
                    self.assign_task(priority, parser, data)
                    logging.info("add task succeed")
                except:
                    logging.error("assign task runtime error.")
            else:
                logging.error("duplicates")

    def assign_task(self,
                    priority=Consts.QUEUE_PRIORITY_NORMAL,
                    parser=lambda: None,
                    data=""):
        pass

    def get_parser(self, job):
        pass

    def is_duplicates(self, data):
        return False


class ExtracterGenerator(StructureGenerator):
    def assign_tasks(self):
        jobs = self.filter_parsed_jobs()
        for job in jobs:
            priority = self.get_priority(job)
            db_conf = self.get_extracter_db_config(job)
            mappings = self.get_extracter_mappings(job)
            extracter = self.get_extracter(db_conf, mappings)
            try:
                self.assign_task(priority, extracter)
                logging.info("add task succeed")
            except:
                logging.error("assign task runtime error.")

    def assign_task(self,
                    priority=Consts.QUEUE_PRIORITY_NORMAL,
                    parser=lambda: None,
                    data=""):
        pass

    def get_extracter(self, db_conf, mappings):

        def extracter():
            try:
                self.if_not_exist_create_db_schema(db_conf)
                logging.info("create db schema succeed")
            except:
                logging.error("create db schema error")
            try:
                self.extract_fields(mappings)
                logging.info("extract fields succeed")
            except:
                logging.error("extract fields error")

        return extracter

    def if_not_exist_create_db_schema(self, conf):
        pass

    def extract_fields(self, mappings):
        pass

    def get_extracter_db_config(self):
        pass


class ExecutionTasks(object):

    def exec_task(queue=Consts.QUEUE_PRIORITY_NORMAL):
        with Connection([queue]):
            w = Worker()
            w.work()
