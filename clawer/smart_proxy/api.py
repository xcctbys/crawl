#coding:utf8
import os
import sys
import requests
sys.path.append(os.getcwd())

from smart_proxy.models import ProxyIp, IpUser
from smart_proxy.utils.get_ip_into_my import *
# from models import ProxyIp


class Proxy(object):
	def __init__(self):
		pass

	def get_proxy(self, num=5, province=None, is_valid=True):
		print province
		if province:
			ip_list = ProxyIp.objects.filter(province__icontains=province, is_valid=is_valid).order_by('?')
			#ip_list = ProxyIp.objects.filter(province__icontains=province, is_valid=is_valid).order_by('-update_datetime')
			ip_list = [item.ip_port for item in ip_list]
			# print ip_list
		else:
			# print ProxyIp.objects.filter(is_valid=True)
			ip_list = ProxyIp.objects.filter(is_valid=is_valid).order_by('?')
			#ip_list = ProxyIp.objects.filter(is_valid=is_valid).order_by('-update_datetime')
			ip_list = [item.ip_port for item in ip_list]

		if len(ip_list) < num:
			backup = ['OTHER']
			if province == 'BEIJING':
				backup = ['HEBEI','TIANJIN','SHANXI','HENAN','LIAONING','OTHER',]
			for province in backup:
				#temp_list = ProxyIp.objects.filter(province__icontains=province, is_valid=is_valid).order_by('-update_datetime')
				temp_list = ProxyIp.objects.filter(province__icontains= province , is_valid=is_valid).order_by('?')
				temp_list = [item.ip_port for item in temp_list]
				ip_list.extend(temp_list)
		if len(ip_list) <= num:
			return ip_list
		else:
			return ip_list[:num]

	def change_valid(self, ip_port=None, _id=None):
		if _id:
			try:
				one_ip = ProxyIp.objects.filter(id=_id)[0]
				print '修改前：',one_ip.is_valid
				one_ip.is_valid = not one_ip.is_valid
				one_ip.save()
				print '修改后：',one_ip.is_valid
			except Exception as e:
				print '_id或者ip_port传入字段不正确',e
				return
		if ip_port:
			try:
				one_ip = ProxyIp.objects.filter(ip_port=ip_port)[0]
				print '修改前：',one_ip.is_valid
				one_ip.is_valid = not one_ip.is_valid
				one_ip.save()
				print '修改后：',one_ip.is_valid
			except Exception as e:
				print '_id或者ip_port传入字段不正确',e
				return

	def test_really_is_valid(self, ip_port=None, test_uri=None):
		reqst = requests.Session()
		reqst.headers.update({'Accept': 'text/html, application/xhtml+xml, */*',
					'Accept-Encoding': 'gzip, deflate',
					'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
					'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})
		if not ip_port:
			print '您必须提供ip_port,如：ip_port=127.0.0.1:80'
		proxy = {'http':'http://'+ ip_port}
		if test_uri:
			try:
			# ‘http://lwons.com/wx’ 更加快点。
				resp = reqst.get(test_uri, timeout=15, proxies=proxy)
			except Exception as e:
				print e
				print '这个ip代理 %s 失效了，还不能够访问地址 %s' % (ip_port, test_uri)
				return
			if resp.status_code == 200:
				print '这个ip代理 %s 是有效的，可以访问地址 %s http响应码为 %d' % (ip_port, test_uri, resp.status_code)
			else:
				print '这个ip代理 %s 失效了，还不能够访问地址 %s http响应码为 %d' % (ip_port, test_uri, resp.status_code)
		else:
			try:
			# ‘http://lwons.com/wx’ 更加快点。
				resp = reqst.get('http://lwons.com/wx', timeout=15, proxies=proxy)
			except Exception as e:
				print e
				print '这个ip代理 %s 失效了，还不能够访问地址 %s' % (ip_port, 'http://lwons.com/wx')
				return
			if resp.status_code == 200:
				print '这个ip代理 %s 是有效的，可以访问地址 %s http响应码为 %d' % (ip_port,'http://lwons.com/wx', resp.status_code)
			else:
				print '这个ip代理 %s 失效了，还不能够访问地址 %s http响应码为 %d' % (ip_port, 'http://lwons.com/wx', resp.status_code)

class UseProxy(object):
	def __init__(self):
		pass
	def set_all_default(self):
		province_list = ('ANHUI',
						'BEIJING',
						'CHONGQING',
						'FUJIAN',
						'GANSU',
						'GUANGDONG',
						'GUANGXI',
						'GUIZHOU',
						'HAINAN',
						'HEBEI',
						'HEILONGJIANG',
						'HENAN',
						'HUBEI',
						'HUNAN',
						'JIANGSU',
						'JIANGXI',
						'JILIN',
						'LIAONING',
						'NEIMENGGU',
						'NINGXIA',
						'QINGHAI',
						'SHAANXI',
						'SHANDONG',
						'SHANGHAI',
						'SHANXI',
						'SICHUAN',
						'TIANJIN',
						'XINJIANG',
						'YUNNAN',
						'ZHEJIANG',
						'ZONGJU',
						'XIZANG')
		for province in province_list:
			one_set = IpUser(province=province)
			one_set.save()

	def change_use_proxy_one_province(self, province=None, is_use_proxy=None):
		one_province = IpUser.objects.filter(province__icontains=province)[0]
		if is_use_proxy is None:
			return
		else:
			one_province.is_use_proxy = is_use_proxy
			one_province.save()

	def change_use_proxy_all_province(self, is_use_proxy=None):
		for item in IpUser.objects.all():
			item.is_use_proxy = is_use_proxy
			item.save()

	def get_province_is_use_proxy(self, province=None):
		if province is None:
			return False
		else:
			one_province = IpUser.objects.filter(province__icontains=province)
			# print 'len(one_province):', len(one_province)
			# print one_province
			return one_province[0].is_use_proxy if one_province else None                                                                                                                                               


def getproxy_http_to_my():
    test =PaidProxy(num=100,sortby= 'time',protocol= 'http')
    ip_list = test.get_ipproxy()
    read = PutIntoMy()
    read.readLines(ip_list)


def getproxy_https_to_my():
    test =PaidProxy(num=100,sortby= 'time',protocol= 'https')
    ip_list = test.get_ipproxy()
    read = PutIntoMy()
    read.readLines(ip_list)

def proxyuser_default():
	userproxy=UseProxy
	userproxy.set_all_default()
	change_use_proxy_all_province(is_use_proxy=True)

		
if __name__ == '__main__':
	proxy = Proxy()
	print proxy.get_proxy()
	proxy.change_valid(_id=1)