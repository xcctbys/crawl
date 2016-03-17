# encoding=utf-8
"""china court

hits: http://rmfygg.court.gov.cn/psca/lgnot/solr/searchBulletinInterface.do?callback=jQuery152043560746777802706_1448866417716&start=1&limit=16&wd=rmfybulletin&list%5B0%5D=bltntype%3A&_=1448866625744
"""

import json
import sys
import logging
import unittest
import requests
import os
import re


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


class Analysis(object):

    def __init__(self, path, url=None):
        self.pdf_url_host = "http://rmfygg.court.gov.cn/psca/lgnot/bulletin/download/"
        self.path = path
        self.url = url
        self.result = {}
        self.list = []
        self.js_article = None
        self.text = None
        self.js_list = None

    def parse(self):
        if os.path.exists(self.path) is False:
            r = requests.get(self.url)
            self.text = r.text
        else:
            with open(self.path, "r") as f:
                self.text = f.read()

        js_content = re.sub(r"^.*?\(", "", self.text)
        js_content = js_content[:-1]
        js_dict = json.loads(js_content)

        js_list = js_dict.get("objs")

        for article in js_list:
            new_a = {}
            self.js_article = article
            self.parse_court(new_a)
            self.parse_party(new_a)
            self.parse_publishdate(new_a)
            self.parse_pdf_url(new_a)
            self.content(new_a)
            self.list.append(new_a)
        self.result["list"] = self.list
        logging.debug("result is %s", json.dumps(self.result, indent=4))

    def parse_court(self, new_a):
        title = self.js_article.get("courtcode")
        new_a["courtcode"] = title

    def parse_party(self, new_a):
        content = self.js_article.get("party2")
        new_a["party"] = content.strip()

    def parse_publishdate(self, new_a):
        time = self.js_article.get("publishdate")
        new_a["publishdate"] = time.strip()

    def parse_pdf_url(self, new_a):
        pdf_id = self.js_article.get("id")
        pdf_url = "%s%s%s" % (self.pdf_url_host, pdf_id, ".pdf")
        new_a["pdf_url"] = pdf_url

    def content(self, new_a):
        time = self.js_article.get("content")
        new_a["content"] = time.strip()


class TestAnalysis(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.path = "test.txt"

    def test_parse(self):
        """http://rmfygg.court.gov.cn/psca/lgnot/solr/searchBulletinInterface.do?callback=jQuery152043560746777802706_1448866417716&start=17630&limit=16&wd=rmfybulletin&list%5B0%5D=bltntype%3A&_=1448866625744
        """
        self.analysis = Analysis(self.path, "http://rmfygg.court.gov.cn/psca/lgnot/solr/searchBulletinInterface.do?"
                                            "callback=jQuery152043560746777802706_1448866417716&start=1&limit=16&wd"
                                            "=rmfybulletin&list%5B0%5D=bltntype%3A&_=1448866625744")
        self.analysis.parse()

        self.assertNotEqual(self.analysis.result, [])


if __name__ == "__main__":
    if DEBUG:
        unittest.main()

    in_data = sys.stdin.read()
    logging.debug("in data is: %s", in_data)

    in_json = json.loads(in_data)
    url = in_json.get("url")
    analysis = Analysis(in_json["path"], url)
    analysis.parse()

    print json.dumps(analysis.result)
