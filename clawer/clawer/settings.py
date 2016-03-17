#encoding=utf-8

import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG


ADMINS = (
   ("xiaotaop", "xiaotaop@princetechs.com"),
)


MANAGERS = ADMINS


# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.4/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["clawer.princetechs.com"]

TIME_ZONE = 'Asia/Shanghai'
TIME_FORMAT = "H:i:s"
DATE_FORMAT = "Y-m-d"
DATETIME_FORMAT = "Y-m-d H:i:s"

LANGUAGE_CODE = 'zh.CN'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), '../static').replace('\\','/'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '_$56$ft*1=0s-428iey4*2&amp;oy*)$&amp;76f!(!l3(0m+ddl-7!+9s'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'clawer.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'clawer.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "clawer", 'templates').replace('\\','/'),
)

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'


EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'
EMAIL_HOST = 'smtp.exmail.qq.com'
EMAIL_PORT = 465
EMAIL_HOST_USER='robot@princetechs.com'
EMAIL_HOST_PASSWORD='Robot0023'
USE_TLS = True


AUTH_PROFILE_MODULE = 'clawer.UserProfile'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'raven.contrib.django.raven_compat',
    "south",
    #"djcelery",
    "html5helper",
    "captcha",
    "enterprise",
    "clawer",
)



CLAWER_TASK_URL_MULTIPLE_DAY = 7
DOWNLOAD_JS = os.path.join(os.path.dirname(__file__), "../download.js")
REDIS_DATA_COMPRESSED = True


JSONS_URL = 'http://clawer.princetechs.com/media/clawer_result/enterprise/json'
UPDATE_BY = "day" # "hour" | "day"

# JSONS_URL = "http://clawer.princetechs.com/media/clawer_result/4"
# UPDATE_BY = "hour" # "hour" | "day"

MULTIPROCESS = True # True | False
