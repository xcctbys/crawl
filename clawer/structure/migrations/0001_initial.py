# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Parser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parser_id', models.CharField(unique=True, max_length=100)),
                ('python_script', models.TextField()),
                ('update_date', models.DateField(verbose_name=datetime.datetime(2016, 5, 24, 16, 23, 40, 269928))),
            ],
        ),
        migrations.CreateModel(
            name='StructureConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('job_copy_id', models.CharField(unique=True, max_length=100)),
                ('update_date', models.DateField(verbose_name=datetime.datetime(2016, 5, 24, 16, 23, 40, 270560))),
                ('job', models.OneToOneField(to='storage.Job')),
                ('parser', models.OneToOneField(to='structure.Parser')),
            ],
        ),
    ]
