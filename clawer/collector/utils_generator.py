#encoding=utf-8

import logging
import os
import time
import datetime
import subprocess
import socket
import traceback
import threading

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from collector.models import Job, CrawlerTask, CrawlerTaskGenerator, CrawlerGeneratorErrorLog, CrawlerGeneratorLog
import redis
import rq
from django.conf import settings

class DataPreprocess(object):

    def __init__(self, job_id):
        self.uris = None
        self.script = None
        self.schemes = ['http', 'https', 'ftp', 'ftps']
        job_doc = None
        try:
            job_doc = Job.objects.with_id(job_id)
        except Exception as e:
            logging.error("Can't find job_id: %s in mongodb!"%(job_id))
        self.job_id = job_id
        self.job = job_doc


    def __validate_uris(self, uri_list, schemes=None):
        """ validate uri from uri list,
            return valid uri list
        """
        uris=[]
        if not isinstance(uri_list, list):
            return uris
        # you can add param by yourself, default: schemes=['http', 'https', 'ftp', 'ftps']
        if schemes is not None and isinstance(schemes, list):
            self.schemes.extend(schemes)
        val = URLValidator(self.schemes)
        for uri in uri_list:
            try:
                val(uri)
                uris.append(uri)
            except ValidationError, e:
                logging.error("URI ValidationError: %s" %(uri))

        return uris

    def __dereplicate_uris(self, uri_list):
        """ dereplicate uri list using APIs from other modules
            return dereplicated uri list
        """
        pass
        return uri_list

    def read_from_strings(self, textarea, schemes=None):
        """ validate strings from textarea with schemes
            return valid uri list
        """
        uri_list = textarea.strip().split()
        valid_uris = self.__validate_uris(uri_list, schemes)
        dereplicated_uris = self.__dereplicate_uris(valid_uris)
        self.uris = dereplicated_uris
        return dereplicated_uris

    def save_text(self, text, schemes=None):
        """
        """
        uris = self.read_from_strings(text, schemes)
        for uri in uris:
            try:
                CrawlerTask(job= self.job, uri= uri).save()
            except Exception as e:
                logging.error("error occured when saving uri-- %s"%(type(e)))
        return True

    def save_script(self, script, cron):
        """ saving script with cron settings to mongodb
            if params are None or saving excepts return False
            else return True
        """
        if script is None:
            logging.error("Error occured when saving script -- script is None")
            return False
        if cron is None:
            logging.error("Error occured when saving script -- cron is None")
            return False
        try:
            CrawlerTaskGenerator(job = self.job, code = script, cron = cron).save()
        except Exception as e:
            logging.error("Error occured when saving script --%s"%(type(e)))
            return False
        return True


    def save(self, text=None, script=None, settings=None):
        """ save uri(schemes) or script(cron) to mongodb server
            return True if success else False
        """
        if text is not None:
            try:
                schemes = settings.pop('schemes', None)
                assert self.save_text(text, schemes)
            except AssertionError :
                logging.error("Error occured when saving text")
        elif script is not None:
            if not settings.has_key('cron'):
                logging.error("cron is not found in settings")
                return
            try:
                assert self.save_script(script, settings['cron'])
            except AssertionError:
                logging.error("Error occured when saving script")
        else:
            logging.error("Please input text or script!")

class GeneratorQueue(object):
    """ queue for generator dispatching
        there is 4 queues which are uri_super, uri_high, uri_medium, uri_low with 7 priority levels which are from -1 to 5
        each queue has a max length
    """
    SUPER_QUEUE = "uri_super"
    HIGHT_QUEUE = "uri_high"
    MEDIUM_QUEUE = "uri_medium"
    LOW_QUEUE = "uri_low"
    MAX_COUNT = 1000

    # def __init__(self, redis_url= settings.REDIS, queue_length=settings.MAX_QUEUE_LENGTH):
    def __init__(self, redis_url= None, queue_length=None):
        self.connection = redis.Redis.from_url(redis_url) if redis_url else redis.Redis()
        self.super_queue = rq.Queue(self.SUPER_QUEUE, connection=self.connection)
        self.high_queue = rq.Queue(self.HIGHT_QUEUE, connection=self.connection)
        self.medium_queue = rq.Queue(self.MEDIUM_QUEUE, connection=self.connection)
        self.low_queue = rq.Queue(self.LOW_QUEUE, connection=self.connection)
        self.max_queue_length = queue_length if queue_length is not None else self.MAX_COUNT
        # self.jobs = []

    def enqueue(self, priority, func, *args, **kwargs):
        q = None
        at_front = False
        if priority == -1:
            q = self.super_queue
        elif priority == 0 :
            q = self.high_queue
            at_front = True
        elif priority == 1:
            q = self.high_queue
            # at_front = False
        elif priority == 2:
            q = self.medium_queue
            at_front = True
        elif priority == 3:
            q = self.medium_queue
            # at_front = False
        elif priority == 4:
            q = self.low_queue
            at_front = True
        elif priority == 5:
            q = self.low_queue
            # at_front = False
        else:
            q = self.low_queue

        if q.count > self.max_queue_length:
            print "%s queue count is big than %d" % (q ,self.max_queue_length)
            return None
        kwargs['at_front'] = at_front
        job = q.enqueue(func, *args, **kwargs)
        # self.jobs.append(job)
        return job.id

class SafeProcess(object):

    def __init__(self, args, stdout=None, stderr=None, stdin=None):
        self.args = args
        self.stdout = stdout
        self.stderr = stderr
        self.stdin = stdin
        self.process = None
        self.timer = None
        self.process_exit_status = None
        self.timeout = 0

    def run(self, timeout=30):
        self.timeout = timeout
        self.timer = threading.Timer(timeout, self.force_exit)
        self.timer.start()

        self.process = subprocess.Popen(self.args, stdout=self.stdout, stderr=self.stderr, stdin=self.stdin)
        return self.process

    def wait(self):
        self.process_exit_status = self.process.wait()
        self.timer.cancel()
        return self.process_exit_status

    def force_exit(self):
        if not self.timer:
            return

        if self.timer.is_alive() and self.process:
            if self.process.stdout:
                self.process.stdout.write("timeout after %d seconds" % self.timeout)
            self.process.terminate()
        self.process_exit_status = 1


class GenerateCrawlerTask(object):

    def __init__(self, task_generator):
        from collector.models import CrawlerGeneratorLog
        self.task_generator = task_generator
        self.job = task_generator.job
        self.out_path = "/tmp/task_generator_%s" % str(self.task_generator.id)
        self.hostname = socket.gethostname()[:16]
        self.generate_log = CrawlerGeneratorLog(job=self.job, task_generator=self.task_generator, hostname=self.hostname)
        self.start_time = time.time()
        self.end_time = None
        self.content_bytes = 0


    def generate_task(self):
        """ 执行脚本，生成uri """
        from collector.models import Job, CrawlerTask, CrawlerTaskGenerator, CrawlerGeneratorLog
        logging.info("run task generator %s" % str(self.task_generator.id))
        if not (self.task_generator.status==CrawlerTaskGenerator.STATUS_ON and self.job.status==Job.STATUS_ON):
            return False

        path = self.task_generator.product_path()
        self.task_generator.write_code(path)
        out_f = open(self.out_path, "w")
        # [settings.Python, path]
        safe_process = SafeProcess(['~/Documents/virtualenv/bin/python', path], stdout=out_f, stderr=subprocess.PIPE)
        try:
            p = safe_process.run(1800)
        except OSError , e:
            print type(e)
            self.failed(e.child_traceback)
            return False
        except Exception, e:
            self.failed(e)
            return False

        err = p.stderr.read()
        status = safe_process.wait()
        if status != 0:
            logging.error("run task generator %s failed: %s" % (str(self.task_generator.id), err))
            out_f.close()
            self.failed(err)
            return False
        out_f.close()


        return True

    def failed(self, reason):
        from collector.models import CrawlerGeneratorLog

        if self.end_time is None:
            self.end_time = time.time()

        self.generate_log.status = CrawlerTaskGenerator.STATUS_FAIL
        self.generate_log.failed_reason = reason #[:1024]
        self.generate_log.content_bytes = self.content_bytes
        self.generate_log.spend_msecs = int(1000*(self.end_time - self.start_time))
        self.generate_log.save()

    def generate_task_failed(self):
        return False


    def run(self):
        from clawer.models import ClawerTaskGenerator, Clawer, ClawerTask, ClawerGenerateLog



        out_f = open(self.out_path, "r")
        for line in out_f:
            try:
                self.content_bytes += len(line)
                js = json.loads(line)
                if self.url_cache.check_url(js["uri"]):
                    continue

                clawer_task = ClawerTask.objects.create(clawer=self.clawer,
                                                        task_generator=self.task_generator,
                                                        uri=js["uri"],
                                                        cookie=js.get("cookie"),
                                                        args=js.get("args"))
                #trace it
                self.monitor.trace_task_status(clawer_task)
            except:
                logging.error("add %s failed: %s", line, traceback.format_exc(10))
                self.failed(traceback.format_exc(10))

        out_f.close()
        os.remove(self.out_path)

        #success
        if self.end_time is None:
            self.end_time = time.time()
        self.generate_log.status = ClawerGenerateLog.STATUS_SUCCESS
        self.generate_log.content_bytes = self.content_bytes
        self.generate_log.spend_msecs = int(1000*(self.end_time - self.start_time))
        self.generate_log.save()

        return True










def generate_uri_task( crawler_generator):
    """
    generate uri with script and settings in slave
    this function needs to be pushed into queue
    """

    return True

class GeneratorDispatch(object):
    """dispatch generator """
    def __init__(self, job_id):
        super(GeneratorDispatch, self).__init__()
        try:
            job_doc = Job.objects.with_id(job_id)
        except Exception as e:
            logging.error("Can't find job_id: %s in mongodb!"%(job_id))
        self.job_id = job_id
        self.job = job_doc
        self.priority = job_doc.priority

    def get_generator_object(self):
        try:
            generator_object =  CrawlerTaskGenerator.objects(job = self.job_id, status = 4).first()
        except Exception as e:
            logging.error("Something wrong when getting generating objects")
        return generator_object


    def dispatch_uri(self):
        """
            Dispatch generator task function according to job priority
        """
        queue = GeneratorQueue()
        generator_object = self.get_generator_object()
        priority = self.priority
        while(priority < 6):
            if not queue.enqueue(priority, generate_uri_task, args = [generator_object]) :
                if priority in (4, 5):
                    logging.error("The Queue is filled in! The new job is discarded.")
                    break
                else:
                    # push the job in the front of closed queue with lower priority
                    # eg: if priority =2 ,then push job to high queue's front end, priority = 0
                    #   if priority = 1, then push job to medium queue's front end, priority = 2
                    priority += 2 if not priority%2 else 1
            else:
                break
        return queue



