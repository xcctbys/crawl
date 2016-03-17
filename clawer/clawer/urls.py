from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings



admin.autodiscover()


#apis 
user_api_urls = patterns("clawer.apis.user", 
    url(r"^login/$", "login"),
    url(r"^logout/$", "logout"),
    url(r"^keepalive/$", "keepalive"),
    url(r"^is/logined/$", "is_logined"),
    
    url(r"^my/menus/$", "get_my_menus"),

)

logger_api_urls = patterns("clawer.apis.logger",
    url(r"^all/$", "all"),
)

monitor_api_urls = patterns("clawer.apis.monitor",
    url(r"^task/stat/$", "task_stat"),
    url(r"^hour/$", "hour"),
    url(r"^day/$", "day"),
    url(r"^hour/echarts/$", "hour_echarts"),
    url(r"^day/echarts/$", "day_echarts"),
)

home_api_urls = patterns("clawer.apis.home",
    url(r"^clawer/all/$", "clawer_all"),
    url(r"^clawer/add/$", "clawer_add"),
    
    url(r"^clawer/task/$", "clawer_task"),
    url(r"^clawer/task/add/$", "clawer_task_add"),
    url(r"^clawer/task/reset/$", "clawer_task_reset"),
    
    url(r"^clawer/task/generator/update/$", "clawer_task_generator_update"),
    url(r"^clawer/task/generator/history/$", "clawer_task_generator_history"),
    url(r"^clawer/generate/log/$", "clawer_generate_log"),
    
    url(r"^clawer/analysis/history/$", "clawer_analysis_history"),
    url(r"^clawer/analysis/log/$", "clawer_analysis_log"),
    url(r"^clawer/analysis/update/$", "clawer_analysis_update"),
    
    url(r"^clawer/setting/update/$", "clawer_setting_update"),
    
    url(r"^clawer/download/log/$", "clawer_download_log"),
)

apis_urls = patterns("clawer.apis", 
    url(r"^user/", include(user_api_urls)),
    url(r"^home/", include(home_api_urls)),
    url(r"^logger/", include(logger_api_urls)),
    url(r"^monitor/", include(monitor_api_urls)),
)



#views
logger_urls = patterns("clawer.views.logger",
    url(r"^$", "index"),
)

monitor_urls = patterns("clawer.views.monitor",
    url(r"^realtime/dashboard/$", "realtime_dashboard"),
    url(r"^hour/$", "hour"),
    url(r"^day/$", "day"),
)


urlpatterns = patterns('clawer.views.home',
    # Examples:
    url(r'^$', 'index'),
    
    url(r'^clawer/$', "clawer"),
    url(r'^clawer/all/$', "clawer_all"),
    url(r"^clawer/download/log/$", "clawer_download_log"),
    url(r"^clawer/task/$", "clawer_task"),
    url(r"^clawer/analysis/log/$", "clawer_analysis_log"),
    url(r"^clawer/generate/log/$", "clawer_generate_log"),
    url(r"^clawer/setting/$", "clawer_setting"),
    
    url(r"^logger/", include(logger_urls)),
    url(r"^monitor/", include(monitor_urls)),
    
    url(r'^apis/', include(apis_urls)),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r"^captcha/", include("captcha.urls")),
    
    url(r"^enterprise/", include("enterprise.urls")),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)


if settings.DEBUG:
    urlpatterns += patterns("",
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
    )
    
    
handler404 = 'clawer.views.home.page_404'
handler500 = 'clawer.views.home.page_500'
