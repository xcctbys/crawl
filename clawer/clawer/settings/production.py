#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from settings import *


DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'clawer',
        'USER': 'cacti',
        'PASSWORD': 'cacti',
        'HOST': '10.0.1.3',
        'PORT': '',
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
            '127.0.0.1:11211',
        ],
    }
}

ALLOWED_HOSTS = ["*"]

MEDIA_ROOT = "/data/media/"
MEDIA_URL = "http://10.0.1.2/media/"

PYTHON = "/usr/local/bin/python"
SHELL = os.environ.get('SHELL', '/bin/bash')
CRON_FILE = os.path.join(os.path.dirname(__file__), "cron.f")
URI_TTL = 60*60*24

CRONTAB_USER = "nginx"
CRONTAB_HOME = "/home/clawer/cr-clawer/confs/cr"
CLAWER_SOURCE = "/data/clawer/"
CLAWER_RESULT = "/data/clawer_result/"
CLAWER_RESULT_URL = "http://10.0.1.2/media/clawer_result/"

REDIS = "redis://10.0.1.3:6379/0"
URL_REDIS = "redis://10.0.1.3:6379/0"
MONITOR_REDIS = "redis://10.0.1.3:6379/0"

# add my zhangyongming 2016.5.3
SUPER_MAX_QUEUE_LENGTH = 1000
HIGH_MAX_QUEUE_LENGTH = 2000
MEDIUM_MAX_QUEUE_LENGTH = 3000
LOW_MAX_QUEUE_LENGTH = 4000


# for storage
MongoDBS = {
    'default': {
        'host': 'mongodb://10.0.1.3/default',
    },
    'log': {
        'host': 'mongodb://10.0.1.3/log',
    },
    'source': {
        'host': 'mongodb://10.0.1.3/source',
    },
    'structure': {
        'host': 'mongodb://10.0.1.3/structure',
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
            'formatter': 'simple'
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
            'handlers': ['null'],
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
