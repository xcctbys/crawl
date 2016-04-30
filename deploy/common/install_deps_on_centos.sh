#!/bin/sh

###
# Use to init cr-clawer projects's deps on centos.
# Useage:
#   source install_deps_on_centos.sh
#   install_deps_on_centos
###

yum install -y gcc gcc-c++ blas-devel lapack-devel mysql-devel \
               python python-devel zlib-devel libjpeg-turbo-devel \
               libxml2 libxml2-devel libxslt libxslt-devel
