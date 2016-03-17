#!/bin/bash

WORKDIR="/home/webapps/nice-clawer/sources/bankrupt_instrument"
PYTHON="/home/virtualenvs/dj18/bin/python"
MAX_TIME=72000


function safe_run()
{
    file="/tmp/bankrupt_instrument_$1.lock"

    (
        flock -xn -w 10 200 || exit 1
        cd ${WORKDIR}; ${PYTHON} InstrumentParsing.py $1
    ) 200>${file}
}


time safe_run $*

