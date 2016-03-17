#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-01-15 10:06:53
# @Author  : yijiaw
# @Link    : http://example.org
# @Version : $Id$

import time
import datetime


def trans_time(s):
    time_format = ['%Y年%m月%d日','%Y-%m-%d','%Y.%m.%d','%Y-%m-%d %l:%M:%S','%Y-%m-%d %H:%M:%S']
    for time_in in time_format:
        try:
            a = time.strptime(s, time_in)
            time1 = datetime.datetime(*a[:6])
            return time1 
        except:
            pass
    return None


def trans_float(s):
    res = []
    for c in list(s):
        if '0' <= c and c <= '9' or c == '.':
            res.append(c)
    if res == []:
        #return 0.0
        return None
    else:
        return float("".join(res))


if __name__ == '__main__':
    trans_time('2014年6月24日')
    trans_time('2015-05-18')
    print trans_float('15.12万元')
