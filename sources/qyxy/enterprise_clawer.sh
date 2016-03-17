#!/bin/bash

WORKDIR="/home/webapps/nice-clawer/sources/qyxy"
PYTHON="/home/virtualenvs/dj18/bin/python"
MAX_TIME=72000


function safe_run()
{
    file="/tmp/enterprise_$1.lock"

    (
        flock -xn -w 10 200 || exit 1
        cd ${WORKDIR}; ${PYTHON} run.py $1 $2
    ) 200>${file}
}


time safe_run $*

