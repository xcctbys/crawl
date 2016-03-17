# required

* bootstrap >= 3.0

# usage

user header 

   {% load gravatar %}
   
   {% user_header user header_size is_show_name %}

form field
   
   {% load formfield %}
   {% form_field field %}

pagination

	{% load pagination %}
	{% pagination pager prefix request %}

card style

    {% load node_grid %}
    {% node_card "task" tasks 3 "tags/task_node.html" {"request":request} %}

list style

    {% load node_grid %}
    
    # {% node_list label nodes node_template node_template_data %}
    {% node_list "task" tasks "tags/task_node.html" {"request":request} %}
     
navs 

    {% load navs %}
    
    {% nav current_tab tabs %}
    
baidu share button

    {% load share %}
    
    {% baidu_share title description link %}
    
	
high performance model base

    CELERY_IMPORTS = (
	    "html5helper.model",
	)
	
	from html5helper.model import BaseModel
	from django.db import models
	
	class Blog(BaseModel):
	    name = models.CharField(max_length=20)
	    
	    class Meta:
	        app_label="html5helper"
	        
# Django utils

    from django.utils.timesince import timesince, timeuntil

#settings.py

	USER_SHOW_VIEW="app.views.home"   # must hava user_id as arg
	APP_DOMAIN = "www.diyyifu.com"