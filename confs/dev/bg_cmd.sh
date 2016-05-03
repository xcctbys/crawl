#!/bin/bash

WORKDIR=/Users/princetechs5/crawler/cr-clawer/clawer
PYTHON=/Users/princetechs5/Documents/virtualenv/bin/python

# if [ ! -d ${WORKDIR} ]; then
#     WORKDIR=/Users/princetechs5/crawler/cr-clawer/clawer
# fi

# if [ ! -f ${PYTHON} ]; then
#     PYTHON=/Users/princetechs5/Documents/virtualenv/bin/python
# fi

cd ${WORKDIR}; ${PYTHON} manage.py $*
