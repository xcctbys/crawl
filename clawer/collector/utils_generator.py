#encoding=utf-8

import logging
import os
import time
import subprocess
import socket
import traceback
import threading
import json
import redis
import rq
import codecs
from datetime import datetime
from croniter import croniter
import multiprocessing

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from collector.models import Job, CrawlerTask, CrawlerTaskGenerator, CrawlerGeneratorErrorLog, CrawlerGeneratorLog, CrawlerGeneratorAlertLog
from collector.utils_cron import CronTab
from django.conf import settings

pool = None

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

    def run(self):
        if not self.generate_task():
            return
        self.save_task()


    def generate_task(self):
        """ 执行脚本，生成uri """
        # from collector.models import Job, CrawlerTask, CrawlerTaskGenerator, CrawlerGeneratorLog
        logging.info("run task generator %s" % str(self.task_generator.id))
        if not (self.task_generator.status==CrawlerTaskGenerator.STATUS_ON and self.job.status==Job.STATUS_ON):
            return False

        # path = self.task_generator.product_path()
        # self.task_generator.write_code(path)
        path = "/Users/princetechs5/crawler/cr-clawer/clawer/clawer/media/codes/570f73f6c3666e0af4a9efad_product.py"
        out_f = open(self.out_path, "w")
        settings.Python = "/Users/princetechs5/Documents/virtualenv/bin/python"
        safe_process = SafeProcess([ settings.Python, path], stdout=out_f, stderr=subprocess.PIPE)
        try:
            p = safe_process.run(1800)
        except OSError , e:
            print type(e)
            self.save_generate_log(CrawlerGeneratorLog.STATUS_FAIL, e.child_traceback)
            return False
        except Exception, e:
            self.save_generate_log(CrawlerGeneratorLog.STATUS_FAIL, e)
            return False

        err = p.stderr.read()
        status = safe_process.wait()
        if status != 0:
            logging.error("run task generator %s failed: %s" % (str(self.task_generator.id), err))
            out_f.close()
            self.save_generate_log(CrawlerGeneratorLog.STATUS_FAIL, err)
            return False
        self.save_generate_log(CrawlerGeneratorLog.STATUS_SUCCESS, "generate task succeed!")
        out_f.close()
        return True

    def __dereplicate_uris(self, uris):
        """ dereplicate uri using APIs from other modules
            return  true if uri is not dereplicated or false
        """
        return uris

    def save_task(self):
        out_f = open(self.out_path, "r")
        uris = []
        val = URLValidator()
        for line in out_f:
            try:
                self.content_bytes += len(line)
                js = json.loads(line)
                # validate uri
                val(js['uri'])
                uris.append(js['uri'])
            except ValidationError, e:
                logging.error("URI ValidationError: %s" %(uri))
        out_f.close()
        os.remove(self.out_path)
        dereplicated_uris = self.__dereplicate_uris(uris)

        for uri in dereplicated_uris:
            try:
                crawler_task = CrawlerTask( job=self.job,
                                            task_generator=self.task_generator,
                                            uri=uri)
                # crawler_task.args = ""
                crawler_task.save()
            except:
                logging.error("add %s failed: %s", line, traceback.format_exc(10))
                self.save_generate_log( CrawlerGeneratorLog.STATUS_FAIL ,traceback.format_exc(10))
        self.save_generate_log(CrawlerGeneratorLog.STATUS_SUCCESS, "After generating, save task succeed!")
        return True

    def save_generate_log(self, status, reason):
        # from collector.models import CrawlerGeneratorLog

        if self.end_time is None:
            self.end_time = time.time()
        if status == CrawlerGeneratorLog.STATUS_FAIL:
            self.generate_log.status = CrawlerGeneratorLog.STATUS_FAIL
        elif status == CrawlerGeneratorLog.STATUS_SUCCESS:
            self.generate_log.status = CrawlerGeneratorLog.STATUS_SUCCESS

        self.generate_log.failed_reason = reason #[:1024]
        self.generate_log.content_bytes = self.content_bytes
        self.generate_log.spend_msecs = int(1000*(self.end_time - self.start_time))
        self.generate_log.save()



def generate_uri_task( crawler_generator):
    """
    generate uri with script and settings in slave
    this function needs to be pushed into queue
    """
    generator =  GenerateCrawlerTask(crawler_generator)
    generator.run()
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
            generator_object =  CrawlerTaskGenerator.objects(job = self.job_id, status = CrawlerTaskGenerator.STATUS_ON).first()
        except Exception as e:
            logging.error("Something wrong when getting generating objects")
        return generator_object


    def run(self):
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


class CrawlerCronTab(object):
    """Overwrite python-crontab for myself"""
    # filename = settings.CRON_FILE
    def __init__(self, filename=None):
        super(CrawlerCronTab, self).__init__()
        self.filename = filename
        if not os.path.exists(self.filename):
            logging.error("The cron file %s is not exist!"%(filename))
            raise IOError("Crontab filename doesn't exist!")
        self.crontab = CronTab(tabfile = filename)
        self.cron_timeout = 60

    def remove_offline_jobs_from_crontab(self):
        jobs = Job.objects(status = Job.STATUS_OFF)
        for job in jobs:
            generator = CrawlerTaskGenerator.objects(job = job, status= CrawlerTaskGenerator.STATUS_ON).first()
            if not generator:
                continue
            comment = self._task_generator_cron_comment(job)
            count = self.crontab.remove_all(comment= comment)

    def update_online_jobs(self):
        jobs= Job.objects(status = Job.STATUS_ON)
        print len(jobs)
        for job in jobs:
            generator = CrawlerTaskGenerator.objects(job = job).order_by('-add_datetime').first()
            if not generator:
                continue
            if not self._test_save_code(generator):
                continue
            if not self._test_crontab(generator):
                continue
            if not self._test_install_crontab(generator):
                continue

            generator.status = CrawlerTaskGenerator.STATUS_ON
            generator.save()
            CrawlerTaskGenerator.objects(job = job, status = CrawlerTaskGenerator.STATUS_ON, id__ne= generator.id).update(status = CrawlerTaskGenerator.STATUS_OFF)

    def save_cron_to_file(self, filename= None):
        self.crontab.write(self.filename if not filename else filename)

    def _task_generator_cron_comment(self, job):
        return "job name:%s with id:%s"%(job.name, job.id)

    def _test_install_crontab(self, generator):
        comment = self._task_generator_cron_comment(generator.job)
        self.crontab.remove_all(comment = comment)
        if generator.status == CrawlerTaskGenerator.STATUS_OFF:
            return False
        command = "GeneratorDispatch('%s').run()"%(str(generator.job.id))
        cron = self.crontab.new(command= command, comment = comment)
        cron.setall(generator.cron.strip())
        return cron.render()

    def _test_crontab(self, generator):
        user_cron = CronTab()
        job = user_cron.new(command="/usr/bin/echo")
        job.setall(generator.cron.strip())
        if job.is_valid() == False:
            generator.cron = "%d * * * *" % random.randint(1, 59)
        return job.render()

    def _test_save_code(self, generator):
        path = generator.product_path()
        generator.write_code(path)
        return True

    def task_generator_install(self):
        """
            定期更新所有job的生成器crontab的本地文件信息
        """
        self.remove_offline_jobs_from_crontab()
        self.update_online_jobs()
        self.save_cron_to_file()
        return True

    def save_crons(self):
        base =  datetime(2010, 1, 25, 4, 46)
        # base = datetime.datetime.now()
        iters = croniter('*/5 * * * *', base)  # every 1 minites
        next = iters.get_next(datetime)
        return next

    def save_next_crons(self):
        from dateutil.parser import parse
        # timeout = settings.GENERATE_TIMEOUT

        # 获取出当前分钟 需要执行的任务列表
        last_time = datetime.now()
        # 定时任务，到时间强制退出。
        timer = threading.Timer(self.cron_timeout, force_exit)
        timer.start()
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        for job in self.crontab.crons:
            # 获得当前需要运行的cron任务
            now = datetime.now()
            base = parse(job.get_last_run())
            slices= job.slices.clean_render()
            iters = croniter(slices , base)
            next_time = iters.get_next(datetime)
            if next_time < now:
                try:
                    command = job.command
                    pool.apply_async(exec_command, (command,))
                except:
                    raise
                job.set_last_run(now)
        # 将本次运行的cron任务的上次运行时间写回到tabfile文件中
        self.save_cron_to_file()
         # 预警机制
        end_time = datetime.now()
        # import datetime
        # if end_time - last_time > datetime.timedelta(seconds=60):
        #     logging.error("Cron runtime exceeds 60s. Exit!")

    def task_generator_run(self):
        """
            每分钟运行例程
        """

        return True

def exec_command(command):
    c = compile(command, "", 'exec')
    exec c

def force_exit():
    pgid = os.getpgid(0)
    if pool is not None:
        pool.terminate()
        raise UnboundLocalError("Pool is not None!")
    os.killpg(pgid, 9)
    logging.error("Cron runtime exceeds 60s. Exit!")
    CrawlerGeneratorAlertLog(type = "TIMEOUT", reason="Cron runtime exceeds 60s. Exit!", hostname= socket.gethostname() )
    os._exit(1)

