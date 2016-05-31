#encoding=utf-8
from mongoengine import *
import datetime
import os
import logging
import traceback
import json
import redis
import codecs

from django.contrib.auth.models import User as DjangoUser
from django.conf import settings
from django.core.cache import cache

from html5helper import redis_cluster


class Job(Document):
    (STATUS_ON, STATUS_OFF) = range(1, 3)
    STATUS_CHOICES = ((STATUS_ON, u"启用"), (STATUS_OFF, u"下线"), )
    (PRIOR_0, PRIOR_1, PRIOR_2, PRIOR_3, PRIOR_4, PRIOR_5, PRIOR_6) = range(-1, 6)
    PRIOR_CHOICES = ((PRIOR_0, u"-1"),
                     (PRIOR_1, u"0"),
                     (PRIOR_2, u"1"),
                     (PRIOR_3, u"2"),
                     (PRIOR_4, u"3"),
                     (PRIOR_5, u"4"),
                     (PRIOR_6, u"5"), )

    creator = StringField(max_length=128, null=True)
    name = StringField(max_length=128)
    info = StringField(max_length=1024)
    customer = StringField(max_length=128, null=True)
    status = IntField(default=STATUS_ON, choices=STATUS_CHOICES)
    priority = IntField(default=PRIOR_6, choices=PRIOR_CHOICES)
    add_datetime = DateTimeField(default=datetime.datetime.now)
    meta = {"db_alias": "source"}


class CrawlerTaskGenerator(Document):
    """ collection of generator scripts """
    (STATUS_ALPHA, STATUS_BETA, STATUS_PRODUCT, STATUS_ON, STATUS_OFF, STATUS_TEST_FAIL) = range(1, 7)
    STATUS_CHOICES = ((STATUS_ALPHA, u"alpha"),
                      (STATUS_BETA, u"beta"),
                      (STATUS_PRODUCT, u"production"),
                      (STATUS_ON, u"启用"),
                      (STATUS_OFF, u"下线"),
                      (STATUS_TEST_FAIL, u"测试失败"), )
    (TYPE_PYTHON, TYPE_SHELL) = range(1, 3)
    TYPE_CHOICES = ((TYPE_PYTHON, u'PYTHON'), (TYPE_SHELL, u'SHELL'), )
    job = ReferenceField(Job)
    code = StringField()    #python or shell code
    code_type = IntField(default=TYPE_PYTHON, choices=TYPE_CHOICES)
    schemes = ListField(StringField(max_length=16))
    cron = StringField(max_length=128)
    status = IntField(default=STATUS_ALPHA, choices=STATUS_CHOICES)
    add_datetime = DateTimeField(default=datetime.datetime.now)
    meta = {"db_alias": "source"}

    def status_name(self):
        for item in self.STATUS_CHOICES:
            if item[0] == self.status:
                return item[1]
        return ""

    def get_code_type(self):
        for item in self.STATUS_CHOICES:
            if item[0] == self.code_type:
                return item[1]
        return ""

    def code_dir(self):
        path = os.path.join(settings.MEDIA_ROOT, "codes")
        if os.path.exists(path) is False:
            os.makedirs(path, 0775)
        return path

    def alpha_path(self):
        return os.path.join(self.code_dir(), "%s_alpha" % str(self.job.id))

    def product_path(self):
        return os.path.join(self.code_dir(), "%s_product" % str(self.job.id))

    def write_code(self, path):
        with codecs.open(path, "w", "utf-8") as f:
            f.write(self.code)


class CrawlerTask(Document):
    (STATUS_LIVE, STATUS_DISPATCH, STATUS_PROCESS, STATUS_FAIL, STATUS_SUCCESS, STATUS_ANALYSIS_FAIL,
     STATUS_ANALYSIS_SUCCESS, STATUS_EXTRACT_FAIL, STATUS_EXTRACT_SUCCESS) = range(1, 10)
    STATUS_CHOICES = ((STATUS_LIVE, u"新增"),
                      (STATUS_DISPATCH, u'分发中'),
                      (STATUS_PROCESS, u"进行中"),
                      (STATUS_FAIL, u"下载失败"),
                      (STATUS_SUCCESS, u"下载成功"),
                      (STATUS_ANALYSIS_FAIL, u"分析失败"),
                      (STATUS_ANALYSIS_SUCCESS, u"分析成功"),
                      (STATUS_EXTRACT_FAIL, u"导出失败"),
                      (STATUS_EXTRACT_SUCCESS, u"导出成功"), )
    job = ReferenceField(Job, reverse_delete_rule=CASCADE)
    task_generator = ReferenceField(CrawlerTaskGenerator, null=True)
    uri = StringField(max_length=8000)
    args = StringField(max_length=2048, null=True)    # 存储cookie， header等信息
    status = IntField(default=STATUS_LIVE, choices=STATUS_CHOICES)
    from_host = StringField(max_length=128, blank=True, null=True)    # 从哪台主机生成
    add_datetime = DateTimeField(default=datetime.datetime.now)
    retry_times = IntField(default=0)
    meta = {"db_alias": "source"}    # 默认连接的数据库


class CrawlerGeneratorLog(Document):
    """log : execution results of generator scripts  """
    (STATUS_FAIL, STATUS_SUCCESS) = range(1, 3)
    STATUS_CHOICES = ((STATUS_FAIL, u"失败"), (STATUS_SUCCESS, u"成功"), )
    job = ReferenceField(Job, reverse_delete_rule=CASCADE)
    task_generator = ReferenceField(CrawlerTaskGenerator, reverse_delete_rule=CASCADE)
    status = IntField(default=0, choices=STATUS_CHOICES)
    failed_reason = StringField(max_length=10240, null=True, blank=True)
    content_bytes = IntField(default=0)
    spend_msecs = IntField(default=0)    #unit is microsecond
    hostname = StringField(null=True, blank=True, max_length=32)
    add_datetime = DateTimeField(default=datetime.datetime.now)

    meta = {"db_alias": "log"}


class CrawlerGeneratorCronLog(Document):
    """ log: execution results of crontab command """
    (STATUS_FAIL, STATUS_SUCCESS) = range(1, 3)
    STATUS_CHOICES = ((STATUS_FAIL, u"失败"), (STATUS_SUCCESS, u"成功"), )
    job = ReferenceField(Job, reverse_delete_rule=CASCADE)
    status = IntField(default=0, choices=STATUS_CHOICES)
    cron = StringField(max_length=128)
    failed_reason = StringField(max_length=10240, null=True, blank=True)
    spend_msecs = IntField(default=0)    #unit is microsecond
    add_datetime = DateTimeField(default=datetime.datetime.now)

    meta = {"db_alias": "log"}


class CrawlerGeneratorDispatchLog(Document):
    job = ReferenceField(Job, reverse_delete_rule=CASCADE)
    task_generator = ReferenceField(CrawlerTaskGenerator, reverse_delete_rule=CASCADE)
    content = StringField(max_length=1024, null=True)
    add_datetime = DateTimeField(default=datetime.datetime.now)

    meta = {"db_alias": "log"}


class CrawlerGeneratorErrorLog(Document):
    name = StringField(max_length=128)
    content = StringField(max_length=10240, null=True)
    hostname = StringField(null=True, max_length=32)
    add_datetime = DateTimeField(default=datetime.datetime.now)

    meta = {"db_alias": "log"}


class CrawlerGeneratorAlertLog(Document):
    name = StringField(max_length=128)
    content = StringField(max_length=10240, null=True)
    hostname = StringField(null=True, max_length=32)
    add_datetime = DateTimeField(default=datetime.datetime.now)

    meta = {"db_alias": "log"}

####### 以下模板为 下载器拥有


# 生产者：用户新增一个job时，设置 下载器配置 时产生。
# 消费者：下载程序
class CrawlerDownloadSetting(Document):
    job = ReferenceField(Job)
    dispatch_num = IntField(default=100)
    max_retry_times = IntField(default=5)
    proxy = StringField()
    cookie = StringField()
    download_timeout = IntField(default=200)
    last_update_datetime = DateTimeField(default=datetime.datetime.now)
    add_datetime = DateTimeField(default=datetime.datetime.now)
    meta = {"db_alias": "source"}


# 生产者：由管理员产生，配置布暑该平台支持的下载器语言
# 消费者：用户设置下载器时，types字段引用，
class CrawlerDownloadType(Document):
    language = StringField()
    is_support = BooleanField(default=True)
    add_datetime = DateTimeField(default=datetime.datetime.now)
    meta = {"db_alias": "source"}    # 默认连接的数据库


# 生产者：由用户新增一个job时，设置下载器产生。
# 消费者：下载程序
class CrawlerDownload(Document):
    (STATUS_ON, STATUS_OFF) = range(0, 2)
    STATUS_CHOICES = ((STATUS_ON, u"启用"), (STATUS_OFF, u"下线"))
    job = ReferenceField(Job)
    # job = StringField()
    code = StringField()    # code
    types = ReferenceField(CrawlerDownloadType)
    status = IntField(default=0, choices=STATUS_CHOICES)
    add_datetime = DateTimeField(default=datetime.datetime.now)
    meta = {"db_alias": "source"}    # 默认连接的数据库


# 生产者：下载程序
# 消费者：分析器
class CrawlerDownloadData(Document):
    job = ReferenceField(Job)
    # job = StringField(max_length=10240, required=True)
    downloader = ReferenceField(CrawlerDownload)
    crawlertask = ReferenceField(CrawlerTask)
    requests_headers = StringField()
    response_headers = StringField()
    requests_body = StringField()
    response_body = StringField()
    hostname = StringField()
    #大文件存储,存储下载的图片,pdf等.
    files_down = FileField(default=0)
    remote_ip = StringField()
    add_datetime = DateTimeField(default=datetime.datetime.now)
    meta = {"db_alias": "source"}    # 默认连接的数据库


# 生产者：该日志由下载器在分发工作时队列满等警告产生
# 消费者：用户及管理员查看
class CrawlerDispatchAlertLog(Document):
    (ALTER, SUCCESS, FAILED) = range(1, 4)
    ALTER_TYPES = ((ALTER, u'警告'), (SUCCESS, u'分发成功'), (FAILED, u'分发失败'))
    job = ReferenceField(Job, reverse_delete_rule=CASCADE)
    types = IntField(choices=ALTER_TYPES, default=1)
    reason = StringField(max_length=10240, required=True)
    content_bytes = IntField(default=0)
    hostname = StringField(required=True, max_length=32)
    add_datetime = DateTimeField(default=datetime.datetime.now)
    meta = {"db_alias": "log"}    # 默认连接的数据库


# 生产者： 下载程序
# 消费者： 用户及管理员查看
class CrawlerDownloadLog(Document):
    (STATUS_FAIL, STATUS_SUCCESS) = range(1, 3)
    STATUS_CHOICES = ((STATUS_FAIL, u"失败"), (STATUS_SUCCESS, u"成功"), )
    job = ReferenceField(Job)
    # job = StringField(max_length=10240, required=True)
    task = ReferenceField(CrawlerTask)
    status = IntField(default=0, choices=STATUS_CHOICES)
    requests_size = IntField()
    response_size = IntField()
    failed_reason = StringField(max_length=10240, required=False)
    downloads_hostname = StringField(required=True, max_length=32)
    spend_time = IntField(default=0)    #unit is microsecond
    add_datetime = DateTimeField(default=datetime.datetime.now)
    meta = {"db_alias": "log"}    # 默认连接的数据库


#生产者：各爬虫
#消费者：各爬虫
class CrawlerDownloadArgs(Document):
    province = StringField(maxlength=20)
    register_number = StringField(maxlength=25)
    unifield_number = StringField(maxlength=25)
    enterprise_name = StringField(maxlength=100)
    download_args = DictField()    #该企业号需要的信息如'id':'','ent_id':''等
    update_datetime = DateTimeField(default=datetime.datetime.now)
    meta = {"db_alias": "source"}    # 默认连接的数据库
