# Prequired

- Django 1.4.x
- Redis
- Memcached
- RQ


# Start Develop environment


## Install Mariadb in CentOS 7

      yum install -y mariadb*

## Install some python libs

Install python. Install virtualenv.

    cd ~/Documents/pyenv/
    virtualenv dj14

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
    ./run.sh rq


# Create Database on MySQL

       CREATE DATABASE `clawer` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

       #create user
       CREATE USER 'cacti'@'localhost' IDENTIFIED BY 'cacti';
       GRANT ALL ON *.* TO 'cacti'@'localhost';

       CREATE USER 'cacti'@'%' IDENTIFIED BY 'cacti';
       GRANT ALL ON *.* TO 'cacti'@'%';


# Crontab

      #############################
      # topologic #


      # 中证服务器配置
      ## master
      ### for root
      */5    *    *    *    * cd /home/webapps/nice-clawer/confs/cr;./bg_cmd.sh task_generator_install
      20     *    *    *    * cd /home/webapps/nice-clawer/confs/cr;./bg_cmd.sh clawer_monitor_hour
      40     3    *    *    * cd /home/webapps/nice-clawer/confs/cr;./bg_cmd.sh clawer_monitor_day
      */50   *    *    *    * cd /home/webapps/nice-clawer/sources/qyxy/structured/scripts/cr/; sh run.sh structured
      ### for nginx user
      */5    *    *    *    * cd /home/webapps/nice-clawer/confs/cr;./bg_cmd.sh task_dispatch
      30     *    *    *    * cd /home/webapps/nice-clawer/confs/cr;./bg_cmd.sh task_analysis_merge


      ##slave
      */5    *    *    *    * cd /home/webapps/nice-clawer/confs/cr;./bg_cmd.sh task_analysis --thread=2 --run=290
      30     *    *    *    * cd /home/webapps/nice-clawer/confs/cr;./shrink_tmp.sh



# Supervisor for Clawer worker

Run in China

      ## start download worker
      # mkdir /home/web_log/nice-clawer
      # chown -R nginx:nginx /home/web_log/nice-clawer
      # mkdir /data/clawer
      # chown -R nginx:nginx /data/clawer
      # mkdir /data/media
      # chown -R nginx:nginx /data/media

      ln -s /home/webapps/cr-clawer/confs/cr/supervisord
      chkconfig supervisord on
      service supervisord restart
