from uri_filter.tests.test_uri_filter import *
from uri_filter.api.api_filter_timing import *
from uri_filter.api.api_uri_filter import *



def test_connect(connum):
    count = 0
    for i in range(1,connum):
        count = count +1
        uri_list = []
        code=str(i)
        uri_list.append(code)
        if count%1000 ==0:
            print count
        timing_filter_api('uri_generator',uri_list,20)

        bloom_filter_api('uri_generator',uri_list)


if __name__== '__main__':
    test_connect(230000)