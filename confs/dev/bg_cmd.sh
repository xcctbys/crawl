#!/bin/bash

WORKDIR=/d/gitroom/cr-clawer/clawer
PY=~/Documents/pyenv/dj18/bin/python

if [ ! -d ${WORKDIR} ]; then
    WORKDIR=~/Documents/gitroom/cr-clawer/clawer
fi

if [ ! -f ${PY} ]; then
    PY=/d/virtualenvs/dj14/Scripts/python
fi

cd ${WORKDIR}; ${PY} manage.py $*
