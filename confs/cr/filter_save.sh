#!/bin/bash

WORKDIR="/home/clawer/cr-clawer/clawer"
PYTHON="/usr/local/bin/python"
LOCALDIR="/Users/princetechs/cr-clawer"

/usr/local/bin/redis-cli -h 127.0.0.1 -p 6379 -a pwd  bgsave
/usr/local/bin/mongofiles  put ${LOCALDIR}/dump.rdb