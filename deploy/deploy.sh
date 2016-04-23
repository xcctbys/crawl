#!/bin/sh
FABRIC_BIN="/usr/local/bin/fab"
FABFILE="fabfile.py"

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

deploy_nginx_servers() {
  ${FABRIC_BIN} -f ${FABFILE} deploy_nginx_servers
}

deploy_redis_servers() {
  ${FABRIC_BIN} -f ${FABFILE} deploy_redis_servers
}

deploy_structure_servers() {
  ${FABRIC_BIN} -f ${FABFILE} deploy_structure_servers
}

useage() {
  echo "Usage: ./deploy.sh {all|captcha|downloader|filter|genertor|mongo|mysql|nginx|redis|structure}"
  echo ""
  echo "        all:            所有环境部署"
  echo "        mongo:          MongoDB部署"
  echo "        mysql:          MySQL部署"
  echo "        nginx:          Nginx部署"
  echo "        redis:          Redis部署"
  echo "        filter:         防重器部署"
  echo "        captcha:        破解器部署"
  echo "        genertor:       生成器部署"
  echo "        downloader:     下载器部署"
  echo "        structure:      解析器部署"
  echo ""
}

case "$1" in
  all)
    deploy_captcha_servers
    deploy_downloader_servers
    deploy_filter_servers
    deploy_genertor_servers
    deploy_mongo_servers
    deploy_mysql_servers
    deploy_nginx_servers
    deploy_redis_servers
    deploy_structure_servers
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
  nginx)
    deploy_nginx_servers
    ;;
  redis)
    deploy_nginx_servers
    ;;
  structure)
    deploy_structure_servers
    ;;
  help)
    useage
    ;;
  *)
    useage
    ;;
esac
