#encoding=utf-8

from html5helper.decorator import render_json
from clawer.models import ClawerTask, RealTimeMonitor, ClawerHourMonitor, Clawer, ClawerDayMonitor
from clawer.utils import check_auth_for_api, EasyUIPager
import datetime




@render_json
@check_auth_for_api
def task_stat(request):
    result = {"is_ok":True, "status":[], "series":[], "xAxis":[]}
    monitor = RealTimeMonitor()
    
    for (status, name) in ClawerTask.STATUS_CHOICES:
        result["status"].append(name)
        
        remote_data = monitor.load_task_stat(status)
        dts = sorted(remote_data["data"].keys())
        if result["xAxis"] == []:
            result["xAxis"] = [x.strftime("%d %H:%M") for x in dts]
        serie = [remote_data["data"][x]["count"] for x in dts]
        result["series"].append(serie)
    
    return result


@render_json
@check_auth_for_api
def hour(request):
    clawer_id = request.GET.get("clawer")
    
    qs = ClawerHourMonitor.objects.all()
    if clawer_id:
        qs = qs.filter(clawer_id=clawer_id)
        
    return EasyUIPager(qs, request).query()



@render_json
@check_auth_for_api
def hour_echarts(request):
    clawer_id = request.GET.get("clawer_id")
    end = datetime.datetime.now().replace(minute=0, second=0)
    start = end - datetime.timedelta(30)
    result = {"is_ok":True, "series":[], "xAxis":[], "clawers":[]}
    
    clawers = []
    if clawer_id:
        clawer = Clawer.objects.get(id=clawer_id)
        clawers.append(clawer)
    else:
        clawers = Clawer.objects.filter(status=Clawer.STATUS_ON)
        
    offset = start
    while offset <= end:
        result['xAxis'].append(offset.strftime("%Y-%m-%d %H"))
        offset += datetime.timedelta(minutes=60)
            
    for clawer in clawers:
        qs = ClawerHourMonitor.objects.filter(clawer=clawer, hour__range=(start, end)).order_by("-hour")
        serie = {} # hour -> bytes
        
        for hour in result['xAxis']:
            serie.update({hour: 0})
            
        for item in qs:
            serie.update({item.hour.strftime("%Y-%m-%d %H"): item.bytes})
        
        result["series"].append([x[1] for x in sorted(serie.items(), key=lambda i: i[0])])
        result["clawers"].append(clawer.as_json())
        
    
    return result


@render_json
@check_auth_for_api
def day(request):
    clawer_id = request.GET.get("clawer")
    
    qs = ClawerDayMonitor.objects.all()
    if clawer_id:
        qs = qs.filter(clawer_id=clawer_id)
        
    return EasyUIPager(qs, request).query()


@render_json
@check_auth_for_api
def day_echarts(request):
    clawer_id = request.GET.get("clawer_id")
    end = datetime.datetime.now().replace(hour=0, minute=0, second=0)
    start = end - datetime.timedelta(30)
    result = {"is_ok":True, "series":[], "xAxis":[], "clawers":[]}
    
    clawers = []
    if clawer_id:
        clawer = Clawer.objects.get(id=clawer_id)
        clawers.append(clawer)
    else:
        clawers = Clawer.objects.filter(status=Clawer.STATUS_ON)
        
    offset = start
    while offset <= end:
        result['xAxis'].append(offset.strftime("%Y-%m-%d"))
        offset += datetime.timedelta(1)
        
    for clawer in clawers:
        qs = ClawerDayMonitor.objects.filter(clawer_id=clawer.id, day__range=(start, end)).order_by("-day")
        serie = {} # day -> bytes
        
        for hour in result['xAxis']:
            serie.update({hour: 0})
            
        for item in qs:
            serie.update({item.day.strftime("%Y-%m-%d"): item.bytes})
        
        result["series"].append([x[1] for x in sorted(serie.items(), key=lambda i: i[0])])
        result["clawers"].append(clawer.as_json())
        
    return result