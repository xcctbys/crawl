from django.db import models

# Create your models here.

class ProxyIp(BaseModel):
    ip_port = models.CharField(max_length=20, unique=True)
    province = models.CharField(max_length=20)
    is_valid = models.BooleanField()
    creade_datetime = models.DateTimeField(auto_now_add=True)
    update_datetime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.ip_port