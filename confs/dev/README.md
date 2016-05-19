# Set up local environment

## rqworker

./run_local.sh rq
./run_local.sh rq_down


## crontab

      */5    *    *    *    * cd /Users/princetechs5/crawler/cr-clawer/confs/dev;./bg_cmd.sh generator_install  # for generator
      *      *    *    *    * cd /Users/princetechs5/crawler/cr-clawer/confs/dev;./bg_cmd.sh generator_dispatch  # for generator

      */5    *    *    *    * cd /Users/princetechs5/crawler/cr-clawer/confs/dev;./bg_cmd.sh downloader_dispatch  # for downloader

      */10    *    *    *    * cd /Users/princetechs5/crawler/cr-clawer/confs/dev;./bg_cmd.sh crawlerproxyip  # for crawler proxy ip
      */5    *    *    *    * cd /Users/princetechs5/crawler/cr-clawer/confs/dev;./bg_cmd.sh crawlerproxyip_fast  # for round porxy ip fast
      */10    *    *    *    * cd /Users/princetechs5/crawler/cr-clawer/confs/dev;./bg_cmd.sh roundproxyip  # for round porxy ip
