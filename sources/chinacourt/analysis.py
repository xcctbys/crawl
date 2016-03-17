#encoding=utf-8
"""china court

http://rmfyb.chinacourt.org/paper/html/2015-08/22/content_101571.htm?div=-1
"""

import json
import sys
import logging
import unittest
import requests
import os

from bs4 import BeautifulSoup


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR
    
logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


class Analysis(object):
    
    def __init__(self, path, url=None):
        self.path = path
        self.url = url
        self.soup = None
        self.result = {}
        self.text = None
        
    def parse(self):
        if os.path.exists(self.path) is False:
            r = requests.get(self.url)
            self.text = r.text
        else:
            with open(self.path, "r") as f:
                self.text = f.read()
                
        self.soup = BeautifulSoup(self.text, "html5lib")
        self.parse_add_datetime()
        self.parse_title()
        self.parse_layout()
        self.parse_meta()
        self.parse_content()

        logging.debug("result is %s", json.dumps(self.result, indent=4))

    def parse_title(self):
        td = self.soup.find("td", {"class": "font01", "align": "center"})
        title = td.get_text().strip()
        self.result["title"] = title.strip()
            
    def parse_content(self):
        div = self.soup.find("div", {"id": "ozoom"})
        self.result["content"] = div.get_text().strip()
    
    def parse_add_datetime(self):
        td = self.soup.find("td", {"width": "35%", "align": "center"})
        self.result["add_datetime"] = td.get_text().strip()

    def parse_layout(self):
        td = self.soup.find("td", {"class": "font_red"})
        self.result["layout"] = td.get_text().strip()

    def parse_meta(self):
        content = ""
        tds = self.soup.find_all("td", {"class":"font02", "align":"center", "style":"color: #827E7B;"})
        for td in tds:
            content += td.get_text()
            logging.debug("td is %s", td)
        self.result["meta"] = content
    

class TestAnalysis(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.path = "test.txt"
        
    def test_parse(self):
        """
            http://rmfyb.chinacourt.org/paper/html/2015-08/22/content_101571.htm?div=-1
        """
        self.analysis = Analysis(self.path, "http://rmfyb.chinacourt.org/paper/html/2015-08/22/content_101573.htm?div=-1")
        self.analysis.parse()
        
        self.assertNotEqual(self.analysis.result, {})
        self.assertIsNotNone(self.analysis.result["add_datetime"])    
        self.assertIsNotNone(self.analysis.result["title"])
        self.assertIsNotNone(self.analysis.result["content"])
        self.assertIsNotNone(self.analysis.result["meta"])


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
