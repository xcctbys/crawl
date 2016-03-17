#encoding=utf-8

from enterprise.models import Enterprise, Province
from clawer.utils import EasyUIPager, check_auth_for_api
from html5helper.decorator import render_json

from django.utils.encoding import smart_unicode


@render_json
def get_all(request):
    province = request.GET.get("province")
    q = request.GET.get("q")  # use like
    
    queryset = Enterprise.objects
    if q:
        queryset = queryset.filter(name__icontains=q)
    if province:
        queryset = queryset.filter(province=int(province))
        
    pager = EasyUIPager(queryset, request)
    return pager.query()


@render_json
@check_auth_for_api
def add(request):
    names_file = request.FILES["names_file"]
    success = 0
    failed = 0
    multiple = 0
    line_count = 0
    
    for line in names_file:
        line_count += 1
        
        fields = line.strip().split(",")
        if len(fields) < 3:
            failed += 1
            continue
        
        name = smart_unicode(fields[0])
        province = Province.to_id(smart_unicode(fields[1]))
        register_no = fields[2]
        
        if not province:
            failed += 1
            continue
        
        if Enterprise.objects.filter(name=name).count() > 0:
            multiple += 1
            continue
        elif Enterprise.objects.filter(register_no=register_no).count() > 0:
            multiple += 1
            continue
        
        Enterprise.objects.create(name=name, province=province, register_no=register_no)
        success += 1
    
    return {"is_ok": True, "line_count": line_count, 'success': success, 'failed': failed, 'multiple': multiple}



@render_json
@check_auth_for_api
def province_echarts(request):
    result = {"is_ok":True, "series":[], "xAxis":[]}
    
    serie = [Enterprise.objects.filter(province=x[0]).count() for x in Province.choices]
    result["series"].append(serie)
    xs = []
    for x in Province.choices:
        if x[0] % 2 == 0:
            xs.append("\n"+x[1])
        else:
            xs.append(x[1])
    result["xAxis"] = xs
    
    return result
