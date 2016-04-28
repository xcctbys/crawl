#coding=utf-8

#from api.api_uri_filter import *
#from uri_fileter.api import FilterAPI


def filterapiclient(filter_typename='', uri_list=[]):
    urilist = ['www.baidu.com','www.baidu.com','www.prittn.com']
    filter_typename = 'urigenerator'
    list = FilterAPI(filter_typename,urilist)
    list.filter()
    return 0

def read_urilist_from_txt(file_path):

    result=[]
    fd = file( file_path, "rw" )

    for line in fd.readlines():
        for i in (map(str,line.strip('\r\n ').split(','))):
            result.append(i)
    print(result)
    return result
    '''
    for item in result:
            print item
    '''


if __name__== '__main__':
    file_path = "/tmp/filter_test.txt"
    t = read_urilist_from_txt(file_path)