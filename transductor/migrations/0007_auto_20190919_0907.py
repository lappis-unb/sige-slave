# Generated by Django 2.1.5 on 2019-09-19 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transductor', '0006_auto_20190916_1138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='energytransductor',
            name='installation_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
