#coding=utf-8

import json
import hashlib
import datetime
from uri_filter.views import myHandler , send_POST
from util_filter.utils.bloomfilter import BloomFilter

class FilterAPIClient(filter_typeid,uri_list, access_token = 'princetechs'):
    def __init__(self):
        self.filter_typed = filter_typeid
        self.uri_list = uri_list
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



