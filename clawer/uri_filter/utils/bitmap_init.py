#_*_coding:utf_8_

from django.conf import settings
import math
from pybloomfilter import BloomFilter


class  CreatBitmap():
    def __init__(self,'uri',URI_NUM_SCALE, ACCEPT_ERROR_RATE ):
        self.uri_num = URI_NUM_SCALE    #预计要去重的uri数量级和
        self.err_rate = ACCEPT_ERROR_RATE  #能够接受的去重失误率
        self.filter_typename = filter_typename
    '''
    def make_bitmap(self):
        ln2 = math.log(2, math.e)
        mem_size = - self.uri_num * math.log(self.err_rate,math.e)/math.pow(ln2, 2)
        mem_size = math.ceil(mem_size)
        mem_size = mem_size + 8 + mem_size%8  # 保证bitmap位数是8的位数
        hashfx_num = 0.7*mem_size/self.uri_num
        hashfx_num = math.ceil(hashfx_num)
        print mem_size, hashfx_num
        return mem_size, hashfx_num
    '''
    if self.filter_typename = 'uri':
        uri = BloomFilter(self.uri_num,self.err_rate,'/tmp/urifilter.bloom')
    elif self.filter_typename = 'ip'
        ip = BloomFilter(self.uri_num,self.err_rate,'/tmp/ipfilter.bloom')

     #write  to  redis
     #write to mongodb
     #write to file





if __name__=='__main__':
    creatbitmap = CreatBitmap()
    creatbitmap.make_bitmap()