# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-23 10:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shows', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='showepisode',
            name='credits',
            field=models.ManyToManyField(through='shows.EpisodeCredit', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='showepisode',
            name='series',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='episodes', to='shows.ShowSeries'),
        ),
        migrations.AddField(
            model_name='showepisode',
            name='show',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='episodes', to='shows.Show'),
        ),
        migrations.AddField(
            model_name='show',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shows.ShowCategory'),
        ),
        migrations.AddField(
            model_name='episodecredit',
            name='episode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shows.ShowEpisode'),
        ),
        migrations.AddField(
            model_name='episodecredit',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credits', to=settings.AUTH_USER_MODEL),
        ),
    ]
