#encoding=utf-8
import os
import sys
import random

import requests
import time

import json

#
# def Download():
# 	def __init__(self):
# 		self.uri = "http://rmfygg.court.gov.cn/psca/lgnot/bulletin/download/4633100.pdf"
# 		self.reqst = requests.Session()
# 		self.reqst.headers.update(
# 			{'Accept': 'text/html, application/xhtml+xml, */*',
# 			'Accept-Encoding': 'gzip, deflate',
# 			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
# 			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})
#
# 	def down(self):
# 		try:
# 			resp = self.reqst.get(self.uri, timeout=25)
# 			# print resp.headers
# 			# print resp.request.headers
# 			# print resp.text
# 			end_time = time.time()
# 			spend_time = end_time - start_time
#
#
# 			requests_headers = unicode(resp.request.headers)
# 			response_headers = unicode(resp.headers)
# 			requests_body = 'None'
#
# 			response_body = unicode(resp.text)
# 			print response_body
# 			remote_ip = resp.headers.get('remote_ip', 'None')
# 			hostname = str(socket.gethostname())
# 			# write_downloaddata_to_mongo
# 			# cdd = CrawlerDownloadData(  job=self.task.job,
#              #                            downloader=self.crawler_download,
#              #                            crawlertask=self.task,
# 			# 							requests_headers=requests_headers,
#              #                            response_headers=response_headers,
#              #                            requests_body=requests_body,
#              #                            response_body=response_body,
#              #                            hostname=hostname,
#              #                            remote_ip=remote_ip)
#
# 			if resp.headers.get('Content-Type', 'None') == 'application/pdf':
# 				cdd.files_down.put(resp.text, content_type = 'pdf')
# 			if resp.headers.get('Content-Type', 'None') in ['image/jpeg','image/png','image/gif']:
# 				cdd.files_down.put(resp.text, content_type = 'image/png')
# 			# cdd.save()
# 			# # write_downloaddata_success_log_to_mongo
# 			# cdl = CrawlerDownloadLog(job = self.task.job,
#              #                        task = self.task,
# 			# 						status = CrawlerDownloadLog.STATUS_SUCCESS,
# 			# 						requests_size = sys.getsizeof(cdd.requests_headers) + sys.getsizeof(cdd.requests_body),
# 			# 						response_size = sys.getsizeof(cdd.response_headers) + sys.getsizeof(cdd.response_body),
# 			# 						failed_reason = 'None',
# 			# 						downloads_hostname = hostname,
# 			# 						spend_time = spend_time)
# 			# cdl.save()
#
# 			# # 改变这个任务的状态为下载成功
# 			# self.task.status = CrawlerTask.STATUS_SUCCESS
# 			# self.task.save()
#
# 		except Exception as e:
# 			# 改变这个任务的状态为下载失败
#             # self.task.status = CrawlerTask.STATUS_FAIL
#             # self.task.save()
#             #
#             # end_time = time.time()
#             # spend_time = end_time - start_time
#             # # write_downloaddata_fail_log_to_mongo
#             # cdl = CrawlerDownloadLog(	job = self.task.job,
# 			# 						task = self.task,
# 			# 						status = CrawlerDownloadLog.STATUS_FAIL,
# 			# 						requests_size = 0,
# 			# 						response_size = 0,
# 			# 						failed_reason = str(e),
# 			# 						downloads_hostname = str(socket.gethostname()),
# 			# 						spend_time = spend_time)
#             # cdl.save()
# 		    print e,'sentry.excepterror()'
#

def downpdf():
	#uri = "http://rmfygg.court.gov.cn/psca/lgnot/bulletin/download/4633100.pdf"
	#uri = "http://rmfygg.court.gov.cn/psca/userfiles/images//org1/2016/03/30/1459305954821.jpg"
	uri="http://rmfygg.court.gov.cn/psca/userfiles/images//org1/2015/12/15/1450166808575.jpg"



	reqst = requests.Session()
	reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

	try:
		resp = reqst.get(uri, timeout=25)
		print uri
		# print resp.headers
		# print resp.request.headers
		# print resp.text
		#end_time = time.time()
		#spend_time = end_time - start_time
		requests_headers = unicode(resp.request.headers)
		response_headers = unicode(resp.headers)
		requests_body = 'None'
		#
		#path = '/tmp/112.pdf'
		code = random.randrange(0, 10000)
		code =str(code)
		print code
		path ='/tmp/'+code+'.jpg'
		r = requests.get(uri, stream=True)
		with open(path , 'wb') as fd:
			for chunk in r.iter_content(8 * 1024):
				fd.write(chunk)
		print 5555




		# response_body = unicode(resp.text)
		# print response_body
		# file = open('/tmp/111.pdf','wb')
		# print 'ioioioio'
		# file.write(response_body)
		# print 44444
		# file.close()
		# print 33333


		#remote_ip = resp.headers.get('remote_ip', 'None')
		#hostname = str(socket.gethostname())
		# write_downloaddata_to_mongo
		# cdd = CrawlerDownloadData(  job=self.task.job,
        #                            downloader=self.crawler_download,
        #                            crawlertask=self.task,
		# 							requests_headers=requests_headers,
        #                            response_headers=response_headers,
        #                            requests_body=requests_body,
        #                            response_body=response_body,
        #                            hostname=hostname,
        #                            remote_ip=remote_ip)

		if resp.headers.get('Content-Type', 'None') == 'application/pdf':
			print 222
			#cdd.files_down.put(resp.text, content_type = 'pdf')
		if resp.headers.get('Content-Type', 'None') in ['image/jpeg','image/png','image/gif','image/jpg']:
			print 'imag'
			#cdd.files_down.put(resp.text, content_type = 'image/png')
			# cdd.save()
			# # write_downloaddata_success_log_to_mongo
			# cdl = CrawlerDownloadLog(job = self.task.job,
            #                        task = self.task,
			# 						status = CrawlerDownloadLog.STATUS_SUCCESS,
			# 						requests_size = sys.getsizeof(cdd.requests_headers) + sys.getsizeof(cdd.requests_body),
			# 						response_size = sys.getsizeof(cdd.response_headers) + sys.getsizeof(cdd.response_body),
			# 						failed_reason = 'None',
			# 						downloads_hostname = hostname,
			# 						spend_time = spend_time)
			# cdl.save()

			# # 改变这个任务的状态为下载成功
			# self.task.status = CrawlerTask.STATUS_SUCCESS
			# self.task.save()

	except Exception as e:
			# 改变这个任务的状态为下载失败
            # self.task.status = CrawlerTask.STATUS_FAIL
            # self.task.save()
            #
            # end_time = time.time()
            # spend_time = end_time - start_time
            # # write_downloaddata_fail_log_to_mongo
            # cdl = CrawlerDownloadLog(	job = self.task.job,
			# 						task = self.task,
			# 						status = CrawlerDownloadLog.STATUS_FAIL,
			# 						requests_size = 0,
			# 						response_size = 0,
			# 						failed_reason = str(e),
			# 						downloads_hostname = str(socket.gethostname()),
			# 						spend_time = spend_time)
            # cdl.save()
		    print 'error'


if __name__=="__main__":
    # dow=Download()
    # dow.down
	downpdf()