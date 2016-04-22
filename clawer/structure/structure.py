# -*- coding: utf-8 -*-

import logging
import os

from redis import Redis
from rq import Connection, Worker, Quene
from mangoengine import *

from collector.models import CrawlerTask, CrawlerDownloadData
from collector.utils_generator import SafeProcess
from models import StructureConfig, Parser

class Consts(object):
    QUEUE_PRIORITY_TOO_HIGN = u"structure:higher"
    QUEUE_PRIORITY_HIGN = u"structure:high"
    QUEUE_PRIORITY_NORMAL = u"structure:normal"
    QUEUE_PRIORITY_LOW = u"structure:low"


class StructureGenerator(object):

    def filter_downloaded_tasks(self):
        downloaded_tasks = self.CrawlerTask.objects(status = STATUS_SUCCESS)
        
        return downloaded_tasks                         #返回状态为下载成功的爬虫任务

    def filter_parsed_tasks(self):
        parsed_tasks = self.CrawlerTask.objects(status = STATUS_ANALYSIS_SUCCESS)
        
        return parsed_tasks                             #返回状态为解析成功的爬虫任务

    def get_task_priority(self, task):                  #将爬虫任务中的Job的priority(range(-1,6))装化为解析任务的priority(Consts)        
        if task.job.priority == -1:
            task_priority = Consts.QUEUE_PRIORITY_TOO_HIGH
        elif task.job.priority == 0 or task.job.priority == 1:
            task_priority = Consts.QUEUE_PRIORITY_HIGH
        elif task.job.priority == 2 or task.job.priority == 3:
            task_priority = Consts.QUEUE_PRIORITY_NORMAL            
        elif task.job.priority == 4 or task.job.priority == 5:
            task_priority = Consts.QUEUE_PRIORITY_LOW
        else:
            task_priority = None
            
        return task_priority

    def get_task_source_data(self, task):
        task_source_data = self.CrawlerDownloadData.objects(crawlertask__uri__ = task.uri)
        
        return task_source_data                         #根据uri返回爬虫的下载数据（类型）


class ParserGenerator(StructureGenerator):
    def assign_tasks(self):
        tasks = self.filter_downloaded_tasks()
        for task in tasks:
            parser = self.get_parser(task)
            priority = self.get_priority(task)
            data = self.get_task_source_data(task)
            if not self.is_duplicates(data):
                try:
                    self.assign_task(priority, parser, data)
                    logging.info("add task succeed")
                except:
                    logging.error("assign task runtime error.")
            else:
                logging.error("duplicates")

    def assign_task(self, priority = Consts.QUEUE_PRIORITY_NORMAL,
                    parser = lambda:None,
                    data = ""):
        self.connection = redis.Redis.from_url(redis_url) if redis_url else redis.Redis()
        pass

    def get_parser(self, task):
        if task is not None:
            try:
                structureconfig = self.StructureConfig.objects(job__name__ = task.job.name)
            except Exception as e:
                logging.error("Error finding StructureConfig -- No file for the job name")
            cur_dir = os.getcwd();
            parsers_dir = cur_dir + "/parsers"
            if os.path.isdir(parsers_dir):     #判断解析器目录是否存在，如不存在则创建
                pass
            else:
                os.mkdir(parsers_dir)
            os.chdir(parsers_dir)
            parser_py_script = open.(str(structureconfig.parser.parser_id) + ".py",'w')
            parser_py_script.write(structureconfig.parser.python_script)
            parser_py_script.close                          #将python脚本写进解析器文件中并关闭文件
            
            os.chdir(current_dir)                           #切换回之前的工作目录
        
    def is_duplicates(self, data):
        return False


class ExtracterGenerator(StructureGenerator):
    def assign_tasks(self):
        tasks = self.filter_parsed_tasks()
        for task in tasks:
            priority = self.get_priority(task)
            db_conf = self.get_extracter_db_config(task)
            mappings = self.get_extracter_mappings(task)
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
