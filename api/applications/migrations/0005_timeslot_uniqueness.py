# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-01-26 17:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0004_showapplication_connected_show'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='timeslotrequest',
            unique_together=set([('day', 'hour')]),
        ),
    ]
