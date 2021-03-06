# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-01-26 17:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shows', '0009_auto_20200106_1736'),
        ('applications', '0003_extra_application_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='showapplication',
            name='connected_show',
            field=models.OneToOneField(blank=True, help_text='When this slot has been turned into a show, it shows up here', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='application', to='shows.Show', verbose_name='Connected Show'),
        ),
    ]
