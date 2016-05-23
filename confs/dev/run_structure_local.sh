!/bin/bash

WORKDIR=/home/max/Documents/gitroom/cr-clawer/clawer

STRUCTURE_REDIS=redis://127.0.0.1

DJANGO_SETTINGS_MODULE="clawer.settings.local" rqworker --url ${STRUCTURE_REDIS}  -v -P ${WORKDIR} structure:higher structure:high structure:normal structure:low
