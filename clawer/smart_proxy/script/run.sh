WORKDIR=/home/webapps/cr-clawer/smart_proxy/ #指定哪个项目
PYTHON=/home/virtualenvs/dj18/bin/python #指定哪个python
function safe_run() #安全执行，加锁，设置时间，及运行django命令 python django-admin manage.py roundproxyip
{
    file="/tmp/structure_$1.lock"

    (
        flock -xn -w 10 200 || exit 1
        cd ${WORKDIR}; ${PYTHON} manage.py $*
    ) 200>${file}
}
time safe_run  $*