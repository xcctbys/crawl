from django.db import models

# Create your models here.

class ProxyIp(models.Model):
    ip_port = models.CharField(max_length=24, unique=True, blank=False)
    province = models.CharField(max_length=20)
    is_valid = models.BooleanField()
    creade_datetime = models.DateTimeField(auto_now_add=True)
    update_datetime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.ip_port