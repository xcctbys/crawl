#_*_coding:utf_8_

from django.conf import settings
import math


class  CreatBitmap():
    def __init__(self,URI_NUM_SCALE, ACCEPT_ERROR_RATE):
        self.uri_num = URI_NUM_SCALE    #预计要去重的uri数量级和
        self.err_rate = ACCEPT_ERROR_RATE  #能够接受的去重失误率

    def make_bitmap(self):
        ln2 = math.log(2, math.e)
        mem_size = - self.uri_num * math.log(self.err_rate,math.e)/math.pow(ln2, 2)
        mem_size = math.ceil(mem_size)
        hashfx_num = 0.7*mem_size/self.uri_num
        hashfx_num = math.ceil(hashfx_num)
        print mem_size, hashfx_num
        return mem_size, hashfx_num







if __name__=='__main__':
    creatbitmap = CreatBitmap(1000000,0.0001)
    creatbitmap.make_bitmap()