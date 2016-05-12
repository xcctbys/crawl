# encoding=utf-8

import logging
import re
import json
import urllib
import unittest
import traceback
import os
import cPickle as pickle
try:
    import pwd
except:
    pass
from bs4 import BeautifulSoup
import requests
import MySQLdb

import datetime
import gevent
from gevent import Greenlet
# 如果要达到异步的效果，就要添加这个猴子补丁
import gevent.monkey
gevent.monkey.patch_socket()

requests.packages.urllib3.disable_warnings()


STEP =  1 # 每个step取10个。
ROWS = 10
DEBUG = False  # 是否开启DEBUG
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


# 所需爬取的相应关键词
KEYWORD = [
        u'违约',
        u'逾期',
        u'诉讼',
        u'纠纷',
        u'代偿',
        u'破产',
        u'清算'
]

# 装饰器
def exe_time(func):
    def fnc(*args, **kwargs):
        start = datetime.datetime.now()
        # print "call "+ func.__name__ + "()..."
        print func.__name__ +" start :"+ str(start) +" " +str(args)
        func(*args, **kwargs)
        end = datetime.datetime.now()
        print func.__name__ +" end :"+ str(end)
    return fnc


class History(object):  # 实现程序的可持续性，每次运行时读取上次运行时保存的参数，跳到相应位置继续执行程序

    def __init__(self):
        # self.company_num = 0  # 初始化pickle中用作公司名称位置索引值
        self.total_page = 0
        self.current_page = 0
        self.path = "/tmp/baidu_company_search"  # pickle文件存放路径（提交至平台的代码记住带上tmp前斜杠）

    def load(self):  # pickle的载入
        if os.path.exists(self.path) is False:  # 读取pickle失败则返回
            return

        with open(self.path, "r") as f:  # 打开pickle文件并载入
            old = pickle.load(f)
            # self.company_num = old.company_num  # 取出文件中存入的索引值
            self.total_page = old.total_page
            self.current_page = old.current_page

    def save(self):  # pickle的保存
        with open(self.path, "w") as f:
            pickle.dump(self, f)


class Generator(object):
    HOST = "http://www.baidu.com/s?"

    def __init__(self):  # 初始化
        self.uris = set()
        self.args = set()
        self.history = History()
        self.history.load()
        # self.source_url = "http://clawer.princetechs.com/enterprise/api/get/all/"
        self.enterprises= []
        self.step = STEP

    def search_url_with_batch(self):
        self.obtain_enterprises()
        for company in self.enterprises:
            logging.debug("%s"%(company))
            for each_keyword in KEYWORD:  # 遍历搜索关键词
                keyword = each_keyword
                self.page_url(company, keyword)  # 传参调用url构造函数

    def search_url_with_batch_asyn(self):
        self.obtain_enterprises()
        for company in self.enterprises:
            threads = []
            logging.debug("%s"%(company))
            for each_keyword in KEYWORD:  # 遍历搜索关键词
                keyword = each_keyword
                threads.append( gevent.spawn( self.page_url, company, keyword) )
            gevent.joinall(threads)

    def obtain_enterprises(self):
        if self.history.current_page <= 0 and self.history.total_page <= 0:
            self._load_total_page()

        for _ in range(self.step):
            r = self.paginate(self.history.current_page, ROWS)
            self.history.current_page += 1
            self.history.total_page = r['total_page']

            for item in r['rows']:
                self.enterprises.append(item['name'])

            if self.history.current_page > self.history.total_page:
                self.history.current_page = 0
                self.history.total_page = 0
                # self.history.save()
                break
        self.history.save()

    def _load_total_page(self):
        r = self.paginate(0, ROWS)
        self.history.current_page = 0
        self.history.total_page = r['total_page']
        self.history.save()

    @exe_time
    def page_url(self, current_company, current_keyword):
        for page_num in range(0, 10, 10):  # 遍历实现baidu搜索结果页翻页（第一页为0，第二页为10，第三页为20...）
            params = {"wd": current_company.encode("gbk") + " " + current_keyword.encode("gbk"),
                      "pn": page_num}  # 构造url参数
            url = "%s%s" % (self.HOST, urllib.urlencode(params))  # 构造url
            headers= {"user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:45.0) Gecko/20100101 Firefox/45.0"}
            # {"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"}
            r = requests.get(url,verify = False, headers = headers, timeout=60)  # 浏览器代理请求url
            soup = BeautifulSoup(r.text, "html5lib")  # 使用html5lib解析页面内容
            contents = soup.find("div", {"id": "content_left"})  # 找到页面中id为content_left的div
            divs = contents.find_all("div", {"class": "result"})  # 在目标div中找到所有class为result的div
            for div in divs:  # 遍历divs获取每一条div
                all_em = div.h3.find_all("em")  # 找到div.h3标签中所有的em标签
                if len(all_em) > 1:
                    ems = [em.get_text().strip() for em in all_em] # 将em建为一个列表
                    if current_company in ems and current_keyword in ems: # 判断关键词是否在em标签中，若判断为真则使用浏览器代理获取目标url中的headers信息
                        target_head = requests.head(div.h3.a["href"], headers= headers).headers
                        target_url = target_head["Location"]  # 获取目标链接真实url]
                        proto, rest = urllib.splittype(target_url)
                        host, rest = urllib.splithost(rest)
                        if "wenku.baidu.com" in host:  # 百度文库
                            continue
                        if "www.docin.com" in host:  # 豆丁
                            continue
                        if "www.doc88.com" in host:  # 道客巴巴
                            continue
                        if "vdisk.weibo.com" in host:  # 微博微盘
                            continue
                        if "www.pkulaw.cn/" in host:  # 北大法宝
                            continue
                        test = "%s%s%s%s%s" % (target_url, " ", current_company, "_", current_keyword)  # 将url、公司、关键字重新组合
                        self.uris.add(test)  # 将url加入uris中

    def paginate(self, current_page, rows=10):
        conn = MySQLdb.connect(host='localhost', user="root", passwd="", db='clawer', port=3306,charset='utf8')
        sql = "select count(*) from enterprise_enterprise"
        cur = conn.cursor()
        count = cur.execute(sql)
        total_rows =cur.fetchone()[0]
        total_page = total_rows/rows
        # print total_page
        if current_page  > total_page:
            current_page = 0
        sql = "select name from enterprise_enterprise limit %d, %d"%(current_page*rows, rows)
        count = cur.execute(sql)
        columns = [desc[0] for desc in cur.description]
        result = []
        for r in cur.fetchall():
            # for v in r:
                # print str(v.encode('utf-8'))
            result.append(dict(zip(columns, r)))

        conn.close()
        return  {'rows': result, 'total_page':total_page, 'current_page': current_page, 'total_rows': total_rows}


class GeneratorTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    # @unittest.skip("skipping read from file")
    def test_obtain_enterprises(self):
        self.generator = Generator()
        self.generator.obtain_enterprises()
        for name in self.generator.enterprises:
            logging.debug("enterprise name is %s."%(name))

        self.assertGreater(len(self.generator.enterprises), 0)

    @unittest.skip("skipping read from file")
    def test_obtain_urls(self):
        self.generator = Generator()
        self.generator.search_url_with_batch()

        for uri in self.generator.uris:
            logging.debug("urls is %s", uri)
        logging.debug("urls count is %d", len(self.generator.uris))

        self.assertGreater(len(self.generator.uris), 0)

    @unittest.skip("skipping read from file")
    def test_mysql(self):
        generator = Generator()
        result = generator.paginate(0, 10)
        print result


    @unittest.skip("skipping read from file")
    def test_generator_over_totalpage(self):
        generator = Generator()
        conn = MySQLdb.connect(host='localhost', user='cacti', passwd='cacti', db='clawer', charset='utf8', port=3306)
        sql='select count(*) from enterprise_enterprise'
        cur = conn.cursor()
        count = cur.execute(sql)
        total_rows = cur.fetchone()[0]
        total_page = total_rows/10

        result = generator.paginate(total_page+1, 10)
        print result
        self.assertEqual(result['current_page'], 0)



if __name__ == "__main__":

    if DEBUG:  # 如果DEBUG为True则进入测试单元
        unittest.main()
    else:
        generator = Generator()
        # generator.search_url_with_batch()
        generator.search_url_with_batch_asyn()

        for uri in generator.uris:
            str_uri = uri.encode("utf-8").split(" ")
            print json.dumps({"uri": str_uri[0], "args": str_uri[1]})
