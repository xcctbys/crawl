#!/bin/bash

WORKDIR="/home/webapps/nice-clawer/sources/bankrupt_pdf"
PYTHON="/home/virtualenvs/dj18/bin/python"


function safe_run()
{
    file="/tmp/bankrupt_$1.lock"

    (
        flock -xn -w 10 200 || exit 1
        cd ${WORKDIR}; ${PYTHON} run.py $1 $2
    ) 200>${file}
}


time safe_run $*

