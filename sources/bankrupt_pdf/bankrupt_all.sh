#!/bin/bash

WORKDIR="/home/webapps/nice-clawer/sources/bankrupt_pdf"
PYTHON="/home/virtualenvs/dj18/bin/python"


function safe_run()
{
    file="/tmp/bankrupt_all.lock"

    (
        flock -xn -w 10 200 || exit 1
        cd ${WORKDIR}; ${PYTHON} run.py $1 $2
    ) 200>${file}
}

start="20160119"
count=11
i=0

while [ $i -lt ${count} ]
do
    
    i=`expr $i + 1`
    dt=`expr $start + $i`
    echo "$i $dt"
    time safe_run 3600 ${dt}
done

