# Generated by Django 3.2.18 on 2023-05-01 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_collector', '0003_alter_memorymap_model_transductor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memorymap',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
