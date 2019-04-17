# Generated by Django 2.2 on 2019-04-17 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RunScheduleApp', '0002_auto_20190416_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='training',
            name='distance_main',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True, verbose_name='Distance [km]'),
        ),
        migrations.AlterField(
            model_name='training',
            name='time_main',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='Time [min]'),
        ),
    ]
