#coding=utf-8
#!/usr/bin/env python
import requests

proxy = {'http':'http://'}


def test_ip_dead(nums,uri,proxy):
    reqst = requests.Session()
    for i in range(1,nums):
        print i
        rest = reqst.get(uri,proxies=proxy,timeout=30)
        print rest.content
        print rest


if __name__ == "__main__":
    proxy = {'http':'http://115.159.180.195:80'}
    print proxy
    nums= 2
    #211.94.187.236   工商主页
    uri = 'http://www.baidu.com'
    uri1 = 'http://qyxy.baic.gov.cn/'
    uri2 = 'http://qyxy.baic.gov.cn/gjjbj'
    uri3 = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!getBjQyList.dhtml'
    uri4 = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!openInfo.dhtml?entId=a1a1a1a027fc643a0128149ecf4a34d9&entNo=110112604140634&credit_ticket=D2F4F0C478C0A069F630916462BB0226&str=2&timeStamp=1463104859826'
    uri5 = 'http://qyxy.baic.gov.cn/beijing'
    test_ip_dead(nums,uri,proxy)