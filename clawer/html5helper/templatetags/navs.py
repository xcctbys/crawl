#coding=utf-8
""" all navs
"""

from django.template import Context
from django import template


register = template.Library()


@register.tag("nav")
def do_nav(parser, token):
    """ show navigate at header of page. tabs format is:
    MAIN_NAV = [
        {"name": u"主页", "url": "/"},
        {"name": u"提醒", "url": "/task/digg/"},
        {"name": u"笔记", "url": "/life/"},
        {"name": u"读书", "url": "/book/"},
        {"name": u"站点日记", "url": "/sitelog/"},
    ]
    """
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, tab, tabs = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0]) 
    return NavNode(tab, tabs)

class NavNode(template.Node):
    def __init__(self, tab, tabs): 
        self.tab = template.Variable(tab)
        self.tabs = template.Variable(tabs)
        
    def render(self, context):
        t = template.loader.get_template("html5helper/tags/nav.html")
        new_context = Context({'tabs': self.tabs.resolve(context),
                               "current_tab": self.tab.resolve(context)}, 
                              autoescape=context.autoescape)
        return t.render(new_context)
    
    
@register.tag("nav_list")
def do_nav_list(parser, token):
    """ show nav as list. nav format is:
    {
        "header": "", 
        "items": [
            {"name": "", "link": "", "number": 1, "icon": ""},
        ],
    }
    """
    try:
        tag_name, cur_item, nav = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0]) 
    return NavListNode(cur_item, nav)

class NavListNode(template.Node):
    def __init__(self, cur_item, nav): 
        self.cur_item = template.Variable(cur_item)
        self.nav = template.Variable(nav)
        
    def render(self, context):
        t = template.loader.get_template("html5helper/tags/nav_list.html")
        nav = self.nav.resolve(context)
        cur_item = self.cur_item.resolve(context)
        
        new_context = Context({"cur_item": cur_item, "nav": nav}, 
                              autoescape=context.autoescape)
        return t.render(new_context)