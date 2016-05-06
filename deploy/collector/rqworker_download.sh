#!/bin/bash

WORKDIR=/home/webapps/cr-crawler/cr-clawer/clawer

DJANGO_SETTINGS_MODULE="clawer.settings_local" rqworker --url redis://127.0.0.1/0  -v -P ${WORKDIR} down_super down_high down_medium down_low
