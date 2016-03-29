# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Clawer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('info', models.CharField(max_length=1024)),
                ('customer', models.CharField(max_length=128, null=True, blank=True)),
                ('status', models.IntegerField(default=1, choices=[(1, '\u542f\u7528'), (2, '\u4e0b\u7ebf')])),
                ('add_datetime', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ClawerAnalysis',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.TextField()),
                ('status', models.IntegerField(default=1, choices=[(1, '\u542f\u7528'), (2, '\u4e0b\u7ebf')])),
                ('add_datetime', models.DateTimeField(auto_now_add=True)),
                ('clawer', models.ForeignKey(to='clawer.Clawer')),
            ],
        ),
        migrations.CreateModel(
            name='ClawerAnalysisLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=0, choices=[(1, '\u5931\u8d25'), (2, '\u6210\u529f')])),
                ('failed_reason', models.CharField(max_length=10240, null=True, blank=True)),
                ('hostname', models.CharField(max_length=16, null=True, blank=True)),
                ('result', models.TextField(null=True, blank=True)),
                ('add_datetime', models.DateTimeField(auto_now_add=True)),
                ('analysis', models.ForeignKey(to='clawer.ClawerAnalysis')),
                ('clawer', models.ForeignKey(to='clawer.Clawer')),
            ],
        ),
        migrations.CreateModel(
            name='ClawerDayMonitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.DateField()),
                ('bytes', models.IntegerField(default=0)),
                ('is_exception', models.BooleanField(default=False)),
                ('add_datetime', models.DateTimeField(auto_now_add=True)),
                ('clawer', models.ForeignKey(to='clawer.Clawer')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='ClawerDownloadLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=0, choices=[(1, '\u5931\u8d25'), (2, '\u6210\u529f')])),
                ('failed_reason', models.CharField(max_length=10240, null=True, blank=True)),
                ('content_bytes', models.IntegerField(default=0)),
                ('content_encoding', models.CharField(max_length=32, null=True, blank=True)),
                ('hostname', models.CharField(max_length=16, null=True, blank=True)),
                ('spend_time', models.IntegerField(default=0)),
                ('add_datetime', models.DateTimeField(auto_now=True)),
                ('clawer', models.ForeignKey(to='clawer.Clawer')),
            ],
        ),
        migrations.CreateModel(
            name='ClawerGenerateLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=0, choices=[(1, '\u5931\u8d25'), (2, '\u6210\u529f')])),
                ('failed_reason', models.CharField(max_length=10240, null=True, blank=True)),
                ('content_bytes', models.IntegerField(default=0)),
                ('spend_msecs', models.IntegerField(default=0)),
                ('hostname', models.CharField(max_length=16, null=True, blank=True)),
                ('add_datetime', models.DateTimeField(auto_now=True)),
                ('clawer', models.ForeignKey(to='clawer.Clawer')),
            ],
        ),
        migrations.CreateModel(
            name='ClawerHourMonitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hour', models.DateTimeField()),
                ('bytes', models.IntegerField(default=0)),
                ('is_exception', models.BooleanField(default=False)),
                ('add_datetime', models.DateTimeField(auto_now_add=True)),
                ('clawer', models.ForeignKey(to='clawer.Clawer')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='ClawerSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dispatch', models.IntegerField(default=100, verbose_name='\u6bcf\u6b21\u5206\u53d1\u4e0b\u8f7d\u4efb\u52a1\u6570')),
                ('analysis', models.IntegerField(default=200, verbose_name='\u6bcf\u6b21\u5206\u6790\u4efb\u52a1\u6570')),
                ('proxy', models.TextField(null=True, blank=True)),
                ('cookie', models.TextField(null=True, blank=True)),
                ('download_engine', models.CharField(default=b'requests', max_length=16, choices=[(b'requests', b'REQUESTS'), (b'phantomjs', b'PHANTOMJS'), (b'selenium', b'SELENIUM')])),
                ('download_js', models.TextField(null=True, blank=True)),
                ('prior', models.IntegerField(default=0)),
                ('last_update_datetime', models.DateTimeField(auto_now=True)),
                ('report_mails', models.CharField(max_length=256, null=True, blank=True)),
                ('add_datetime', models.DateTimeField(auto_now_add=True)),
                ('clawer', models.ForeignKey(to='clawer.Clawer')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='ClawerTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uri', models.CharField(max_length=1024)),
                ('cookie', models.CharField(max_length=1024, null=True, blank=True)),
                ('args', models.CharField(max_length=1024, null=True, blank=True)),
                ('status', models.IntegerField(default=1, choices=[(1, '\u65b0\u589e'), (2, '\u8fdb\u884c\u4e2d'), (3, '\u4e0b\u8f7d\u5931\u8d25'), (4, '\u4e0b\u8f7d\u6210\u529f'), (5, '\u5206\u6790\u5931\u8d25'), (6, '\u5206\u6790\u6210\u529f')])),
                ('store', models.CharField(max_length=512, null=True, blank=True)),
                ('add_datetime', models.DateTimeField(auto_now_add=True)),
                ('clawer', models.ForeignKey(to='clawer.Clawer')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='ClawerTaskGenerator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.TextField()),
                ('cron', models.CharField(max_length=128)),
                ('status', models.IntegerField(default=1, choices=[(1, 'alpha'), (2, 'beta'), (3, 'production'), (4, '\u542f\u7528'), (5, '\u4e0b\u7ebf'), (6, '\u6d4b\u8bd5\u5931\u8d25')])),
                ('add_datetime', models.DateTimeField(auto_now_add=True)),
                ('clawer', models.ForeignKey(to='clawer.Clawer')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Logger',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(max_length=64)),
                ('title', models.CharField(max_length=512)),
                ('content', models.TextField()),
                ('from_ip', models.GenericIPAddressField()),
                ('add_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nickname', models.CharField(max_length=64)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='clawertask',
            name='task_generator',
            field=models.ForeignKey(blank=True, to='clawer.ClawerTaskGenerator', null=True),
        ),
        migrations.AddField(
            model_name='clawergeneratelog',
            name='task_generator',
            field=models.ForeignKey(to='clawer.ClawerTaskGenerator'),
        ),
        migrations.AddField(
            model_name='clawerdownloadlog',
            name='task',
            field=models.ForeignKey(to='clawer.ClawerTask'),
        ),
        migrations.AddField(
            model_name='claweranalysislog',
            name='task',
            field=models.ForeignKey(to='clawer.ClawerTask'),
        ),
    ]
