#!/bin/bash


DAY_AGO=3
DISK_USAGE=80


function shrink_clawer() 
{
     used=`df -h | grep xvdb | awk '{print int($5)}'`
     if [ ${used} -gt ${DISK_USAGE} ]; then
         #remove 7 days ago file
         for (( i=${DAY_AGO}; i<=30; i++ )) 
         do
             d=`date "+%Y/%m/%d" -d "${i} days ago"`
             path="/data/clawer/${d}"
             /bin/rm -vrf  ${path}
         done
     fi
}

function shrink_tmp() 
{
    cd /tmp && /bin/rm -rfv tmp* & 
    cd /tmp && /bin/rm -rfv xvfb-run* & 
    echo>/tmp/firefox.log
}

function main()
{
    shrink_tmp
    shrink_clawer
}


time main
