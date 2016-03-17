#encoding=utf-8


from html5helper.decorator import render_template


def realtime_dashboard(request):
    return render_template("clawer/monitor/realtime_dashboard.html", request=request)


def hour(request):
    return render_template("clawer/monitor/hour.html", request=request)


def day(request):
    return render_template("clawer/monitor/day.html", request=request)