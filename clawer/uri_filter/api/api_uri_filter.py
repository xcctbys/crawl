#coding=utf-8


import os

import sys

from uri_filter.pybloom.pybloom import *

def bloom_filter_api(filter_type, uri_list =[], uri_size=1000000, err_rate=0.01,):

    if filter_type == 'uri_generator':
        redisdb = 1
        tablename = 'uri_generator'
    elif filter_type == 'uri_parse':
        redisdb = 2
        tablename = 'uri_parse'

    elif filter_type == 'ip':
        redisdb = 3
        tablename = 'ip'
    else :
        redisdb = 4
        tablename = filter_type

    blmfilter = BloomFilter(uri_size, err_rate, redisdb)


    filter_list_unique = []


    if uri_list == []:
        print '[]'
        return filter_list_unique
    else:
        for uri in uri_list:
            if blmfilter.add(uri) == True:
                pass
            else:
                filter_list_unique.append(uri)
        return filter_list_unique



if __name__ == "__main__":
    # import doctest
    # doctest.testmod()
    uri_list = ['wwww.baidu.com','wwww.baidu.com','wwww.princetechs.com','wwww.hao.com','wwww.clawr.com']
    bl =  bloom_filter_api('uri_generator',uri_list)
    print type(bl)
    print bl
