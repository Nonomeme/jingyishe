# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-03 07:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('question', '0002_auto_20170103_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='link',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='course',
            name='title',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='course',
            name='university',
            field=models.CharField(max_length=256),
        ),
    ]
