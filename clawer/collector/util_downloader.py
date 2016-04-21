#coding:utf8
import os
import os.path
import sys

from collector.models import CrawlerDownloadType, CrawlerTask, Job, CrawlerTaskGenerator, CrawlerDownloadSetting, CrawlerDownload, CrawlerDownloadData, CrawlerDownloadLog

class Download(object):
	def __init__(self, task, crawler_download, crawler_download_setting):
		self.task = task
		self.crawler_download = crawler_download
		self.crawler_download_setting = crawler_download_setting
		self.crawler_download_data = CrawlerDownloadData()
		self.crawler_download_log = CrawlerDownloadLog()

	def exec_command(self, commandstr):
		# print commandstr
		# sys.path.append('/Users/princetechs3/my_code')
		c = compile(commandstr, "", 'exec')
		exec c

	def download(self):
		if self.crawler_download.types.language == 'python' and self.crawler_download.types.is_support:
			try:
				# print 'save code from db;import crawler_download.code; run()'
				filename = os.path.join( settings.CODE_PATH, 'pythoncode%s.py' % str(self.crawler_download._id))
				if not os.path.exists(filename):
					with open(filename, 'w') as f:
						f.write(crawler_download.code)
				result = self.exec_command('import pythonmycode%s.py; pythonmycode%s.run("%s")' % (str(self.crawler_download._id), str(self.crawler_download._id), task.uri))

			except:
				print 'sentry.excepterror()'
				# print self.crawler_download_log.save()
				return
			# print self.crawler_download_data.save()
			# print self.crawler_download_log.save()
			pass

		elif self.crawler_download.types.language == 'shell' and self.crawler_download.types.is_support:
			# print 'result = commands.getstatusoutput(sh code)'
			filename = os.path.join( settings.CODE_PATH, 'shellcode%s.sh' % str(self.crawler_download._id))
			if not os.path.exists(filename):
				with open(filename, 'w') as f:
					f.write(crawler_download.code)
			# os.system("chmod +x %s" % filename)
			result = commands.getstatusoutput('sh %s' % filename)
			pass

		elif self.crawler_download.types.language == 'curl' and self.crawler_download.types.is_support:
			result = commands.getstatusoutput('curl %s' % task.uri)
			pass
		else:
			pass
			# if task.args.get['method']=='POST':
			# 	r = self.reqst.post(self.task.url data=task.args)
			# 	result = r.content
			# else:
			# 	r = self.reqst.get(self.task.url)
			# 	result = r.content
		pass


def download_clawer_task(task):
	#加载对应job的设置任务
	print '----------------------come in------------------------------'
	crawler_download = CrawlerDownload.objects(job=task.job)[0]
	crawler_download_setting = CrawlerDownloadSetting.objects(job=task.job)[0]
	down = Download(task, crawler_download, crawler_download_setting)
	down.download()
	
