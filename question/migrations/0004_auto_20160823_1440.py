# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-23 06:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('question', '0003_auto_20160823_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personfollow',
            name='userFollower',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userFollower', to='question.User'),
        ),
    ]