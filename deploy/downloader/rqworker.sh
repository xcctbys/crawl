#!/bin/bash

WORKDIR=/home/clawer/cr-clawer/clawer

DJANGO_SETTINGS_MODULE="clawer.settings_cr" rqworker --url redis://10.0.1.3/2  -v -P ${WORKDIR} down_super down_high down_mid down_low
