#coding=utf-8

from django import template


register = template.Library()

PAGE_NUMBER = 2


@register.inclusion_tag("html5helper/tags/pagination.html", name="pagination")
def do_pagination(pager, prefix, request=None):
    if not pager:
        return {"pager":None}
    
    if prefix and prefix[-1] == "/":
        prefix = prefix[:len(prefix) - 1]
        
    cur_page = pager.number
    start = cur_page - PAGE_NUMBER
    if start <= 0:
        start = 1
    end = cur_page + PAGE_NUMBER
    if end >= pager.paginator.num_pages:
        end = pager.paginator.num_pages 
    pages = range(start, end+1)
    
    first_pages = []
    if pager.paginator.num_pages>2*PAGE_NUMBER and cur_page>PAGE_NUMBER*2:
        first_pages = range(1, 3)        
    
    last_pages = []
    if pager.paginator.num_pages>2*PAGE_NUMBER and cur_page<pager.paginator.num_pages-PAGE_NUMBER:
        last_pages = range(pager.paginator.num_pages-2, pager.paginator.num_pages+1)        
    
    params = ""
    if request:
        full_path = request.get_full_path()
        quote_index = full_path.find("?")
        if quote_index > -1:
            params = full_path[quote_index:]
    
    return {"pager":pager, "prefix":prefix, "pages":pages, "params":params, "last_pages":last_pages, "first_pages":first_pages}