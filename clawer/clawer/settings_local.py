#encoding=utf-8

import os

from settings import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'clawer',                      # Or path to database file if using sqlite3.
        "USER": "cacti",
        "PASSWORD": "cacti",
        "HOST": "127.0.0.1",
        'TEST_CHARSET': 'utf8',
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

PYTHON = "/Users/pengxt/Documents/pyenv/dj14/bin/python"
CRONTAB_USER = "pengxt"
CLAWER_SOURCE = "/Users/pengxt/Documents/clawer/source/"
CLAWER_RESULT = "/Users/pengxt/Documents/clawer/result/"
CLAWER_RESULT_URL = "http://localhost:8000/media/clawer/result/"


MEDIA_URL = 'http://localhost:8000/media/'
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), "media")

REDIS = "redis://localhost:6379//0"
URL_REDIS = "redis://localhost:6379//0"
MONITOR_REDIS = "redis://localhost:6379//0"

EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'
EMAIL_HOST = 'smtp.exmail.qq.com'
EMAIL_PORT = 465   
EMAIL_HOST_USER='robot@princetechs.com'  
EMAIL_HOST_PASSWORD='Robot0023' 
USE_TLS = True

#captcha
CAPTCHA_STORE = os.path.join(os.path.dirname(__file__), "captcha")


"""
RAVEN_CONFIG = {
    'dsn': '',
}
"""

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
            'filename': os.path.join(os.path.dirname(__file__), "clawer.debug.log"),
            'backupCount': 1,
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
        'dbfile': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(os.path.dirname(__file__), "db.debug.log"),
            'backupCount': 1,
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        '': {
            'handlers':['file'],
            'propagate': True,
            'level':'DEBUG',
        },
        'django': {
            'handlers':['null'],
            'propagate': True,
            'level':'DEBUG',
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['dbfile'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}