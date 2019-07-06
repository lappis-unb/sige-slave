# Generated by Django 2.1.5 on 2019-06-24 12:53

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('transductor', '0005_auto_20190624_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='energytransductor',
            name='installation_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 6, 24, 15, 53, 56, 869424, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='energytransductor',
            name='last_clock_battery_change',
            field=models.DateTimeField(default=datetime.datetime(2019, 6, 24, 15, 53, 56, 869518, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='energytransductor',
            name='last_collection',
            field=models.DateTimeField(default=datetime.datetime(2019, 6, 24, 15, 53, 56, 869329, tzinfo=utc)),
        ),
    ]
