# -*- coding: utf-8 -*-

import os
import json
from fabric.api import env, roles, run, cd
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project
from fabric.contrib.files import append

with open("config/servers.json") as conf:
    env.roledefs = json.load(conf)

# Consts
REMOTE_PROJECT_PATH = "/home/webapps"

env.user = "root"
env.password = "plkj"


@roles("WebServer")
def deploy_web_server():
    # Rsync local project files to remote server.
    _rsync_project(local_project_path="~/Projects/cr-clawer",
                   remote_project_path=REMOTE_PROJECT_PATH)
    _add_crontab(crontab_path="collector/crontab.txt", mode="w")


@roles("CaptchaServers")
def deploy_captcha_servers():
    _rsync_project(local_project_path="~/Projects/cr-clawer",
                   remote_project_path=REMOTE_PROJECT_PATH)


@roles("DownloaderServers")
def deploy_downloader_servers():
    _rsync_project(local_project_path="~/Projects/cr-clawer",
                   remote_project_path=REMOTE_PROJECT_PATH)


@roles("FilterServers")
def deploy_filter_servers():
    _rsync_project(local_project_path="~/Projects/cr-clawer",
                   remote_project_path=REMOTE_PROJECT_PATH)


@roles("GeneratorServers")
def deploy_genertor_servers():
    _rsync_project(local_project_path="~/Projects/cr-clawer",
                   remote_project_path=REMOTE_PROJECT_PATH)


@roles("StructureSevers")
def deploy_structure_servers():
    _rsync_project(local_project_path="~/Projects/cr-clawer",
                   remote_project_path=REMOTE_PROJECT_PATH)


@roles("MongoServers")
def deploy_mongo_servers():
    _rsync_project(local_project_path="~/Projects/cr-clawer",
                   remote_project_path=REMOTE_PROJECT_PATH)
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
    # Install deps.
    run("yum install -y make wget gcc")

    if exists("redis-3.0.7.tar.gz"):
        # Already install redis, do nothing.
        pass
    else:
        # Get redis package.
        run("wget http://download.redis.io/releases/redis-3.0.7.tar.gz")
        run("tar xzvf redis-3.0.7.tar.gz")

        # Compile and install redis.
        with cd("redis-3.0.7"):
            with cd("deps"):
                run("make hiredis jemalloc linenoise lua")
            run("make")
            run("make install")

        # Stop fire wall and change system config.
        run("systemctl stop firewalld.service")
        run("systemctl disable firewalld.service")
        run("sysctl vm.overcommit_memory=1")
        run("sysctl -w fs.file-max=100000")

        # Start redis service on port 7001, 7002, 7003, 7004.
        # 7001 -> Generator rq
        # 7002 -> Downloader rq
        # 7003 -> Structure rq
        # 7004 -> Filter bitmap
        run("nohup redis-server redis-3.0.7/redis.conf --port 7001 >& /dev/null < /dev/null &", pty=False)
        run("nohup redis-server redis-3.0.7/redis.conf --port 7002 >& /dev/null < /dev/null &", pty=False)
        run("nohup redis-server redis-3.0.7/redis.conf --port 7003 >& /dev/null < /dev/null &", pty=False)
        run("nohup redis-server redis-3.0.7/redis.conf --port 7004 >& /dev/null < /dev/null &", pty=False)


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


def _rsync_project(local_project_path="~/Projects/cr-clawer", remote_project_path="/home/cr-clawer"):
    run("yum install -y rsync")
    rsync_project(local_dir=local_project_path, remote_dir=remote_project_path, exclude=".git")


def _add_crontab(crontab_path="", mode="a"):
    with open(crontab_path, "r") as cronfile:
        lines = cronfile.readlines()
    if mode == "a":
        run("crontab -l > /tmp/crondump")
        run("echo {0} >> /tmp/crondump".format(lines))
        run("crontab /tmp/crondump")
    else:
        run("crontab {0}".format("{0}/cr-clawer/deploy/{1}".format(REMOTE_PROJECT_PATH, crontab_path)))
