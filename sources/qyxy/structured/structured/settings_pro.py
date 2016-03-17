# -*- coding: utf-8 -*-
from settings import *
import logging


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'enterprise',
        'USER': 'cacti',
        'PASSWORD': 'cacti',
        'HOST': '10.100.80.50',
        'PORT': '3306',
    }
}

#JSONS_URL = 'http://10.100.90.51:8080/media/clawer_result/enterprise/json'
#JSONS_URL = "http://clawer.princetechs.com/media/clawer_result/4"
JSONS_URL = "http://10.100.90.51:8080/media/clawer_result/7"
MULTIPROCESS = False
LOG_LEVEL = logging.ERROR
LOG_FORMAT = '%(asctime)s %(name)s %(levelname)s %(pathname)s:%(lineno)d:: %(message)s'
LOG_FILE = 'structured.log'
logger = None
UPDATE_BY = "hour"

EMAIL_HOST = 'smtp.exmail.qq.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'robot@princetechs.com'
EMAIL_HOST_PASSWORD = 'Robot0023'

ADMINS = (
    ('admin', 'haijunt@princetechs.com'),
    ('admin', 'yijiaw@princetechs.com'),
    ('admin', 'ziyangw@princetechs.com'),
    ('admin', 'liliw@princetechs.com'),
)


RAVEN_CONFIG = {
    'dsn': 'http://917b2f66b96f46b785f8a1e635712e45:556a6614fe28410dbf074552bd566750@sentry.princetechs.com//2',
}
