#coding:utf8
import os
import os.path
import sys
import commands
import requests
import time
import socket
from collector.models import CrawlerDownloadType, CrawlerTask, Job, CrawlerTaskGenerator, CrawlerDownloadSetting, CrawlerDownload, CrawlerDownloadData, CrawlerDownloadLog
from django.conf import settings


class Download(object):
	def __init__(self, task, crawler_download, crawler_download_setting):
		self.task = task
		self.crawler_download = crawler_download
		self.crawler_download_setting = crawler_download_setting
		self.crawler_download_data = CrawlerDownloadData()
		self.crawler_download_log = CrawlerDownloadLog()

		self.reqst = requests.Session()
		self.reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

	def exec_command(self, commandstr):
		print commandstr
		sys.path.append( '/Users/princetechs3/my_code' )
		# sys.path.append('/Users/princetechs3/my_code')
		c = compile(commandstr, "", 'exec')
		exec c

	def download(self):
		self.task.status == CrawlerTask.STATUS_PROCESS
		self.task.retry_times += 1
		self.task.save()

		print 'come in download---------------------------'
		if not self.crawler_download.types.is_support:
			cdl = CrawlerDownloadLog(	job = self.task.job,
											task = self.task,
											status = CrawlerDownloadLog.STATUS_FAIL,
											requests_size = 0,
											response_size = 0,
											failed_reason = "%s is %s" % (self.crawler_download.types.language, self.crawler_download.types.is_support)
											downloads_hostname = str(socket.gethostname()),
											spend_time = spend_time)
			cdl.save()

			# 改变这个任务的状态为下载失败
			self.task.status == CrawlerTask.STATUS_FAIL
			self.task.save()

			return
		print self.crawler_download.types.language, self.crawler_download.types.is_support
		if self.crawler_download.types.language == 'python' and self.crawler_download.types.is_support:
			start_time = time.time()
			print 'it is python-------------------------'
			try:
				# print 'save code from db;import crawler_download.code; run()'
				sys.path.append( settings.CODE_PATH )
				filename = os.path.join( settings.CODE_PATH, 'pythoncode%s.py' % str(self.crawler_download.id))
				# sys.path.append( '/Users/princetechs3/my_code' )
				# filename = os.path.join( '/Users/princetechs3/my_code', 'pythoncode%s.py' % str(self.crawler_download.id))
				if not os.path.exists(filename):
					with open(filename, 'w') as f:
						f.write(self.crawler_download.code)
				result = self.exec_command('import pythoncode%s; pythoncode%s.run("%s")' % (str(self.crawler_download.id), str(self.crawler_download.id), self.task.uri))
				
				end_time = time.time()

				spend_time = end_time - start_time
				requests_headers = result.get('requests_headers', None)
				response_headers = result.get('response_headers', None)
				requests_body = result.get('requests_body', None)
				response_body = result.get('response_body', None)
				remote_ip = result.get('remote_ip', None)
				hostname = str(sys.gethostname())

				# write_downloaddata_to_mongo
				cdd = CrawlerDownloadData(	job=self.task.job, 
											downloader=self.crawler_download,
											crawlertask=self.task,
											requests_headers=requests_headers,
											response_headers=response_headers,
											requests_body=requests_body,
											response_body=response_body,
											hostname=hostname,
											remote_ip=remote_ip)
				cdd.save()
				# write_downloaddata_success_log_to_mongo
				cdl = CrawlerDownloadLog(	job = self.task.job,
											task = self.task,
											status = CrawlerDownloadLog.STATUS_SUCCESS,
											requests_size = sys.getsizeof(cdd.requests_headers) + sys.getsizeof(cdd.requests_body),
											response_size = sys.getsizeof(cdd.response_headers) + sys.getsizeof(cdd.response_body),
											failed_reason = None,
											downloads_hostname = str(socket.gethostname()),
											spend_time = spend_time)
				cdl.save()

				# 改变这个任务的状态为下载成功
				self.task.status == CrawlerTask.STATUS_SUCCESS
				self.task.save()

			except Exception as e:
				self.task.status == CrawlerTask.STATUS_FAIL
				self.task.save()

				end_time = time.time()
				spend_time = end_time - start_time
				# write_downloaddata_fail_log_to_mongo
				cdl = CrawlerDownloadLog(	job = self.task.job,
											task = self.task,
											status = CrawlerDownloadLog.STATUS_FAIL,
											requests_size = 0,
											response_size = 0,
											failed_reason = str(e),
											downloads_hostname = str(socket.gethostname()),
											spend_time = spend_time)
				cdl.save()

				# 改变这个任务的状态为下载失败
				self.task.status == CrawlerTask.STATUS_FAIL
				self.task.save()

				print e,'sentry.excepterror()'
				return
			pass



		elif self.crawler_download.types.language == 'shell' and self.crawler_download.types.is_support:
			print 'it is shell ---------------------------'
			# print 'result = commands.getstatusoutput(sh code)'
			# filename = os.path.join( settings.CODE_PATH, 'shellcode%s.sh' % str(self.crawler_download.id))
			try:
				filename = os.path.join( '/Users/princetechs3/my_code', 'pythoncode%s.py' % str(self.crawler_download.id))
				if not os.path.exists(filename):
					with open(filename, 'w') as f:
						f.write(self.crawler_download.code)
				# os.system("chmod +x %s" % filename)
				result = commands.getstatusoutput('sh %s %s' % (filename,self.task.uri)) 
				print result
			except Exception as e:
				self.task.status == CrawlerTask.STATUS_FAIL
				self.task.save()
				print e,'sentry.excepterror()'
			pass

		elif self.crawler_download.types.language == 'curl' and self.crawler_download.types.is_support:
			print 'it is curl ----------------------------'
			try:
				result = commands.getstatusoutput('curl %s' % self.task.uri)
				print result
			except Exception as e:
				self.task.status == CrawlerTask.STATUS_FAIL
				self.task.save()
				print e,'sentry.excepterror()'
			pass
		else:
			try:
				resp = self.reqst.get(self.task.uri)
				print resp.headers
				print resp.request.headers
				print resp.encoding
				print resp.text
			except Exception as e:
				self.task.status == CrawlerTask.STATUS_FAIL
				self.task.save()
				print e,'sentry.excepterror()'



def download_clawer_task(task):
	#加载对应job的设置任务
	print '----------------------come in------------------------------'
	try:
		crawler_download = CrawlerDownload.objects(job=task.job)[0]
		# print crawler_download.code,crawler_download.types.language
		crawler_download_setting = CrawlerDownloadSetting.objects(job=task.job)[0]
		# print crawler_download_setting
	except Exception as e:
		self.task.status == CrawlerTask.STATUS_FAILED
		self.task.save()
		print e,'sentry.excepterror()'
	down = Download(task, crawler_download, crawler_download_setting)
	down.download()
	
