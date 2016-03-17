#coding = utf-8

from django.contrib import admin
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from html5helper import autoregister

from clawer import models
from captcha import models as captcha_models
from enterprise import models as enterprise_models


class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    can_delete = False
    verbose_name_plural = 'profile'


# Define a new User admin
class UserAdmin(DjangoUserAdmin):
    inlines = (UserProfileInline, )
    list_display = ( "id", "username", "nickname", "last_login", "date_joined", "groups_name")
    search_fields = ["=id", "=username",]
    #list_filter = ("weixin_openid", "weibo_token")
    ordering = ("-date_joined", )
    
    def groups_name(self, user):
        names = [ x.name for x in user.groups.all()]
        return ",".join(names)
    
    def nickname(self, user):
        return user.get_profile().nickname
    
    

admin.site.unregister(DjangoUser)
admin.site.register(DjangoUser, UserAdmin)

autoregister.autoregister_admin(models)
autoregister.autoregister_admin(captcha_models)
autoregister.autoregister_admin(enterprise_models)

