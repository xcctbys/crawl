# encoding=utf-8

import json
import re
import os
import ConfigParser
import gzip
from LawPaperBase import LawPaperBase
from InstrumentSplit import InstrumentSplit
import mysql.connector
import sys
import raven


sentry_client = None
configuration_file = "sys/Configuration.cfg"

class InstrumentParsing():
    configuration_file = "sys/Configuration.cfg"
    record_file = "sys/downloaded_item.txt"
    last_file = []
    base = None
    partition = None
    connector = None
    json_path = None
    json_host = None
    pdf_path = None
    pdf_host = None
    db_host = None
    db_user = None
    db_pwd = None
    db_name = None
    urls = set()
    iszip = False
    pattern_date = u"[\s0-9一二三四五六七八九十零〇]+年[\s0-9一二三四五六七八九十零〇]+月[\s0-9一二三四五六七八九十零〇]+[日]*"

    def __init__(self, conf=None, iszip = False):
        self.iszip = iszip
        print "Start"

        # get the last json file parsed
        self.get_configuration(conf)
        print "Get Configuration"
        print "-" * 30 + "Configuration" + "-" * 30
        print "json_path", self.json_path
        print "json_host", self.json_host
        print "pdf_path", self.pdf_path
        print "pdf_host", self.pdf_host
        print "db", self.db_host
        print "-" * 73
        self.connector = self.get_connection()
        print "Connected Database"
        # self.check_db_config(conf)

        if os.path.exists(self.record_file):
            with open(self.record_file, "r+") as fi:
                for line in fi:
                    self.last_file.append(line)
        available_file_list = self.get_available_file()
        
        if len(available_file_list) == 0:
            exit(1)
        self.base = LawPaperBase()
        self.partition = InstrumentSplit()
        print "Caching URLs stored"
        self.__get__urls__()
        print "Start Inserting..."
        complete_files = self.insert_data(available_file_list)
        self.connector.close()
        with open(self.record_file, "a") as fo:
            for path in complete_files:
                fo.write(path)
                fo.write("\n")

    def get_configuration(self, conf):
        config = ConfigParser.SafeConfigParser({'bar': 'Life', 'baz': 'hard'})
        if conf is None:
            if not os.path.exists(self.configuration_file):
                self.default_config()
            config.read(self.configuration_file)
        else:
            config.read(conf)
            self.check_db_config(config)

        self.json_path = config.get("JSON", "path")
        if self.json_path is None or self.json_path == "":
            self.json_path = "/media/clawer_result/enterprise/json/"
        self.json_host = config.get("JSON", 'host')
        if self.json_host is None or self.json_host == "":
            self.json_host = "10.100.90.51"

        self.pdf_path = config.get("PDF", "path")
        if self.pdf_path is None or self.pdf_path == "":
            self.pdf_path = "/media/clawer_result/bankrupt/pdf/"
        self.pdf_host = config.get("PDF", "host")
        if self.pdf_host is None or self.pdf_host == "":
            self.pdf_host = "10.100.90.51"

        self.db_host = config.get("DB", "host")
        if self.db_host is None or self.db_host == "":
            self.db_host = "10.100.80.50"
        self.db_user = config.get("DB", "user")
        if self.db_user is None or self.db_user == "":
            self.db_user = "cacti"
        self.db_pwd = config.get("DB", "password")
        if self.db_pwd is None or self.db_pwd == "":
            self.db_pwd = "cacti"
        self.db_name = config.get("DB", "name")
        if self.db_name is None or self.db_name == "":
            self.db_name = "bankrupt"

    def default_config(self):

        config = ConfigParser.RawConfigParser()
        config.add_section("JSON")
        config.add_section("PDF")
        config.add_section("DB")

        config.set("JSON", 'path', "/media/clawer_result/enterprise/json/")
        config.set("JSON", 'host', "10.100.90.51")

        config.set("PDF", 'path', "/media/clawer_result/bankrupt/pdf/")
        config.set("PDF", 'host', "10.100.90.51")

        config.set("DB", 'host', "10.100.80.50")
        config.set("DB", 'user', "root")
        config.set("DB", 'password', "")

        with open(self.configuration_file, "w+") as configfile:
            config.write(configfile)

    def check_db_config(self, conf):
        cursor = self.connector.cursor()
        config = {
            "json_path": conf.get("JSON", "path"),
            "json_host": conf.get("JSON", 'host'),
            "pdf_path": conf.get("PDF", "path"),
            "pdf_host": conf.get("PDF", 'host')}
        query = ("""UPDATE config SET (json_path = %(json_path)s,
              json_host = %(json_host)s, pdf_path = %(pdf_path)s,
              pdf_host = %(pdf_host)s
              )""")
        cursor.execute(query, config)
        self.connector.commit()
        cursor.close()

    def __get__urls__(self):
        query = ("SELECT url FROM bankrupt_content")
        cursor = self.connector.cursor()
        cursor.execute(query)
        for url in cursor:
            self.urls.add(url[0].decode("utf-8"))
        cursor.close()

    def insert_execute(self, cursor, law_data):

        placeholders = ', '.join(['%s'] * len(law_data))
        columns = ', '.join(law_data.keys())
        sql = "INSERT INTO bankrupt_content ( %s ) VALUES ( %s )" % (columns, placeholders)
        cursor.execute(sql, law_data.values())
        self.connector.commit()

    def insert_data(self, file_list):
        completed_files = set()
        cursor = self.connector.cursor()
        open_fun = open
        for _file in file_list:
            if self.iszip:
                open_fun = gzip.open
                # with open(_file, 'rb') as fin:
            # else:
                # with
            # with gzip.open(_file, 'rb') as fin:
            with open_fun(_file, 'r') as fin:
                for line in fin:
                    line_item = json.loads(line, encoding="utf-8")
                    items = line_item["list"]
                    for item in items:
                        url = item["pdf_url"]
                        if url in self.urls:
                            continue
                        self.urls.add(url)
                        completed_files.add(_file)
                        court = item["courtcode"]
                        publish_date = item["publishdate"]
                        pdf_path = ""
                        if "abs_path" in item:
                            pdf_path = item["abs_path"]
                        contents = self.partition.split(item["content"])
                        for content in contents:
                            try:
                                law_data = self.event_termination(content, url, court, publish_date, pdf_path)
                                if len(law_data) > 0:
                                    for data in law_data.values():
                                        self.insert_execute(cursor, data)
                                    continue
                            except:
                                pass

                            try:
                                law_data = self.event_ruin(content, url, court, publish_date, pdf_path)
                                if len(law_data) > 0:
                                    for data in law_data.values():
                                        self.insert_execute(cursor, data)
                                    continue
                            except:
                                pass
                            

                            try:
                                law_data = self.event_compulsory(content, url, court, publish_date, pdf_path)
                                if len(law_data) > 0:
                                    for data in law_data.values():
                                        self.insert_execute(cursor, data)
                                    continue
                            except:
                                pass
                            

                            try:
                                law_data = self.event_creditors_meeting(content, url, court, publish_date, pdf_path)
                                if len(law_data) > 0:
                                    for data in law_data.values():
                                        self.insert_execute(cursor, data)
                                    continue
                            except:
                                pass
                            

                            try:
                                law_data = self.event_declaration(content, url, court, publish_date, pdf_path)
                                if len(law_data) > 0:
                                    for data in law_data.values():
                                        self.insert_execute(cursor, data)
                                    continue
                            except:
                                pass
                            

                            try:
                                law_data = self.event_reforming(content, url, court, publish_date, pdf_path)
                                if len(law_data) > 0:
                                    for data in law_data.values():
                                        self.insert_execute(cursor, data)
                                    continue
                            except:
                                pass
                            

                            try:
                                law_data = self.event_reforming_plan(content, url, court, publish_date, pdf_path)
                                if len(law_data) > 0:
                                    for data in law_data.values():
                                        self.insert_execute(cursor, data)
                                    # print "Successful, reforming_plan"
                                    continue
                            except:
                                pass
                            

                            try:
                                law_data = self.event_application(content, url, court, publish_date, pdf_path)
                                if len(law_data) > 0:
                                    for data in law_data.values():
                                        self.insert_execute(cursor, data)
                                    continue
                            except:
                                pass
                            

                            try:
                                law_data = self.event_other(content, url, court, publish_date, pdf_path)
                                if len(law_data) > 0:
                                    for data in law_data.values():
                                        self.insert_execute(cursor, data)
                                    continue
                                
                            except:
                                pass
                            print "lost!"


        cursor.close()
        return completed_files

    def get_connection(self):
        cnx = mysql.connector.connect(user=self.db_user, password=self.db_pwd,
                                      host=self.db_host,
                                      database=self.db_name)
        return cnx

    def get_available_file(self):
        year_files = os.listdir(self.json_path)

        available_files = []
        for year in year_files:
            file_path = self.json_path
            path_year = file_path + str(year) + "/"
            month_files = os.listdir(path_year)
            for month in month_files:
                path_month = path_year + str(month) + "/"
                day_files = os.listdir(path_month)
                for day in day_files:
                    path_day = path_month + str(day) + "/"
                    json_file = os.listdir(path_day)
                    for jf in json_file:
                        file_path = path_day + jf
                        if file_path not in self.last_file:
                            if file_path.find("_insert") != -1:
                                available_files.append(file_path)
        return available_files

    def event_termination(self, content, url, court, publish_date, pdf_path):
        # 终止破产程序
        results = {}
        names, replace_name = self.base.get_enterprise_name(content)
        is_contains = False
        if replace_name is None:
            replace_name = []
        pattern = None
        for check_name in [names] + replace_name:
            pattern_check = u"裁定终结" + check_name + u"破产"
            pattern_check_1 = u"终结" + check_name + u"破产"
            pattern_check_2 = u"终结[\u0000-\uffff]{0,15}破产"
            pattern_check_3 = u"破产程序终结"
            if content.__contains__(pattern_check):
                is_contains = True
                pattern = pattern_check
            elif content.__contains__(pattern_check_1):
                is_contains = True
                pattern = pattern_check_1
            elif content.__contains__(pattern_check_3):
                is_contains = True
                pattern = pattern_check_3
            elif len(re.findall(pattern_check_2, content)) > 0:
                is_contains = True
                pattern = re.findall(pattern_check_2, content)[0]

        if is_contains:

            publish_date = self.base.convert_date(publish_date, True)
            dates = re.findall(self.pattern_date, content)
            publish_position = content.index(pattern)
            date = self.base.get_decision_date(dates, content, publish_position)
            if date is None:
                date = publish_date
            else:
                date = self.base.convert_date(date)
            index = 0
            for name in names.split(u"、"):
                if name == u"":
                    continue

                results[index] = {
                    "obligor": unicode(name),
                    "event_date": unicode(date),
                    "pdf_path": unicode(pdf_path),
                    "category": u"终结破产",
                    "court": unicode(court),
                    "publish_date": publish_date,
                    "url": unicode(url)
                }
                index += 1
        return results

    def event_ruin(self, content, url, court, publish_date, pdf_path):
        results = {}
        if content.__contains__(u"终结"):
            return results
        names, replace_name = self.base.get_enterprise_name(content)
        is_contains = False
        if replace_name is None:
            replace_name = []
        for check_name in [names] + replace_name:
            pattern_check = u"宣告" + check_name + u"破产"
            pattern_check_1 = u"宣告[\u0000-\uffff]{0,10}破产"
            if content.__contains__(pattern_check):
                is_contains = True
            elif len(re.findall(pattern_check_1, content)) > 0:
                is_contains = True

        pattern = None
        for check_name in [names] + replace_name:
            pattern_check = u"宣告" + check_name + u"破产"
            pattern_check_1 = u"宣告[\u0000-\uffff]{0,10}破产"
            if content.__contains__(pattern_check):
                is_contains = True
                pattern = pattern_check
            elif len(re.findall(pattern_check_1, content)) > 0:
                is_contains = True
                pattern = re.findall(pattern_check_1, content)[0]

        if is_contains:
            publish_date = self.base.convert_date(publish_date, True)
            dates = re.findall(self.pattern_date, content)
            publish_position = content.index(pattern)
            date = self.base.get_decision_date(dates, content, publish_position)
            if date is None:
                date = publish_date
            else:
                date = self.base.convert_date(date)
            index = 0
            for name in names.split(u"、"):
                if name == u"":
                    continue

                results[index] = {
                    "obligor": unicode(name),
                    "event_date": unicode(date),
                    "pdf_path": unicode(pdf_path),
                    "category": u"破产清算",
                    "court": unicode(court),
                    "publish_date": publish_date,
                    "url": unicode(url)
                }
                index += 1

        return results

    def event_compulsory(self, content, url, court, publish_date, pdf_path):

        results = {}
        if content.__contains__(u"强制清算") and not content.__contains__(u"传票"):
            names, _ = self.base.get_enterprise_name(content)
            dates = re.findall(self.pattern_date, content)
            publish_date = self.base.convert_date(publish_date, True)
            if content.find(u"终结") != -1:
                date = self.base.convert_date(self.base.get_decision_date(dates, content, content.index(u"终结")))
            elif content.find(u"受理") != -1:
                date = self.base.convert_date(self.base.get_decision_date(dates, content, content.index(u"受理")))
            else:
                date = publish_date

            index = 0
            for name in names.split(u"、"):
                if name == u"":
                    continue
                results[index] = {
                    "obligor": unicode(name),
                    "event_date": unicode(date),
                    "pdf_path": unicode(pdf_path),
                    "category": u"强制清算",
                    "court": unicode(court),
                    "publish_date": publish_date,
                    "url": unicode(url)
                }
                index += 1
        return results

    def event_creditors_meeting(self, content, url, court, publish_date, pdf_path):
        # results = pd.DataFrame(columns=(u"被申请人", u"事件文本", u"事件类型", u"受理法院", u"发布时间" ,u"URL"))
        results = {}
        if content.__contains__(u"债权人会议") and not content.__contains__(u"终结") and not (
                    content.__contains__(u"批准") and content.__contains__(u"重整计划")):
            names, _ = self.base.get_enterprise_name(content)
            date = self.base.convert_date(publish_date, True)
            index = 0
            for name in names.split(u"、"):
                if name == u"":
                    continue
                results[index] = {
                    "obligor": unicode(name),
                    "event_date": unicode(date),
                    "pdf_path": unicode(pdf_path),
                    "category": u"债权人会议",
                    "court": unicode(court),
                    "publish_date": unicode(date),
                    "url": unicode(url)
                }
                index += 1
        return results

    def event_declaration(self, content, url, court, publish_date, pdf_path):
        ## 申报债权
        results = {}
        names, _ = self.base.get_enterprise_name(content)
        if content.__contains__(u"申报债权") or content.__contains__(u"债权申报"):
            date = self.base.convert_date(publish_date, True)
            index = 0
            for name in names.split(u"、"):
                results[index] = {
                    "obligor": unicode(name),
                    "event_date": unicode(date),
                    "pdf_path": unicode(pdf_path),
                    "category": u"申报债权",
                    "court": unicode(court),
                    "publish_date": unicode(date),
                    "url": unicode(url)
                }
                index += 1
        return results

    def event_reforming(self, content, url, court, publish_date, pdf_path):
        ## 重整程序
        results = {}

        if content.__contains__(u"重整") and not content.__contains__(u"终结") and not (
                    content.__contains__(u"批准") and content.__contains__(u"重整计划")):
            names, _ = self.base.get_enterprise_name(content)
            date = self.base.convert_date(publish_date, True)
            index = 0
            for name in names.split(u"、"):
                if name == u"":
                    continue
                results[index] = {
                    "obligor": unicode(name),
                    "event_date": unicode(date),
                    "pdf_path": unicode(pdf_path),
                    "category": u"重整程序",
                    "court": unicode(court),
                    "publish_date": unicode(date),
                    "url": unicode(url)
                }
                index += 1
        return results

    def event_reforming_plan(self, content, url, court, publish_date, pdf_path):
        ## 重整计划
        results = {}
        if content.__contains__(u"批准") and content.__contains__(u"重整计划"):
            names, _ = self.base.get_enterprise_name(content)

            date = self.base.convert_date(publish_date, True)
            index = 0
            for name in names.split(u"、"):
                if name == u"":
                    continue
                results[index] = {
                    "obligor": unicode(name),
                    "event_date": unicode(date),
                    "pdf_path": unicode(pdf_path),
                    "category": u"重整程序",
                    "court": unicode(court),
                    "publish_date": unicode(date),
                    "url": unicode(url)
                }
                index += 1
        return results

    def event_application(self, content, url, court, publish_date, pdf_path):
        ## 申请破产
        results = {}
        if content.__contains__(u"申请") and content.__contains__(u"破产"):
            names, _ = self.base.get_enterprise_name(content)
            date = self.base.convert_date(publish_date, True)
            index = 0
            for name in names.split(u"、"):
                if name == u"":
                    continue
                results[index] = {
                    "obligor": unicode(name),
                    "event_date": unicode(date),
                    "pdf_path": unicode(pdf_path),
                    "category": u"重整程序",
                    "court": unicode(court),
                    "publish_date": unicode(date),
                    "url": unicode(url)
                }
                index += 1
        return results

    def event_other(self, content, url, court, publish_date, pdf_path):
        ## 其它
        results = {}
        names, _ = self.base.get_enterprise_name(content)
        date = self.base.convert_date(publish_date, True)
        index = 0
        for name in names.split(u"、"):
            results[index] = {
                "obligor": unicode(name),
                "event_date": unicode(date),
                "pdf_path": unicode(pdf_path),
                "category": u"重整程序",
                "court": unicode(court),
                "publish_date": unicode(date),
                "url": unicode(url)
            }
            index += 1
        return results


def send_sentry_report():
    if sentry_client:
        sentry_client.captureException()

if __name__ == '__main__':
    args = sys.argv
    configfile = None
    sentry_dns = None
    if len(args) > 1:
        configfile = args[1]

    config = ConfigParser.SafeConfigParser({'bar': 'Life', 'baz': 'hard'})

    if configfile is None:
        if os.path.exists(configuration_file):
            config.read(configuration_file)
    else:
        if os.path.exists(configfile):
            config.read(configfile)

    sentry_dns = config.get("SETTING", "sentry_dns")
    if sentry_dns is None or sentry_dns== "":
        sentry_dns = 'http://917b2f66b96f46b785f8a1e635712e45:556a6614fe28410dbf074552bd566750@sentry.princetechs.com//2'
    sentry_client = raven.Client(dsn=sentry_dns)

    try:
        InstrumentParsing(conf = configfile)
    except:
        send_sentry_report()
    
    print "End"
