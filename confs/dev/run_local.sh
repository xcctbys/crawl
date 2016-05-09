#!/bin/bash

WORKDIR=~/crawler/cr-clawer/clawer
PY=~/Documents/virtualenv/bin/python
RQWORKER=~/Documents/virtualenv/bin/rqworker

# WORKDIR_DOWN=~/crawler/cr-clawer/clawer
#PY_DOWN=~/Documents/virtualenv/bin/python
# RQWORKER_DOWN=~/Documents/virtualenv/bin/rqworker
WORKDIR_DOWN=~/Documents/pyenv/cr-clawer/clawer
RQWORKER_DOWN=/Users/princetechs3/anaconda/bin/rqworker


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

function rq_down()
{
    shift
    queues=$@
    DJANGO_SETTINGS_MODULE="clawer.settings_local" ${RQWORKER_DOWN} --url redis://127.0.0.1/0  -v -P ${WORKDIR_DOWN} down_super down_high down_mid down_low
}

case $1 in
"app")
    app
;;
"rq")
    rq $*
;;
"rq_down")
	rq_down $*
;;
*)
    echo "Usage: ./run.sh (app|rq)"
;;
esac
