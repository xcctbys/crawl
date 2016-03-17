#coding=utf-8
import math
import requests
import logging
import traceback
import subprocess
import time
import rq
import redis
from random import random
import types
import socket
import shutil
import os
import json

from django.conf import settings
from django.core.mail import send_mail

from html5helper.utils import do_paginator
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import threading
import urlparse
import datetime
import stat
from enterprise.utils import EnterpriseDownload
import raven




def check_auth_for_api(view_func):
    """ mobile GET must have secret="", return dict
    """
    def wrap(request, *args, **kwargs):
        if request.user and request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        
        login_error = {"is_ok":False, "reason":u"登陆凭证已经失效，请重新登陆", "login_timeout":True}
        return login_error
    return wrap
    

class EasyUIPager(object):
    
    def __init__(self, queryset, request):
        self.queryset = queryset
        self.request = request
        
    def query(self):
        """ return dict
        """
        page = int(self.request.GET.get("page", '1'))
        rows = int(self.request.GET.get("rows", '20'))
        sort = self.request.GET.get("sort", "id")
        order = self.request.GET.get("order", "desc")
        
        result = {"is_ok":True, "rows":[], "total":0, "page": page, "total_page":0}
        
        def get_order(o):
            return "" if o == "asc" else "-"
        
        qs = self.queryset
        if sort:
            items = qs.order_by("%s%s" % (get_order(order), sort))
        else:
            items = qs
        pager = do_paginator(items, page, rows)
        result["total"] = pager.paginator.count
        result["rows"] = [x.as_json() for x in pager]
        result["total_page"] = math.ceil(float(result["total"])/rows)
        
        return result
        

class Download(object):
    ENGINE_REQUESTS = "requests"
    ENGINE_PHANTOMJS = "phantomjs"
    ENGINE_SELENIUM = "selenium"
    
    ENGINE_CHOICES = (
        (ENGINE_REQUESTS, "REQUESTS"),
        (ENGINE_PHANTOMJS, "PHANTOMJS"),
        (ENGINE_SELENIUM, "SELENIUM"),
    )
    
    def __init__(self, url, engine=ENGINE_REQUESTS, js=None):
        self.engine = engine
        self.url = url
        self.spend_time = 0  #unit is million second
        self.cookie = ""
        self.content = None
        self.failed_exception = None
        self.content_encoding = None
        self.failed = False
        self.headers = {}
        self.response_headers = {}
        self.proxies = []
        self.cookies = {}
        self.js = None
        self.sentry = SentryClient()
        
    def add_cookie(self, cookie):
        self.headers["Cookie"] = cookie
        nvs = cookie.split(";")
        for nv in nvs:
            tmp = nv.split("=")
            if len(tmp) != 2:
                continue
            self.cookies[tmp[0]] = tmp[1] 
        
    def add_proxies(self, proxies):
        self.proxies = proxies
        
    def add_headers(self, headers):
        self.headers.update(headers)
        
    def split_proxy(self, proxy):
        tmp = urlparse.urlsplit(proxy)
        addr = tmp.hostname
        port = tmp.port or 80
        return addr, port
        
    def download(self):
        
        if self.url.find("enterprise://") == 0:
            self.download_with_enterprise()
            return
        
        if self.engine == self.ENGINE_REQUESTS:
            self.download_with_requests()
        elif self.engine == self.ENGINE_PHANTOMJS:
            self.download_with_phantomjs()
        elif self.engine == self.ENGINE_SELENIUM:
            self.download_with_selenium()
        else:
            self.download_with_phantomjs()
    
    def download_with_requests(self):
        r = None
        start = time.time()
        
        try:
            r = requests.get(self.url, headers=self.headers, proxies=self.proxies)
        except:
            self.failed = True
            self.failed_exception = traceback.format_exc(10)
            self.sentry.capture()
        
        if self.failed:
            end = time.time()
            self.spend_time = end - start
            return
        
        self.response_headers = r.headers
        self.content = r.content
        self.content_encoding = r.encoding
        end = time.time()
        self.spend_time = end - start
    
    def download_with_phantomjs(self):
        start = time.time()
        args = ["/usr/bin/phantomjs", '--disk-cache=true', '--local-storage-path=/tmp/phantomjs_cache', '--load-images=false']
        
        if len(self.proxies) > 1:
            proxy = self.proxies[random.randint(0, len(self.proxies) - 1)]
            args.append("--proxy=%s" % proxy)
        args += [settings.DOWNLOAD_JS, self.url]
        if "Cookie" in self.headers:
            args.append(self.headers["Cookie"])

        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  #("%s %s" % (settings.PYTHON, path), "r")
        self.content = p.stdout.read()
        self.failed_exception = p.stderr.read()
        status = p.wait()
        
        end = time.time()
        self.spend_time = end - start
        
        if status != 0:
            self.failed = True    
            return
        
    def download_with_selenium(self):
        from selenium import webdriver
        
        start = time.time()
        
        firefox_log_file = open("/tmp/firefox.log", "a+")
        firefox_binary = FirefoxBinary(log_file=firefox_log_file)
        
        firefox_profile = webdriver.FirefoxProfile()
        if len(self.proxies) > 0:
            proxy = self.proxies[0]
            addr, port = self.split_proxy(proxy)
            firefox_profile.set_preference("network.proxy.type", 1)
            firefox_profile.set_preference("network.proxy.http", addr)
            firefox_profile.set_preference("network.proxy.http_port", port)
            firefox_profile.update_preferences()
        
        driver = webdriver.Firefox(firefox_binary=firefox_binary, firefox_profile=firefox_profile)
        driver.set_page_load_timeout(30)
        
        try:
            if self.cookies:
                driver.add_cookie(self.cookies)
            driver.get(self.url)
            if self.js:
                driver.execute_script(self.js)
            self.content = driver.execute_script("return document.documentElement.outerHTML;")
        except:
            self.failed_exception = traceback.format_exc(10)
            self.failed = True
            self.sentry.capture()
        finally:
            driver.close()
            driver.quit()
        #remove files
        try:
            if os.path.exists(driver.profile.path):
                shutil.rmtree(driver.profile.path)
            if driver.profile.tempfolder is not None:
                shutil.rmtree(driver.profile.tempfolder)
        except:
            logging.error(traceback.format_exc(10))
            self.sentry.capture()
    
        end = time.time()
        self.spend_time = end - start
        
    def download_with_enterprise(self):
        start = time.time()
        
        try:
            downloader = EnterpriseDownload(self.url)
            self.content = downloader.download()
        except:
            self.failed = True
            self.failed_exception = traceback.format_exc(10)
            self.sentry.capture()
            logging.warning(self.failed_exception)
            
        end = time.time()
        self.spend_time = end - start
        
            

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
    
        
class UrlCache(object):
    
    def __init__(self, redis_url=settings.URL_REDIS):
        self.redis_url = redis_url
        self.connection = None
        self.max_url_count = 10000
        self.key_name = "urlcache"
        
    def check_url(self, url):
        if not self.connection:
            self.connection = redis.Redis.from_url(self.redis_url)
        
        if self.connection.sismember(self.key_name, url):
            return True
        
        if self.connection.scard(self.key_name) >= self.max_url_count:
            self.connection.spop(self.key_name)
        
        self.connection.sadd(self.key_name, url)
        
        return False
        
    def flush(self):
        if not self.connection:
            self.connection = redis.Redis.from_url(self.redis_url)
            
        self.connection.flushall()
        
        
class BackgroundQueue(object):
    QUEUE_NAME = "background"
    
    def __init__(self, is_urgency=False, redis_url=settings.REDIS):
        self.connection = redis.Redis.from_url(redis_url)
        self.queue = rq.Queue(self.QUEUE_NAME, connection=self.connection)
        self.jobs = []
        
    def enqueue(self, func, *args, **kwargs):
        job = self.queue.enqueue_call(func, *args, **kwargs)
        self.jobs.append(job)
        return job.id
    

class DownloadQueue(object):
    QUEUE_NAME = "task_downloader"
    URGENCY_QUEUE_NAME = "urgency_task_downloader"
    FOREIGN_QUEUE_NAME = "foreign_task_downloader"
    MAX_COUNT = 10000
    
    def __init__(self, redis_url=settings.REDIS):
        self.connection = redis.Redis.from_url(redis_url)
        self.queue = rq.Queue(self.QUEUE_NAME, connection=self.connection)
        self.urgency_queue = rq.Queue(self.URGENCY_QUEUE_NAME, connection=self.connection)
        self.foreign_queue = rq.Queue(self.FOREIGN_QUEUE_NAME, connection=self.connection)
        self.jobs = []
        
    def enqueue(self, queue_name, func, *args, **kwargs):
        q = None
        if queue_name == self.QUEUE_NAME:
            q = self.queue
        elif queue_name == self.FOREIGN_QUEUE_NAME:
            q = self.foreign_queue
        elif queue_name == self.URGENCY_QUEUE_NAME:
            q = self.urgency_queue
        else:
            q = self.queue
        
        if q.count > self.MAX_COUNT:
            print "queue count is big than %d" % self.MAX_COUNT
            return None
        
        job = q.enqueue(func, *args, **kwargs)
        self.jobs.append(job)
        return job.id
    
    
class SentryClient(object):
    
    def __init__(self):
        self.client = None
        if hasattr(settings, 'RAVEN_CONFIG'):
            self.client = raven.Client(dsn=settings.RAVEN_CONFIG["dsn"])
        
    def capture(self):
        if not self.client:
            return
        
        self.client.captureException()
    

class DownloadClawerTask(object):
    
    def __init__(self, clawer_task, clawer_setting):
        from clawer.models import ClawerDownloadLog, RealTimeMonitor
        
        self.clawer_task = clawer_task
        self.download_log = ClawerDownloadLog(clawer=clawer_task.clawer, task=clawer_task, hostname=socket.gethostname())
        self.monitor = RealTimeMonitor()
        self.background_queue = BackgroundQueue()
        self.headers = {"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0) Gecko/20100101 Firefox/40.0"}
        self.sentry = SentryClient()
        
        self.clawer_setting = clawer_setting
        
        self.downloader = Download(self.clawer_task.uri, engine=self.clawer_setting.download_engine, js=self.clawer_setting.download_js)
        
        if self.clawer_setting.proxy:
            self.downloader.add_proxies(self.clawer_setting.proxy.strip().split("\n"))
        
        if self.clawer_task.cookie:
            self.headers["cookie"] = self.clawer_task.cookie
            self.downloader.add_cookie(self.clawer_task.cookie)
        if self.clawer_setting.cookie:
            self.headers["cookie"] = self.clawer_task.cookie
            self.downloader.add_cookie(self.clawer_task.cookie)
            
        self.downloader.add_headers(self.headers)
        
    def download(self):
        from clawer.models import ClawerTask, ClawerDownloadLog
    
        if not self.clawer_task.status in [ClawerTask.STATUS_LIVE, ClawerTask.STATUS_PROCESS]:
            return 0
        
        failed = False
        
        self.downloader.download()
        
        if self.downloader.failed:
            self.download_failed()
            return 0
            
        #save
        try:
            path = self.clawer_task.store_path()
            if os.path.exists(os.path.dirname(path)) is False:
                os.makedirs(os.path.dirname(path), 0775)
                
            with open(path, "w") as f:
                content = self.downloader.content
                if isinstance(content, types.UnicodeType):
                    content = content.encode("utf-8")
                f.write(content)
            
            self.clawer_task.store = path
        except:
            failed = True
            self.download_log.failed_reason = traceback.format_exc(10)
            self.sentry.capture()
            
        if failed:
            self.download_failed()
            return 0
        
        #success handle
        self.clawer_task.status = ClawerTask.STATUS_SUCCESS
        self.clawer_task.save()
        
        if self.downloader.response_headers.get("content-length"):
            self.download_log.content_bytes = self.downloader.response_headers["Content-Length"]
        else:
            self.download_log.content_bytes = len(self.downloader.content)
        self.download_log.status = ClawerDownloadLog.STATUS_SUCCESS
        self.download_log.content_encoding = self.downloader.content_encoding
        self.download_log.spend_time = int(self.downloader.spend_time*1000)
        self.download_log.save()
        
        self.monitor.trace_task_status(self.clawer_task)
        return self.clawer_task.id
        
    def download_failed(self):
        from clawer.models import ClawerTask, ClawerDownloadLog
        
        self.download_log.status = ClawerDownloadLog.STATUS_FAIL
        if self.downloader.failed_exception:
            self.download_log.failed_reason = self.downloader.failed_exception
        self.download_log.spend_time = int(self.downloader.spend_time*1000)
        self.background_queue.enqueue(clawer_download_log_delay_save, [self.download_log])
        
        self.clawer_task.status = ClawerTask.STATUS_FAIL
        self.background_queue.enqueue(clawer_task_delay_save, [self.clawer_task])
        
        self.monitor.trace_task_status(self.clawer_task)
    

class AnalysisClawerTask(object):
    
    def __init__(self, clawer, clawer_task):
        from clawer.models import RealTimeMonitor, ClawerAnalysisLog
        
        self.clawer = clawer
        self.clawer_task = clawer_task
        self.monitor = RealTimeMonitor()
        self.background_queue = BackgroundQueue()
        self.hostname = socket.gethostname()[:16]
        self.runing_analysis = self.clawer.runing_analysis()
        self.analysis_log = ClawerAnalysisLog(clawer=self.clawer, task=self.clawer_task, hostname=self.hostname, analysis=self.runing_analysis)
    
    def analysis(self):
        from clawer.models import ClawerAnalysisLog, ClawerTask
        
        path = self.runing_analysis.product_path()
        
        out_f = open(self.analysis_log.result_path(), "w+b")
        safe_process = SafeProcess([settings.PYTHON, path], stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=out_f)
        try:
            p = safe_process.run(300)
        except Exception, e:
            self.analysis_log.status = ClawerAnalysisLog.STATUS_FAIL
            self.analysis_log.failed_reason = e.child_traceback
        
        try:
            p.stdin.write(json.dumps({"path":self.clawer_task.store, "url":self.clawer_task.uri, "args":self.clawer_task.args}))
            p.stdin.close()    
            
            err = p.stderr.read()
            retcode = safe_process.wait()
            if retcode == 0:
                out_f.seek(0)
                result = json.loads(out_f.read())
                result["_url"] = self.clawer_task.uri
                if self.clawer_task.cookie:
                    result["_cookie"] = self.clawer_task.cookie
                self.analysis_log.result = json.dumps(result)
                self.analysis_log.status = ClawerAnalysisLog.STATUS_SUCCESS
            else:
                self.analysis_log.status = ClawerAnalysisLog.STATUS_FAIL
                self.analysis_log.failed_reason = err
                
            out_f.close()
            os.remove(self.analysis_log.result_path()) 
        except:
            self.analysis_log.status = ClawerAnalysisLog.STATUS_FAIL
            self.analysis_log.failed_reason = traceback.format_exc(10)
        
        self.background_queue.enqueue(clawer_analysis_log_delay_save, [self.analysis_log])    
        
        #update clawer task status
        if self.analysis_log.status == ClawerAnalysisLog.STATUS_SUCCESS:
            self.clawer_task.status = ClawerTask.STATUS_ANALYSIS_SUCCESS
        elif self.analysis_log.status == ClawerAnalysisLog.STATUS_FAIL:
            self.clawer_task.status = ClawerTask.STATUS_ANALYSIS_FAIL
        self.background_queue.enqueue(clawer_task_delay_save, [self.clawer_task])
        #trace it
        self.monitor.trace_task_status(self.clawer_task)
    

class GenerateClawerTask(object):
    
    def __init__(self, task_generator):
        from clawer.models import ClawerGenerateLog, RealTimeMonitor
        
        self.task_generator = task_generator
        self.clawer = self.task_generator.clawer
        self.out_path = "/tmp/task_generator_%d" % self.task_generator.id
        self.monitor = RealTimeMonitor()
        self.hostname = socket.gethostname()[:16]
        self.generate_log = ClawerGenerateLog(clawer=self.clawer, task_generator=self.task_generator, hostname=self.hostname)
        self.start_time = time.time()
        self.end_time = None
        self.content_bytes = 0
        self.url_cache = UrlCache()
        
    def run(self):
        from clawer.models import ClawerTaskGenerator, Clawer, ClawerTask, ClawerGenerateLog
        
        logging.info("run task generator %d" % self.task_generator.id)
        if not (self.task_generator.status==ClawerTaskGenerator.STATUS_ON and self.clawer.status==Clawer.STATUS_ON):
            return False
        
        path = self.task_generator.product_path()
        self.task_generator.write_code(path)
        
        out_f = open(self.out_path, "w")
        
        safe_process = SafeProcess([settings.PYTHON, path], stdout=out_f, stderr=subprocess.PIPE)
        try:
            p = safe_process.run(1800)
        except Exception, e:
            self.failed(e.child_traceback)
            return False
        
        err = p.stderr.read()
        status = safe_process.wait()
        if status != 0:
            logging.error("run task generator %d failed: %s" % (self.task_generator.id, err))
            out_f.close()
            self.failed(err)
            return False
        out_f.close()
        
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
    
    def failed(self, reason):
        from clawer.models import ClawerGenerateLog
        
        if self.end_time is None:
            self.end_time = time.time()
            
        self.generate_log.status = ClawerGenerateLog.STATUS_FAIL
        self.generate_log.failed_reason = reason[:1024]
        self.generate_log.content_bytes = self.content_bytes
        self.generate_log.spend_msecs = int(1000*(self.end_time - self.start_time))
        self.generate_log.save()
        

class MonitorClawerHour(object):
    
    def __init__(self):
        from clawer.models import Clawer
        
        self.result_path = settings.CLAWER_RESULT
        self.clawers = Clawer.objects.filter(status=Clawer.STATUS_ON)
        self.hour = datetime.datetime.now().replace(minute=0, second=0, microsecond=0) - datetime.timedelta(minutes=120)
        self.reports = []  # {'title': "", 'content': '', 'to': []}
    
    def monitor(self):
        if os.path.exists(self.result_path) is False:
            return
        
        for clawer in self.clawers:
            self._do_check(clawer)
            
        for clawer in self.clawers:
            self._do_report(clawer)
            
        self._send_mail()
        
    def _do_check(self, clawer):
        from clawer.models import ClawerHourMonitor
        #remove old
        ClawerHourMonitor.objects.filter(clawer=clawer, hour=self.hour).delete()
        
        clawer_hour_monitor = ClawerHourMonitor(clawer=clawer, hour=self.hour)
        target_path = os.path.join(self.result_path, "%s/%s" % (clawer.id, self.hour.strftime("%Y/%m/%d/%H.json.gz")))
        if os.path.exists(target_path) is False:
            clawer_hour_monitor.bytes = 0
            print "not found target path is %s" % target_path
        else:
            file_stat = os.stat(target_path)
            clawer_hour_monitor.bytes = file_stat[stat.ST_SIZE]
            print "target size is %s" % clawer_hour_monitor.bytes
            
        clawer_hour_monitor.save()
        print "clawer hour monitor id %d, bytes %d" % (clawer_hour_monitor.id, clawer_hour_monitor.bytes)
    
    def _do_report(self, clawer):
        from clawer.models import ClawerHourMonitor
        
        need_report = False
        
        try:
            current = ClawerHourMonitor.objects.get(hour = self.hour, clawer = clawer)
        except:
            return
            
        if need_report == False:
            clawer_hour_monitors = ClawerHourMonitor.objects.filter(hour__lt=self.hour, clawer=clawer).order_by("hour")[:3]
            for item in clawer_hour_monitors:
                variance = current.bytes - item.bytes
                if variance < 0 and abs(variance) < item.bytes*0.1:
                    need_report = True
                    current.is_exception = True
                    current.save()
                    break
            
        if need_report is False:
            return
        
        #send mail
        report_mails = clawer.settings().valid_report_mails()
        title = u'爬虫ID:%d(%s) 在 %s，数据异常' % (clawer.id, clawer.name, current.hour.strftime("%Y-%m-%d %Hh"))
        content = u'%s - 当前归并数据大小 %d bytes\r\n' % (socket.gethostname(), current.bytes)
        self.reports.append({'title': title, 'content': content, 'to': report_mails})
        
    def _send_mail(self):
        if len(self.reports) <= 0:
            return
        
        for report in self.reports:
            if report["to"]:
                send_mail(report['title'], report['content'], settings.EMAIL_HOST_USER, report['to'], fail_silently=False)
                
        #send to admin
        title = u"%d条报警，%s" % (len(self.reports), self.reports[0]["title"])
        content = u"\n".join([u"%s\n\t%s" % (x['title'], x['content']) for x in self.reports])
        admins = [x[1] for x in settings.ADMINS]
        send_mail(title, content, settings.EMAIL_HOST_USER, admins, fail_silently=False)
        
        
        
class MonitorClawerDay(MonitorClawerHour):
    
    def __init__(self):
        super(MonitorClawerDay, self).__init__()
        self.day = (datetime.datetime.now() - datetime.timedelta(1)).date()
        
    def _do_check(self, clawer):
        from clawer.models import ClawerDayMonitor
        #remove old
        ClawerDayMonitor.objects.filter(clawer=clawer, day=self.day).delete()
        
        clawer_day_monitor = ClawerDayMonitor(clawer = clawer, day = self.day)
        for hour in range(24):
            target_path = os.path.join(self.result_path, "%s/%s/%02d.json.gz" % (clawer.id, self.day.strftime("%Y/%m/%d"), hour))
            if os.path.exists(target_path) is False:
                print "not found target path is %s" % target_path
                continue
        
            file_stat = os.stat(target_path)
            clawer_day_monitor.bytes = file_stat[stat.ST_SIZE]
            print "target size is %s" % clawer_day_monitor.bytes
        
        clawer_day_monitor.save()
        print "clawer day monitor id %d, bytes %d" % (clawer_day_monitor.id, clawer_day_monitor.bytes)
    
    def _do_report(self, clawer):
        from clawer.models import ClawerDayMonitor
        
        need_report = False
        
        try:
            last_day_monitor = ClawerDayMonitor.objects.get(clawer=clawer, day=self.day)
            if last_day_monitor.bytes <= 0:
                need_report = True
        except:
            last_day_monitor = None
            need_report = True
            
        if need_report is False:
            return
        
        #add to reports
        report_mails = clawer.settings().valid_report_mails()
        title = u'爬虫ID:%d(%s) 在 %s，数据异常' % (clawer.id, clawer.name, last_day_monitor.day.strftime("%Y-%m-%d"))
        content = u'%s 当前归并数据大小 %d bytes' % (socket.gethostname(), last_day_monitor.bytes)
        self.reports.append({'title': title, 'content': content, 'to': report_mails})
        

#rqworker function
def download_clawer_task(clawer_task, clawer_setting):
    downloader = DownloadClawerTask(clawer_task, clawer_setting)
    ret = downloader.download()
    return ret


def clawer_task_reset(clawer_id, status):
    from clawer.models import ClawerTask
    
    new_status = ClawerTask.STATUS_LIVE
    if status in [ClawerTask.STATUS_ANALYSIS_FAIL, ClawerTask.STATUS_ANALYSIS_SUCCESS]:
        new_status = ClawerTask.STATUS_SUCCESS
        
    ret = ClawerTask.objects.filter(clawer_id=clawer_id, status=status).update(status=new_status)
    return ret


def clawer_download_log_delay_save(clawer_download_log):
    clawer_download_log.save()
    return clawer_download_log.id
    
    
def clawer_task_delay_save(clawer_task):
    clawer_task.save()
    return clawer_task.id


def clawer_analysis_log_delay_save(clawer_analysis_log):
    clawer_analysis_log.save()
    return clawer_analysis_log.id