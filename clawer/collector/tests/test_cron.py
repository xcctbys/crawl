#encoding=utf-8
import json
import os
import datetime
import logging
import unittest

from django.test import TestCase
from django.conf import settings

from mongoengine.context_managers import switch_db
from collector.utils_cron import CronTab, CronItem, CronSlice, CronSlices

import subprocess

class TestCronSlices(TestCase):
    """docstring for TestCronSlice"""
    def setUp(self):
        TestCase.setUp(self)
        # line = "* * * * * ls -al # ls"
        # self.slices = CronSlice(line= line)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_is_valid(self):
        cron = "*/2 * * * *"
        flag = CronSlices.is_valid(cron)
        self.assertTrue(flag)
    def test_is_not_valid(self):
        crons = (
            "* *",
            " * * * * * *",
            "*/-1 * * * *",
            "* */70 * * *",
            )
        for cron in crons:
            self.assertFalse(CronSlices.is_valid(cron))


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

    def test_clean_render(self):
        my_cron  = CronTab()
        job = my_cron.new(command='echo `date`', comment='echo')
        job.minute.every(1)
        result = job.slices.clean_render()
        self.assertEqual(result, "* * * * *")

    def test_write_to_file(self):
        # line = "* * * * * echo `date` @2016-04-17 18:22:56.665851 # echo"
        my_cron  = CronTab()
        job = my_cron.new(command='echo `date`', comment='echo')
        job.minute.every(1)
        my_cron.write( '/tmp/output.tab' )
        self.assertTrue(True)

    def test_write_to_file_with_same_comment(self):
        my_cron  = CronTab()
        job = my_cron.new(command='ls -al', comment='ls')
        my_cron.write( '/tmp/output.tab' )
        job2 = my_cron.new(command='ls -l', comment='ls')
        job2.enable(False)
        my_cron.write( '/tmp/output.tab' )

        crons = my_cron.find_comment('ls')
        count = 0
        for cron in crons:
            count+=1
        self.assertEqual(count, 2)

    def test_change_enable_cron_to_disable(self):
        my_cron  = CronTab()
        my_cron.read('/tmp/output.tab' )
        crons = my_cron.find_comment('ls')
        for cron in crons:
            if cron.is_enabled():
                cron.enable(False)
        my_cron.write('/tmp/output.tab')

        test_cron = CronTab()
        test_cron.read('/tmp/output.tab' )
        crons = test_cron.find_comment('ls')
        for cron in crons:
            self.assertFalse(cron.is_enabled())


    def test_read_from_file(self):
        my_cron  = CronTab()
        my_cron.read('/tmp/output.tab' )
        cron = my_cron.find_comment('echo')
        for result in cron:
            print result.last_run
            self.assertEqual(result.command, "echo `date`")
        self.assertTrue(cron)

