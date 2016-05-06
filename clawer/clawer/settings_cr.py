#encoding=utf-8
"""中证信用的配置
"""
from settings import *
import os



DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'clawer',                      # Or path to database file if using sqlite3.
        'USER': 'cacti',                      # Not used with sqlite3.
        'PASSWORD': 'cacti',                  # Not used with sqlite3.
        'HOST': '10.0.1.2',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'KEY_PREFIX': "crawler",
        'LOCATION': [
            '10.0.1.2:11211',
        ],
    }
}

ALLOWED_HOSTS = ["*"]

MEDIA_ROOT = "/data/media/"
MEDIA_URL = "http://10.0.1.3/media/"

PYTHON = "/usr/local/bin/python"
CRONTAB_USER = "nginx"
CRONTAB_HOME = "/home/clawer/cr-clawer/confs/cr"
CLAWER_SOURCE = "/data/clawer/"
CLAWER_RESULT = "/data/clawer_result/"
CLAWER_RESULT_URL = "http://10.0.1.3/media/clawer_result/"

REDIS = "redis://10.0.1.2:6379/0"
URL_REDIS = "redis://10.0.1.2:6379//0"
MONITOR_REDIS = "redis://10.100.90.51/0"
# add by wang ziyang 2016-04-14
#MAX_QUEUE_LENGTH = 500

# add my zhangyongming 2016.5.3
SUPER_MAX_QUEUE_LENGTH = 1000
HIGH_MAX_QUEUE_LENGTH = 2000
MEDIUM_MAX_QUEUE_LENGTH = 3000
LOW_MAX_QUEUE_LENGTH = 4000

SHELL = os.environ.get('SHELL', '/bin/bash')
CRON_FILE= os.path.join(os.path.dirname(__file__), "cron.f")
URI_TTL = 60*60*24

# for storage

MongoDBS = {
    'default': {
        'host': 'mongodb://10.0.1.2/default',
    },
    'log': {
        'host': 'mongodb://10.0.1.2/log',
    },
    'source': {
        'host': 'mongodb://10.0.1.2/source',
    },
    'structure': {
        'host': 'mongodb://10.0.1.2/structure',
    }
}

from mongoengine import connect

for name, db in MongoDBS.iteritems():
    connect(host=db['host'], alias= name)


#captcha
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
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
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
            'filename': os.path.join("/home/web_log/cr-clawer/", "clawer.pro.log"),
            'backupCount': 24,
            'formatter': 'verbose',
            'level': 'ERROR',
        },
    },
    'loggers': {
        '': {
            'handlers':['file'],
            'propagate': True,
            'level':'ERROR',
        },
        'django': {
            'handlers':['null'],
            'propagate': True,
            'level':'ERROR',
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
