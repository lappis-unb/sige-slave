# Generated by Django 2.1.5 on 2019-02-05 12:18

from django.db import migrations, models
from django.contrib.postgres.operations import HStoreExtension


class Migration(migrations.Migration):

    dependencies = [
        ('measurement', '0003_auto_20190123_1537'),
    ]

    operations = [
        HStoreExtension(),

        migrations.CreateModel(
            name='HourMeasurement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hour', models.FloatField(default=None)),
            ],
        ),
        migrations.CreateModel(
            name='MinuteMeasurement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minute', models.FloatField(default=None)),
            ],
        ),
        migrations.CreateModel(
            name='QuarterMeasurement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quarter', models.FloatField(default=None)),
            ],
        ),
    ]
