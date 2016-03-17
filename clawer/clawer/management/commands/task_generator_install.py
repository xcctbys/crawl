# coding=utf-8

from crontab import CronTab

from django.core.management.base import BaseCommand
from django.conf import settings

from html5helper.utils import wrapper_raven
from clawer.models import ClawerTaskGenerator, ClawerSetting, Clawer

import random
from optparse import make_option

                

class Command(BaseCommand):
    args = ""
    help = "Install generator to crontab."
    
    option_list = BaseCommand.option_list + (
        make_option('--foreign',
            dest = 'foreign',
            action = "store_true",
            default = False,
            help = 'Run task generators of foreigh'
        ),
    )
    
    def __init__(self):
        self.cron = CronTab(user=settings.CRONTAB_USER)
        self.is_foreign = False
    
    @wrapper_raven
    def handle(self, *args, **options):
        self.is_foreign = options["foreign"]
        self.install()
        
    def install(self):
        self._remove_offline()
        
        clawers = Clawer.objects.filter(status=Clawer.STATUS_ON)
        for clawer in clawers:
            clawer_setting = clawer.settings()
            
            if self.is_foreign and clawer_setting.prior != ClawerSetting.PRIOR_FOREIGN:
                continue
            if self.is_foreign is False and clawer_setting.prior == ClawerSetting.PRIOR_FOREIGN:
                continue
            
            try:
                task_generator = ClawerTaskGenerator.objects.filter(clawer=clawer).order_by("-id")[0]
            except:
                continue
                
            if self._test_alpha(task_generator) is False:
                continue
            if self._test_beta(task_generator) is False:
                continue
            if self._test_product(task_generator) is False:
                continue
            
            task_generator.status = ClawerTaskGenerator.STATUS_ON
            task_generator.save()
            
            print "success! generator %d, clawer %d" % (task_generator.id, clawer.id)
            #make old offline
            ClawerTaskGenerator.objects.filter(clawer_id=clawer.id, \
                status=ClawerTaskGenerator.STATUS_ON).exclude(id=task_generator.id).update(status=ClawerTaskGenerator.STATUS_OFF)
                
        #done
        self._save_cron()
        
    def _remove_offline(self):
        clawers = Clawer.objects.filter(status=Clawer.STATUS_OFF)
        
        for clawer in clawers:
            task_generator = clawer.runing_task_generator()
            if not task_generator:
                continue
            
            comment = self._task_generator_cron_comment(task_generator)
            self.cron.remove_all(comment=comment)
            
    def _task_generator_cron_comment(self, task_generator):
        return "clawer %d task generator" % task_generator.clawer_id            
        
    def _test_alpha(self, task_generator):
        path = task_generator.alpha_path()
        task_generator.write_code(path)
        return True
    
    def _test_beta(self, task_generator):
        user_cron = CronTab(user=settings.CRONTAB_USER)
        job = user_cron.new(command="/usr/bin/echo")
        job.setall(task_generator.cron.strip())
        if job.is_valid() == False:
            task_generator.cron = "%d * * * *" % random.randint(1, 59)
        
        return True
    
    def _test_product(self, task_generator):
        return self._try_install_crontab(task_generator)
        
    def _try_install_crontab(self, task_generator):
        comment = self._task_generator_cron_comment(task_generator)
        self.cron.remove_all(comment=comment)
        
        if task_generator.status == ClawerTaskGenerator.STATUS_OFF:
            return False
        
        prior = task_generator.clawer.settings().prior
        if self.is_foreign and prior != ClawerSetting.PRIOR_FOREIGN:
            return False
        
        cmd = "bg_cmd.sh"
        if prior == ClawerSetting.PRIOR_FOREIGN:
            cmd = "foreign_bg_cmd.sh"
        
        job = self.cron.new(command="cd %s; sh %s task_generator_run %d" % (settings.CRONTAB_HOME, cmd, task_generator.id), comment=comment)
        job.setall(task_generator.cron.strip())
        return True
    
    def _save_cron(self):
        self.cron.write_to_user(user=settings.CRONTAB_USER)
        