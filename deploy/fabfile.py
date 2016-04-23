# -*- coding: utf-8 -*-

import json
from fabric.api import env, roles

with open("servers.json") as conf:
    env.roledefs = json.load(conf)


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
