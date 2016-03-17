#encoding=utf-8
# Create your views here.

import random
import traceback

from html5helper.utils import get_request_ip, do_paginator
from html5helper.decorator import render_template, render_json
from captcha.models import Captcha, LabelLog, Category
from django.core.urlresolvers import reverse



def index(request):
    title = u"图片识别"
    category_id = request.GET.get("category_id")
    
    random_count = 50
    if category_id:
        category_id = int(category_id)
        category = Category.objects.get(id=category_id)
        captchas = Captcha.objects.filter(label_count__lt=3, category=category_id)[:random_count]
        labeled_captcha_count = Captcha.objects.filter(label_count__gt=2, category=category_id).count()
        captcha_count = Captcha.objects.filter(category=category_id).all().count()
    else:
        captchas = Captcha.objects.filter(label_count__lt=3)[:random_count]
        labeled_captcha_count = Captcha.objects.filter(label_count__gt=2).count()
        captcha_count = Captcha.objects.all().count()
        category = None
        
    if len(captchas) > 1:
        random_index = random.randint(0, len(captchas))
        captcha = captchas[random_index]
    elif len(captchas) == 1:
        captcha = captchas[0]
    else:
        captcha = None
        
    categories = Category.objects.all()
    
    return render_template("captcha/index.html", request=request, labeled_captcha_count=labeled_captcha_count, catpcha_count=captcha_count, title=title,
                           captcha=captcha, categories=categories, category=category)
    
    
def labeled(request, page=1):
    qs = Captcha.objects.filter(label_count__gt=2)
    pager = do_paginator(qs, page, 20)
    prefix = reverse("captcha.views.labeled")
    
    return render_template("captcha/labeled.html", request=request, pager=pager, prefix=prefix)


@render_json
def make_label(request):
    captcha_id = request.POST.get("captcha_id")
    label = request.POST.get("label")
    
    try:
        captcha = Captcha.objects.get(id=captcha_id)
    except:
        return {"is_ok":False, "reason": traceback.format_exc(1)}
    
    if not label.strip():
        return {"is_ok":False, "reason":u"文字不能为空"}
    
    captcha.label_count += 1
    captcha.save()
    
    LabelLog.objects.create(captcha=captcha, label=label, ip=get_request_ip(request))
    return {"is_ok":True}


@render_json
def all_labeled(request):
    category = int(request.GET.get("category"))
    qs = Captcha.objects.filter(label_count__gt=2, category=category)
    
    return {"is_ok":True, "captchas":[x.as_json() for x in qs]}