#encoding=utf-8
"""qyxy analysis

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
        self.result = {}
        self.text = None
        
    def parse(self):
        if os.path.exists(self.path) is False:
            r = requests.get(self.url)
            self.text = r.text
        else:
            with open(self.path, "r") as f:
                self.text = f.read()
                
        self.result = json.loads(self.text)
        
        
class TestAnalysis(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.path = "595050.txt"
        
    def test_parse(self):
        """request it and parse
        """
        self.analysis = Analysis(self.path)
        self.analysis.parse()
    


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
    
    