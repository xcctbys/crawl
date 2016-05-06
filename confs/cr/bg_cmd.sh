#!/bin/bash

WORKDIR="/home/clawer/cr-clawer/clawer"
PYTHON="/usr/local/bin/python"

function safe_run()
{
    file="/tmp/$1.lock"

    (
        flock -xn -w 10 200 || exit 1
        cd ${WORKDIR}; ${PYTHON} manage_cr.py $*
    ) 200>${file}
}

time safe_run $*

