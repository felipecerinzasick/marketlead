# Generated by Django 2.2.4 on 2019-11-23 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0002_auto_20191123_1231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='unique_id',
            field=models.CharField(editable=False, max_length=50),
        ),
    ]
