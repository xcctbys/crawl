# encoding=utf-8
""" example is http://rmfyb.chinacourt.org/paper/html/2015-011/23/node_4.htm
"""

import json
import logging
import unittest
import requests
import os
import cPickle as pickle

from bs4 import BeautifulSoup
import urlparse
try:
    import pwd
except:
    pass
import traceback
import datetime


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


class History(object):
    def __init__(self):
        self.current_date =  datetime.date.today()
        self.count = 1
        self.path = "/tmp/chinacourt_byday"
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
            if old.current_date == self.current_date:
                self.count = old.count
            else:
                self.current_date = datetime.date.today()
                self.count = 1
                self.save()

    def save(self):
        with open(self.path, "w") as f:
            pickle.dump(self, f)
            if hasattr(self, "uid"):
                os.chown(self.path, self.uid, self.gid)


class Generator(object):
    HOST = "http://rmfyb.chinacourt.org/"

    def __init__(self):
        self.uris = set()
        self.history = History()

        try:
            pwname = pwd.getpwnam("nginx")
            self.uid = pwname.pw_uid
            self.gid = pwname.pw_gid
        except:
            logging.error(traceback.format_exc(10))

        self.history.load()
        # print  self.history.count

    def obtain_urls(self):
        if self.history.count < 8:
            for page in range(self.history.count, self.history.count+1):
                # print self.history.current_date
                self.do_obtain(self.history.current_date, page)
            self.history.count += 1

            self.history.save()

    def page_url(self, dt, page):
        return urlparse.urljoin(self.HOST, "/paper/html/%s/node_%d.htm" % (dt.strftime("%Y-%m/%d"), page))

    def do_obtain(self, dt, page):
        url = self.page_url(dt, page)
        r = requests.get(url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"})
        if r.status_code != 200:
            return
        soup = BeautifulSoup(r.text, "html5lib")
        div = soup.find("div", {"style": "height:416px; overflow-y:scroll; width:100%;"})
        logging.debug("div is %s", div)
        links = div.find_all("a")
        for a in links:
            logging.debug("a is %s", a)
            a_div = a.find("div", {"style": "display:inline"})
            if a_div and "id" in a_div.attrs and a_div["id"].find("mp") > -1:
                node_url = urlparse.urljoin(url, a["href"])
                self.uris.add(node_url)
                logging.debug("uri is %s", node_url)


class GeneratorTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        pass

    def test_obtain_urls(self):
        self.generator = Generator()
        self.generator.obtain_urls()
        logging.debug("urls count is %d", len(self.generator.uris))


class HistoryTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        print "test end"

    def test_load(self):
        self.history = History()
        self.history.load()
        logging.debug("oldjs.count is %d", self.history.count)
        logging.debug("time is %s", self.history.current_date)


if __name__ == "__main__":
    if DEBUG:
        unittest.main()

    generator = Generator()
    generator.obtain_urls()
    for uri in generator.uris:
        print json.dumps({"uri": uri})