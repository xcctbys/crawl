# encoding=utf-8
"""baidu search

hits: http://wo.cs.com.cn/html/2012-11/24/content_461302.htm?div=-1
"""

import json
import sys
import logging
import unittest
import requests
import os
import urllib
from bs4 import BeautifulSoup

DEBUG = False  # 是否开启DEBUG
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


class Analysis(object):  # 页面分析类

    def __init__(self, path, args, url=None):  # 值初始化
        self.path = path
        self.url = url
        self.result = {}
        self.div = None
        self.text = None
        self.soup = None
        self.args = args # 传入查询的公司和关键字参数

    def parse(self):
        if os.path.exists(self.path) is False:  # 如果读取需要解析的文件失败则发起请求获取目标页面源码
            r = requests.get(self.url, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"})
            self.text = r.content
        else:
            with open(self.path, "r") as f:  # 读取下载器已经下载至本地的文件
                self.text = f.read()
        self.soup = BeautifulSoup(self.text, "html5lib")  # 使用html5lib解析页面
        html_content = self.soup.find("html")  # 获取html标签中内容
        html_data = urllib.urlencode({"html_data": html_content})
        self.result["html"] = html_data.split('html_data=')[1]
        self.result["keyword"] = self.args
        logging.debug("result is %s", json.dumps(self.result, indent=4))


class TestAnalysis(unittest.TestCase):  # 测试类（当DEBUG为True时运行）

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.path = "test.txt"  # 需解析的文件名
        self.args = "公司 诉讼"

    def test_parse(self):
        """http://wo.cs.com.cn/html/2012-11/24/content_461302.htm?div=-1
        """
        self.analysis = Analysis(self.path, self.args, "http://wo.cs.com.cn/html/2012-11/24/content_461302.htm?div=-1")  # 需解析的url
        self.analysis.parse()

        self.assertNotEqual(self.analysis.result, [])


if __name__ == "__main__":
    if DEBUG:
        unittest.main()

    in_data = sys.stdin.read()
    logging.debug("in data is: %s", in_data)

    in_json = json.loads(in_data)
    url = in_json.get("url")
    args = in_json.get("args")
    analysis = Analysis(in_json["path"], args, url)
    analysis.parse()

    print json.dumps(analysis.result)