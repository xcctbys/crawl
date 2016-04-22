#coding=utf-8

import json
import hashlib
import datetime
from uri_filter.views import myHandler , send_POST
import os
from util_filter.utils.bloomfilter import BloomFilter
from pybloomfilter import BloomFilter

class FilterAPIClient(filter_typename,uri_list, access_token = 'princetechs'):
    def __init__(self):
        self.filter_name = filter_typename
        self.bfilter_list = uri_list
        self.filter_list_new = []


    if self.filter_name == 'urigenerator':
       if os.path.exists('/usr/bloomfilter/urigenerator.bloom') == True:
           urigenerator = BloomFilter.open('/usr/bloomfilter/urigenerator.bloom')
       else:
           urigenerator = BloomFilter(1000000,0.0001,'/usr/bloomfilter/urigenerator.bloom')
       for uri in uri_list:
           if urigenerator.add(uri) == True:
              pass
           elif urigenerator.add(uri) == False:
              uri_list_new.append(uri)

    elif self.filter_name == 'ip':
        if os.path.exists('/usr/bloomfilter/ip.bloom') == True:
            ipfilter = BloomFilter.open('/usr/bloomfilter/ipfilter.bloom')
        else:
            ipfilter = BloomFilter(1000000,0.0001,'/usr/bloomfilter/ipfilter.bloom')
        for ip in uri_list:
           if ip.add(ip) == True:
              pass
           elif ip.add(ip) == False:
              ip_list_new.append(ip)

    elif self.filter_name == 'uriparse':
        if os.path.exists('/usr/bloomfilter/uriparse.bloom' == True:
            uriparse = BloomFilter.open('/usr/bloomfilter/uriparse.bloom')
        else:
            uriparse = BloomFilter(1000000,0.0001,'/usr/bloomfilter/uriparse.bloom')
        for uri in uri_list:
           if uriparse.add(uri) == True:
              pass
           elif uriparse.add(uri) == False:
              ip_list_new.append(ip)

    return uri_list_new



    def uri_filter_api(self):
        '''
        encode_urilist = json.dumps(self.uri_list)
        sendPost(encode_urilist)

        get encode_urilist
        json.loads(encode_urilist)
        uri_list_unique = bloomfilter(encode_uri_list)
        send_POST(uri_list_unique)
        do_POST()
        get encode_urilist_unique
        uri_list_unique = json.loads(encode_urilist_unique)


        '''
        uri_list_unique = BloomFilter(self.uri_list)


        return uri_list_unique



if __name__=='__main__':
    urifilter = FilterAPIClient('urigenerator',['www.baidu.com','www.baidu.com','www.pritn.com'])
    print urifilter
