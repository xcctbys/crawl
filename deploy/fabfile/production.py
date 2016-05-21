# -*- coding: utf-8 -*-

import os
import time
import json
from fabric.api import env, roles, run, cd
from fabric.contrib.project import rsync_project
from fabric.contrib.files import append, exists

with open("config/production/servers.json") as conf:
    env.roledefs = json.load(conf)

# Consts
LOCAL_PROJECT_PATH = "/root/cr-clawer"
REMOTE_PROJECT_PATH = "/home/webapps"

env.user = "root"
env.password = "P@ssw0rd2015"


@roles("WebServer")
def deploy_web_server():
    # Create folder structure
    _create_used_folders()

    # Rsync local project files to remote server.
    _rsync_project(local_project_path=LOCAL_PROJECT_PATH,
                   remote_project_path=REMOTE_PROJECT_PATH)

    _install_project_deps()

    # Install memcached
    run("yum install -y memcached")
    run("service memcached start")
    run("chkconfig memcached on")

    # Create web log folder
    run("mkdir -p /home/logs/cr-clawer")
    run("chown -R nginx:nginx /home/logs/cr-clawer")

    # Start web server on port 4000
    _supervisord("web")

    # Install nginx and start nginx server and proxy 127.0.0.1:4000.
    run("yum install epel-release")
    run("yum install nginx")
    with cd("{0}/cr-clawer/deploy/".format(REMOTE_PROJECT_PATH)):
        run("yes | cp -rf config/production/cr-clawer.conf /etc/nginx/conf.d/cr-clawer.conf")
    run("service nginx start")
    run("chkconfig nginx on")

    # Add generator and downloader's crontab
    _add_crontab("web/crontab.txt", "w")


@roles("GeneratorServers")
def deploy_generator_servers():
    # Create folder structure
    _create_used_folders()

    # Rsync local project files to remote server.
    _rsync_project(local_project_path=LOCAL_PROJECT_PATH,
                   remote_project_path=REMOTE_PROJECT_PATH)

    _install_project_deps()

    # Use supervisor to monitor rq workers.
    _supervisord("generator")


@roles("DownloaderServers")
def deploy_downloader_servers():
    # Create folder structure
    _create_used_folders()

    # Rsync local project files to remote server.
    _rsync_project(local_project_path=LOCAL_PROJECT_PATH,
                   remote_project_path=REMOTE_PROJECT_PATH)
    _install_project_deps()

    # Use supervisor to monitor rq workers.
    _supervisord("downloader")


@roles("StructureSevers")
def deploy_structure_servers():
    # Create folder structure
    _create_used_folders()

    # Rsync local project files to remote server.
    _rsync_project(local_project_path=LOCAL_PROJECT_PATH,
                   remote_project_path=REMOTE_PROJECT_PATH)

    _install_project_deps()

    # Use supervisor to monitor rq workers.
    _supervisord("structure")


def ssh_key(key_file="~/.ssh/id_rsa.pub"):
    key_text = _read_ssh_pub_key(key_file)
    run("[ -d ~/.ssh ] || mkdir -p ~/.ssh")
    append('~/.ssh/authorized_keys', key_text)


def start():
    _start()


def stop():
    _stop()


def upgrade():
    # Rsync local project files to remote server.
    _rsync_project(local_project_path=LOCAL_PROJECT_PATH,
                   remote_project_path=REMOTE_PROJECT_PATH)

    # Restart Services.
    _restart()


###################
# Internal Function
def _read_ssh_pub_key(key_file):
    key_file = os.path.expanduser(key_file)
    # Check is it a pub key.
    if not key_file.endswith('pub'):
        raise RuntimeWarning('Trying to push non-public part of key pair')
    with open(key_file) as f:
        return f.read()


def _rsync_project(local_project_path=LOCAL_PROJECT_PATH, remote_project_path="/home/cr-clawer"):
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
        run("crontab {0}/cr-clawer/deploy/{1}".format(REMOTE_PROJECT_PATH, crontab_path))


def _install_project_deps():

    # Install all projects deps, such as python-devel, mysql-devel and pip, setuptools ...
    run("yum install -y wget python-devel python-pip mysql-devel gcc gcc-c++ blas-devel \
        lapack-devel libxml2 libxml2-devel libxslt libxslt-devel")
    PIP = "pip install --no-index -f pypi"
    with cd("{0}/cr-clawer/deploy".format(REMOTE_PROJECT_PATH)):
        run("{0} --upgrade pip setuptools".format(PIP))
        run("{0} -r {1}".format(PIP, "requirements/production.txt"))


def _create_used_folders():
    # Create project folder
    run("mkdir -p {0}".format(REMOTE_PROJECT_PATH))

    # Create log folder
    run("mkdir -p /home/logs")


def _supervisord(server):
    with cd("{0}/cr-clawer/deploy".format(REMOTE_PROJECT_PATH)):
        run("rm -rf /etc/supervisord.conf")
        run("yes | cp {0}/supervisord.conf /etc/supervisord.conf".format(server))
        if not exists("/etc/systemd/system/supervisord.service"):
            run("yes | cp config/production/supervisord.service /etc/systemd/system/")
    run("service supervisord start")
    run("chkconfig supervisord on")


def _start():
    run("service supervisord start")
    if exists("/etc/nginx/conf.d/cr-clawer.conf"):
        run("service nginx start")


def _stop():
    run("service supervisord stop")
    if exists("/etc/nginx/conf.d/cr-clawer.conf"):
        run("service nginx stop")


def _restart():
    run("service supervisord stop")
    time.sleep(2)
    run("service supervisord start")

    if exists("/etc/nginx/conf.d/cr-clawer.conf"):
        run("service nginx stop")
        time.sleep(2)
        run("service nginx start")
