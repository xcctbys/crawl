#!/bin/bash

# WORKDIR=/d/gitroom/nice-clawer/clawer
# PY=~/Documents/pyenv/dj14/bin/python
WORKDIR="/home/webapps/nice-clawer/clawer"
PY="/home/virtualenvs/py27/bin/python"

if [ ! -d ${WORKDIR} ]; then
    WORKDIR=/home/webapps/nice-clawer/clawer
fi

if [ ! -f ${PY} ]; then
    PY=/home/virtualenvs/py27/bin/python
fi


function app()
{
    cd ${WORKDIR};${PY} manage_cr.py runserver 0.0.0.0:8000
}

function celery()
{
    cd ${WORKDIR};${PY} manage_cr.py celery worker --broker="redis://localhost:6379/0" -l info
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
