<h1 align="center">云爬虫用户手册</h1>

### 部署

1. 远程登录跳板机

```
ssh root@112.74.184.173
```

2. 克隆代码到跳板机

```
# Password: cr0044
git clone cr@git.princetechs.com:/data/repos/cr-clawer.git
```

3. 配置及环境准备

```
# 配置服务器列表
vim /home/cr-clawer/deploy/config/production/servers.json

# 添加如下内容
    {
      "WebServer": {
        "hosts": ["172.16.80.5"]
      },
      "GeneratorServers": {
        "hosts": ["172.16.80.4"]
      },
      "DownloaderServers": {
        "hosts": ["172.16.80.1", "172.16.80.2", "172.16.80.3"]
      },
      "StructureSevers": {
        "hosts": ["172.16.20.3"]
      }
    }

# 创建Mongo数据库和用户

mongo --host dds-wz9a828f745eac341.mongodb.rds.aliyuncs.com --port 3717 -u root -p Password123 --authenticationDatabase admin

use default
db.createUser({user: "clawer", pwd: "plkjplkj", roles: [{role: "readWrite", db: "default"}]})

use log
db.createUser({user: "clawer", pwd: "plkjplkj", roles: [{role: "readWrite", db: "log"}]})

use source
db.createUser({user: "clawer", pwd: "plkjplkj", roles: [{role: "readWrite", db: "source"}]})

use structure
db.createUser({user: "clawer", pwd: "plkjplkj", roles: [{role: "readWrite", db: "structure"}]})

```

4. 自动化部署服务器

```
cd /home/cr-clawer/deploy
./deploy all
```
