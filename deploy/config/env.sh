#!/bin/sh

###
# Confg cr-clawer enviroment variable.
###

# Use Fabric we need config fabfile path. Values in "../fabfile/{production.py | development.py | test.py}".
FABFILE="fabfile/production.py"

# Project root path. Note: Value must be absolute path.
PROJECT_ROOT_PATH="/home/clawer"

# Git
GIT_REPO="git.princetechs.com:/data/repos/cr-clawer.git"
GIT_USER="zhongyid"
GIT_BRANCH="dev"
