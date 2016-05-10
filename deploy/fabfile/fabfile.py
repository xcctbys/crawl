# -*- coding: utf-8 -*-

import json
from fabric.api import env, roles, run

with open("servers.json") as conf:
    env.roledefs = json.load(conf)

consts = {
    "PROJECT_DIR": "/home/clawer",
    "GIT_REPO_URL": "git.princetechs.com:/data/repos/cr-clawer.git",
    "GIT_BRANCH": "dev",
    "GIT_USER": "zhongyid",
    "GIT_PASSWORD": "zhongyid0033",
}


@roles("WebServer")
def deploy_web_server():
    _if_project_not_exist_clone()
    _install_deps()
    _run_web_service()


@roles("CaptchaServers")
def deploy_captcha_servers():
    pass


@roles("DownloaderServers")
def deploy_downloader_servers():
    pass


@roles("FilterServers")
def deploy_filter_servers():
    pass


@roles("GeneratorServers")
def deploy_genertor_servers():
    pass


@roles("MongoServers")
def deploy_mongo_servers():
    pass


@roles("MysqlServers")
def deploy_mysql_servers():
    pass


@roles("NginxServers")
def deploy_nginx_servers():
    pass


@roles("RedisServers")
def deploy_redis_servers():
    pass


@roles("StructureSevers")
def deploy_structure_servers():
    pass


def _if_project_not_exist_clone():
    run("sh scripts/clone_project.sh")


def _install_deps():
    run("sh ./scripts/install_deps.sh")


def _run_web_service():
    run("sh ./scripts/run_web_service.sh")
