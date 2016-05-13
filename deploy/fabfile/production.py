# -*- coding: utf-8 -*-

import os
import json
from fabric.api import env, roles, run, cd
from fabric.contrib.project import rsync_project
from fabric.contrib.files import append

with open("config/production/servers.json") as conf:
    env.roledefs = json.load(conf)

# Consts
LOCAL_PROJECT_PATH = "/root/cr-clawer"
REMOTE_PROJECT_PATH = "/home/webapps"
MYSQL_ROOT_PASSWORD = "plkjplkj"
MYSQL_PROJECT_DATABASE = "clawer"
MYSQL_PROJECT_USER = "cacti"
MYSQL_PROJECT_PASSWORD = "cacti"

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

    # Install nginx and start nginx server.
    run("yum install epel-release")
    run("yum install nginx")
    with cd("{0}/cr-clawer/deploy/".format(REMOTE_PROJECT_PATH)):
        run("yes | cp -rf config/nginx.conf /etc/nginx/nginx.conf")
    run("service nginx start")
    run("chkconfig nginx on")


@roles("GeneratorServers")
def deploy_genertor_servers():
    # Create folder structure
    _create_used_folders()

    # Rsync local project files to remote server.
    _rsync_project(local_project_path=LOCAL_PROJECT_PATH,
                   remote_project_path=REMOTE_PROJECT_PATH)

    _install_project_deps()


@roles("DownloaderServers")
def deploy_downloader_servers():
    # Create folder structure
    _create_used_folders()

    # Rsync local project files to remote server.
    _rsync_project(local_project_path=LOCAL_PROJECT_PATH,
                   remote_project_path=REMOTE_PROJECT_PATH)
    _install_project_deps()


@roles("StructureSevers")
def deploy_structure_servers():
    # Create folder structure
    _create_used_folders()

    # Rsync local project files to remote server.
    _rsync_project(local_project_path=LOCAL_PROJECT_PATH,
                   remote_project_path=REMOTE_PROJECT_PATH)


@roles("CaptchaServers")
def deploy_captcha_servers():
    _rsync_project(local_project_path=LOCAL_PROJECT_PATH,
                   remote_project_path=REMOTE_PROJECT_PATH)


def ssh_key(key_file="~/.ssh/id_rsa.pub"):
    key_text = _read_ssh_pub_key(key_file)
    run("[ -d ~/.ssh ] || mkdir -p ~/.ssh")
    append('~/.ssh/authorized_keys', key_text)


#####################
# Internal Function #
#####################
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
    run("mkdir -p /home/web_log")
