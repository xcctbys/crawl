#!/bin/bash

WORKDIR=/d/gitroom/cr-clawer/clawer
PY=~/Documents/pyenv/dj14/bin/python

if [ ! -d ${WORKDIR} ]; then
    WORKDIR=~/Documents/gitroom/cr-clawer/clawer
fi


function app()
{
    cd ${WORKDIR};${PY} manage.py runserver 0.0.0.0:8000
}

function celery()
{
    cd ${WORKDIR};${PY} manage.py celery worker --broker="redis://localhost:6379/0" -l info
}

case $1 in
"app")
    app
;;
"celery")
    celery
;;
*)
    echo "Usage: ./run.sh (app|celery)"
;;
esac
