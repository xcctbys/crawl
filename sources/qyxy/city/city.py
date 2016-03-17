# -*- coding:UTF-8 -*-

import requests
import bs4
import re
import logging
import Queue
import multiprocessing
import sys
import urllib
from bs4 import BeautifulSoup
import unittest
import os
import pandas as pd
import csv

DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.WARN

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


class Spider(object):
    def __init__(self, keywords_path):
        self.keywords_path = keywords_path
        self.query_url = "http://report.bbdservice.com/show/searchCompany.do"
        self.output_path = "enterprise.csv"
        self.unknown_keyword_path = "unknown.csv"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
        }
        self.keywords = []
        self.output_keywords = []
        self.unknown_keywords = []
        self.result = []  # {'name':'', 'no':'', 'where':''}
        self.timeout = 90

    def transform(self):
        self._load_keywords()
        self._load_output()

        i = 0
        try:
            for keyword in self.keywords:
                if keyword in self.output_keywords:
                    continue
                self._parse(keyword)

                i += 1
                logging.error(u"index %d, keyword %s", i, keyword)
        finally:
            self._to_csv()

    def _to_csv(self):
        dataset = [(x["name"].encode("utf-8"), x['no'], x["where"].encode("utf-8"), x["fund"].encode("utf-8")) for x in
                   self.result]
        df = pd.DataFrame(data=dataset, columns=["name", "no", "where", "fund"])
        df.to_csv(self.output_path, mode="a", index=False, header=False)

        unknown_dataset = [(x.encode('utf-8')) for x in self.unknown_keywords]
        unknown_df = pd.DataFrame(data=unknown_dataset, columns=["name"])
        unknown_df.to_csv(self.unknown_keyword_path, mode="w", index=False, header=False)

    def _load_keywords(self):
        with open(self.keywords_path) as f:
            for line in f:
                line = unicode(line.strip(), "utf-8")
                line = line.replace("(", u"（").replace(")", u"）")
                self.keywords.append(line)

    def _load_output(self):
        if os.path.exists(self.output_path) is False:
            return

        with open(self.output_path) as f:
            reader = csv.reader(f)
            for line in reader:
                keyword = line[0].strip()
                if not keyword:
                    continue
                self.output_keywords.append(unicode(keyword, "utf-8"))

        self.output_keywords = list(set(self.output_keywords))

    def _parse(self, keyword):
        url = "%s?%s" % (self.query_url, urllib.urlencode({"term": keyword.encode("utf-8")}))
        r = requests.get(url, headers=self.headers, timeout=self.timeout)
        if r.status_code != 200:
            logging.warn("request %s, return code %d", url, r.status_code)
            return

        data = {"name": "", "no": "", "where": "", "fund": "", "legal_person": "", "birthday": "",}

        soup = BeautifulSoup(r.text, "html5lib")
        div = soup.find("div", {"class": "table-text"})
        children_div = div.find_all("div", {"class": "div-table"})
        for child in children_div:
            table = child.find("table", {"border": "0"})
            span = table.find("span", {"class": "spa-size"})
            title = span.get_text().strip()
            if title != keyword:
                continue
            data["name"] = title

            ul = child.find("ul")
            lis = ul.find_all("li")
            for li in lis:
                key = li.find("span", {"class": "span-color"}).get_text().strip()
                value = li.find("span", {"class": "left"}).get_text().strip()
                if key.find(u"注册号") > -1:
                    data["no"] = value
                elif key.find(u"法定代表人") > -1:
                    data["legal_preson"] = value
                elif key.find(u"注册资本") > -1:
                    data["fund"] = value
                elif key.find(u"成立日期") > -1:
                    data["birthday"] = value
                elif key.find(u"住所") > -1:
                    data["where"] = value
            break

        if data["name"] is "":
            logging.warn(u"not found name for %s", keyword)
            self.unknown_keywords.append(keyword)
            return

        logging.debug("data is %s", data)
        self.result.append(data)

    def _clear_fund(self, fund):
        data = ""
        for c in fund:
            if c.isnumeric():
                data += c
        return int(data)


class No2City(object):
    def __init__(self, in_path, out_path):
        self.in_path = in_path
        self.out_path = out_path
        self.city_path = "city_no.txt"
        self.cities = {}
        self.companyes = {}

    def transform(self):
        self._load_cities()
        company_noes = open(self.in_path, "r", )
        company_noes_reader = csv.reader(company_noes, delimiter=' ', quotechar='|')
        result = open(self.out_path, "w")
        result_writer = csv.writer(result, delimiter=' ',
                                   quotechar=',', quoting=csv.QUOTE_MINIMAL)
        result_writer.writerow(['公司名', '城市', '地址'])
        for row in company_noes_reader:
            rows = str(row[0]).split(',')
            if rows[1] is None:
                continue
            city_no = str(rows[1])[0:2]
            city_name = self._transform_no2name(city_no)
            if city_name is not None:
                result_writer.writerow([rows[0], city_name, rows[2]])
        result.close()

    def _transform_no2name(self, city_no):
        if city_no in self.cities:
            return self.cities[city_no]
        else:
            return None

    def _load_cities(self):
        with open(self.city_path, "r") as f:
            for line in f:
                [no, city] = line.split(",")
                self.cities[no] = city
                #
                # def _load_companyes_no(self):
                #     with open(self.in_path, "r") as f:
                #         for line in f:


class TestSpider(unittest.TestCase):
    # def test_transform(self):
    #     spider = Spider("test.txt")
    #     spider.transform()
    #     self.assertEqual(len(spider.result), 1)

    def test_transform(self):
        no2City = No2City('test.csv', 'test_out.csv')
        no2City.transform()
        test_out = open('test_out.csv')
        line = test_out.readline()
        self.assertGreater(len(line),10)


# if __name__ == "__main__":
#     no2City = No2City('test.csv', 'test_out.csv')
#     no2City.transform()

if __name__ == "__main__":
    if DEBUG:
        unittest.main()

    spider = Spider("company_bonds.txt")
    spider.transform()
