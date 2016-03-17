from django.conf.urls import patterns, include, url



urlpatterns = patterns('captcha.views',
    # Examples:
    url(r'^$', 'index'),
    url(r'^labeled/$', 'labeled'),
    url(r'^labeled/(?P<page>\d+)/$', 'labeled'),
    url(r'^all/labeled/$', 'all_labeled'),
    
    url(r"^make/label/$", "make_label"),
)
