#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from settings import *


DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'csciwlpc',
        'USER': 'plkj',
        'PASSWORD': 'Password2016',
        'HOST': 'csciwlpc.mysql.rds.aliyuncs.com',
        'PORT': '3306',
        'OPTIONS': {
            'sql_mode': 'TRADITIONAL',
            'charset': 'utf8',
            'init_command': 'SET '
            'storage_engine=INNODB,'
            'character_set_connection=utf8,'
            'collation_connection=utf8_bin'
        }

    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'KEY_PREFIX': "crawler",
        'LOCATION': [
            '172.16.80.5:11211',
        ],
    }
}

ALLOWED_HOSTS = ["*"]

MEDIA_ROOT = "/data/media/"
MEDIA_URL = "http://172.16.80.5/media/"

PYTHON = "/usr/bin/python"
SHELL = os.environ.get('SHELL', '/bin/bash')
CRON_FILE = os.path.join(os.path.dirname(__file__), "cron.f")
URI_TTL = 60*60*24

CRONTAB_USER = "nginx"
CRONTAB_HOME = "/home/webapps/cr-clawer/confs/cr"
CLAWER_SOURCE = "/data/clawer/"
CLAWER_RESULT = "/data/clawer_result/"
CLAWER_RESULT_URL = "http://172.16.80.5/media/clawer_result/"

REDIS = "redis://:Password123@13153c2b13894978.m.cnsza.kvstore.aliyuncs.com/0"
GENERATOR_REDIS = "redis://:Password123@13153c2b13894978.m.cnsza.kvstore.aliyuncs.com/1"
DOWNLOADER_REDIS = "redis://:Password123@13153c2b13894978.m.cnsza.kvstore.aliyuncs.com/2"
STRUCTURE_REDIS = "redis://:Password123@13153c2b13894978.m.cnsza.kvstore.aliyuncs.com/3"
EXTRACTER_REDIS = "redis://:Password123@13153c2b13894978.m.cnsza.kvstore.aliyuncs.com/5"
FILTER_REDIS = "redis://:Password123@13153c2b13894978.m.cnsza.kvstore.aliyuncs.com/4"
MONITOR_REDIS = "redis://:Password123@13153c2b13894978.m.cnsza.kvstore.aliyuncs.com/0"

# add generator rq 2016.5.3
SUPER_MAX_QUEUE_LENGTH = 1000
HIGH_MAX_QUEUE_LENGTH = 2000
MEDIUM_MAX_QUEUE_LENGTH = 3000
LOW_MAX_QUEUE_LENGTH = 4000


# for storage

MongoDBS = {
    'default': {
        'host': "mongodb://clawer:plkjplkj@dds-wz9a828f745eac341.mongodb.rds.aliyuncs.com:3717,dds-wz9a828f745eac342.mongodb.rds.aliyuncs.com:3717/default?replicaSet=mgset-1160325",
    },
    'log': {
       'host': "mongodb://clawer:plkjplkj@dds-wz9a828f745eac341.mongodb.rds.aliyuncs.com:3717,dds-wz9a828f745eac342.mongodb.rds.aliyuncs.com:3717/log?replicaSet=mgset-1160325",
    },
    'source': {
        'host': "mongodb://clawer:plkjplkj@dds-wz9a828f745eac341.mongodb.rds.aliyuncs.com:3717,dds-wz9a828f745eac342.mongodb.rds.aliyuncs.com:3717/source?replicaSet=mgset-1160325",
    },
    'structure': {
       'host': "mongodb://clawer:plkjplkj@dds-wz9a828f745eac341.mongodb.rds.aliyuncs.com:3717,dds-wz9a828f745eac342.mongodb.rds.aliyuncs.com:3717/structure?replicaSet=mgset-1160325",
    }
}

from mongoengine import connect

for name, db in MongoDBS.iteritems():
    connect(host=db['host'], alias=name)

# captcha
CAPTCHA_STORE = "/data/media/captcha"


RAVEN_CONFIG = {
    'dsn': 'http://917b2f66b96f46b785f8a1e635712e45:556a6614fe28410dbf074552bd566750@sentry.princetechs.com//2',
}

# Extracter config file path
EXTRACTER_CONFIG_PATH = 'structure/extracters/csciwlpc_conf.json'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(pathname)s:%(lineno)d:: %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join("/home/logs/cr-clawer/", "clawer.pro.log"),
            'backupCount': 24,
            'formatter': 'verbose',
            'level': 'ERROR',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'ERROR',
        },
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'ERROR',
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
