#!/bin/bash

PY=~/Documents/pyenv/dj18/bin/py.test
WORKDIR=~/Documents/gitroom/cr-clawer/clawer


cd ${WORKDIR}; $PY --durations=10 --pastebin=failed $* 
