# -*- coding: utf-8 -*-

import gzip
import requests
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from enterprise.structured import Parse
from enterprise.structured import Configs
from enterprise.models import Basic
from datetime import date, datetime, timedelta
from cStringIO import StringIO
from multiprocessing import Pool


class Command(BaseCommand):
    def handle(self, *args, **options):
        is_multiprocess = settings.MULTIPROCESS
        update_by = settings.UPDATE_BY

        begin = time.time()

        if is_first_update():
            if update_by == "hour":
                first_update_by_hour(is_multiprocess)
            else:
                first_update_by_day(is_multiprocess)

        elif update_by == "hour":
            update_by_hour(is_multiprocess)

        else:
            update_by_day(is_multiprocess)

        end = time.time()
        print("Done! Cost %s s" % (end - begin))


def first_update_by_hour(is_multiprocess):
    base_url = settings.JSONS_URL
    suffix = ".json.gz"

    if not is_multiprocess:
        diff = date.today - date(2016, 1, 1)
        for dec_day in reversed(range(1, diff.days)):
            d = date.today() - timedelta(dec_day)
            d_str = d.strftime("%Y/%m/%d")

            for hour in range(1, 25):
                hour_str = "%02d" % hour
                url = base_url + "/" + d_str + "/" + hour_str + "/" + suffix
                json_data = requests_json(url)
                parse(json_data)

    else:
        p = Pool(processes=4)
        diff = date.today - date(2016, 1, 1)
        for dec_day in reversed(range(1, diff.days)):
            d = date.today() - timedelta(dec_day)
            d_str = d.strftime("%Y/%m/%d")

            for hour in range(1, 25):
                hour_str = "%02d" % hour
                url = base_url + "/" + d_str + "/" + hour_str + "/" + suffix
                json_data = requests_json(url)
                p.apply_async(parse, args=(json_data))

        p.close()
        p.join()


def first_update_by_day(is_multiprocess):
    base_url = settings.JSONS_URL
    provinces = Configs.PROVINCES
    suffix = ".json.gz"

    if not is_multiprocess:
        diff = date.today - date(2016, 1, 1)
        for dec_day in reversed(range(1, diff.days)):
            d = date.today() - timedelta(dec_day)
            d_str = d.strftime("%Y/%m/%d")

            for prinvince in provinces:
                url = base_url + "/" + prinvince + "/" + d_str + suffix
                json_data = requests_json(url)
                parse(json_data, prinvince)
    else:
        p = Pool(processes=4)
        today = date.today()
        diff = today - date(2016, 1, 1)
        for dec_day in reversed(range(1, diff.days)):
            d = today - timedelta(dec_day)
            d_str = d.strftime("%Y/%m/%d")

            for prinvince in provinces:
                url = base_url + "/" + prinvince + "/" + d_str + suffix
                print url
                json_data = requests_json(url)
                p.apply_async(parse, args=(json_data, prinvince))

        p.close()
        p.join()


def update_by_hour(is_multiprocess):
    base_url = settings.JSONS_URL
    suffix = ".json.gz"
    today = datetime.now()
    today_str = today.strftime("%Y/%m/%d")
    hour = today.hour - 1
    hour_str = "%02d" % hour
    url = base_url + "/" + today_str + "/" + hour_str + "/" + suffix
    json_data = requests_json(url)
    parse(json_data)


def update_by_day(is_multiprocess):
    base_url = settings.JSONS_URL
    provinces = Configs.PROVINCES
    suffix = ".json.gz"
    yesterday = date.today() - timedelta(1)
    yesterday_str = yesterday.strftime("%Y/%m/%d")

    if not is_multiprocess:
        for prinvince in provinces:
            url = base_url + "/" + prinvince + "/" + yesterday_str + suffix
            json_data = requests_json(url)
            parse(json_data, prinvince)
    else:
        p = Pool()
        for prinvince in provinces:
            url = base_url + "/" + prinvince + "/" + yesterday_str + suffix
            json_data = requests_json(url)
            p.apply_async(parse, args=(json_data, prinvince))

        p.close()
        p.join()


def requests_json(url):
    json_data = ""

    response = requests.get(url)
    if int(response.status_code) == 200:
        gz = gzip.GzipFile(fileobj=StringIO(response.content))
        json_data = gz.readlines()

    return json_data


def is_first_update():
    is_first_update = Basic.objects.all()
    return not is_first_update


def parse(companies, prinvince="None"):
    worker = Parse(companies, prinvince)
    worker.parse_companies()
