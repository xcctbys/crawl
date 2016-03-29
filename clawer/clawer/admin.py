#coding = utf-8
from django_smart_autoregister import auto_configure_admin


auto_configure_admin(applications=["boss", "captcha", "collector", "structure", "storage", "clawer"])
