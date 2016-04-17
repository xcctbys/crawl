#encoding=utf-8
import json
import os
import datetime
import logging
import unittest

from django.test import TestCase
from django.conf import settings

from mongoengine.context_managers import switch_db
from collector.utils_cron import CronTab, CronItem

import subprocess

class TestCronItem(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        line = "* * * * * ls -al # ls"
        # self.cronitem = CronItem(line= line)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_construct(self):
        item = CronItem(line='noline')
        self.assertTrue(item.is_enabled())
        with self.assertRaises(UnboundLocalError):
            item.delete()
        item.command = str('nothing')
        self.assertEqual(item.render(), '* * * * * nothing')

    # def test_is_valid(self):
    #     valid = self.cronitem.is_valid()
    #     self.assertTrue(valid)

    # def test_render(self):
    #     render = self.cronitem.render()
    #     print render
    #     self.assertEqual(render, "* * * * * ls -al # ls")

class TestCrontab(TestCase):
    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_write_to_file(self):
        # line = "* * * * * echo `date` @2016-04-17 18:22:56.665851 # echo"
        my_cron  = CronTab()
        job = my_cron.new(command='echo `date`', comment='echo')
        job.minute.every(1)
        my_cron.write( '/tmp/output.tab' )
        self.assertTrue(True)

    def test_read_from_file(self):
        my_cron  = CronTab()
        my_cron.read('/tmp/output.tab' )
        cron = my_cron.find_comment('echo')
        for result in cron:
            print result.last_run
            self.assertEqual(result.command, "echo `date`")
        self.assertTrue(cron)

