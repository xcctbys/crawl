# encoding=utf-8
""" example is http://www.live.chinacourt.org/fygg/index/kindid/6.shtml
"""

import logging
import json
import unittest
import traceback
import os
import cPickle as pickle
try:
    import pwd
except:
    pass
import time
import requests
import re


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


class History(object):

    def __init__(self):
        self.page = 1
        self.path = "/tmp/china_court_bankruptcy"
        try:
            pwname = pwd.getpwnam("nginx")
            self.uid = pwname.pw_uid
            self.gid = pwname.pw_gid
        except:
            logging.error(traceback.format_exc(10))

    def load(self):
        if os.path.exists(self.path) is False:
            return

        with open(self.path, "r") as f:
            old = pickle.load(f)
            self.page = old.page

    def save(self):
        with open(self.path, "w") as f:
            pickle.dump(self, f)
            if hasattr(self, "uid"):
                os.chown(self.path, self.uid, self.gid)


class Generator(object):
    STEP = 21

    def __init__(self):
        self.uris = set()
        self.history = History()
        self.history.load()
        self.timeStamp = int(time.time())

    def obtain_urls(self):
        for i in range(1, self.STEP):
            url = "http://rmfygg.court.gov.cn/psca/lgnot/solr/searchBulletinInterface.do?callback=jQuery" \
                  "152043560746777802706_1448866417716&start=" + str(self.history.page) + "&limit=16&wd=rmfybulletin" \
                  "&list%5B0%5D=bltntype%3A64&_=" + str(self.timeStamp)

            r = requests.get(url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"})
            if r.status_code != 200:
                return
            js_content = re.sub(r"^.*?\(", "", r.text)
            js_content = js_content[:-1]
            js_dict = json.loads(js_content)
            js_list = js_dict.get("objs")
            if len(js_list) < 1:
                return

            self.uris.add(url)
            self.history.page += 1
        self.history.save()


class GeneratorTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_obtain_urls(self):
        self.generator = Generator()
        self.generator.obtain_urls()

        for uri in self.generator.uris:
            logging.debug("urls is %s", uri)

        logging.debug("urls count is %d", len(self.generator.uris))

        self.assertGreater(len(self.generator.uris), 0)


if __name__ == "__main__":

    if DEBUG:
        unittest.main()

    generator = Generator()
    generator.obtain_urls()

    for uri in generator.uris:
        print json.dumps({"uri": uri})
