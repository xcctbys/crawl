#coding:utf8
import os
import os.path
import sys
import random
import cPickle as pickle

class GetProxies(object):
	def __init__(self):
		self.dir = os.path.join(os.getcwd(), 'proxies')
		self.filename = self.get_last_time_filename(self.dir)
		print self.dir, self.filename
		pass
	def get_last_time_filename(self, path):
		return max(os.listdir(path))

	def load_pickle(self):
		f = file(os.path.join(self.dir,self.filename), 'rb')
		a_list = pickle.load(f)
		return a_list
	def get_proxies(self):
		a_list = self.load_pickle()
		return {'http':random.choice(a_list), 'https': random.choice(a_list)} 

if __name__ == '__main__':
	stand = GetProxies()
	print stand.get_proxies()