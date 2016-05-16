#!/bin/bash

WORKDIR=/home/clawer/cr-clawer/clawer

GENERATOR_REDIS=redis://10.0.1.3/1

DJANGO_SETTINGS_MODULE="clawer.settings_cr" rqworker --url ${GENERATOR_REDIS}  -v -P ${WORKDIR} uri_super uri_high uri_medium uri_low

