#!/usr/bin/env bash

############################  SETUP PARAMETERS
app_name='cr-clawer'
[ -z "$APP_PATH" ] && APP_PATH="$HOME/Projects/cr-clawer"
[ -z "$REPO_URI" ] && REPO_URI='zhongyid@git.princetechs.com:/data/repos/cr-clawer.git'
[ -z "$REPO_BRANCH" ] && REPO_BRANCH='dev'

############################  BASIC SETUP TOOLS
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

############################ SETUP FUNCTIONS
install_deps_on_centos() {
  for dep in $*; do
    yum install -y $dep
  done
  ret="$?"
  success "All deps is done."
}

init_mysql_root_password() {
  mysqladmin -u root password "plkj"
  ret="$?"
  success "Init mysql root password done."
}

eval_sql() {
  mysql -uroot -pplkj -e "$1"
}

create_mysql_dev_account() {
  eval_sql "CREATE USER 'cacti'@'localhost' IDENTIFIED BY 'cacti';"
  eval_sql "GRANT ALL ON *.* TO 'cacti'@'localhost';"
  eval_sql "CREATE USER 'cacti'@'%' IDENTIFIED BY 'cacti';"
  eval_sql "GRANT ALL ON *.* TO 'cacti'@'%';"
  ret="$?"
  success "Create mysql dev account 'cacti' done. Password is 'cacti' too."
}

create_mysql_dev_database() {
  db="$1"
  eval_sql "CREATE DATABASE $db DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
  ret="$?"
  success "Create mysql dev database $db done."
}

create_virtualenv() {
  path="$1"
  if [ ! -e $path ]; then
    rm -rf $path
  fi
  pip install virtualenv
  virtualenv $path
  ret="$?"
  success "Create virtualenv done."
}

easy_install_python_lib() {
  libs="$*"
  for lib in $libs; do
    easy_install $lib
  done
  ret="$?"
  success "Install $libs done."
}

pip_install_python_lib() {
  virtualenv_name=$1
  requirements_file=$2
  if [ -e $virtualenv_name ] && [ -e $requirements_file ]; then
    source $virtualenv_name/bin/activate
    pip install -r "$requirements_file"
  elif [ ! -e $virtualenv_name ]; then
    error "Can't find virtualenv."
  elif [ ! -e $requirements_file ]; then
    error "Can't find requirements file."
  fi
  ret="$?"
  success "Install projects python libs done."
}

clone_projects() {
  if [ -e $APP_PATH ]; then
    cd $APP_PATH
    git pull
  else
    git clone -b $REPO_BRANCH $REPO_URI $APP_PATH
  fi
  ret="$?"
  success "Clone projects $APP_PATH done."
}

change_dir_to_project() {
  dir=$1
  cd $dir
}

create_mysql_schem() {
  virtualenv_name=$1 
  if [ -e $virtualenv_name ]; then
    source $virtualenv_name/bin/active
    python manage.py migrate
  fi
}
############################ MAIN()
if [ "$(uname)" == "Darwin" ]; then
  init_mysql_root_password
  create_mysql_dev_account
  create_mysql_dev_database "clawer"
  easy_install_python_lib   "pip" \
                            "setuptools"
  clone_projects
  change_dir_to_project     "$APP_PATH/clawer"
  create_virtualenv         "dj18"
  pip_install_python_lib    "dj18" \
                            "requirements.txt"
  create_mysql_schem        "dj18"

  msg                       "\nThanks for installing $app_name."
  msg                       "© `date +%Y` http://www.princetechs.com"
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
  install_deps_on_centos    "gcc" \
                            "gcc-c++" \
                            "blas-devel" \
                            "lapack-devel" \
                            "mariadb" \
                            "mariadb-server" \
                            "mysql-devel" \
                            "python" \
                            "python-devel" \
                            "zlib-devel" \
                            "libjpeg-turbo-devel" \
                            "libxml2" \
                            "libxml2-devel" \
                            "libxslt" \
                            "libxslt-devel"

  init_mysql_root_password
  create_mysql_dev_account
  create_mysql_dev_database "clawer"
  easy_install_python_lib   "pip" \
                            "setuptools"
  clone_projects
  change_dir_to_project     "$APP_PATH/clawer"
  create_virtualenv         "dj18"
  pip_install_python_lib    "dj18" \
                            "requirements.txt"
  create_mysql_schem        "dj18"

  msg                       "\nThanks for installing $app_name."
  msg                       "© `date +%Y` http://www.princetechs.com"
else
  error "Don't support your platform. It's already support CentOS and Mac."
fi
