#coding=utf-8
#!/usr/bin/env python


import os
#sys.path.append('/Users/princetechs/cr-clawer/clawer/uri_filter/pybloom')
#from util_filter.utils.bloomfilter import BloomFilter
##from pybloomfilter import BloomFilter
from uri_filter.pybloom.pybloom import *

# from uri_filter.pybloom import pybloom


def singleton(cls, *args, **kw):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

def isset(v):
   try :
     type (eval(v))
   except :
     return  0
   else :
     return  1


#@singleton
class FilterAPI():
    urigenerator = BloomFilter(100000000, 0.0001, 1)
    def __init__(self, filter_typename='', uri_list=[]):
        self.filter_name = filter_typename
        self.bfilter_list = uri_list
        self.filter_list_unique = []
        #self.filename = '/home/xcc/Downloads/bloomfilter'
        self.filename = '/Users/princetechs/Downloads/bloomfilter'

    def filter(self):

        '''
        if self.filter_name == 'urigenerator':
            #rint ##########1


            if os.path.exists('/home/xcc/Downloads/bloomfilter/urigenerator.bloom') == True:
                print 222222222
                if isinstance(urigenerator, BloomFilter):
                    #if isset('user_name'):
                    #ass
                else:
                    f=open('/home/xcc/Downloads/bloomfilter/urigenerator.bloom','rwb')
                    urigenerator=BloomFilter.fromfile(f)
                    f.close()

            else:
                urigenerator = BloomFilter(100000000, 0.0001)
                os.makedirs('/home/xcc/Downloads/bloomfilter')
                f = open('/home/xcc/Downloads/bloomfilter/urigenerator.bloom', 'wb')
                urigenerator.tofile(f)
                f.close()
            for uri in self.bfilter_list:
                if urigenerator.add(uri) == True:
                    print 00  #
                    # pass
                else:
                    self.filter_list_unique.append(uri)
                    f = open('/home/xcc/Downloads/bloomfilter/urigenerator.bloom', 'wb')
                    urigenerator.tofile(f)
                    f.close()

            print self.filter_list_unique
            return self.filter_list_unique

        '''





        if self.filter_name == 'urigenerator':

            #if isinstance(urigenerator, BloomFilter):
                #pass
            bloomfilepath= self.filename + '/urigenerator.bloom'
            if os.path.exists(bloomfilepath) == True:
                #f = open('/home/xcc/Downloads/bloomfilter/urigenerator.bloom', 'rwb')
                f = open(bloomfilepath, 'rwb')
                urigenerator = BloomFilter.fromfile(f)
                f.close()
                print  4444444

            else:
                urigenerator = BloomFilter(100000000, 0.0001)
                os.makedirs(self.filename)

                #f = open('/home/xcc/Downloads/bloomfilter/urigenerator.bloom', 'wb')
                f = open(bloomfilepath, 'wb')
                urigenerator.tofile(f)
                f.close()
            for uri in self.bfilter_list:
                if urigenerator.add(uri) == True:
                    print 00#
                    #pass
                else:
                    self.filter_list_unique.append(uri)
                    #f = open('/home/xcc/Downloads/bloomfilter/urigenerator.bloom', 'wb')
                    f = open(bloomfilepath, 'wb')
                    urigenerator.tofile(f)
                    f.close()


            print self.filter_list_unique
            return self.filter_list_unique



        elif  self.filter_name == 'ip':
            print  ##########1
            if isinstance(ipfilter, BloomFilter):
                pass

            elif os.path.exists('home/xcc/Downloads/bloomfilter/ipfilter.bloom') == True:
                f = open('home/xcc/Downloads/bloomfilter/ipfilter.bloom', 'rwb')
                BloomFilter.fromfile(f)
                f.close()

            else:
                ipfilter = BloomFilter(1000000, 0.0001)
                f = open('home/xcc/Downloads/bloomfilter/ipfilter.bloom', 'wb')
                BloomFilter.tofile(f)
                f.close()
            for ip in bfilter_list:
                if ipfilter.add(ip) == True:
                    pass
                else:
                    filter_list_unique.append(ip)

        elif self.filter_name == 'uriparse':
            print  ##########1
            if isinstance(ipfilter, BloomFilter):
                pass

            elif os.path.exists('home/xcc/Downloads/bloomfilter/uriparse.bloom') == True:
                f = open('home/xcc/Downloads/bloomfilter/uriparse.bloom', 'rwb')
                urigenerator = BloomFilter.fromfile(f)
                f.close()

            else:
                uriparse = BloomFilter(1000000, 0.0001)
                f = open('home/xcc/Downloads/bloomfilter/uriparse.bloom', 'wb')
                BloomFilter.tofile(f)
                f.close()
            for uri in bfilter_list:
                if uriparse.add(uri) == True:
                    pass
                else:
                    filter_list_unique.append(uri)



        else:
            diy_filter_name = self.filter_name
            if isinstance(eval(diy_filter_name_),BloomFilter) == True:
                pass

            ###已经在内存里

            else:
                bloomfilename =diy_filter_name+'.bloom'
                    bloomfilepath = os.path.join('home/xcc/Downloads/bloomfilter/',bloomfilename)
                print bloomfilepath
                print ######dir###
                if os.path.exists(bloomfilepath) == True:
                    f = open(bloomfilepath, 'rwb')
                    fromfilestr = '=BloomFilter.fromfile(f)'
                    exec(diy_filter_name+makefilterstr)
                    f.close()

                else:
                    makefilterstr= '=BloomFilter(1000000, 0.0001)'
                    exec (diy_filter_name + makefilterstr)
                    f = open(bloomfilepath, 'wb')
                    BloomFilter.tofile(f)
                    f.close()


            for uri in bfilter_list:
                if uriparse.add(uri) == True:
                    pass
                else:
                    filter_list_unique.append(uri)



    '''
    def uri_filter_api(self):

        encode_urilist = json.dumps(self.uri_list)
        sendPost(encode_urilist)

        get enc o                            de_urilist
        json.loads(encode_urilist)
        uri_list_unique = bloomfilter(encode_uri_list)
        send_POST(uri_list_unique)
        do_POST()
        get encode_urilist_unique
        uri_list_unique = json.loads(encode_urilist_unique)



        uri_list_unique = BloomFilter(self.uri_list)
    '''



if __name__=='__main__':
    urilist = ['www.baidu.com','www.baidu.com','www.prittn.com']
    list = FilterAPI('urigenerator',urilist)
    list.filter()
