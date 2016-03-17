#encoding=utf-8
from html5helper.decorator import render_template
from enterprise.models import Province


def get_all(request):
    return render_template('enterprise/get_all.html', request=request, Province=Province)