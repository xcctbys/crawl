#coding=utf-8


from html5helper.decorator import render_template


def index(request):
    return render_template("clawer/logger/index.html", request=request)
