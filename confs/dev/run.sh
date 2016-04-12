#!/bin/bash

WORKDIR=~/Documents/gitroom/cr-clawer/clawer
PY=~/Documents/pyenv/dj18/bin/python
RQWORKER=~/Documents/pyenv/dj18/bin/rqworker


function app()
{
    cd ${WORKDIR}; ${PY} manage.py runserver 0.0.0.0:8000
}

function rq()
{
    shift
    queues=$@
    DJANGO_SETTINGS_MODULE="clawer.settings_local" ${RQWORKER} --url redis://127.0.0.1/0  -v -P ${WORKDIR} ${queues}
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
