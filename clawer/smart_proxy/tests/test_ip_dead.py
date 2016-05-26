#coding=utf-8
#!/usr/bin/env python
import requests
import time

#proxy = {'http':'http://'}


def test_ip_dead(nums,uri_list):
    reqst = requests.Session()
    print 1111
    for i in range(1,nums):
        print i
        for uri in uri_list:
            print uri
            rest = reqst.get(uri,timeout=60)
            print rest.content
            print rest
            exp = 120
            print exp
            time.sleep(exp)
            print i


if __name__ == "__main__":
    #proxy = {'http':'http://61.135.217.14:80'}
    #print proxy
    nums= 10000
    #211.94.187.236   工商主页
    uri22= 'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/showInfo.html'
    uri23='http://gsxt.gdgs.gov.cn'
    uri = 'http://www.baidu.com'
    uri1 = 'http://qyxy.baic.gov.cn/'
    uri2 = 'http://qyxy.baic.gov.cn/gjjbj'
    uri3 = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!getBjQyList.dhtml'
    uri4 = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!openInfo.dhtml?entId=a1a1a1a027fc643a0128149ecf4a34d9&entNo=110112604140634&credit_ticket=D2F4F0C478C0A069F630916462BB0226&str=2&timeStamp=1463104859826'
    uri5 = 'http://qyxy.baic.gov.cn/beijing'
    uri11 ='http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!openEntInfo.dhtml?entId=308F6BA7DA4D46BF81B02745E0E6B133&credit_ticket=82686F809C80EA54D1DCE356A4FDC88D&entNo=110101600395241&timeStamp=1464141392430'
    uri12='http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!openInfo.dhtml?entId=308F6BA7DA4D46BF81B02745E0E6B133&entNo=110101600395241&credit_ticket=82686F809C80EA54D1DCE356A4FDC88D&str=2&timeStamp=1464141479578'
    uri13='http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!openInfo.dhtml?entId=308F6BA7DA4D46BF81B02745E0E6B133&entNo=110101600395241&credit_ticket=82686F809C80EA54D1DCE356A4FDC88D&str=3&timeStamp=1464141513196'
    uri_list=[uri1,uri3,uri5,uri4,uri12]
    test_ip_dead(nums,uri_list)