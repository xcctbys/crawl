# -*- coding: utf-8 -*-

import gzip
import requests
import time
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from clawer_parse.parse import Parse
from clawer_parse.models import Basic
from multiprocessing import Pool
from datetime import date, timedelta, datetime
from cStringIO import StringIO
from configs import configs
from clawer_parse import multiprocessing_logging
from clawer_parse.globalval import GlobalVal


class Command(BaseCommand):


    def handle(self, *args, **options):
        begin = time.time()
        base_url = settings.JSONS_URL
        suffix = ".json.gz"
        is_multiprocess = settings.MULTIPROCESS
        update_by = settings.UPDATE_BY

        globalval = GlobalVal()
        globalval.set_count_zero()

        config_logging()
        
        if is_first_run():
            if update_by == "hour":
                first_update_by_hour(is_multiprocess, base_url, suffix)
                #update_by_hour(is_multiprocess, base_url, suffix)
            else:
                first_update_by_day(is_multiprocess, base_url, suffix)

        elif update_by == "hour":
            update_by_hour(is_multiprocess, base_url, suffix)

        else:
            update_by_day(is_multiprocess, base_url, suffix)

        count_parsed = globalval.get_count_parsed()
        count_all = globalval.get_count_all()
        count_update = globalval.get_count_update()

        end = time.time()
        secs = round(end - begin)
        cost_time = "✅  Done! Cost " + str(secs) + "s ✅ " 
        parse_information = " Done_num:" + str(count_parsed) +" All_num:" + str(count_all) + " Update_num:" + str(count_update)
        settings.logger.info(cost_time + parse_information)


def first_update_by_hour(is_multiprocess, base_url, suffix):
   # base_url = settings.JSONS_URL
   # suffix = ".json.gz"

    if not is_multiprocess:
        diff = date.today() - date(2016,2,28)
        for dec_day in reversed(range(1, diff.days)):
            d = date.today() - timedelta(dec_day)
            d_str = d.strftime("%Y/%m/%d")

            for hour in range(0, 25):
                hour_str = "%02d" % hour
                url = base_url + "/" + d_str + "/" + hour_str + suffix
                print url 
                json_data = requests_json(url)
                parse(json_data)

    else:
        p = Pool(processes=4)
        diff = date.today - date(2016, 2, 23)
        for dec_day in reversed(range(1, diff.days)):
            d = date.today() - timedelta(dec_day)
            d_str = d.strftime("%Y/%m/%d")

            for hour in range(0, 25):
                hour_str = "%02d" % hour
                url = base_url + "/" + d_str + "/" + hour_str + suffix
                json_data = requests_json(url)
                p.apply_async(parse, args=(json_data))

        p.close()
        p.join()


def first_update_by_day(is_multiprocess, base_url, suffix):
   # base_url = settings.JSONS_URL
    provinces = Configs.PROVINCES
   # suffix = ".json.gz"

    if not is_multiprocess:
        diff = date.today - date(2016, 2, 23)
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
        diff = today - date(2016, 2, 23)
        for dec_day in reversed(range(1, diff.days)):
            d = today - timedelta(dec_day)
            d_str = d.strftime("%Y/%m/%d")

            for prinvince in provinces:
                url = base_url + "/" + prinvince + "/" + d_str + suffix
                json_data = requests_json(url)
                p.apply_async(parse, args=(json_data, prinvince))

        p.close()
        p.join()


def update_by_hour(is_multiprocess, base_url, suffix):
    # base_url = settings.JSONS_URL
    # suffix = ".json.gz"
    today = datetime.now()
    today_str = today.strftime("%Y/%m/%d")
    yesterday = today - timedelta(1)
    yesterday_str = yesterday.strftime("%Y/%m/%d")
    end_hour = today.hour

    if end_hour < 4:
        for hour in range(19, 24):
            hour_str = "%02d" % hour
            url = base_url + "/" + yesterday_str + "/" + hour_str + suffix
            json_data = requests_json(url)
            parse(json_data)
    else:
        begin_hour = end_hour - 4
        for hour in range(begin_hour, end_hour):
            hour_str = "%02d" % hour
            url = base_url + "/" + today_str + "/" + hour_str + suffix
            print url
            json_data = requests_json(url)
            parse(json_data)


def update_by_day(is_multiprocess, base_url, suffix):
   # base_url = settings.JSONS_URL
    provinces = Configs.PROVINCES
   # suffix = ".json.gz"
    yesterday = date.today() - timedelta(1)
    yesterday_str = yesterday.strftime("%Y/%m/%d")

    if not is_multiprocess:
        for prinvince in provinces:
            url = base_url + "/" + prinvince + "/" + yesterday_str + suffix
            json_data = requests_json(url)
            parse(json_data, prinvince)
    else:
        p = Pool(processes=4)
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


def is_first_run():
    is_first_run = Basic.objects.all()
    return not is_first_run


def parse(companies, prinvince="None"):
    #config_logging()
    worker = Parse(companies, prinvince)
    worker.parse_companies()


def config_logging():
    settings.logger = logging.getLogger('structured')
    settings.logger.setLevel(settings.LOG_LEVEL)
    fh = logging.FileHandler(settings.LOG_FILE)
    fh.setLevel(settings.LOG_LEVEL)
    ch = logging.StreamHandler()
    ch.setLevel(settings.LOG_LEVEL)

    formatter = logging.Formatter(settings.LOG_FORMAT)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    settings.logger.addHandler(fh)
    settings.logger.addHandler(ch)
    multiprocessing_logging.install_mp_handler(settings.logger)
