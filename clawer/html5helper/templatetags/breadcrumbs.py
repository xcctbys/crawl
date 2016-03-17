#coding=utf-8
""" breadcrumbs
"""


from django import template
from django.template import Context


register = template.Library()


@register.tag("breadcrumbs")
def do_pagination(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, breadcrumbs = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires one argument" % token.contents.split()[0]) 
    return BreadcrumbsNode(breadcrumbs)

class BreadcrumbsNode(template.Node):
    def __init__(self, breadcrumbs):
        self.breadcrumbs = template.Variable(breadcrumbs)
    
    def render(self, context):
        t = template.loader.get_template("html5helper/tags/breadcrumbs.html")
        breadcrumbs = self.breadcrumbs.resolve(context)
        if len(breadcrumbs) > 0:
            breadcrumbs[-1]["is_active"] = True
        new_context = Context({"breadcrumbs": breadcrumbs}, 
                              autoescape=context.autoescape)
        return t.render(new_context)