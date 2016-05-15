#!/bin/bash

WORKDIR=/home/clawer/cr-clawer/clawer

REDIS_GENERATOR=redis://10.0.1.3/0

DJANGO_SETTINGS_MODULE="clawer.settings_cr" rqworker --url ${REDIS_GENERATOR}  -v -P ${WORKDIR} uri_super uri_high uri_medium uri_low

