#!/bin/bash

WORKDIR=/home/mingming/Documents/gitroom/cr-clawer/clawer
PYTHON=/home/mingming/Documents/pyenv/dj18/bin/python

# if [ ! -d ${WORKDIR} ]; then
#     WORKDIR=/Users/princetechs5/crawler/cr-clawer/clawer
# fi

# if [ ! -f ${PYTHON} ]; then
#     PYTHON=/Users/princetechs5/Documents/virtualenv/bin/python
# fi

cd ${WORKDIR}; ${PYTHON} manage.py $*
