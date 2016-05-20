# -*- coding: utf-8 -*-
import random
import logging
import os
import sys
import datetime
import redis
import rq
from mongoengine import *

from collector.models import CrawlerTask, CrawlerDownloadData, Job, CrawlerDownload
from models import StructureConfig, Parser, CrawlerAnalyzedData, Extracter, CrawlerExtracterInfo
from django.conf import settings
#from django.models import model_to_dict
import django

class Consts(object):
    QUEUE_PRIORITY_TOO_HIGH = u"structure:higher"
    QUEUE_PRIORITY_HIGH = u"structure:high"
    QUEUE_PRIORITY_NORMAL = u"structure:normal"
    QUEUE_PRIORITY_LOW = u"structure:low"
    QUEUE_MAX_LENGTH = 10000

class StructureGenerator(object):
    def filter_downloaded_tasks(self):
        downloaded_tasks = CrawlerTask.objects(status = CrawlerTask.STATUS_SUCCESS)
        if downloaded_tasks is None:
            logging.info("No downloaded (status = 5) tasks")
        return downloaded_tasks                        #返回状态为下载成功的爬虫任务

    def filter_parsed_tasks(self):
        parsed_tasks = CrawlerTask.objects(status = CrawlerTask.STATUS_ANALYSIS_SUCCESS)
        if parsed_tasks is None:
            logging.info("No parsed (status = 7) tasks")
        return parsed_tasks                            #返回状态为解析成功的爬虫任务

    def get_task_priority(self, task):              #将爬虫任务中的Job的priority(range(-1,6))化为解析任务的priority(Consts)        
        if task.job.priority == -1:
            task_priority = Consts.QUEUE_PRIORITY_TOO_HIGH
        elif task.job.priority == 0 or task.job.priority == 1:
            task_priority = Consts.QUEUE_PRIORITY_HIGH
        elif task.job.priority == 2 or task.job.priority == 3:
            task_priority = Consts.QUEUE_PRIORITY_NORMAL            
        elif task.job.priority == 4 or task.job.priority == 5:
            task_priority = Consts.QUEUE_PRIORITY_LOW
        else:
            task_priority = Consts.QUEUE_PRIORITY_LOW
        return task_priority

    def get_task_source_data(self, task):
        task_source_data = CrawlerDownloadData.objects(crawlertask = task).first()
        return task_source_data                        #根据uri返回爬虫的下载数据（类型）

    def get_task_analyzed_data(self, task):
        task_analyzed_data = CrawlerAnalyzedData.objects(crawler_task = task).first()
        return task_analyzed_data

class ParserGenerator(StructureGenerator):
    def __init__(self):
        self.queuegenerator = QueueGenerator()
        self.queues = self.queuegenerator.rq_queues

    def get_parser(self):                                #返回解析脚本中的RawParser类的实例
        return parser_func

    def is_duplicates(self, data):
        return False

    def assign_parse_task(self, priority, parser_function, data):
        try:
            parse_job_id = self.queuegenerator.enqueue(priority, parser_function, args = [data])
            if parse_job_id == None:
                return None
            else:
                CrawlerAnalyzedData(crawler_task = data.crawlertask,
                    update_date = datetime.datetime.now()).save()
                logging.info("Parse task successfully added")
                return parse_job_id
        except:
            logging.error("Error assigning task when enqueuing")

    def assign_parse_tasks(self):
        tasks = self.filter_downloaded_tasks()
        for task in tasks:
            parser_function = self.get_parser()
            priority = self.get_task_priority(task)
            data = self.get_task_source_data(task)
            if not self.is_duplicates(data):
                if self.assign_parse_task(priority, parser_function, data) is not None:
                    pass
                else:
                    logging.info('Queue for priority "% s" is full' % priority)
                    break
            else:
                logging.error("Parse task duplicates -- % s (uri)" % data.crawlertask.uri)
        return self.queues
    
class QueueGenerator(object):
    def __init__(self, redis_url = settings.STRUCTURE_REDIS, queue_length = Consts.QUEUE_MAX_LENGTH):
        self.connection = redis.Redis.from_url(redis_url) if redis_url else redis.Redis()
        self.too_high_queue = rq.Queue(Consts.QUEUE_PRIORITY_TOO_HIGH, connection=self.connection)
        self.high_queue = rq.Queue(Consts.QUEUE_PRIORITY_HIGH, connection=self.connection)
        self.normal_queue = rq.Queue(Consts.QUEUE_PRIORITY_NORMAL, connection=self.connection)
        self.low_queue = rq.Queue(Consts.QUEUE_PRIORITY_LOW, connection=self.connection)
        self.max_queue_length = queue_length if queue_length is not None else settings.MAX_QUEUE_LENGTH
        self.rq_queues = (self.too_high_queue,
            self.high_queue,
            self.normal_queue,
            self.low_queue)
        
    def enqueue(self, priority, func, *args, **kwargs):
        q = None
        if priority == Consts.QUEUE_PRIORITY_TOO_HIGH:
            q = self.too_high_queue
        elif priority == Consts.QUEUE_PRIORITY_HIGH:
            q = self.high_queue
        elif priority == Consts.QUEUE_PRIORITY_NORMAL:
            q = self.normal_queue
        elif priority == Consts.QUEUE_PRIORITY_LOW:
            q = self.low_queue
        else:
            q = self.low_queue
        if (q.count + 1) > Consts.QUEUE_MAX_LENGTH:
            logging.error("Cannot enqueue now because the queue: %s is full" % q.name)
            print "Cannot enqueue now because the queue: %s is full" % q.name
            return None
        else:
            parser_job = q.enqueue_call(func, *args, **kwargs)
            #parser_job.meta.setdefault("failures", 0)
            return  parser_job.id

def parser_func(data):
    #print "This is the start of parser_func"
    if data is not None:
        structureconfig = StructureConfig.objects(job = data.crawlertask.job).first()
        crawler_analyzed_data = CrawlerAnalyzedData.objects(crawler_task = data.crawlertask).first()
        if structureconfig is not None:
            current_dir = os.getcwd()
            #parsers_dir = "/home/webapps/cr-clawer/clawer/structure/parsers"
            parsers_dir = "/home/max/Documents/gitroom/cr-clawer/clawer/structure/parsers"
            if not os.path.isdir(parsers_dir):     #判断解析器目录是否存在，如不存在则创建
                os.mkdir(parsers_dir)
            os.chdir(parsers_dir)
            parser_init = open("__init__.py", 'w')
            parser_init.close()            
            parser_py_script = open(str(structureconfig.parser.parser_id) + ".py", 'w')
            parser_py_script.write(structureconfig.parser.python_script)
            parser_py_script.close()                #将python脚本写进解析器文件中并关闭文件
            sys.path.append(parsers_dir)           #把解析器路徑添加到系統路徑
            try:
                parser_module = __import__(str(structureconfig.parser.parser_id))
                rawparser = parser_module.RawParser()
                analyzed_data = str(rawparser.parser(data))

                if analyzed_data is not None:
                    data.crawlertask.update(status = 7)       #如果解析函数执行完且结果为不为空的字符串，则认为解析成功，写回标志位
                    #print "Status updated!"
                    crawler_analyzed_data.update(update_date = datetime.datetime.now(),
                        analyzed_data = analyzed_data)
                    logging.info("% s (uri) is successfully parsed -- Results saved" % data.crawlertask.uri)
                    return analyzed_data
                else:
                    logging.error("Something wrong while parsing % s (uri) -- NULL result" % data.crawlertask.uri)
            except Exception as e:
                data.crawlertask.update(status = 6)
                logging.error("Error parsing with % d.py" % structureconfig.parser.parser_id)
                os.chdir(current_dir)                    #切换回之前的工作目录
        else:
            logging.error("Error finding Configuration file (StructureConfig) for task: % s (uri)" % data.crawlertask.uri)             
    else:
        logging.error("Error finding parser from % s (uri) -- Null data" % data.crawlertask.uri)

class ExtracterGenerator(StructureGenerator):

    def __init__(self):
        self.queuegenerator = QueueGenerator()
        self.queues = self.queuegenerator.rq_queues

    def assign_extract_tasks(self):
        tasks = self.filter_parsed_tasks()
        for task in tasks:
            priority = self.get_priority(task)
            # db_conf = self.get_extracter_db_config(task)
            # mappings = self.get_extracter_mappings(task)
            # extracter = self.get_extracter(db_conf, mappings)
            ectracter = self.get_extracter()
            try:
                self.assign_task(priority, extracter)
                logging.info("Add extract task succeed")
            except:
                logging.error("Assign extract task runtime error.")

    # def assign_extract_task(self, priority=Consts.QUEUE_PRIORITY_NORMAL, parser=lambda: None, data=""):
    def assign_extract_task(self, priority, extract_function, data):
        try:
            extract_job_id = self.queuegenerator.enqueue(priority, extract_function, args=[data])
            if not extract_job_id:
                return None
            else:
                CrawlerExtracterInfo(extract_task=data.crawler_task, update_date=datetime.datetime.now()).save()
                logging.info("Extract task successfully added")
                return extract_job_id
        except:
            logging.error("Error assigning extract task when enqueuing")

    def get_extracter_conf():
        structureconfig = StructureConfig.objects(job=data.crawlertask.job).first()
        crawler_extract_info = CrawlerExtracterInfo.objects(extract_task=data.crawler_task).first()
        if structureconfig:
            try:
                extracter_conf = structureconfig.extracter.extracter_config
            except Exception as e:
                logging.error('Get extracter config error')
                raise e
            return extracter_conf

    def get_extracter(self, data):
        """获得导出器"""
        def extracter():
            if not data:
                logging.error("Error: there is not data to extract")
                return None
            try:
                structureconfig = StructureConfig.objects(job=data.crawlertask.job).first()
                crawler_extract_info = CrawlerExtracterInfo.objects(extract_task=data.crawler_task).first()
                if not structureconfig:
                    logging.error("Error: can not find structure configure")
                    return None
                data = self.get_task_analyzed_data(task)  # 获取一条解析成功的数据
                extracter_conf = self.get_extracter_conf() # 获取配置文件
                result = self.extract_fields(extracter_conf, data)
                if result:
                    data.crawler_task.update(status=9)  # status: 9导出成功, 8导出失败
                    crawler_extract_info.update(update_date=datetime.datetime.now())
                    logging.info('Extract fields succeed')
            except Exception as e:
                data.crawler_task.update(status=8) 
                logging.error('Extract fields error')
                raise e

            return extracter



    # def get_extracter_db_config():
        # pass

    # def get_extracter_mappings():
        # pass

    # def get_extracter(self, db_conf, mappings):

        # def extracter():
            # try:
                # self.if_not_exist_create_db_schema(db_conf)
                # logging.info("create db schema succeed")
            # except:
                # logging.error("create db schema error")
            # try:
                # self.extract_fields(mappings)
                # logging.info("extract fields succeed")
            # except:
                # logging.error("extract fields error")

        # return extracter

    # def if_not_exist_create_db_schema(self, conf):
        # pass

    def extract_fields(self, extracter_conf, data):
        print 'starting extract fields!'
        print '♫' * 30
        pass


class ExecutionTasks(object):
    def exec_task(self, queue=Consts.QUEUE_PRIORITY_NORMAL):
        with rq.Connection():
            w = rq.Worker([queue])
            #w.push_exc_handler(self.retry_handler)
            w.work()

    # def retry_handler(self, job, exc_type, exc_value, traceback):
    #     print "This is the start of RQ Exception Handler!"
    #     job.meta["failures"] += 1
    #     if job.meta["failures"] > 3:
    #         parsejobinfo = ParseJobInfo.objects(rq_parse_job_id= job.id).first()
    #         parsejobinfo.crawlerdownloaddata.crawlertask.update(status = 6)
    #         logging.info("Job: %s fails for couple of times and the status of its CrawlerTask will be modified as '6'" % job.id)
    #         return True                                #失败次数超过三次就将Job送到失败队列中
    #     else:
    #         job.set_status(rq.JobStatus.QUEUED)
    #         job.exc_info = None
    #         requeue_queue = rq.Queue(job.origin, connection=self.connection)
    #         requeue_queue.enqueue_job(job)
    #         return False 

def insert_test_data():
    
    right_script = """class RawParser(object):
    def parser(self, crawlerdownloaddata):
        data = "JSON Format Data After Parsing"
        return data"""

    wrong_script = """class RawParser(object):
    def parser(self, crawlerdownloaddata):
        print crawlerdownloaddata.wrong"""
    
    for count in range(0,100):
        test_job = Job("creator",
            "job_%d" % count,
            "info",
            "customer",
            random.choice(range(1,3)),
            random.choice(range(-1,6)),
            datetime.datetime.now())
        test_job.save()

        #test_parser = Parser(count, right_script)
        test_parser = Parser(count, random.choice([right_script, wrong_script]))
        test_parser.save()

        #test_crawlertask = CrawlerTask(test_job, uri = "test_uri_%d" % count, status = random.choice(range(1,8)))
        test_crawlertask = CrawlerTask(test_job, uri = "test_uri_%d" % count, status = 5)
        test_crawlertask.save()

        test_downloader = CrawlerDownload(test_job)
        test_downloader.save()

        StructureConfig(test_job, test_parser).save()

        CrawlerDownloadData(test_job, test_downloader, test_crawlertask).save()

    print "Data Inserted!"

def empty_test_data():
    
    Job.drop_collection()
    Parser.drop_collection()
    CrawlerTask.drop_collection()
    CrawlerDownload.drop_collection()
    StructureConfig.drop_collection()
    CrawlerDownloadData.drop_collection()

    CrawlerAnalyzedData.drop_collection()
    #ParseJobInfo.drop_collection()

    print "Data Cleaned!"
