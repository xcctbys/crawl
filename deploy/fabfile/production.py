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
MYSQL_ROOT_PASSWORD = "plkjplkj"
MYSQL_PROJECT_DATABASE = "clawer"
MYSQL_PROJECT_USER = "cacti"
MYSQL_PROJECT_PASSWORD = "cacti"

env.user = "root"
env.password = "P@ssw0rd2015"


@roles("WebServer")
def deploy_web_server():
    # Rsync local project files to remote server.
    _rsync_project(local_project_path="~/Projects/cr-clawer",
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
    _rsync_project(local_project_path="~/Projects/cr-clawer",
                   remote_project_path=REMOTE_PROJECT_PATH)
    _install_project_deps()


@roles("DownloaderServers")
def deploy_downloader_servers():
    _rsync_project(local_project_path="~/Projects/cr-clawer",
                   remote_project_path=REMOTE_PROJECT_PATH)
    _install_project_deps()


@roles("FilterServers")
def deploy_filter_servers():
    _rsync_project(local_project_path="~/Projects/cr-clawer",
                   remote_project_path=REMOTE_PROJECT_PATH)
    _install_project_deps()


@roles("CaptchaServers")
def deploy_captcha_servers():
    _rsync_project(local_project_path="~/Projects/cr-clawer",
                   remote_project_path=REMOTE_PROJECT_PATH)


@roles("StructureSevers")
def deploy_structure_servers():
    _rsync_project(local_project_path="~/Projects/cr-clawer",
                   remote_project_path=REMOTE_PROJECT_PATH)


@roles("MongoServers")
def deploy_mongo_servers():

    # Configure the package management system(yum).
    repo_path = "/etc/yum.repos.d/mongodb-org-3.2.repo"
    repo = """[mongodb-org-3.2]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/3.2/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-3.2.asc
"""

    if not exists(repo_path):
        append(repo_path, repo)

    # Install mongodb and all libs.
    run("yum install -y mongodb-org")

    run("chown -R mongod:mongod /var/lib/mongo")

    # Start mongodb server and Add self turn on.
    run("service mongod start")
    run("chkconfig mongod on")

    # Stop fire wall and change system config.
    # TODO: Add iptables, because it's unsafe.
    run("systemctl stop firewalld.service")
    run("systemctl disable firewalld.service")


@roles("MysqlServers")
def deploy_mysql_servers():
    if not exists("/var/run/mariadb/mariadb.pid"):
        # Install mariadb and all libs.
        run("yum install -y mariadb-*")

        # Start mariadb server and add self turn on.
        run("systemctl start mariadb")
        run("systemctl enable mariadb")
        run("mysqladmin -u root password {0}".format(MYSQL_ROOT_PASSWORD))

        # Create project database.
        sql = "CREATE DATABASE {0} DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;"
        _execute_in_mysql(sql.format(MYSQL_PROJECT_DATABASE))

        # Create project user and grant all privileges of the project database to the user.
        sql = "CREATE USER '{0}'@'localhost' IDENTIFIED BY '{1}';GRANT ALL ON {2}.* TO 'cacti'@'localhost';CREATE USER '{0}'@'%' IDENTIFIED BY '{1}';GRANT ALL ON {2}.* TO 'cacti'@'%';FLUSH PRIVILEGES;"
        _execute_in_mysql(sql.format(MYSQL_PROJECT_USER, MYSQL_PROJECT_PASSWORD, MYSQL_PROJECT_DATABASE))

        # Stop fire wall and change system config.
        # TODO: Add iptables, because it's unsafe.
        run("systemctl stop firewalld.service")
        run("systemctl disable firewalld.service")


@roles("NginxServers")
def deploy_nginx_servers():
    pass


@roles("RedisServers")
def deploy_redis_servers():
    # Install deps.
    run("yum install -y make wget gcc")

    if not exists("redis-3.0.7.tar.gz"):
        # Already install redis, do nothing.
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
    # TODO: Add iptables, because it's unsafe.
    run("systemctl stop firewalld.service")
    run("systemctl disable firewalld.service")

    # Redis system configs.
    run("sysctl vm.overcommit_memory=1")
    run("sysctl -w fs.file-max=100000")

    # Create redis configs dir.
    run("mkdir -p /etc/redis")

    # Create redis data dir.
    run("mkdir -p /var/db/redis/7001")
    run("mkdir -p /var/db/redis/7002")
    run("mkdir -p /var/db/redis/7003")
    run("mkdir -p /var/db/redis/7004")

    # rsync config file.
    _rsync_project(local_project_path="config/redis", remote_project_path="/root/")
    run("yes | cp -r redis/redis /etc/redis/")
    run("yes | cp -r redis/init.d/ /etc/init.d/")
    run("yes | cp -r redis/system/ /etc/systemd/system/")

    # Add self turn on.
    run("chkconfig redis_7001 on")
    run("chkconfig redis_7002 on")
    run("chkconfig redis_7003 on")
    run("chkconfig redis_7004 on")

    # Start redis service on port 7001, 7002, 7003, 7004.
    # 7001 -> Generator rq
    # 7002 -> Downloader rq
    # 7003 -> Structure rq
    # 7004 -> Filter bitmap
    run("service redis_7001 start")
    run("service redis_7002 start")
    run("service redis_7003 start")
    run("service redis_7004 start")

    # Clear
    run("rm -rf /root/redis")


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
        run("crontab {0}/cr-clawer/deploy/{1}".format(REMOTE_PROJECT_PATH, crontab_path))


def _execute_in_mysql(sql):
    run('mysql -u{0} -p{1} -e "{2}"'.format("root", MYSQL_ROOT_PASSWORD, sql))


def _install_project_deps():

    # Install all projects deps, such as python-devel, mysql-devel and pip, setuptools ...
    run("yum install -y wget python-devel mysql-devel gcc gcc-c++ blas-devel \
        lapack-devel libxml2 libxml2-devel libxslt libxslt-devel")
    PIP = "pip install --no-index -f pypi"
    with cd("{0}/cr-clawer/deploy".format(REMOTE_PROJECT_PATH)):
        run("{0} pip setuptools".format(PIP))
        run("{0} -r {1}".format(PIP, "requirements/production.txt"))
