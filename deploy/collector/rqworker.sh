#!/bin/bash

WORKDIR=~/crawler/cr-clawer/clawer
RQWORKER=~/Documents/virtualenv/bin/rqworker

DJANGO_SETTINGS_MODULE="clawer.settings_local" ${RQWORKER} --url redis://127.0.0.1/0  -v -P ${WORKDIR} uri_super uri_high uri_medium uri_low
