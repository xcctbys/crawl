# -*- coding: utf-8 -*-

import os
import json
from fabric.api import env, roles, run
from fabric.contrib.project import rsync_project
from fabric.contrib.files import append

with open("config/servers.json") as conf:
    env.roledefs = json.load(conf)

# Consts
COMMON_PATH = "../common"

env.user = "root"
env.password = "plkj"


@roles("WebServer")
def deploy_web_server():
    _copy_project(local_project_path="~/Projects/cr-clawer",
                  remote_project_path="/home/webapps")


@roles("CaptchaServers")
def deploy_captcha_servers():
    _copy_project(local_project_path="~/Projects/cr-clawer",
                  remote_project_path="/home/webapps")


@roles("DownloaderServers")
def deploy_downloader_servers():
    _copy_project(local_project_path="~/Projects/cr-clawer",
                  remote_project_path="/home/webapps")


@roles("FilterServers")
def deploy_filter_servers():
    _copy_project(local_project_path="~/Projects/cr-clawer",
                  remote_project_path="/home/webapps")


@roles("GeneratorServers")
def deploy_genertor_servers():
    _copy_project(local_project_path="~/Projects/cr-clawer",
                  remote_project_path="/home/webapps")


@roles("StructureSevers")
def deploy_structure_servers():
    _copy_project(local_project_path="~/Projects/cr-clawer",
                  remote_project_path="/home/webapps")


@roles("MongoServers")
def deploy_mongo_servers():
    _copy_project(local_project_path="~/Projects/cr-clawer",
                  remote_project_path="/home/webapps")
    run("cd /home/webapps/cr-clawer && cp deploy/mongo/mongodb.repo /etc/yum.repos.d/")
    run("yum -y update")
    run("yum -y install mongodb-org mongodb-org-server")
    run("systemctl start mongod")
    run("systemctl status mongod")


@roles("MysqlServers")
def deploy_mysql_servers():
    pass


@roles("NginxServers")
def deploy_nginx_servers():
    pass


@roles("RedisServers")
def deploy_redis_servers():
    pass


def ssh_key(key_file="~/.ssh/id_rsa.pub"):
    key_text = _read_ssh_pub_key(key_file)
    run("[ -d ~/.ssh ] || mkdir -p ~/.ssh")
    append('~/.ssh/authorized_keys', key_text)


#####################
# Internal Function #
#####################
def _read_ssh_pub_key(key_file):
    key_file = os.path.expanduser(key_file)
    if not key_file.endswith('pub'):
        raise RuntimeWarning('Trying to push non-public part of key pair')
    with open(key_file) as f:
        return f.read()


def _copy_project(local_project_path="~/Projects/cr-clawer", remote_project_path="/home/cr-clawer"):
    run("yum install -y rsync")
    rsync_project(local_dir=local_project_path, remote_dir=remote_project_path, exclude=".git")
