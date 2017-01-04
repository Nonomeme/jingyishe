# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-03 07:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('question', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='count',
        ),
        migrations.AddField(
            model_name='course',
            name='popularity',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='course',
            name='rank',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='course',
            name='courseDate',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='expert',
            name='link',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='expert',
            name='tag',
            field=models.CharField(max_length=256),
        ),
    ]