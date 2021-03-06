# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-03-11 13:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shows', '0007_auto_20171119_1722'),
    ]

    operations = [
        migrations.CreateModel(
            name='StreamConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=70)),
                ('host', models.CharField(max_length=80)),
                ('port', models.IntegerField()),
                ('mountpoint', models.CharField(default='/stream', max_length=40)),
                ('priority_online', models.IntegerField(default=10, verbose_name='Online Priority')),
                ('priority_offline', models.IntegerField(default=3, verbose_name='Offline Priority')),
                ('slate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shows.ScheduleSlate', verbose_name='Active Slate')),
                ('slug', models.SlugField(default='urf-online', unique=True)),
            ],
            options={
                'verbose_name': 'Stream',
            },
        ),
    ]
