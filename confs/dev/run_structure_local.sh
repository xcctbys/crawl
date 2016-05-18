#!/bin/bash

WORKDIR=~/Documents/gitroom/cr-clawer/clawer

GENERATOR_REDIS=redis://127.0.0.1

DJANGO_SETTINGS_MODULE="clawer.settings.local" rqworker --url ${GENERATOR_REDIS}  -v -P ${WORKDIR} structure:higher structure:high structure:normal structure:low
