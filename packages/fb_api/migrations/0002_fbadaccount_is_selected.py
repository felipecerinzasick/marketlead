# Generated by Django 2.2.4 on 2019-12-19 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fb_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fbadaccount',
            name='is_selected',
            field=models.BooleanField(default=False),
        ),
    ]
