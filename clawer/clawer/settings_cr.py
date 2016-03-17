#encoding=utf-8
"""中证信用的配置
"""
from settings import *



DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'clawer',                      # Or path to database file if using sqlite3.
        'USER': 'cacti',                      # Not used with sqlite3.
        'PASSWORD': 'cacti',                  # Not used with sqlite3.
        'HOST': '10.100.80.50',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'KEY_PREFIX': "crawler",
        'LOCATION': [
            '10.100.90.51:11211',
        ],
    }
}

ALLOWED_HOSTS = ["*"]

MEDIA_ROOT = "/data/media/"
MEDIA_URL = "http://10.100.90.51/media/"

PYTHON = "/home/virtualenvs/py27/bin/python"
CRONTAB_USER = "nginx"
CRONTAB_HOME = "/home/webapps/nice-clawer/confs/cr"
CLAWER_SOURCE = "/data/clawer/"
CLAWER_RESULT = "/data/clawer_result/"
CLAWER_RESULT_URL = "http://10.100.90.51/media/clawer_result/"

REDIS = "redis://10.100.90.51/0"
URL_REDIS = "redis://10.100.90.52/0"
MONITOR_REDIS = "redis://10.100.90.51/0"


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
            'filename': os.path.join("/home/web_log/nice-clawer/", "clawer.pro.log"),
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