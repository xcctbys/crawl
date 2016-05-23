# -*- coding: utf-8 -*-
import random
import logging
import os
import sys
import datetime
import redis
import rq
import json
from mongoengine import *

from collector.models import CrawlerTask, CrawlerDownloadData, Job, CrawlerDownload
from models import StructureConfig, ExtracterStructureConfig, Parser, CrawlerAnalyzedData, Extracter, CrawlerExtracterInfo
from django.conf import settings
#from django.models import model_to_dict
import django

from extracters.sql_generator import JsonToSql as SqlGenerator

class Consts(object):
    QUEUE_PRIORITY_TOO_HIGH = u"structure:higher"
    QUEUE_PRIORITY_HIGH = u"structure:high"
    QUEUE_PRIORITY_NORMAL = u"structure:normal"
    QUEUE_PRIORITY_LOW = u"structure:low"
    QUEUE_MAX_LENGTH = 10000

class ExtracterConsts(object):
    QUEUE_PRIORITY_TOO_HIGH = u"extracter:higher"
    QUEUE_PRIORITY_HIGH = u"extracter:high"
    QUEUE_PRIORITY_NORMAL = u"extracter:normal"
    QUEUE_PRIORITY_LOW = u"extracter:low"
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
        return task_analyzed_data           # 返回解析成功的数据
        


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
            structure_job = q.enqueue_call(func, *args, **kwargs)
            #parser_job.meta.setdefault("failures", 0)
            return  structure_job.id

class ExtracterQueueGenerator(object):
    def __init__(self, redis_url = settings.STRUCTURE_REDIS, queue_length = ExtracterConsts.QUEUE_MAX_LENGTH):
        self.connection = redis.Redis.from_url(redis_url) if redis_url else redis.Redis()
        self.too_high_queue = rq.Queue(ExtracterConsts.QUEUE_PRIORITY_TOO_HIGH, connection=self.connection)
        self.high_queue = rq.Queue(ExtracterConsts.QUEUE_PRIORITY_HIGH, connection=self.connection)
        self.normal_queue = rq.Queue(ExtracterConsts.QUEUE_PRIORITY_NORMAL, connection=self.connection)
        self.low_queue = rq.Queue(ExtracterConsts.QUEUE_PRIORITY_LOW, connection=self.connection)
        self.max_queue_length = queue_length if queue_length is not None else settings.MAX_QUEUE_LENGTH
        self.rq_queues = (self.too_high_queue,
            self.high_queue,
            self.normal_queue,
            self.low_queue)
        
    def enqueue(self, priority, func, *args, **kwargs):
        q = None
        if priority == ExtracterConsts.QUEUE_PRIORITY_TOO_HIGH:
            q = self.too_high_queue
        elif priority == ExtracterConsts.QUEUE_PRIORITY_HIGH:
            q = self.high_queue
        elif priority == ExtracterConsts.QUEUE_PRIORITY_NORMAL:
            q = self.normal_queue
        elif priority == ExtracterConsts.QUEUE_PRIORITY_LOW:
            q = self.low_queue
        else:
            q = self.low_queue
        if (q.count + 1) > ExtracterConsts.QUEUE_MAX_LENGTH:
            logging.error("Cannot enqueue now because the queue: %s is full" % q.name)
            print "Cannot enqueue now because the queue: %s is full" % q.name
            return None
        else:
            extracter_job = q.enqueue_call(func, *args, **kwargs)
            return  extracter_job.id
    

def parser_func(data):
    #print "This is the start of parser_func"
    if data is not None:
        structureconfig = StructureConfig.objects(job = data.crawlertask.job).first()
        crawler_analyzed_data = CrawlerAnalyzedData.objects(crawler_task = data.crawlertask).first()
        if structureconfig is not None:
            current_dir = os.getcwd()
            parsers_dir = "/home/webapps/cr-clawer/clawer/structure/parsers"
            # parsers_dir = "structure/parsers"
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

    sqlgenerator = SqlGenerator()        # 用于处理源数据生成sql，并导入关系数据库
    def __init__(self):
        self.queuegenerator = ExtracterQueueGenerator()
        self.queues = self.queuegenerator.rq_queues
        
    def get_task_priority(self, task):
        if task.job.priority == -1:
            task_priority = ExtracterConsts.QUEUE_PRIORITY_TOO_HIGH
        elif task.job.priority == 0 or task.job.priority == 1:
            task_priority = ExtracterConsts.QUEUE_PRIORITY_HIGH
        elif task.job.priority == 2 or task.job.priority == 3:
            task_priority = ExtracterConsts.QUEUE_PRIORITY_NORMAL            
        elif task.job.priority == 4 or task.job.priority == 5:
            task_priority = ExtracterConsts.QUEUE_PRIORITY_LOW
        else:
            task_priority = ExtracterConsts.QUEUE_PRIORITY_LOW
        return task_priority

    def assign_extract_tasks(self):
        """分配所有导出任务"""
        tasks = self.filter_parsed_tasks()
        for task in tasks:
            priority = self.get_task_priority(task)
            # db_conf = self.get_extracter_db_config(task)
            # mappings = self.get_extracter_mappings(task)
            # extracter = self.get_extracter(db_conf, mappings)
            data = self.get_task_analyzed_data(task)  # 获取一条解析成功的数据
            conf = self.get_extracter_conf(data)  # 获取一条与任务相关的导出器配置
            sql_file_name = conf['database']['destination_db']['dbname']
            sql_file_name = '/tmp/table_%s.sql' % sql_file_name
            print sql_file_name
            if not os.path.exists('sql_file_name'):
                self.sqlgenerator.test_table(conf, 'sql_file_name')
                self.sqlgenerator.test_daoru('sql_file_name')
            extract_function = self.extracter
            try:
                self.assign_extract_task(priority, extract_function, conf, data)
                logging.info("Add extract task succeed")
            except:
                logging.error("Assign extract task runtime error.")
        return self.queues

    # def assign_extract_task(self, priority=Consts.QUEUE_PRIORITY_NORMAL, parser=lambda: None, data=""):
    def assign_extract_task(self, priority, extract_function, conf, data):
        """分配一项导出任务"""
        try:
            extract_job_id = self.queuegenerator.enqueue(priority, extract_function, args=[conf, data])
            if not extract_job_id:
                return None
            else:
                CrawlerExtracterInfo(extract_task=data.crawler_task, update_date=datetime.datetime.now()).save()
                print 'assign task %s succeed !' % extract_job_id
                logging.info("Extract task successfully added")
                return extract_job_id
        except:
            logging.error("Error assigning extract task when enqueuing")

    def get_extracter_conf(self, data):
        """获取导出器配置
            参数data为一条JSON格式源数据, str类型"""
        extracterstructureconfig = ExtracterStructureConfig.objects(job=data.crawler_task.job).first() # 获取导出器配置 
        
        if extracterstructureconfig:
            try:
                extracter_configure = extracterstructureconfig.extracter.extracter_config.encode('utf8')  # extracter_conf 为字符串格式的配置
                configure_dict = json.loads(extracter_configure)
            except Exception as e:
                logging.error('Get extracter config error')
            return configure_dict

    @classmethod
    def extract_fields(self, extracter_conf, data):
        """生成sql语句并导出字段"""
        print 'starting extract fields!'
        try:
            # self.sqlgenerator.test_table(extracter_conf, '/tmp/my_table.sql')
            # self.sqlgenerator.test_daoru('/tmp/my_table.sql')
            self.sqlgenerator.test_get_data(extracter_conf, data, '/tmp/insert_data.sql')
            self.sqlgenerator.test_daoru('/tmp/insert_data.sql')
        except Exception as e:
            print e
        return True

    @classmethod
    def extracter(self, conf, data):
        """导出器"""
        if not data:
            logging.error("Error: there is no data to extract")
            return None
        try:
            result = self.extract_fields(conf, data.analyzed_data)   # data.analyzed_data 为一条解析后的JSON源数据
            if result:
                data.crawler_task.update(status=9)  # status: 9导出成功, 8导出失败
                crawler_extract_info = CrawlerExtracterInfo.objects(extract_task=data.crawler_task).first()
                crawler_extract_info.update(extracted_status=True, update_date=datetime.datetime.now()) # 更新导出状态信息
                logging.info('Extract fields succeed')
        except Exception as e:
            data.crawler_task.update(status=8) 
            logging.error('Extract fields error')
            print e
        return True




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



class ExecutionTasks(object):
    def exec_task(self, queue=Consts.QUEUE_PRIORITY_NORMAL):
        with rq.Connection():
            w = rq.Worker([queue])
            #w.push_exc_handler(self.retry_handler)
            w.work()

class ExecutionExtracterTasks(object):
    def exec_task(self, queue=ExtracterConsts.QUEUE_PRIORITY_NORMAL):
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

class TestExtracter(object):
    """测试导出器"""
    def __init__(self):
        pass

    def insert_extracter_test_data(self):

        config = open('structure/extracters/gs_table_conf.json').read()
        analyzeddata=open('structure/extracters/guangxi.json')


        for count in range(20):
            test_job = Job("creator",
                    "job_%d" % count,
                    "info",
                    "customer",
                    random.choice(range(1, 3)),
                    random.choice(range(-1, 6)),
                    datetime.datetime.now())
            test_job.save()

            # test_extracter = ExtracterGenerator.extracter
            test_extracter = Extracter(count, config)
            test_extracter.save()

            test_crawlertask = CrawlerTask(test_job, uri="test_uri_%d" % count, status=7)
            test_crawlertask.save()
            
            ExtracterStructureConfig(job=test_job, extracter=test_extracter).save()

            CrawlerAnalyzedData(crawler_task=test_crawlertask, analyzed_data=analyzeddata.readline()).save()
        print "Extracter Test Data Inserted"

    def empty_test_data(self):
        
        Job.drop_collection()
        Extracter.drop_collection()
        CrawlerTask.drop_collection()
        ExtracterStructureConfig.drop_collection()
        CrawlerAnalyzedData.drop_collection()
        CrawlerExtracterInfo.drop_collection()
        print "Extracter Test Data Cleaned!"
        

