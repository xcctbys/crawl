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
import ast
import time
import re
import dateutil

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from collector.models import Job, CrawlerTask, CrawlerTaskGenerator, CrawlerGeneratorLog, CrawlerGeneratorErrorLog, CrawlerGeneratorAlertLog, CrawlerGeneratorCronLog, CrawlerGeneratorDispatchLog
from collector.utils_cron import CronTab, CronSlices
from django.conf import settings
from uri_filter.api.api_filter_timing import timing_filter_api

pool = None

TTL = 60*60*24

def dereplicate_uris(uri_list, ttl = settings.URI_TTL):
    """ dereplicate uri list using APIs from other modules
        return dereplicated uri list
    """
    ttl = TTL if not ttl else ttl
    uri_list = timing_filter_api("uri_generator", uri_list, ttl)
    return uri_list

class DataPreprocess(object):
    """ 数据保存 """
    def __init__(self, job_id):
        self.uris = None
        self.script = None
        self.schemes = ['http', 'https', 'ftp', 'ftps']
        job_doc = None
        try:
            job_doc = Job.objects.with_id(job_id)
        except Exception as e:
            content = "%s : Can't find job_id: %s in mongodb!"%(type(e) ,job_id)
            logging.error(content)
            CrawlerGeneratorErrorLog(name="ERROR_JOB", content=content, hostname= socket.gethostname()).save()
            raise KeyError("Can't find job_id: %s in mongodb!"%(str(job_id)))
        self.job_id = job_id
        self.job = job_doc
        self.failed_uris = []

    def get_failed_uris(self):
        return self.failed_uris

    def extend_schemes(self, schemes):
        # you can add param by yourself, default: schemes=['http', 'https', 'ftp', 'ftps']
        if schemes is not None and isinstance(schemes, list):
            self.schemes.extend(schemes)

    def __validate_uris(self, uri_list, schemes=None):
        """ validate uri from uri list,
            return valid uri list
        """
        uris=[]
        if not isinstance(uri_list, list):
            return uris
        self.extend_schemes(schemes)
        val = URLValidator(self.schemes)
        for uri in uri_list:
            for uri in uri.split(";"):
                if uri:
                    try:
                        # for csv file
                        val(uri)
                        uris.append(uri)
                    except ValidationError, e:
                        content = "%s : URI ValidationError: %s" %(type(e) ,uri)
                        # logging.error(content)
                        CrawlerGeneratorErrorLog(name="ERROR_URI", content=content, hostname=socket.gethostname() ).save()
                        self.failed_uris.append(uri)
        return uris



    def read_from_strings(self, textarea, schemes=None):
        """ validate strings from textarea with schemes
            return valid uri list
        """
        uri_list = textarea.strip().splitlines()
        valid_uris = self.__validate_uris(uri_list, schemes)
        dereplicated_uris = dereplicate_uris(valid_uris)
        self.uris = dereplicated_uris
        return dereplicated_uris

    def read_from_file(self, filename=""):
        content = ""
        try:
            with open(filename, 'r') as f:
                content = f.read()
        except Exception as e:
            print "%s :Cannot open this file %s"%(type(e), filename)

        return content

    def save_text(self, text, schemes=None):
        """
        """
        uris = self.read_from_strings(text, schemes)
        for uri in uris:
            try:
                CrawlerTask(job= self.job, uri= uri, from_host= socket.gethostname()).save()
            except Exception as e:
                content = "%s : Error occured when saving uris %s."%(type(e), uri)
                # logging.error(content)
                CrawlerGeneratorErrorLog(name= "ERROR_SAVE", content= content, hostname= socket.gethostname()).save()
        return True

    def save_script(self, script, cron, code_type=1, schemes=[]):
        """ saving script with cron settings to mongodb
            if params are None or saving excepts return False
            else return True
        """
        if script is None:
            content = "ScriptError : Error occured when saving script with job :%s !"%(job.id)
            CrawlerGeneratorErrorLog(name= "ERROR_SAVE", content= content, hostname= socket.gethostname()).save()
            return False
        if not CronSlices.is_valid(cron):
            # logging.error("CronSlices is not valid!")
            content = "CronError : Error occured when saving cron with job :%s !"%(job.id)
            CrawlerGeneratorErrorLog(name= "ERROR_SAVE", content= content, hostname= socket.gethostname()).save()
            return False
        self.extend_schemes(schemes)
        try:
            CrawlerTaskGenerator(job = self.job, code = script, cron = cron, code_type = code_type, schemes= self.schemes).save()
        except Exception as e:
            content = "%s : Error occured when saving script with job :%s !"%(type(e), job.id)
            # logging.error(content)
            CrawlerGeneratorErrorLog(name= "ERROR_SAVE", content= content, hostname= socket.gethostname()).save()
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
            except AssertionError as e:
                content = "%s : Error occured when saving text"%( type(e) )
                # logging.error("Error occured when saving text")
                CrawlerGeneratorErrorLog(name= "ERROR_SAVE", content=content, hostname= socket.gethostname()).save()
        elif script is not None:
            if not settings.has_key('cron'):
                # logging.error("cron is not found in settings")
                content = "cron is not found in settings"
                CrawlerGeneratorErrorLog(name= "ERROR_SAVE", content=content, hostname= socket.gethostname()).save()
                return
            if not settings.has_key('code_type'):
                # logging.error("code_type is not found in settings")
                content = "code type is not found in settings"
                CrawlerGeneratorErrorLog(name= "ERROR_SAVE", content=content, hostname= socket.gethostname()).save()
                return
            try:
                schemes = settings.pop('schemes', None)
                assert self.save_script(script, settings['cron'], settings['code_type'], schemes)
            except AssertionError:
                # logging.error("Error occured when saving script")
                CrawlerGeneratorErrorLog(name= "ERROR_SAVE", content="Error occured when saving script ", hostname= socket.gethostname()).save()
        else:
            # logging.error("Please input text or script!")
            CrawlerGeneratorErrorLog(name= "ERROR_SAVE", content="No text or script found .", hostname= socket.gethostname()).save()

class GeneratorQueue(object):
    """ queue for generator dispatching
        there is 4 queues which are uri_super, uri_high, uri_medium, uri_low with 7 priority levels which are from -1 to 5
        each queue has a max length
    """
    SUPER_QUEUE = "uri_super"
    HIGHT_QUEUE = "uri_high"
    MEDIUM_QUEUE = "uri_medium"
    LOW_QUEUE = "uri_low"
    #MAX_COUNT = 1000

    SUPER_MAX_COUNT = 1000
    HIGH_MAX_COUNT = 2000
    MEDIUM_MAX_COUNT = 3000
    LOW_MAX_COUNT = 4000

    def __init__( self, redis_url= settings.REDIS, \
                  super_queue_length=settings.SUPER_MAX_QUEUE_LENGTH, \
                  high_queue_length=settings.HIGH_MAX_QUEUE_LENGTH, \
                  medium_queue_length=settings.MEDIUM_MAX_QUEUE_LENGTH, \
                  low_queue_length=settings.LOW_MAX_QUEUE_LENGTH):

        self.connection = redis.Redis.from_url(redis_url) if redis_url else redis.Redis()
        self.super_queue = rq.Queue(self.SUPER_QUEUE, connection=self.connection)
        self.high_queue = rq.Queue(self.HIGHT_QUEUE, connection=self.connection)
        self.medium_queue = rq.Queue(self.MEDIUM_QUEUE, connection=self.connection)
        self.low_queue = rq.Queue(self.LOW_QUEUE, connection=self.connection)
        #self.max_queue_length = queue_length if queue_length is not None else self.MAX_COUNT

        self.super_max_queue_length = super_queue_length if super_queue_length is not None else self.SUPER_MAX_COUNT
        self.high_max_queue_length = high_queue_length if high_queue_length is not None else self.HIGH_MAX_COUNT
        self.medium_max_queue_length = medium_queue_length if medium_queue_length is not None else self.MEDIUM_MAX_COUNT
        self.low_max_queue_length = low_queue_length if low_queue_length is not None else self.LOW_MAX_COUNT

        # self.jobs = []

    def enqueue(self, priority, func, *args, **kwargs):
        q = None
        at_front = False
        if priority == -1:
            q = self.super_queue
        elif priority == 0 :
            q = self.high_queue
            at_front = True
        elif priority == 1 :
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


        if q == self.super_queue:
            if q.count >= self.super_max_queue_length:
                return None
        elif q ==self.high_queue:
            if q.count >= self.high_max_queue_length:
                return None
        elif q == self.medium_queue:
            if q.count >= self.medium_max_queue_length:
                return None
        else:
            if q.count >= self.low_max_queue_length:
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
        self.task_generator = task_generator
        try:
            self.job = task_generator.job
        except Exception, e:
            CrawlerGeneratorErrorLog(name="ERROR_JOB", content="Can't find job id in task generator document!", hostname= socket.gethostname()).save()
            raise ValueError("Can't find job id in task generator document")
        self.schemes = task_generator.schemes
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

    @classmethod
    def get_tools_by_code_type(self, code_type):
        if code_type == CrawlerTaskGenerator.TYPE_PYTHON:
            return settings.PYTHON
        elif code_type == CrawlerTaskGenerator.TYPE_SHELL:
            return settings.SHELL
        return None

    def generate_task(self):
        """ 执行脚本，生成uri """
        logging.info("run task generator %s" % str(self.task_generator.id))
        if not (self.task_generator.status==CrawlerTaskGenerator.STATUS_ON and self.job.status==Job.STATUS_ON):
            return False

        path = self.task_generator.product_path()
        self.task_generator.write_code(path)
        out_f = open(self.out_path, "w")
        tools = self.get_tools_by_code_type(self.task_generator.code_type)
        safe_process = SafeProcess([ tools, path], stdout=out_f, stderr=subprocess.PIPE)
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
            # logging.error("run task generator %s failed: %s" % (str(self.task_generator.id), err))
            out_f.close()
            self.save_generate_log(CrawlerGeneratorLog.STATUS_FAIL, err)
            return False
        self.save_generate_log(CrawlerGeneratorLog.STATUS_SUCCESS, "generate task succeed!")
        out_f.close()
        return True

    def save_task(self):
        uris = []
        val = URLValidator(self.schemes)
        out_f = open(self.out_path, "r")
        for line in out_f:
            self.content_bytes += len(line)
            try:
                js = json.loads(line)
            except ValueError, e:
                js = ast.literal_eval(line)
                if not isinstance(js, dict):
                    # logging.error("The line %s is not dict or json"%(line))
                    CrawlerGeneratorErrorLog(name="ERROR_URI", content="The line %s is not dict or json"%(line), hostname= socket.gethostname()).save()
                    continue
            try:
                # validate uri
                if js.has_key('uri'):
                    val(js['uri'])
                    uris.append(js['uri'])
                else:
                    CrawlerGeneratorErrorLog(name="ERROR_JSON", content="JSON ValidationError without key 'uri' : %s" %(js), hostname= socket.gethostname()).save()
            except ValidationError, e:
                CrawlerGeneratorErrorLog(name="ERROR_URI", content="URI ValidationError: %s" %(js['uri']), hostname= socket.gethostname()).save()
        out_f.close()
        os.remove(self.out_path)
        dereplicated_uris = dereplicate_uris(uris)

        for uri in dereplicated_uris:
            try:
                crawler_task = CrawlerTask( job=self.job,
                                            task_generator=self.task_generator,
                                            uri=uri,
                                            from_host= socket.gethostname()
                                            )
                # crawler_task.args = ""
                crawler_task.save()
            except:
                # logging.error("add %s failed: %s", line, traceback.format_exc(10))
                content = traceback.format_exc(10)
                CrawlerGeneratorErrorLog(name="ERROR_URI", content=content, hostname=socket.gethostname() ).save()
        self.save_generate_log(CrawlerGeneratorLog.STATUS_SUCCESS, "After generating, save task succeed!")

    def save_generate_log(self, status, reason):
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
    异步队列任务函数：
    Function:   generate uri with script and settings in slave
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
            # logging.error("Can't find job_id: %s in mongodb!"%(job_id))
            CrawlerGeneratorErrorLog(name="ERROR_JOB", content="Can't find job_id: %s in mongodb!"%(job_id), hostname= socket.gethostname()).save()
            raise KeyError("Can't find job_id: %s in mongodb!"%(str(job_id)))
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
                    CrawlerGeneratorAlertLog(name = "QUEUES_FILLED_UP", content="Low queues is full. Discard the generator(%s) from priority %d Exit!"%(str(generator_object.id), generator_object.job.priority), hostname= socket.gethostname() ).save()
                    break
                else:
                    # push the job in the front of closed queue with lower priority
                    # eg: if priority =2 ,then push job to high queue's front end, priority = 0
                    #   if priority = 1, then push job to medium queue's front end, priority = 2
                    priority += 2 if not priority%2 else 1
            else:
                content="dispatch generator(%s)(%d) into queue with priority %d "%(str(generator_object.id), generator_object.job.priority, priority)
                CrawlerGeneratorDispatchLog(job = generator_object.job, task_generator= generator_object, content= content).save()
                break
        return queue


class CrawlerCronTab(object):
    """Overwrite python-crontab for myself"""
    def __init__(self, filename= settings.CRON_FILE):
        super(CrawlerCronTab, self).__init__()
        self.filename = filename
        if not os.path.exists(self.filename):
            logging.error("The cron file %s is not exist!"%(filename))
            if not os.path.exists(os.path.dirname(filename)):
                os.mkdir(os.path.dirname(filename))
            with open(filename, 'w') as f:
                pass
        self.crontab = CronTab(tabfile = filename)
        self.cron_timeout = 60
        self.exe_number = 0

    def remove_all_jobs_from_crontab(self):
        count = self.crontab.remove_all()

    def remove_offline_jobs_from_crontab(self):
        jobs = Job.objects(status = Job.STATUS_OFF)
        for job in jobs:
            generator = CrawlerTaskGenerator.objects(job = job, status= CrawlerTaskGenerator.STATUS_ON).first()
            if not generator:
                continue
            comment = self._task_generator_cron_comment(job)
            count = self.crontab.remove_all(comment= comment)

    def update_online_jobs(self):
        jobs= Job.objects(status = Job.STATUS_ON).order_by("+priority")
        print "The number of job is %d"%(len(jobs))
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

            if generator.status == CrawlerTaskGenerator.STATUS_ON:
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
            generator.save()
        return job.render()

    def _test_save_code(self, generator):
        path = generator.product_path()
        generator.write_code(path)
        return True

    def task_generator_install(self):
        """
            定期更新所有job的生成器crontab的本地文件信息
        """
        # self.remove_offline_jobs_from_crontab()
        base_time = time.time()
        self.remove_all_jobs_from_crontab()
        time1 = time.time()
        self.update_online_jobs()
        time2 = time.time()
        self.save_cron_to_file()
        time3 = time.time()
        logging.info("TOTAL instal time: %d ms, remove jobs:%d ms, update:%d ms, save:%d ms"%(int(1000*(time3-base_time)), int(1000*(time1-base_time)), int(1000*(time2-time1)), int(1000*(time3-time2))))
        return True

    def exec_and_save_current_crons(self):
        # 获取出当前分钟 需要执行的任务列表
        last_time = datetime.now()
        # 定时任务，到时间强制退出。
        timer = threading.Timer(self.cron_timeout, force_exit)
        timer.start()
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        self.exe_number = 0
        # time.sleep(50)
        for job in self.crontab.crons:
            # 获得当前需要运行的cron任务
            now = datetime.now()
            base = dateutil.parser.parse( str(job.last_run))
            slices= job.slices.clean_render()
            iters = croniter(slices , base)
            next_time = iters.get_next(datetime)
            if next_time < now:
                try:
                    command = job.command
                    comment = job.comment
                    cron = slices
                    pool.apply_async(exec_command, (command, comment, cron, ))
                    self.exe_number+=1
                except:
                    raise
                job.set_last_run(now)
        logging.info('Waiting for all subprocesses done...')
        pool.close()
        pool.join()
        # 将本次运行的cron任务的上次运行时间写回到tabfile文件中
        logging.info('All subprocesses done.')
        self.save_cron_to_file()
        logging.info('Save to file!')
        timer.cancel()

    def task_generator_run(self):
        """
            每分钟运行例程
        """
        self.exec_and_save_current_crons()
        return True


def exec_command(command, comment, cron):
    """
        通过exec执行command，解析comment出JOB的id从而获取此job的信息，并将结果保存至CrawlerGeneratorCronLog中。
    """
    def get_name_id_with_comment(comment):
        p =re.compile("name:(\w+).*?id:(\w+)")
        r = p.search(comment)
        if r:
            return r.groups()
        else:
            return ("", "")
    job_name, job_id = get_name_id_with_comment(comment)
    job = Job.objects(id= job_id).first()
    if not job:
        failed_reason = "Job %s with id %s is not found in mongodb!"%(job_name, job_id)
        logging.error(failed_reason)
        CrawlerGeneratorCronLog(job = job, status = CrawlerGeneratorCronLog.STATUS_FAIL, cron = cron, failed_reason= failed_reason, spend_msecs = 0).save()
        return
    pid = os.getpid()
    start_time = time.time()
    status = CrawlerGeneratorCronLog.STATUS_SUCCESS
    failed_reason =""
    try:
        c = compile(command, "", 'exec')
        exec c in globals(), locals()
    except Exception, e:
        status = CrawlerGeneratorCronLog.STATUS_FAIL
        failed_reason = traceback.format_exc(10)
    end_time = time.time()
    CrawlerGeneratorCronLog(job = job, status = status, cron = cron, failed_reason= failed_reason, spend_msecs =int(1000*(end_time-start_time))).save()



def force_exit():
    """
        通过定时器触发此函数，强制退出运行父进程，并将子进程杀死。
    """
    pgid = os.getpgid(0)
    if pool is not None:
        pool.terminate()
        raise UnboundLocalError("Pool is not None!")
    logging.error("Cron runtime exceeds 60s. Exit!")
    CrawlerGeneratorAlertLog(name = "TIMEOUT", content="Cron runtime exceeds 60s. Exit!", hostname= socket.gethostname() ).save()
    os.killpg(pgid, 9)
    os._exit(1)
