# Generated by Django 2.1.5 on 2019-12-17 15:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20191217_1059'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='criticalvoltageevent',
            name='measurement',
        ),
        migrations.RemoveField(
            model_name='phasedropevent',
            name='measurement',
        ),
        migrations.RemoveField(
            model_name='precariousvoltageevent',
            name='measurement',
        ),
    ]
