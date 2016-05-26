# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smart_proxy', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proxyip',
            name='ip_port',
            field=models.CharField(max_length=24),
        ),
    ]
