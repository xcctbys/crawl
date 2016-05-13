#!/bin/sh

###
# Use to deploy cr-clawer project runtime enviroment.
###

FABRIC_BIN=`which fab`
ENV_PATH="config/env.sh"

############################  BASIC FUNCTIONS
msg() {
  printf '%b\n' "$1" >&2
}

success() {
  if [ "$ret" -eq '0' ]; then
    msg "\33[32m[✔]\33[0m ${1}${2}"
  fi
}

error() {
  msg "\33[31m[✘]\33[0m ${1}${2}"
  exit 1
}

############################  DEPLOY FUNCTIONS
copy_ssh_key_to_remote_servers() {

  ${FABRIC_BIN} -f ${FABFILE} -R WebServer,GeneratorServers,FilterServers,DownloaderServers,StructureSevers,CaptchaServers,MysqlServers,MongoServers,RedisServers,NginxServers ssh_key
}

deploy_web_server() {
  ${FABRIC_BIN} -f ${FABFILE} deploy_web_server
}

deploy_captcha_servers() {
  ${FABRIC_BIN} -f ${FABFILE} deploy_captcha_servers
}

deploy_downloader_servers() {
  ${FABRIC_BIN} -f ${FABFILE} deploy_downloader_servers
}

deploy_filter_servers() {
  ${FABRIC_BIN} -f ${FABFILE} deploy_filter_servers
}

deploy_genertor_servers() {
  ${FABRIC_BIN} -f ${FABFILE} deploy_genertor_servers
}

deploy_mongo_servers() {
  ${FABRIC_BIN} -f ${FABFILE} deploy_mongo_servers
}

deploy_mysql_servers() {
  ${FABRIC_BIN} -f ${FABFILE} deploy_mysql_servers
}

deploy_redis_servers() {
  ${FABRIC_BIN} -f ${FABFILE} deploy_redis_servers
}

deploy_structure_servers() {
  ${FABRIC_BIN} -f ${FABFILE} deploy_structure_servers
}

############################  CONTROL FUNCTIONS
main() {
  case "$1" in
    all)
      deploy_mongo_servers
      deploy_mysql_servers
      deploy_redis_servers
      deploy_web_server
      deploy_captcha_servers
      deploy_downloader_servers
      deploy_filter_servers
      deploy_genertor_servers
      deploy_structure_servers
      ;;
    web)
      deploy_web_server
      ;;
    captcha)
      deploy_captcha_servers
      ;;
    downloader)
      deploy_downloader_servers
      ;;
    filter)
      deploy_filter_servers
      ;;
    genertor)
      deploy_genertor_servers
      ;;
    mongo)
      deploy_mongo_servers
      ;;
    mysql)
      deploy_mysql_servers
      ;;
    redis)
      deploy_redis_servers
      ;;
    structure)
      deploy_structure_servers
      ;;
    sshkey)
      copy_ssh_key_to_remote_servers
      ;;
    help)
      useage
      ;;
    *)
      useage
      ;;
  esac
}

useage() {
  echo "Usage: ./deploy.sh {all|captcha|downloader|filter|genertor|mongo|mysql|redis|structure}"
  echo ""
  echo "        all:            所有环境部署"
  echo "        mongo:          MongoDB部署"
  echo "        mysql:          MySQL部署"
  echo "        redis:          Redis部署"
  echo "        web:            Web后台服务"
  echo "        filter:         防重器部署"
  echo "        captcha:        破解器部署"
  echo "        genertor:       生成器部署"
  echo "        downloader:     下载器部署"
  echo "        structure:      解析器部署"
  echo "        sshkey:         同步本地ssh pub key到远程服务器"
  echo ""
}

############################  MAIN
source $ENV_PATH

if [[ -z $FABRIC_BIN ]]; then
  error "Can't find fab command. Try pip install fabric."
elif [[ -z $FABFILE ]]; then
  error "FABFILE variable can't set. Please config it in config/env.sh."
else
  main $*
fi
