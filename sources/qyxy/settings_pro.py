import logging
import raven

#log
log_level = logging.WARN
log_file = '/data/clawer_result/enterprise/crawler.log'
logger = None

#whether to save html page
save_html = False

html_restore_path = '/data/clawer_result/enterprise/html'
json_restore_path = '/data/clawer_result/enterprise/json'

#our enterprise list to be crawled
enterprise_list_path = './enterprise_list/'

crawler_num = 2


#for sentry
sentry_dns = 'http://917b2f66b96f46b785f8a1e635712e45:556a6614fe28410dbf074552bd566750@sentry.princetechs.com//2'
sentry_client = raven.Client(dsn=sentry_dns)


EMAIL_HOST = 'smtp.exmail.qq.com'
EMAIL_PORT = 465   
EMAIL_HOST_USER='robot@princetechs.com'  
EMAIL_HOST_PASSWORD='Robot0023' 

ADMINS = (
    ('admin', 'xiaotaop@princetechs.com'),
    #('shaoxiongz', 'shaoxiongz@princetechs.com'),
)
