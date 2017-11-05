# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-05 20:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomepageBlock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('publish_at', models.DateTimeField()),
                ('position', models.CharField(choices=[('HERO', 'Hero'), ('SEC_1', 'Secondary 1'), ('SEC_2', 'Secondary 2')], max_length=12)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
    ]
