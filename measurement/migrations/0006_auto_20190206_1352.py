# Generated by Django 2.1.5 on 2019-02-06 15:52

import django.contrib.postgres.fields
import django.contrib.postgres.fields.hstore
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('measurement', '0005_merge_20190206_1348'),
    ]

    operations = [
        migrations.DeleteModel(
            name='HourMeasurement',
        ),
        migrations.DeleteModel(
            name='MinuteMeasurement',
        ),
        migrations.DeleteModel(
            name='QuarterMeasurement',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='active_power_a',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='active_power_b',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='active_power_c',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='apparent_power_a',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='apparent_power_b',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='apparent_power_c',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='consumption_a',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='consumption_b',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='consumption_c',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='current_a',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='current_b',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='current_c',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='dht_current_a',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='dht_current_b',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='dht_current_c',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='dht_voltage_a',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='dht_voltage_b',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='dht_voltage_c',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='frequency_a',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='power_factor_a',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='power_factor_b',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='power_factor_c',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='reactive_power_a',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='reactive_power_b',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='reactive_power_c',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='total_active_power',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='total_apparent_power',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='total_consumption',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='total_power_factor',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='total_reactive_power',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='voltage_a',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='voltage_b',
        ),
        migrations.RemoveField(
            model_name='energymeasurement',
            name='voltage_c',
        ),
        migrations.CreateModel(
            name='MinutelyMeasurement',
            fields=[
                ('energymeasurement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='measurement.EnergyMeasurement')),
                ('frequency_a', models.FloatField(default=0)),
                ('voltage_a', models.FloatField(default=0)),
                ('voltage_b', models.FloatField(default=0)),
                ('voltage_c', models.FloatField(default=0)),
                ('current_a', models.FloatField(default=0)),
                ('current_b', models.FloatField(default=0)),
                ('current_c', models.FloatField(default=0)),
                ('active_power_a', models.FloatField(default=0)),
                ('active_power_b', models.FloatField(default=0)),
                ('active_power_c', models.FloatField(default=0)),
                ('total_active_power', models.FloatField(default=0)),
                ('reactive_power_a', models.FloatField(default=0)),
                ('reactive_power_b', models.FloatField(default=0)),
                ('reactive_power_c', models.FloatField(default=0)),
                ('total_reactive_power', models.FloatField(default=0)),
                ('apparent_power_a', models.FloatField(default=0)),
                ('apparent_power_b', models.FloatField(default=0)),
                ('apparent_power_c', models.FloatField(default=0)),
                ('total_apparent_power', models.FloatField(default=0)),
                ('power_factor_a', models.FloatField(default=0)),
                ('power_factor_b', models.FloatField(default=0)),
                ('power_factor_c', models.FloatField(default=0)),
                ('total_power_factor', models.FloatField(default=0)),
                ('dht_voltage_a', models.FloatField(default=0)),
                ('dht_voltage_b', models.FloatField(default=0)),
                ('dht_voltage_c', models.FloatField(default=0)),
                ('dht_current_a', models.FloatField(default=0)),
                ('dht_current_b', models.FloatField(default=0)),
                ('dht_current_c', models.FloatField(default=0)),
            ],
            options={
                'abstract': False,
            },
            bases=('measurement.energymeasurement',),
        ),
        migrations.CreateModel(
            name='MonthlyMeasurement',
            fields=[
                ('energymeasurement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='measurement.EnergyMeasurement')),
                ('generated_energy_peak_time', models.FloatField(default=0)),
                ('generated_energy_off_peak_time', models.FloatField(default=0)),
                ('consumption_peak_time', models.FloatField(default=0)),
                ('consumption_off_peak_time', models.FloatField(default=0)),
                ('inductive_power_peak_time', models.FloatField(default=0)),
                ('inductive_power_off_peak_time', models.FloatField(default=0)),
                ('capacitive_power_peak_time', models.FloatField(default=0)),
                ('capacitive_power_off_peak_time', models.FloatField(default=0)),
                ('active_max_power_peak_time', models.FloatField(default=0)),
                ('active_max_power_off_peak_time', models.FloatField(default=0)),
                ('reactive_max_power_peak_time', models.FloatField(default=0)),
                ('reactive_max_power_off_peak_time', models.FloatField(default=0)),
                ('active_max_power_list_peak_time', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.hstore.HStoreField(), size=None)),
                ('active_max_power_list_off_peak_time', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.hstore.HStoreField(), size=None)),
                ('reactive_max_power_list_peak_time', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.hstore.HStoreField(), size=None)),
                ('reactive_max_power_list_off_peak_time', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.hstore.HStoreField(), size=None))
            ],
            options={
                'abstract': False,
            },
            bases=('measurement.energymeasurement',),
        ),
        migrations.CreateModel(
            name='QuarterlyMeasurement',
            fields=[
                ('energymeasurement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='measurement.EnergyMeasurement')),
                ('generated_energy_peak_time', models.FloatField(default=0)),
                ('generated_energy_off_peak_time', models.FloatField(default=0)),
                ('consumption_peak_time', models.FloatField(default=0)),
                ('consumption_off_peak_time', models.FloatField(default=0)),
                ('inductive_power_peak_time', models.FloatField(default=0)),
                ('inductive_power_off_peak_time', models.FloatField(default=0)),
                ('capacitive_power_peak_time', models.FloatField(default=0)),
                ('capacitive_power_off_peak_time', models.FloatField(default=0)),
            ],
            options={
                'abstract': False,
            },
            bases=('measurement.energymeasurement',),
        ),
    ]
