#coding=utf-8

import json
import hashlib
import datetime
from uri_filter.views import myHandler , send_POST




class FilterAPIClient(filter_typeid,uri_list, access_token = 'princetechs'):
    def __init__(self):
        self.filter_typed = filter_typeid
        self.uri_list = uri_list
    def uri_filter_api(self):
        uri_list
        encode_urilist = json.dumps(uri_list)
        send_POST(encode_urilist)
        do_Post()
        get encode_urilist
        json.loads(encode_urilist)

        uri_list_unique = bloomfilter(encode_uri_list)
        send_POST(uri_list_unique)
        do_POST()
        get encode_urilist_unique
        uri_list_unique = json.loads(encode_urilist_unique)
        return uri_list_unique



