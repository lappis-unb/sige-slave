# Generated by Django 3.0.2 on 2020-01-23 10:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_voltageeventdebouncer'),
    ]

    operations = [
        migrations.DeleteModel(
            name='VoltageEventDebouncer',
        ),
    ]
