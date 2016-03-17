#encoding=utf-8


from html5helper.decorator import render_template


def index(request):
    return render_template("index.html", request=request)


def clawer(request):
    return render_template("clawer/index.html", request=request)


def clawer_all(request):
    return render_template("clawer/all.html", request=request)


def clawer_task(request):
    return render_template("clawer/task.html", request=request)


def clawer_download_log(request):
    return render_template("clawer/download_log.html", request=request)


def clawer_analysis_log(request):
    return render_template("clawer/analysis_log.html", request=request)


def clawer_generate_log(request):
    return render_template("clawer/generate_log.html", request=request)


def clawer_setting(request):
    return render_template("clawer/setting.html", request=request)


def page_404(request):
    return render_template("404.html", request=request)


def page_500(request):
    return render_template("500.html", request=request)