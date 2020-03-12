# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-03-12 03:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='streamconfiguration',
            name='mobile_mountpoint',
            field=models.CharField(default='/mobile', max_length=40),
        ),
        migrations.AddField(
            model_name='streamconfiguration',
            name='proxy_url',
            field=models.CharField(blank=True, default=None, max_length=70, null=True),
        ),
        migrations.AlterField(
            model_name='streamconfiguration',
            name='priority_offline',
            field=models.IntegerField(default=3, verbose_name='Bed Priority'),
        ),
        migrations.AlterField(
            model_name='streamconfiguration',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]
