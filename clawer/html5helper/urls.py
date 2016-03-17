#coding=utf-8


from django.conf.urls import include, patterns, url


urlpatterns = patterns("html5helper.views", 
    url(r"^markdown/$", "markdown"),
)