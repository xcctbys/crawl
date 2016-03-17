#encoding=utf-8
from django.conf import settings


json_restore_path = '.enterprise_json'
if hasattr(settings, 'ENTERPRISE_JSON_RESTORE_PATH'):
    json_restore_path = settings.ENTERPRISE_JSON_RESTORE_PATH


proxies_file_path = '/tmp/proxies/proxies.pik'
