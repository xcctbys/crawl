# -*- coding: utf-8 -*-
import random
import logging
import datetime
import redis
import rq
import json
import ast
import django.utils
from django.contrib.auth.models import User
from collector.models import Job as JobMongoDB
from storage.models import Job as JobMySQL
from collector.models import CrawlerTask, CrawlerDownloadData, CrawlerDownload
from models import StructureConfig, ExtracterStructureConfig, Parser, CrawlerAnalyzedData, Extracter, CrawlerExtracterInfo, ExtractLog
from django.conf import settings
import django
import traceback

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
        downloaded_tasks = CrawlerTask.objects(status=5)
        if downloaded_tasks is None:
            logging.info("No downloaded (status = 5) tasks")
        return downloaded_tasks

    def filter_parsed_tasks(self):
        parsed_tasks = CrawlerTask.objects(status=CrawlerTask.STATUS_ANALYSIS_SUCCESS)
        if parsed_tasks is None:
            logging.info("No parsed (status = 7) tasks")
        return parsed_tasks

    def get_task_priority(self, task):
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
        task_source_data = CrawlerDownloadData.objects(crawlertask=task).first()
        return task_source_data

    def get_task_analyzed_data(self, task):
        task_analyzed_data = CrawlerAnalyzedData.objects(crawler_task=task).first()
        return task_analyzed_data    # 返回解析成功的数据


class ParserGenerator(StructureGenerator):
    def __init__(self):
        self.queuegenerator = QueueGenerator()
        self.queues = self.queuegenerator.rq_queues

    def get_parser(self):
        return parser_func

    def is_duplicates(self, data):
        return False

    def assign_parse_tasks(self):
        tasks = self.filter_downloaded_tasks()
        print len(tasks)
        for task in tasks:
            parser_function = self.get_parser()
            priority = self.get_task_priority(task)
            data = self.get_task_source_data(task)
            if not self.is_duplicates(data):
                if self.assign_parse_task(priority, parser_function, data) is not None:
                    pass
                else:
                    logging.info('Queue for priority "% s" is full' % priority)
                    pass
            else:
                logging.error("Parse task duplicates -- % s (uri)" % data.crawlertask.uri)
        return self.queues

    def assign_parse_task(self, priority, parser_function, data):
        try:
            if data and not self.null(data.response_body):
                parse_job_id = self.queuegenerator.enqueue(priority, parser_function, args=[data])
                if parse_job_id is None:
                    return None
                else:
                    CrawlerAnalyzedData(crawler_task=data.crawlertask, update_date=datetime.datetime.now()).save()
                    logging.info("Parse task successfully added")
                    return parse_job_id
            elif data and self.null(data.response_body):
                data.crawlertask.update(status=6)
        except:
            logging.error("Error assigning task when enqueuing")

    def null(self, s):
        d = ast.literal_eval(s)
        if not d:
            return True
        else:
            if not d[d.keys()[0]]:
                return True
            else:
                return False


class QueueGenerator(object):
    def __init__(self, redis_url=settings.STRUCTURE_REDIS, queue_length=Consts.QUEUE_MAX_LENGTH):
        self.connection = redis.Redis.from_url(redis_url) if redis_url else redis.Redis()
        self.too_high_queue = rq.Queue(Consts.QUEUE_PRIORITY_TOO_HIGH, connection=self.connection)
        self.high_queue = rq.Queue(Consts.QUEUE_PRIORITY_HIGH, connection=self.connection)
        self.normal_queue = rq.Queue(Consts.QUEUE_PRIORITY_NORMAL, connection=self.connection)
        self.low_queue = rq.Queue(Consts.QUEUE_PRIORITY_LOW, connection=self.connection)
        self.max_queue_length = queue_length if queue_length is not None else settings.MAX_QUEUE_LENGTH
        self.rq_queues = (self.too_high_queue, self.high_queue, self.normal_queue, self.low_queue)

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
            return structure_job.id


class ExtracterQueueGenerator(object):
    def __init__(self, redis_url=settings.EXTRACTER_REDIS, queue_length=ExtracterConsts.QUEUE_MAX_LENGTH):
        self.connection = redis.Redis.from_url(redis_url) if redis_url else redis.Redis()
        self.too_high_queue = rq.Queue(ExtracterConsts.QUEUE_PRIORITY_TOO_HIGH, connection=self.connection)
        self.high_queue = rq.Queue(ExtracterConsts.QUEUE_PRIORITY_HIGH, connection=self.connection)
        self.normal_queue = rq.Queue(ExtracterConsts.QUEUE_PRIORITY_NORMAL, connection=self.connection)
        self.low_queue = rq.Queue(ExtracterConsts.QUEUE_PRIORITY_LOW, connection=self.connection)
        self.max_queue_length = queue_length if queue_length is not None else settings.MAX_QUEUE_LENGTH
        self.rq_queues = (self.too_high_queue, self.high_queue, self.normal_queue, self.low_queue)

    def filter_parsed_tasks(self):
        parsed_tasks = CrawlerTask.objects(status=7)
        if parsed_tasks is None:
            logging.info("No parsed (status = 7) tasks")
        return parsed_tasks

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
            return extracter_job.id


def parser_func(data):
    if data is None:
        return None
    data.crawlertask.update(status=7)
    crawler_analyzed_data = CrawlerAnalyzedData.objects(crawler_task=data.crawlertask).first()
    if crawler_analyzed_data:
        crawler_analyzed_data.update(update_date=datetime.datetime.now(), analyzed_data=data.response_body)
    else:
        data.crawlertask.update(status=6)
    return data.crawlertask.id
    '''
    structureconfig = StructureConfig.objects.get(job_copy_id = data.crawlertask.job.id)
    crawler_analyzed_data = CrawlerAnalyzedData.objects(crawler_task = data.crawlertask).first()

    if structureconfig is not None:
        current_dir = os.getcwd()
        parsers_dir = "/home/webapps/cr-clawer/clawer/structure/parsers"
        # parsers_dir = "structure/parsers"
        if not os.path.isdir(parsers_dir):      #判断解析器目录是否存在，如不存在则创建
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
                logging.info("%s (uri) is successfully parsed -- Results saved" % data.crawlertask.uri)
                return analyzed_data
            elif analyzed_data is None:
                data.crawlertask.update(status = 6)
                crawler_analyzed_data.update(update_date = datetime.datetime.now())
                logging.error("Something wrong while parsing %s (uri) -- NULL result" % data.crawlertask.uri)
        except Exception as e:
            data.crawlertask.update(status = 6)
            crawler_analyzed_data.update(update_date = datetime.datetime.now())
            logging.error("Error parsing with %s.py" % structureconfig.parser.parser_id)

        os.chdir(current_dir)                    #切换回之前的工作目录
    else:
        logging.error("Error finding Configuration file (StructureConfig) for task: %s (uri)" % data.crawlertask.uri)

    return data.clawertask.id
    '''


class ExtracterGenerator(StructureGenerator):

    sqlgenerator = SqlGenerator()    # 用于处理源数据生成sql，并导入关系数据库
    configure = None

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
            print 'start assign extract tasks......'
            priority = self.get_task_priority(task)
            # db_conf = self.get_extracter_db_config(task)
            # mappings = self.get_extracter_mappings(task)
            # extracter = self.get_extracter(db_conf, mappings)
            data = self.get_task_analyzed_data(task)    # 获取一条解析成功的数据
            conf = self.get_extracter_conf(data)    # 获取一条与任务相关的导出器配置
            sql_file_name = conf['database']['destination_db']['dbname']
            sql_file_name = '/tmp/table_%s.sql' % sql_file_name
            if conf != self.configure:  # 如果配置文件发生变化，则重新建表
                self.configure = conf
                self.sqlgenerator.test_table(conf, sql_file_name)
                self.sqlgenerator.test_restore(sql_file_name)
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

        # 直接读入配置文件, 仅支持工商
        conf_path = settings.EXTRACTER_CONFIG_PATH
        configure_dict = open(conf_path).read()
        configure_dict = json.loads(configure_dict)
        return configure_dict

        """
        # 从mongo中读入配置, 需在生成器导入脚本的同时将配置入库
        extracterstructureconfig = ExtracterStructureConfig.objects(job=data.crawler_task.job).first() # 获取导出器配置
        if extracterstructureconfig:
            try:
                extracter_configure = extracterstructureconfig.extracter.extracter_config.encode('utf8')  # extracter_conf 为字符串格式的配置
                configure_dict = json.loads(extracter_configure)
            except Exception as e:
                logging.error('Get extracter config error')
            return configure_dict
        """

    @classmethod
    def extract_fields(self, extracter_conf, data):
        data = ast.literal_eval(data)
        """生成sql语句并导出字段"""
        try:
            sql_file_name = extracter_conf['database']['destination_db']['dbname']
            sql_file_name = '/tmp/data_%s.sql' % sql_file_name
            result = self.sqlgenerator.test_get_data(extracter_conf, data, sql_file_name)
            if not result:
                return False
            self.sqlgenerator.test_restore(sql_file_name)
        except:
            return False
        return True

    @classmethod
    def extracter(self, conf, data):

        if not data:
            return False
        """导出器"""
        try:
            result = self.extract_fields(conf, data.analyzed_data)    # data.analyzed_data 为一条解析后的JSON源数据
            if result:
                data.crawler_task.update(status=CrawlerTask.STATUS_EXTRACT_SUCCESS)    # status: 9导出成功, 8导出失败
                crawler_extract_info = CrawlerExtracterInfo.objects(extract_task=data.crawler_task).first()
                update_date=datetime.datetime.now()
                crawler_extract_info.update(extracted_status=True, update_date=update_date)    # 更新导出状态信息
                logging.info('Extract fields succeed')
                # 日志写入 mongo
                ExtractLog(extract_task=data.crawler_task,
                        job=data.crawler_task.job,
                        status=CrawlerTask.STATUS_EXTRACT_SUCCESS,
                        reason='Extract fields succeed', 
                        add_datetime=update_date).save()

            else:
                data.crawler_task.update(status=CrawlerTask.STATUS_EXTRACT_FAIL)
                logging.error('Extract fields failed')
                ExtractLog(extract_task=data.crawler_task,
                        job=data.crawler_task.job,
                        status=CrawlerTask.STATUS_EXTRACT_FAIL,
                        reason='Extract field failed', 
                        add_datetime=update_date).save()
        except Exception as e:
            logging.error('Extract fields error %s' % e)
            data.crawler_task.update(status=CrawlerTask.STATUS_EXTRACT_FAIL)
            ExtractLog(extract_task=data.crawler_task,
                    job=data.crawler_task.job,
                    status=CrawlerTask.STATUS_EXTRACT_FAIL,
                    reason=traceback.format_exc(), 
                    add_datetime=update_date).save()
            return False
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
            w.work()


class ExecutionExtracterTasks(object):
    def exec_task(self, queue=ExtracterConsts.QUEUE_PRIORITY_NORMAL):
        with rq.Connection():
            w = rq.Worker([queue])
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

    try:
        user = User.objects.get(username='user_name')
    except:
        user = User.objects.create_user('user_name', 'user_email', 'password')

    for count in range(0, 100):
        status = random.choice(range(1, 3))
        priority = random.choice(range(-1, 6))

        test_job_mysql = JobMySQL(creator=user,
                                  name="job_%d" % count,
                                  info="info",
                                  customer="customer",
                                  status=status,
                                  priority=priority,
                                  add_datetime=django.utils.timezone.now())
        test_job_mysql.save()

        test_job_mongodb = JobMongoDB(creator="creator_%d" % count,
                                      name="job_%d" % count,
                                      info="info",
                                      customer="customer",
                                      status=status,
                                      priority=priority,
                                      add_datetime=datetime.datetime.now())
        test_job_mongodb.save()
        test_parser = Parser(parser_id=str(count),
                             python_script=random.choice([right_script, wrong_script]),
                             update_date=django.utils.timezone.now())
        test_parser.save()

        test_crawlertask = CrawlerTask(test_job_mongodb, uri="test_uri_%d" % count, status=5)
        test_crawlertask.save()

        test_downloader = CrawlerDownload(test_job_mongodb)
        test_downloader.save()

        StructureConfig(job=test_job_mysql,
                        parser=test_parser,
                        job_copy_id=test_job_mongodb.id,
                        update_date=django.utils.timezone.now()).save()

        CrawlerDownloadData(test_job_mongodb, test_downloader, test_crawlertask).save()

    print "Data Inserted!"


def empty_test_data():
    JobMongoDB.drop_collection()
    JobMySQL.objects.all().delete()
    Parser.objects.all().delete()
    CrawlerTask.drop_collection()
    CrawlerDownload.drop_collection()
    StructureConfig.objects.all().delete()
    CrawlerDownloadData.drop_collection()
    CrawlerAnalyzedData.drop_collection()

    print "Data Cleaned!"


class TestExtracter(object):
    """测试导出器"""

    def __init__(self):
        pass


    def insert_extracter_test_data(self):

        config = open('structure/extracters/conf_csciwlpc_local.json').read()
        analyzeddata = open('structure/extracters/analyzed_data_csci.json')

        count = 0
        for line in analyzeddata:
            count += 1
            test_job = JobMongoDB("creator", "job_%d" % count, "info", "customer", random.choice(range(1, 3)),
                                  random.choice(range(-1, 6)), datetime.datetime.now())
            test_job.save()

            # test_extracter = ExtracterGenerator.extracter
            test_extracter = Extracter(count, config)
            test_extracter.save()

            test_crawlertask = CrawlerTask(test_job, uri="test_uri_%d" % count, status=7)
            test_crawlertask.save()

            ExtracterStructureConfig(job=test_job, extracter=test_extracter).save()

            processed_line = json.loads(line)['analyzed_data']

            CrawlerAnalyzedData(crawler_task=test_crawlertask, analyzed_data=processed_line).save()
        print "Inserted %s Extracter Test Data " % count

    def empty_test_data(self):

        JobMongoDB.drop_collection()
        Extracter.drop_collection()
        CrawlerTask.drop_collection()
        ExtracterStructureConfig.drop_collection()
        CrawlerAnalyzedData.drop_collection()
        CrawlerExtracterInfo.drop_collection()
        print "Extracter Test Data Cleaned!"
