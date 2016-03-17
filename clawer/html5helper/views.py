#coding=utf-8

from html5helper.decorator import render_json
from html5helper.utils import make_markdown


@render_json
def markdown(request):
    content = request.POST["content"]
    
    return {"is_ok":True, "content": make_markdown(content)}