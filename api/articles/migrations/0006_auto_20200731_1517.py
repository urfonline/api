# Generated by Django 3.0.8 on 2020-07-31 15:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_urfimage_file_hash'),
        ('articles', '0005_article_short_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='featured_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.UrfImage'),
        ),
    ]
