# encoding=utf-8

import logging
import json
import urllib
import unittest
# import traceback
import os
import cPickle as pickle

from bs4 import BeautifulSoup
import requests
import MySQLdb
import timefrom gevent import Greenlet
# import gevent.monkey
# gevent.monkey.patch_socket()
import gevent
requests.packages.urllib3.disable_warnings()


HOST = '10.0.1.3'
# HOST ='localhost'
USER = 'cacti'
PASSWD = 'cacti'
PORT = 3306
STEP =  1 # 每个step取ROWS个。
ROWS = 10
DEBUG = False  # 是否开启DEBUG
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(filename="/tmp/baidu.log" ,level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


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


class History(object):  # 实现程序的可持续性，每次运行时读取上次运行时保存的参数，跳到相应位置继续执行程序

    def __init__(self):
        self.total_page = 0
        self.current_page = 0# 初始化pickle中用作公司名称位置索引值
        self.path = "/tmp/baidu_company_search"  # pickle文件存放路径（提交至平台的代码记住带上tmp前斜杠）

    def load(self):  # pickle的载入
        if os.path.exists(self.path) is False:  # 读取pickle失败则返回
            return

        with open(self.path, "r") as f:  # 打开pickle文件并载入
            old = pickle.load(f)
            self.total_page = old.total_page
            self.current_page = old.current_page

    def save(self):  # pickle的保存
        with open(self.path, "w") as f:
            pickle.dump(self, f)


class Generator(object):
    HOST = "https://www.baidu.com/s?"

    def __init__(self):  # 初始化
        self.uris = set()
        self.args = set()
        self.history = History()
        self.history.load()
        self.enterprises= []
        self.step = STEP

    def search_url_with_batch(self):
        self.obtain_enterprises()
        for company in self.enterprises:
            starts = time.time()
            for each_keyword in KEYWORD:  # 遍历搜索关键词
                keyword = each_keyword
                start = time.time()
                self.page_url(company, keyword)  # 传参调用url构造函数
                end = time.time()
                logging.error("%s search time %f !"%(company.encode('utf8'), end - start) )
            ends = time.time()
            logging.error("The company %s run time %f."%(company.encode('utf8'), ends-starts))

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
                break
        self.history.save()

    def _load_total_page(self):
        r = self.paginate(0, ROWS)
        self.history.current_page = 0
        self.history.total_page = r['total_page']
        self.history.save()

    def page_url(self, current_company, current_keyword):
        for page_num in range(0, 10, 10):  # 遍历实现baidu搜索结果页翻页（第一页为0，第二页为10，第三页为20...）
            params = {"wd": current_company.encode("gbk") + " " + current_keyword.encode("gbk"),
                      "pn": page_num}  # 构造url参数
            url = "%s%s" % (self.HOST, urllib.urlencode(params))  # 构造url
            try:
                r = requests.get(url, verify=False, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"}, timeout=5)  # 浏览器代理请求url
            except Exception as e:
                logging.error(traceback.format_exc(10))
                continue
            soup = BeautifulSoup(r.text, "html5lib")  # 使用html5lib解析页面内容
            contents = soup.find("div", {"id": "content_left"})  # 找到页面中id为content_left的div
            divs = contents.find_all("div", {"class": "result"})  # 在目标div中找到所有class为result的div
            for div in divs:  # 遍历divs获取每一条div
                all_em = div.h3.find_all("em")  # 找到div.h3标签中所有的em标签
                if len(all_em) > 1:
                    ems = [em.get_text().strip() for em in all_em] # 将em建为一个列表
                    if current_company in ems and current_keyword in ems: # 判断关键词是否在em标签中，若判断为真则使用浏览器代理获取目标url中的headers信息
                        target_head = requests.head(div.h3.a["href"], headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"}).headers
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
        conn = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db='clawer', port=PORT,charset='utf8')
        sql = "select count(*) from enterprise_enterprise"
        cur = conn.cursor()
        count = cur.execute(sql)
        total_rows =cur.fetchone()[0]
        total_page = total_rows/rows
        if current_page  > total_page:
            current_page = 0
        sql = "select name from enterprise_enterprise limit %d, %d"%(current_page*rows, rows)
        count = cur.execute(sql)
        columns = [desc[0] for desc in cur.description]
        result = []
        for r in cur.fetchall():
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
        conn = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db='clawer', charset='utf8', port=PORT)
        sql='select count(*) from enterprise_enterprise'
        cur = conn.cursor()
        count = cur.execute(sql)
        total_rows = cur.fetchone()[0]
        total_page = total_rows/10

        result = generator.paginate(total_page+1, 10)
        print result
        self.assertEqual(result['current_page'], 0)


ents = []
class MyGreenlet(Greenlet):

    def __init__(self):
        Greenlet.__init__(self)
        self.g = Generator()

    def _run(self):
        # self.asynchronous()
        self.obtain()

    def obtain(self):
        self.g.obtain_enterprises()
        threads = []
        for company in self.g.enterprises:
            logging.debug("%s"%(company))
            for each_keyword in KEYWORD:  # 遍历搜索关键词
                keyword = each_keyword
                threads.append(gevent.spawn(self.g.page_url, company, keyword))
        gevent.joinall(threads)

if __name__ == "__main__":

    if DEBUG:  # 如果DEBUG为True则进入测试单元
        unittest.main()
    else:
        # start = time.time()
        # generator = Generator()
        # generator.search_url_with_batch()
        # end = time.time()
        # logging.error("Totoal run time = %f ."%(end - start))

        # for uri in generator.uris:
        #     str_uri = uri.encode("utf-8").split(" ")
        #     print json.dumps({"uri": str_uri[0], "args": str_uri[1]})

        startd = time.time()
        mg = MyGreenlet()
        mg.start()
        mg.join()
        endd = time.time()
        logging.error("Total running time is %f"%(endd - startd))

        for uri in mg.g.uris:  # 遍历输出uris
            str_uri = str(uri.encode("utf-8")).split(" ")
            print json.dumps({"uri": str_uri[0], "args": str_uri[1]})
