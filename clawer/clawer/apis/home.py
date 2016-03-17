#encoding=utf-8




import json
import datetime

from html5helper.decorator import render_json
from clawer.models import Clawer, ClawerTask, ClawerTaskGenerator,\
    ClawerAnalysis, ClawerAnalysisLog, Logger, LoggerCategory, ClawerDownloadLog,\
    ClawerGenerateLog
from clawer.utils import check_auth_for_api, EasyUIPager, BackgroundQueue
from clawer.forms import UpdateClawerTaskGenerator, UpdateClawerAnalysis,\
    AddClawerTask, UpdateClawerSetting, AddClawer
from html5helper.utils import get_request_ip



@render_json
@check_auth_for_api
def clawer_all(request):
    obj_id = request.GET.get("obj_id")
    status = request.GET.get("status")
    q = request.POST.get("q")  # use like
    
    queryset = Clawer.objects
    if obj_id:
        queryset = queryset.filter(id=int(obj_id))
    if q:
        queryset = queryset.filter(name__icontains=q)
    if status:
        queryset = queryset.filter(status=int(status))
        
    pager = EasyUIPager(queryset, request)
    return pager.query()


@render_json
@check_auth_for_api
def clawer_add(request):
    form = AddClawer(request.POST)
    if form.is_valid() is False:
        return {"is_ok": False, "reason": form.errors}
    
    if Clawer.objects.filter(name=form.cleaned_data['name']).count() > 0:
        return {"is_ok": False, "reason":u"%s 已经被占用" % form.cleaned_data['name']}
    
    clawer = Clawer.objects.create(name=form.cleaned_data['name'], info=form.cleaned_data['info'], customer=form.cleaned_data['customer'])
    #add log
    Logger.objects.create(user=request.user, category=LoggerCategory.ADD_CLAWER, title=form.cleaned_data["name"], 
                          content=json.dumps(request.POST), from_ip=get_request_ip(request))
    return {"is_ok": True, "clawer": clawer.as_json()}


@render_json
@check_auth_for_api
def clawer_download_log(request):
    status = request.GET.get("status")
    clawer_id = request.GET.get("clawer")
    task_id = request.GET.get("task_id")
    
    queryset = ClawerDownloadLog.objects.filter()
    if status:
        queryset = queryset.filter(status=status) 
    if clawer_id:
        queryset = queryset.filter(clawer_id=clawer_id)
    if task_id:
        queryset = queryset.filter(task_id=task_id)
        
    pager = EasyUIPager(queryset, request)
    return pager.query()


@render_json
@check_auth_for_api
def clawer_task(request):
    task_id = request.GET.get("id")
    status = request.GET.get("status")
    clawer_id = request.GET.get("clawer")
    
    queryset = ClawerTask.objects
    if status:
        queryset = queryset.filter(status=status) 
    if task_id:
        queryset = queryset.filter(id=task_id)
    if clawer_id:
        queryset = queryset.filter(clawer_id=clawer_id)    
    
    pager = EasyUIPager(queryset, request)
    return pager.query()


@render_json
@check_auth_for_api
def clawer_task_reset(request):
    from clawer import utils
    
    clawer_id = int(request.GET.get("clawer"))
    status = int(request.GET.get("status"))
    
    background_queue = BackgroundQueue()
    background_queue.enqueue(utils.clawer_task_reset, [clawer_id, status])
    #add log
    Logger.objects.create(user=request.user, category=LoggerCategory.TASK_RESET, title="%d affected" % -1, 
                          content=json.dumps(request.GET), from_ip=get_request_ip(request))
    return {"is_ok":True, "ret":-1}


@render_json
@check_auth_for_api
def clawer_task_add(request):
    form = AddClawerTask(request.POST)
    if form.is_valid() is False:
        return {"is_ok":True, "reason":u"%s" % form.errors}
    
    clawer_task = ClawerTask.objects.create(clawer=form.cleaned_data["clawer"], 
                                            uri=form.cleaned_data["uri"],
                                            cookie=form.cleaned_data["cookie"] or None)
    
    #add log
    Logger.objects.create(user=request.user, category=LoggerCategory.ADD_TASK, title=form.cleaned_data["uri"], 
                          content=json.dumps(request.POST), from_ip=get_request_ip(request))
    
    return {"is_ok":True, "clawer_task_id":clawer_task.id}


@render_json
@check_auth_for_api
def clawer_task_generator_update(request):
    form = UpdateClawerTaskGenerator(request.POST, request.FILES)
    if form.is_valid() is False:
        return {"is_ok":False, "reason": u"%s" % form.errors}
    
    code_file = request.FILES["code_file"]
    if code_file.name[-3:] != ".py":
        return {"is_ok":False, "reason":u"暂时只支持python文件"}
    
    code = code_file.read()
    
    task_generator = ClawerTaskGenerator.objects.create(clawer=form.cleaned_data["clawer"],
                                                        cron=form.cleaned_data["cron"],
                                                        code=code)
    
    #add log
    Logger.objects.create(user=request.user, category=LoggerCategory.UPDATE_TASK_GENERATOR, title=form.cleaned_data["clawer"].name, 
                          content=json.dumps(request.POST), from_ip=get_request_ip(request))
    
    return {"is_ok":True, "task_generator":task_generator.as_json()}
    
    
@render_json
@check_auth_for_api
def clawer_task_generator_history(request):
    clawer_id = request.GET.get("clawer_id")
    
    qs = ClawerTaskGenerator.objects.filter(clawer_id=clawer_id)
    pager = EasyUIPager(qs, request)
    return pager.query()


@render_json
@check_auth_for_api
def clawer_analysis_history(request):
    clawer_id = request.GET.get("clawer_id")
    
    queryset = ClawerAnalysis.objects.filter(clawer_id=clawer_id)
        
    pager = EasyUIPager(queryset, request)
    return pager.query()


@render_json
@check_auth_for_api
def clawer_analysis_log(request):
    status = request.GET.get("status")
    date = request.GET.get("date")
    clawer_id = request.GET.get("clawer")
    task_id = request.GET.get("task_id")
    
    queryset = ClawerAnalysisLog.objects
    if status:
        queryset = queryset.filter(status=status) 
    if clawer_id:
        queryset = queryset.filter(clawer_id=clawer_id)
    if date:
        start = datetime.datetime.strptime(date, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
        end = start + datetime.timedelta(1)
        queryset = queryset.filter(add_datetime__range=(start, end))
    if task_id:
        queryset = queryset.filter(task_id=task_id)
        
    pager = EasyUIPager(queryset, request)
    return pager.query()


@render_json
@check_auth_for_api
def clawer_generate_log(request):
    status = request.GET.get("status")
    clawer_id = request.GET.get("clawer")
    
    queryset = ClawerGenerateLog.objects
    if status:
        queryset = queryset.filter(status=status) 
    if clawer_id:
        queryset = queryset.filter(clawer_id=clawer_id)
        
    pager = EasyUIPager(queryset, request)
    return pager.query()


@render_json
@check_auth_for_api
def clawer_analysis_update(request):
    form = UpdateClawerAnalysis(request.POST, request.FILES)
    if form.is_valid() is False:
        return {"is_ok":False, "reason": u"%s" % form.errors}
    
    code_file = request.FILES["code_file"]
    if code_file.name[-3:] != ".py":
        return {"is_ok":False, "reason":u"暂时只支持python文件"}
    
    ClawerAnalysis.objects.filter(clawer=form.cleaned_data["clawer"]).update(status=ClawerAnalysis.STATUS_OFF)
    
    code = code_file.read()
    analysis = ClawerAnalysis.objects.create(clawer=form.cleaned_data["clawer"], code=code)
    
    #add log
    Logger.objects.create(user=request.user, category=LoggerCategory.UPDATE_ANALYSIS, title=form.cleaned_data["clawer"].name, 
                          content=json.dumps(request.POST), from_ip=get_request_ip(request))
    
    return {"is_ok":True, "analysis":analysis.as_json()}



@render_json
@check_auth_for_api
def clawer_setting_update(request):
    form = UpdateClawerSetting(request.POST)
    if form.is_valid() is False:
        return {"is_ok":False, "reason": u"%s" % form.errors}
    
    clawer = form.cleaned_data["clawer"]
    clawer_setting = clawer.settings()
    
    clawer_setting.dispatch = form.cleaned_data["dispatch"]
    clawer_setting.analysis = form.cleaned_data["analysis"]
    clawer_setting.proxy = form.cleaned_data["proxy"]
    clawer_setting.cookie = form.cleaned_data["cookie"]
    clawer_setting.download_js = form.cleaned_data["download_js"]
    clawer_setting.download_engine = form.cleaned_data["download_engine"]
    clawer_setting.prior = form.cleaned_data["prior"]
    clawer_setting.report_mails = form.cleaned_data["report_mails"]
    clawer_setting.save()
    
    clawer.status = form.cleaned_data["status"]
    clawer.save()
    #add log
    Logger.objects.create(user=request.user, category=LoggerCategory.UPDATE_SETTING, title=form.cleaned_data["clawer"].name, 
                          content=json.dumps(request.POST), from_ip=get_request_ip(request))
    
    return {"is_ok":True}



