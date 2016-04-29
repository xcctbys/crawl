#!/bin/sh

###
# Use to clone remote cr-clawer git repo to local.
###

ENV_PATH="config/env.sh"

source $ENV_PATH

if [[ ! -d $PROJECT_ROOT_PATH ]]; then
  mkdir -p $PROJECT_ROOT_PATH
  git clone -b $GIT_BRANCH "$GIT_USER@$GIT_REPO" $PROJECT_ROOT_PATH
else
  cd $PROJECT_ROOT_PATH
  git pull
fi
