from django.db import models

# Create your models here.

class ProxyIp(models.Model):
	ip_port = models.CharField(max_length=24, unique=True, blank=False)
	province = models.CharField(max_length=20)
	is_valid = models.BooleanField()
	create_datetime = models.DateTimeField(auto_now_add=True)
	update_datetime = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return self.ip_port

class IpUser(models.Model):
	province = models.CharField(max_length=20)
	is_use_proxy = models.BooleanField(default=False)
	update_datetime = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s %s' % (self.province, self.is_use_proxy)