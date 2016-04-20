#_*_coding:utf_8_
import BitVector
import os
import sys

class SimpleHash():

    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(len(value)):
            ret += self.seed*ret + ord(value[i])
        return (self.cap-1) & ret


def md5(str):
    import hashlib
    import types
    if type(str) is types.StringType:
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
    else:
        return ''


class BloomFilter():

    def __init__(self, BIT_SIZE=1<<25, HASH_NUM=14):
        self.BIT_SIZE = 1 << 25
        self.seeds = [5, 7, 11, 13, 31, 37, 47, 53, 61, 71, 79, 83 , 97, 101, 113, 131, 149 , 157 , 167]
        self.seeds = self.seeds[0:HASH_NUM]
        self.bitset = BitVector.BitVector(size=self.BIT_SIZE)
        self.hashFunc = []

        for i in range(len(self.seeds)):
            self.hashFunc.append(SimpleHash(self.BIT_SIZE, self.seeds[i]))

    def insert(self, value):
        for f in self.hashFunc:
            loc = f.hash(value)
            self.bitset[loc] = 1
    def isContaions(self, value):
        if value == None:
            return False
        ret = True
        for f in self.hashFunc:
            loc = f.hash(value)
            ret = ret & self.bitset[loc]
        return ret

def uri_filter(uri_list):
    uri_list_new = []
    del_list = []
    bloomfilter = BloomFilter()
    if uri_list == []:
        return 0
    for uri in uri_list:
        uricode = md5(uri)
        if bloomfilter.isContaions(uricode) == False:
            bloomfilter.insert(uricode)
        else:
            #print 'uri :%s has exist' % url
            del_list.append(uri)
    uri_list_new = uri_list - del_list



if __name__ == '__main__':
    uri_list = [www.baidu.com,www.baidu.com]
    uri_filter(uri_list)