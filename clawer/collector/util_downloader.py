# coding:utf8
import os
import os.path
import sys
import commands
import requests
import time
import socket
import json
import threading
import random
import traceback
from collector.models import (CrawlerTask, CrawlerDownloadSetting, CrawlerDownload, CrawlerDownloadData,
                              CrawlerDownloadLog)
from django.conf import settings
from enterprise.utils import EnterpriseDownload


class Download(object):
    def __init__(self, task, crawler_download, crawler_download_setting):
        self.task = task
        self.crawler_download = crawler_download
        self.crawler_download_setting = crawler_download_setting

        self.reqst = requests.Session()
        self.reqst.headers.update(
            {'Accept': 'text/html, application/xhtml+xml, */*',
             'Accept-Encoding': 'gzip, deflate',
             'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
             'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

    def exec_command(self, commandstr, path=None):
        if path:
            sys.path.append(path)
        c = compile(commandstr, "", 'exec')
        exec c

    def download_with_enterprise(self):
        start_time = time.time()

        try:
            downloader = EnterpriseDownload(self.task.uri)
            list_res = downloader.download()
            list_result = json.loads(list_res)
            end_time = time.time()
            spend_time = end_time - start_time
            for result in list_result:
                requests_headers = result.get('requests_headers', 'None')
                response_headers = result.get('response_headers', 'None')
                requests_body = result.get('requests_body', 'None')
                response_body = str(result)
                remote_ip = result.get('remote_ip', 'None')
                hostname = str(socket.gethostname())
                cdd = CrawlerDownloadData(job=self.task.job,
                                          downloader=self.crawler_download,
                                          crawlertask=self.task,
                                          requests_headers=requests_headers,
                                          response_headers=response_headers,
                                          requests_body=requests_body,
                                          response_body=response_body,
                                          hostname=hostname,
                                          remote_ip=remote_ip)
                cdd.save()
                cdl = CrawlerDownloadLog(
                    job=self.task.job,
                    task=self.task,
                    status=CrawlerDownloadLog.STATUS_SUCCESS,
                    requests_size=sys.getsizeof(cdd.requests_headers) + sys.getsizeof(cdd.requests_body),
                    response_size=sys.getsizeof(cdd.response_headers) + sys.getsizeof(cdd.response_body),
                    failed_reason='Download task succeed!',
                    downloads_hostname=hostname,
                    spend_time=spend_time)
                cdl.save()

            # 改变这个任务的状态为下载成功
            self.task.status = CrawlerTask.STATUS_SUCCESS
            self.task.save()

        except Exception as e:
            # 改变这个任务的状态为下载失败
            end_time = time.time()
            spend_time = end_time - start_time
            # write_downloaddata_fail_log_to_mongo
            cdl = CrawlerDownloadLog(job=self.task.job,
                                     task=self.task,
                                     status=CrawlerDownloadLog.STATUS_FAIL,
                                     requests_size=0,
                                     response_size=0,
                                     failed_reason=traceback.format_exc(),
                                     downloads_hostname=str(socket.gethostname()),
                                     spend_time=spend_time)
            cdl.save()

            self.task.status = CrawlerTask.STATUS_FAIL
            self.task.save()
            print 'ERROR:', e
            print "Trackback:", traceback.format_exc()

    def download(self):
        self.task.status = CrawlerTask.STATUS_PROCESS
        self.task.retry_times += 1
        self.task.save()

        if self.task.uri.find("enterprise://") == 0:
            self.download_with_enterprise()
            return

        # 对该语言暂时还不支持时，直接任务失败，并写日志。
        if not self.crawler_download.types.is_support:
            cdl = CrawlerDownloadLog(job=self.task.job,
                                     task=self.task,
                                     status=CrawlerDownloadLog.STATUS_FAIL,
                                     requests_size=0,
                                     response_size=0,
                                     failed_reason="%s is %s" % (self.crawler_download.types.language,
                                                                 self.crawler_download.types.is_support),
                                     downloads_hostname=str(socket.gethostname()),
                                     spend_time=-1)
            cdl.save()

            # 改变这个任务的状态为下载失败
            self.task.status = CrawlerTask.STATUS_FAIL
            self.task.save()
            return

        print self.crawler_download.types.language, self.crawler_download.types.is_support

        if self.crawler_download.types.language == 'python':
            start_time = time.time()
            try:
                # print 'save code from db;import crawler_download.code; run()'
                sys.path.append(settings.CODE_PATH)
                filename = os.path.join(settings.CODE_PATH, 'pythoncode%s.py' % str(self.crawler_download.id))
                # sys.path.append( '/Users/princetechs3/my_code' )
                # filename = os.path.join( '/Users/princetechs3/my_code', 'pythoncode%s.py' % str(self.crawler_download.id))
                if not os.path.exists(filename):
                    with open(filename, 'w') as f:
                        f.write(self.crawler_download.code)

                result = self.exec_command('import pythoncode%s; result = pythoncode%s.run("%s")' % (
                    str(self.crawler_download.id), str(self.crawler_download.id), self.task.uri),
                                           path=os.path.dirname(filename))
                end_time = time.time()

                spend_time = end_time - start_time
                requests_headers = result.get('requests_headers', 'None')
                response_headers = result.get('response_headers', 'None')
                requests_body = result.get('requests_body', 'None')
                response_body = str(result)
                remote_ip = result.get('remote_ip', 'None')
                hostname = str(socket.gethostname())
                cdd = CrawlerDownloadData(job=self.task.job,
                                          downloader=self.crawler_download,
                                          crawlertask=self.task,
                                          requests_headers=requests_headers,
                                          response_headers=response_headers,
                                          requests_body=requests_body,
                                          response_body=response_body,
                                          hostname=hostname,
                                          remote_ip=remote_ip)
                cdd.save()
                cdl = CrawlerDownloadLog(
                    job=self.task.job,
                    task=self.task,
                    status=CrawlerDownloadLog.STATUS_SUCCESS,
                    requests_size=sys.getsizeof(cdd.requests_headers) + sys.getsizeof(cdd.requests_body),
                    response_size=sys.getsizeof(cdd.response_headers) + sys.getsizeof(cdd.response_body),
                    failed_reason='Download task succeed!',
                    downloads_hostname=hostname,
                    spend_time=spend_time)
                cdl.save()

                self.task.status = CrawlerTask.STATUS_SUCCESS
                self.task.save()
            except Exception:
                self.task.status = CrawlerTask.STATUS_FAIL
                self.task.save()
                end_time = time.time()
                spend_time = end_time - start_time
                cdl = CrawlerDownloadLog(job=self.task.job,
                                         task=self.task,
                                         status=CrawlerDownloadLog.STATUS_FAIL,
                                         requests_size=0,
                                         response_size=0,
                                         failed_reason=traceback.format_exc(),
                                         downloads_hostname=str(socket.gethostname()),
                                         spend_time=spend_time)
                cdl.save()
                print "Trackback:", traceback.format_exc()

        elif self.crawler_download.types.language == 'shell':
            start_time = time.time()
            try:
                filename = os.path.join(settings.CODE_PATH, 'shellcode%s.sh' % str(self.crawler_download.id))
                if not os.path.exists(filename):
                    with open(filename, 'w') as f:
                        f.write(self.crawler_download.code)
                result = commands.getstatusoutput('sh %s %s' % (filename, self.task.uri))
                result = dict()
                end_time = time.time()
                spend_time = end_time - start_time

                requests_headers = result.get('requests_headers', 'None')
                response_headers = result.get('response_headers', 'None')
                requests_body = result.get('requests_body', 'None')
                response_body = str(result)
                remote_ip = result.get('remote_ip', 'None')
                hostname = str(socket.gethostname())
                cdd = CrawlerDownloadData(job=self.task.job,
                                          downloader=self.crawler_download,
                                          crawlertask=self.task,
                                          requests_headers=requests_headers,
                                          response_headers=response_headers,
                                          requests_body=requests_body,
                                          response_body=response_body,
                                          hostname=hostname,
                                          remote_ip=remote_ip)
                cdd.save()
                cdl = CrawlerDownloadLog(
                    job=self.task.job,
                    task=self.task,
                    status=CrawlerDownloadLog.STATUS_SUCCESS,
                    requests_size=sys.getsizeof(cdd.requests_headers) + sys.getsizeof(cdd.requests_body),
                    response_size=sys.getsizeof(cdd.response_headers) + sys.getsizeof(cdd.response_body),
                    failed_reason='Download task succeed!',
                    downloads_hostname=hostname,
                    spend_time=spend_time)
                cdl.save()
                self.task.status = CrawlerTask.STATUS_SUCCESS
                self.task.save()
            except Exception:
                self.task.status = CrawlerTask.STATUS_FAIL
                self.task.save()
                end_time = time.time()
                spend_time = end_time - start_time
                cdl = CrawlerDownloadLog(job=self.task.job,
                                         task=self.task,
                                         status=CrawlerDownloadLog.STATUS_FAIL,
                                         requests_size=0,
                                         response_size=0,
                                         failed_reason=traceback.format_exc(),
                                         downloads_hostname=str(socket.gethostname()),
                                         spend_time=spend_time)
                cdl.save()
                print "Trackback:", traceback.format_exc()
            pass

        elif self.crawler_download.types.language == 'curl':
            start_time = time.time()
            try:
                result = commands.getstatusoutput('curl %s' % self.task.uri)
                end_time = time.time()
                spend_time = end_time - start_time

                requests_headers = 'None'
                response_headers = 'None'
                requests_body = 'None'
                response_body = str(result)
                remote_ip = 'None'
                hostname = str(socket.gethostname())
                cdd = CrawlerDownloadData(job=self.task.job,
                                          downloader=self.crawler_download,
                                          crawlertask=self.task,
                                          requests_headers=requests_headers,
                                          response_headers=response_headers,
                                          requests_body=requests_body,
                                          response_body=response_body,
                                          hostname=hostname,
                                          remote_ip=remote_ip)
                cdd.save()
                cdl = CrawlerDownloadLog(
                    job=self.task.job,
                    task=self.task,
                    status=CrawlerDownloadLog.STATUS_SUCCESS,
                    requests_size=sys.getsizeof(cdd.requests_headers) + sys.getsizeof(cdd.requests_body),
                    response_size=sys.getsizeof(cdd.response_headers) + sys.getsizeof(cdd.response_body),
                    failed_reason='Download task succeed!',
                    downloads_hostname=hostname,
                    spend_time=spend_time)
                cdl.save()
                self.task.status = CrawlerTask.STATUS_SUCCESS
                self.task.save()
            except Exception:
                self.task.status = CrawlerTask.STATUS_FAIL
                self.task.save()

                end_time = time.time()
                spend_time = end_time - start_time
                cdl = CrawlerDownloadLog(job=self.task.job,
                                         task=self.task,
                                         status=CrawlerDownloadLog.STATUS_FAIL,
                                         requests_size=0,
                                         response_size=0,
                                         failed_reason=traceback.format_exc(),
                                         downloads_hostname=str(socket.gethostname()),
                                         spend_time=spend_time)
                cdl.save()
                print "Trackback:", traceback.format_exc()
            pass
        else:
            start_time = time.time()
            try:
                resp = self.reqst.get(self.task.uri, timeout=25)
                end_time = time.time()
                spend_time = end_time - start_time

                requests_headers = unicode(resp.request.headers)
                response_headers = unicode(resp.headers)
                requests_body = 'None'

                response_body = unicode(resp.text)
                remote_ip = resp.headers.get('remote_ip', 'None')
                hostname = str(socket.gethostname())
                cdd = CrawlerDownloadData(job=self.task.job,
                                          downloader=self.crawler_download,
                                          crawlertask=self.task,
                                          requests_headers=requests_headers,
                                          response_headers=response_headers,
                                          requests_body=requests_body,
                                          response_body=response_body,
                                          hostname=hostname,
                                          remote_ip=remote_ip)

                if resp.headers.get('Content-Type', 'None') == 'application/pdf':
                    code = random.randrange(0, 100)
                    code = str(code)
                    path = '/tmp/' + code + '.pdf'
                    r = requests.get(self.task.uri, stream=True)
                    with open(path, 'wb') as fd:
                        for chunk in r.iter_content(8 * 1024):
                            fd.write(chunk)
                    cdd.files_down.put(resp.text, content_type='pdf')
                if resp.headers.get('Content-Type', 'None') in ['image/jpeg', 'image/png', 'image/gif']:
                    code = random.randrange(0, 100)
                    code = str(code)
                    path = '/tmp/' + code + '.jpg'
                    r = requests.get(self.task.uri, stream=True)
                    with open(path, 'wb') as fd:
                        for chunk in r.iter_content(8 * 1024):
                            fd.write(chunk)
                    cdd.files_down.put(resp.text, content_type='image/png')

                cdd.save()
                cdl = CrawlerDownloadLog(
                    job=self.task.job,
                    task=self.task,
                    status=CrawlerDownloadLog.STATUS_SUCCESS,
                    requests_size=sys.getsizeof(cdd.requests_headers) + sys.getsizeof(cdd.requests_body),
                    response_size=sys.getsizeof(cdd.response_headers) + sys.getsizeof(cdd.response_body),
                    failed_reason='Download task succeed!',
                    downloads_hostname=hostname,
                    spend_time=spend_time)
                cdl.save()
                self.task.status = CrawlerTask.STATUS_SUCCESS
                self.task.save()

            except Exception:
                self.task.status = CrawlerTask.STATUS_FAIL
                self.task.save()
                end_time = time.time()
                spend_time = end_time - start_time
                cdl = CrawlerDownloadLog(job=self.task.job,
                                         task=self.task,
                                         status=CrawlerDownloadLog.STATUS_FAIL,
                                         requests_size=0,
                                         response_size=0,
                                         failed_reason=traceback.format_exc(),
                                         downloads_hostname=str(socket.gethostname()),
                                         spend_time=spend_time)
                cdl.save()
                print "Trackback:", traceback.format_exc()


def force_exit(download_timeout, task):
    """
    通过定时器触发此函数，强制退出运行父进程，并将子进程杀死。
    """
    pgid = os.getpgid(0)
    task.status = CrawlerTask.STATUS_FAIL
    task.save()
    cdl = CrawlerDownloadLog(job=task.job,
                             task=task,
                             status=CrawlerDownloadLog.STATUS_FAIL,
                             requests_size=0,
                             response_size=0,
                             failed_reason='download runtime exceeds %ss. Exit!' % download_timeout,
                             downloads_hostname=str(socket.gethostname()),
                             spend_time=download_timeout)
    cdl.save()

    os.killpg(pgid, 9)    # 这行代码不能够删除
    os._exit(1)


def download_clawer_task(task):
    # 加载对应job的设置任务
    try:
        crawler_download = CrawlerDownload.objects(job=task.job).first()
        crawler_download_setting = CrawlerDownloadSetting.objects(job=task.job).first()
    except Exception:
        task.status = CrawlerTask.STATUS_FAIL
        task.save()
    down = Download(task, crawler_download, crawler_download_setting)

    timer = threading.Timer(crawler_download_setting.download_timeout, force_exit,
                            [crawler_download_setting.download_timeout, task])
    timer.start()
    down.download()
    timer.cancel()
