# -*- coding: utf-8 -*-

import logging
import os
import sys

from redis import Redis
from rq import Connection, Worker, Quene
from mongoengine import *

from collector.models import CrawlerTask, CrawlerDownloadData
from models import StructureConfig, Parser, CrawlerAnalyzedData
from django.conf import settings

class Consts(object):
    QUEUE_PRIORITY_TOO_HIGH = u"structure:higher"
    QUEUE_PRIORITY_HIGN = u"structure:high"
    QUEUE_PRIORITY_NORMAL = u"structure:normal"
    QUEUE_PRIORITY_LOW = u"structure:low"
    QUEUE_MAX_LENGTH = 10000

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
        self.queues = QueueGenerator()
        tasks = self.filter_downloaded_tasks()
        for task in tasks:
            parser = self.get_parser(task)
            priority = self.get_priority(task)
            data = self.get_task_source_data(task)
            if not self.is_duplicates(data):
                try:
                    queues.enqueue(priority, parser, data)
                    logging.info("add task succeed")
                except:
                    logging.error("assign task runtime error.")
            else:
                logging.error("duplicates")
        return self.queues
    #def assign_task(self, priority, parser, data):   
    def get_parser(self, task):
        if task is not None:
            try:
                structureconfig = self.StructureConfig.objects(job__name__ = task.job.name)
            except Exception as e:
                logging.error("Error finding StructureConfig -- No file for the job name")
            cur_dir = os.getcwd()
            parsers_dir = cur_dir + "/parsers"
            if os.path.isdir(parsers_dir):              #判断解析器目录是否存在，如不存在则创建
                pass
            else:
                os.mkdir(parsers_dir)
            os.chdir(parsers_dir)
            parser_init = open("__init__.py")
            parser_init.close()            
            parser_py_script = open(str(structureconfig.parser.parser_id) + ".py",'w')
            parser_py_script.write(structureconfig.parser.python_script)
            parser_py_script.close()                    #将python脚本写进解析器文件中并关闭文件
            os.chdir(current_dir)                       #切换回之前的工作目录
            sys.path.append(parsers_dir)                #把解析器路徑添加到系統路徑
            try:
                parser_module = __import__(str(structureconfig.parser.parser_id))
            except Exception as e:
                logging.error("Error importing parser(function) from parser_id.py")
            def parser_func(self, data):
                try:
                    analyzed_data = parser_module.RawParser.parser(data)
                except:
                    logging.error("Error Parsing")
                CrawlerAnalyzedData(task.uri, task.job, datetime.datetime.now(), analyzed_data).save()
            return parser_func(self, data)                
        else:
            logging.error("Error finding parser -- Null task")
            
    def is_duplicates(self, data):
        return False
    
class QueueGenerator(object):
    def __init__(self, redis_url = settings.REDIS, queue_length = Consts.QUEUE_MAX_LENGTH):
        self.connection = redis.Redis.from_url(redis_url) if redis_url else redis.Redis()
        self.too_high_queue = rq.Queue(Consts.QUEUE_PRIORITY_TOO_HIGH, connection=self.connection)
        self.high_queue = rq.Queue(Consts.QUEUE_PRIORITY_HIGH, connection=self.connection)
        self.normal_queue = rq.Queue(Consts.QUEUE_PRIORITY_NORMAL, connection=self.connection)
        self.low_queue = rq.Queue(Consts.QUEUE_PRIORITY_LOW, connection=self.connection)
        self.max_queue_length = queue_length if queue_length is not None else settings.MAX_QUEUE_LENGTH
        
    def enqueue(self, priority, func, data):
        q = None
        if priority == Consts.QUEUE_PRIORITY_TOO_HIGH:
            q = self.too_high_queue
        elif priority == Consts.QUEUE_PRIORITY_HIGN:
            q = self.high_queue
        elif priority == Consts.QUEUE_PRIORITY_NORMAL:
            q = self.normal_queue
        elif priority == Consts.QUEUE_PRIORITY_LOW:
            q = self.low_queue
        else:
            q = self.low_queue
        if q.count > Consts.QUEUE_MAX_LENGTH:
            return None
        parser_job = q.enqueue(func = func, args = (data), timeout = 30)
        return parser_job.id
        
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
