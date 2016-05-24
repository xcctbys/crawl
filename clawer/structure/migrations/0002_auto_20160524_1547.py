# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parser',
            name='update_date',
            field=models.DateField(verbose_name=datetime.datetime(2016, 5, 24, 15, 47, 16, 356427)),
        ),
        migrations.AlterField(
            model_name='structureconfig',
            name='update_date',
            field=models.DateField(verbose_name=datetime.datetime(2016, 5, 24, 15, 47, 16, 357834)),
        ),
    ]
