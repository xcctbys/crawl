#!/bin/bash

WORKDIR=~/crawler/cr-clawer/clawer
PY=~/Documents/virtualenv/bin/python
RQWORKER=~/Documents/virtualenv/bin/rqworker


function app()
{
    cd ${WORKDIR}; ${PY} manage.py runserver 0.0.0.0:8000
}

function rq()
{
    shift
    queues=$@
    DJANGO_SETTINGS_MODULE="clawer.settings_local" ${RQWORKER} --url redis://127.0.0.1/0  -v -P ${WORKDIR} uri_super uri_high uri_medium uri_low
}

case $1 in
"app")
    app
;;
"rq")
    rq $*
;;
*)
    echo "Usage: ./run.sh (app|rq)"
;;
esac
