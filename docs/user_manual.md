<h1 align="center">云爬虫用户手册</h1>

# 配置

## 生成器
## 下载器
## 解析器

# 部署

1. 远程登录跳板机

        ssh root@112.74.184.173

2. 克隆代码到跳板机

        # password: cr0044
        git clone -b csci cr@git.princetechs.com:/data/repos/cr-clawer.git

3. 配置及环境准备

        # 配置服务器列表
        vim /home/cr-clawer/deploy/config/production/servers.json

        # 添加如下内容
        {
          "webserver": {
            "hosts": ["172.16.80.5"]
          },
          "generatorservers": {
            "hosts": ["172.16.80.4"]
          },
          "downloaderservers": {
            "hosts": ["172.16.80.1", "172.16.80.2", "172.16.80.3"]
          },
          "structuresevers": {
            "hosts": ["172.16.20.3"]
          }
        }

        # 创建mongo数据库和用户

        # if not exist follow databases and users
        mongo --host dds-wz9a828f745eac341.mongodb.rds.aliyuncs.com --port 3717 -u root -p password123 --authenticationdatabase admin
        use default
        db.createuser({user: "clawer", pwd: "plkjplkj", roles: [{role: "readwrite", db: "default"}]})
        use log
        db.createuser({user: "clawer", pwd: "plkjplkj", roles: [{role: "readwrite", db: "log"}]})
        use source
        db.createuser({user: "clawer", pwd: "plkjplkj", roles: [{role: "readwrite", db: "source"}]})
        use structure
        db.createuser({user: "clawer", pwd: "plkjplkj", roles: [{role: "readwrite", db: "structure"}]})
        # else nothing

        # 制作本地python模块镜像源
        yum install python-pip
        pip install --upgrade pip setuptools
        pip download -r /root/cr-clawer/deploy/requirements/production.txt -d /root/cr-clawer/deploy/pypi


4. 自动化部署服务器

        # 部署所有服务器，通常在第一次部署环境时使用
        cd /root/cr-clawer/deploy && ./deploy all

        # 部署同一类型的服务器, 通常在动态扩展机器时使用
        # web:            web后台服务
        # generator:      生成器部署
        # downloader:     下载器部署
        # structure:      解析器部署
        cd /root/cr-clawer/deploy && ./deploy xxx

# 维护

1. 更新

        # 通常在发布新版本时使用，该操作会自动同步所有服务器代码且重启服务
        cd /root/cr-clawer/ && git checkout csci && git pull origin csci
        cd /root/cr-clawer/deploy && ./deploy upgrade
