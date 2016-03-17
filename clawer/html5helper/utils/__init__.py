#coding=utf-8
import time
import markdown
import cStringIO

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

from raven import Client

try:
    client = Client(settings.RAVEN_CONFIG["dsn"])
except:
    client = None


def wrapper_raven(fun):
    """
    wrapper for raven to trace manager commands
    """
    def wrap(cls, *args, **kwargs):
        try:
            return fun(cls, *args, **kwargs)
        except Exception, e:
            if client:
                client.captureException()
            else:
                raise e

    return wrap


def get_request_ip(request):
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):  
        ip =  request.META['HTTP_X_FORWARDED_FOR']  
    else:  
        ip = request.META['REMOTE_ADDR']
    return ip


def make_markdown(text):
    return markdown.markdown(text, 
                             extensions=["extra", "toc", "codehilite", "wikilinks", "sane_lists", "markdown.extensions.nl2br", "markdown.extensions.tables"],
                             output_format="html5",
                             safe_mode=True,
                             lazy_ol=True)
    
    
def do_paginator(objs, page, page_size):
    paginator = Paginator(objs, page_size) # Show 25 contacts per page
    try:
        objs_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        objs_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        objs_page = paginator.page(paginator.num_pages)
    return objs_page


def make_card_grids(objs, column_number=2):
    objs_number = len(objs)
    objs_grids = []
    
    for i in range(column_number):
        objs_grids.append([])
        
    for i in range(objs_number):
        j = i % column_number
        objs_grids[j].append(objs[i])
    return objs_grids


def datetime_to_timestamp(dt):
    return int(_utc_mktime(dt.timetuple()))


def _utc_mktime(utc_tuple):
    if len(utc_tuple) == 6:
        utc_tuple += (0, 0, 0)
    return time.mktime(utc_tuple)


def save_upload_image(image_file, path, resize=(1096, 640), min_size=None):
    """ save form upload file
    Args:
       image_file: request FILES object
       path: save path
       resize: resize, (width, height)
       min_size: minimum size, format is (width, height)
    Returns:
       None
    Exceptions:
       if failed, will raise exception
    """
    try:
        import PIL
        from PIL import ImageFile
        from PIL import Image
        from PIL import ImageFilter
    except Exception, e:
        raise e
    from water_mark import water_mark
    
    
    parser = ImageFile.Parser()
    for chunk in image_file.chunks():  
        parser.feed(chunk)  
    img = parser.close()  
    
    if min_size:
        if min_size[0] != img.size[0] or min_size[1] != img.size[1]:
            raise Exception(u"当前大小为%s，不符合最低大小要求%s" % (img.size, min_size))
    
    if resize:
        img.thumbnail(resize, Image.ANTIALIAS)    
        background_img = Image.new("RGBA", resize)
        box = ((resize[0]-img.size[0])/2, (resize[1]-img.size[1])/2)
        background_img.paste(img, box=box)
        img = background_img
        
    #give water mark
    mark_file = open(settings.WATER_MARK_PATH, "r")
    mark = Image.open(mark_file)
    img_data = water_mark(img, mark)
    mark_img = Image.open(cStringIO.StringIO(img_data))
    mark_img.save(path)
    