#coding=utf-8

import md5
from django.template import Library
from django.conf import settings


register = Library()


@register.inclusion_tag("html5helper/tags/baidu_share.html")
def baidu_share(title="", description="", link="", size=16, tag="share_1"):
    title = settings.SHARE_PREFIX + "^~^ " + title
    content = ""
    if description:
        content = description.replace("\n", ";").replace("\r", "")
    if len(content) > 100:
        content = content[:100] + u"...."
    return {"title":title, "description":content, "link":link, "size":size, "tag":tag}
