# Generated by Django 3.0.8 on 2020-07-31 15:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shows', '0012_scheduleslate_broadcast_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduleslate',
            name='automation_show',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shows.Show'),
        ),
        migrations.AlterField(
            model_name='showsconfiguration',
            name='automation_show',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shows.Show'),
        ),
        migrations.AlterField(
            model_name='showsconfiguration',
            name='current_slate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shows.ScheduleSlate'),
        ),
    ]
