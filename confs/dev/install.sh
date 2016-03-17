#!/bin/bash

PIP=~/Documents/pyenv/dj14/bin/pip

if [ ! -f ${PIP} ]; then
    PIP=~/Documents/pyenv/dj14/Scripts/pip
fi


${PIP} install --upgrade pip

echo "Python ${PIP}"

LIBS="pillow Pygments Markdown MySQL-python django-celery south raven python-memcached django-debug-toolbar six redis requests threadpool python-crontab beautifulsoup4 rq selenium selenium-requests pytest-django jinja2 lxml html5lib django==1.4.15"

for lib in ${LIBS}
do
   ${PIP} install ${lib}
done
