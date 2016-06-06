# Prequired

- Django 1.8
- Redis
- Memcached
- RQ


# How To Setup Develop environment


## Install MySQL

 in CentOS 7

      yum install -y mysql
      #or
      yum install -y mariadb*

in macos

     brew install mysql


## Install some python libs

Install python. Install virtualenv.

    cd ~/Documents/pyenv/
    virtualenv dj18

    cd ~/Documents/gitroom

    #clone code at here

    cd cr-clawer/clawer && ~/Documents/pyenv/dj14/bin/pip install -r requirements.txt

Migrate django db

    ./bg_cmd.sh migrate

Create super user. (admin:admin)

    ./bg_cmd.sh createsuperuser admin


Create two group in http://localhost:8000/admin/

    管理员
    开发者

Run server. Then visit http://localhost:8000/admin/

    ./run.sh app

Start RQ worker

    ./run.sh rq [Queue....]

For example:

    ./run.sh rq clawer download analysis


Start RQ worker for generator

    ./run.sh rq uri_super uri_high uri_medium uri_low


## Test Your code

cd conf

    cd cr-clawer/confs/dev

test it

    ./test.sh

use cmd to show help

    ./test.sh -h

## Create Database on MySQL

       CREATE DATABASE `clawer` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

       # create user
       CREATE USER 'cacti'@'localhost' IDENTIFIED BY 'cacti';
       GRANT ALL ON *.* TO 'cacti'@'localhost';

       CREATE USER 'cacti'@'%' IDENTIFIED BY 'cacti';
       GRANT ALL ON *.* TO 'cacti'@'%';


## Install Crontab

      #############################
      # topologic #

      ## master

      ### for root
      */5    *    *    *    * cd /Users/princetechs5/crawler/cr-clawer/confs/cr;./bg_cmd.sh generator_install  # for generator
      *      *    *    *    * cd /Users/princetechs5/crawler/cr-clawer/confs/cr;./bg_cmd.sh generator_dispatch  # for generator

      20     *    *    *    * cd /home/webapps/cr-clawer/confs/cr;./bg_cmd.sh clawer_monitor_hour
      40     3    *    *    * cd /home/webapps/cr-clawer/confs/cr;./bg_cmd.sh clawer_monitor_day
      */50   *    *    *    * cd /home/webapps/cr-clawer/sources/qyxy/structured/scripts/cr/; sh run.sh structured

      ### for nginx user
      */5    *    *    *    * cd /home/webapps/cr-clawer/confs/cr;./bg_cmd.sh task_dispatch
      30     *    *    *    * cd /home/webapps/cr-clawer/confs/cr;./bg_cmd.sh task_analysis_merge


      ##slave
      */5    *    *    *    * cd /home/webapps/cr-clawer/confs/cr;./bg_cmd.sh task_analysis --thread=2 --run=290
      30     *    *    *    * cd /home/webapps/cr-clawer/confs/cr;./shrink_tmp.sh



## Install Worker


      ## start download worker
      # mkdir /home/web_log/cr-clawer
      # chown -R nginx:nginx /home/web_log/cr-clawer
      # mkdir /data/clawer
      # chown -R nginx:nginx /data/clawer
      # mkdir /data/media
      # chown -R nginx:nginx /data/media

      ln -s /home/webapps/cr-clawer/confs/cr/supervisord
      chkconfig supervisord on
      service supervisord restart



# Program Dir

## clawer

this is main app.

## collector

About uri generator, download etc.

## structure

About analysis data, which from collector.

# storage

Used by collector and structure. It will store original data and middle data etc. Also it will contain some runtime log.

# html5helper

Some utils.
