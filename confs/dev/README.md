# Set up local environment

## rqworker

./run_local.sh rq
./run_local.sh rq_down


## crontab

      */5    *    *    *    * cd /Users/princetechs5/crawler/cr-clawer/confs/dev;./bg_cmd.sh generator_install  # for generator
      *      *    *    *    * cd /Users/princetechs5/crawler/cr-clawer/confs/dev;./bg_cmd.sh generator_dispatch  # for generator
