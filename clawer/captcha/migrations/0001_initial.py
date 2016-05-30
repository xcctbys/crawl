# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Captcha',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('url', models.URLField()),
                ('category', models.IntegerField()),
                ('image_hash', models.CharField(max_length=32)),
                ('label_count', models.IntegerField(default=0)),
                ('add_datetime', models.DateTimeField(auto_now_add=True)),
            ], ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('url', models.CharField(max_length=1024)),
                ('max_number', models.IntegerField(default=0)),
            ], ),
        migrations.CreateModel(
            name='LabelLog',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=32)),
                ('ip', models.GenericIPAddressField()),
                ('add_datetime', models.DateTimeField(auto_now_add=True)),
                ('captcha', models.ForeignKey(to='captcha.Captcha')),
            ], ),
    ]
