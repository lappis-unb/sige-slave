import os
import json

from django.db import models
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.core import serializers
from django.contrib.postgres.fields import ArrayField, HStoreField

from transductor.models import EnergyTransductor


class Measurement(models.Model):
    """
    Abstract class responsible to create a base for measurements and optimize
    performance from queries.

    Attributes:
        collection_date (datetime): The exactly collection time.

    """
    settings.USE_TZ = False
    slave_collection_date = models.DateTimeField(default=timezone.now)


    transductor = models.ForeignKey(
        EnergyTransductor,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )

    class Meta:
        abstract = True

    def save_measurements(self, values_list):
        """
        Method responsible to save measurements based on values list received.

        Args:
            values_list (list): The list with all important
            measurements values.

        Returns:
            None
        """
        raise NotImplementedError

    def check_measurements(self):
        """
        Checks measurements and triggers events if deemed necessary
        """
        raise NotImplementedError


class MinutelyMeasurement(Measurement):

    def __str__(self):
        return '%s' % self.transductor_collection_date


    transductor_collection_date = models.DateTimeField(default=timezone.now)

    frequency_a = models.FloatField(default=0)

    voltage_a = models.FloatField(default=0)
    voltage_b = models.FloatField(default=0)
    voltage_c = models.FloatField(default=0)

    current_a = models.FloatField(default=0)
    current_b = models.FloatField(default=0)
    current_c = models.FloatField(default=0)

    active_power_a = models.FloatField(default=0)
    active_power_b = models.FloatField(default=0)
    active_power_c = models.FloatField(default=0)
    total_active_power = models.FloatField(default=0)

    reactive_power_a = models.FloatField(default=0)
    reactive_power_b = models.FloatField(default=0)
    reactive_power_c = models.FloatField(default=0)
    total_reactive_power = models.FloatField(default=0)

    apparent_power_a = models.FloatField(default=0)
    apparent_power_b = models.FloatField(default=0)
    apparent_power_c = models.FloatField(default=0)
    total_apparent_power = models.FloatField(default=0)

    power_factor_a = models.FloatField(default=0)
    power_factor_b = models.FloatField(default=0)
    power_factor_c = models.FloatField(default=0)
    total_power_factor = models.FloatField(default=0)

    dht_voltage_a = models.FloatField(default=0)
    dht_voltage_b = models.FloatField(default=0)
    dht_voltage_c = models.FloatField(default=0)

    dht_current_a = models.FloatField(default=0)
    dht_current_b = models.FloatField(default=0)
    dht_current_c = models.FloatField(default=0)

    def check_measurements(self):
        used_voltage = float(os.getenv('CONTRACTED_VOLTAGE'))

        precary_lower_boundary = used_voltage * 0.91
        precary_upper_boundary = used_voltage * 1.04

        critical_lower_boundary = used_voltage * 0.86
        critical_upper_boundary = used_voltage * 1.06

        # shortened validations for the if statement
        measurements = [
            ['voltage_a', self.voltage_a],
            ['voltage_b', self.voltage_b],
            ['voltage_c', self.voltage_c]
        ]
        precarious_lower_list = []
        precarious_upper_list = []
        critical_lower_list = []
        critical_upper_list = []
        list_down_phases = []

        from events.models import CriticalVoltageEvent
        from events.models import PrecariousVoltageEvent
        from events.models import PhaseDropEvent

        limit_phase_drop = (used_voltage * 0.8)

        for measurement in measurements:
            if measurement[1] < limit_phase_drop:
                list_down_phases.append([measurement[0], measurement[1]])
            elif measurement[1] < critical_lower_boundary:
                critical_lower_list.append([measurement[0], measurement[1]])
            elif measurement[1] > critical_upper_boundary:
                critical_upper_list.append([measurement[0], measurement[1]])
            elif measurement[1] < precary_lower_boundary:
                precarious_lower_list.append([measurement[0], measurement[1]])
            elif measurement[1] > precary_upper_boundary:
                precarious_upper_list.append([measurement[0], measurement[1]])

        if list_down_phases:
            evt = PhaseDropEvent()
            evt.save_event(self.transductor, list_down_phases)

        if critical_lower_list:
            evt = CriticalVoltageEvent()
            evt.save_event(self.transductor, critical_lower_list)

        if critical_upper_list:
            evt = CriticalVoltageEvent()
            evt.save_event(self.transductor, critical_upper_list)

        if precarious_lower_list:
            evt = PrecariousVoltageEvent()
            evt.save_event(self.transductor, precarious_lower_list)

        if precarious_upper_list:
            evt = PrecariousVoltageEvent()
            evt.save_event(self.transductor, precarious_upper_list)


class QuarterlyMeasurement(Measurement):

    def __str__(self):
        return '%s' % self.transductor_collection_date

    generated_energy_peak_time = models.FloatField(default=0)
    generated_energy_off_peak_time = models.FloatField(default=0)

    consumption_peak_time = models.FloatField(default=0)
    consumption_off_peak_time = models.FloatField(default=0)

    inductive_power_peak_time = models.FloatField(default=0)
    inductive_power_off_peak_time = models.FloatField(default=0)

    capacitive_power_peak_time = models.FloatField(default=0)
    capacitive_power_off_peak_time = models.FloatField(default=0)

    # TODO
    def check_measurements(self):
        pass


class MonthlyMeasurement(Measurement):

    def __str__(self):
        return '%s' % self.transductor_collection_date

    generated_energy_peak_time = models.FloatField(default=0)
    generated_energy_off_peak_time = models.FloatField(default=0)

    consumption_peak_time = models.FloatField(default=0)
    consumption_off_peak_time = models.FloatField(default=0)

    inductive_power_peak_time = models.FloatField(default=0)
    inductive_power_off_peak_time = models.FloatField(default=0)

    capacitive_power_peak_time = models.FloatField(default=0)
    capacitive_power_off_peak_time = models.FloatField(default=0)

    active_max_power_peak_time = models.FloatField(default=0)
    active_max_power_off_peak_time = models.FloatField(default=0)

    reactive_max_power_peak_time = models.FloatField(default=0)
    reactive_max_power_off_peak_time = models.FloatField(
        default=0
    )

    active_max_power_list_peak = ArrayField(
        models.FloatField(), default=None
    )
    active_max_power_list_peak_time = ArrayField(
        models.DateTimeField(), default=None
    )

    active_max_power_list_off_peak = ArrayField(
        models.FloatField(), default=None
    )

    active_max_power_list_off_peak_time = ArrayField(
        models.DateTimeField(), default=None
    )

    reactive_max_power_list_peak = ArrayField(
        models.FloatField(), default=None
    )

    reactive_max_power_list_peak_time = ArrayField(
        models.DateTimeField(), default=None
    )

    reactive_max_power_list_off_peak = ArrayField(
        models.FloatField(), default=None
    )
    reactive_max_power_list_off_peak_time = ArrayField(
        models.DateTimeField(), default=None
    )

    # TODO
    def check_measurements(self):
        pass

    def _get_year(self, year, month):
        return (year - 1) if (month == 1) else year

    def _get_list_data(self, value, initial_date_position, values_list):
        max_power_list = []

        current_year = values_list[0]

        count = 0

        for i in range(0, 8, 2):

            if values_list[initial_date_position][0 + i] != 0:
                value_result = values_list[value + count]
                timestamp = timezone.datetime(
                    current_year,
                    values_list[initial_date_position][0 + i],
                    values_list[initial_date_position][1 + i],
                    values_list[initial_date_position + 1][0 + i],
                    values_list[initial_date_position + 1][1 + i]
                )
            else:
                value_result = values_list[value + count]
                timestamp = timezone.datetime(1900, 1, 1, 1, 1)

            dict = {
                'value': value_result,
                'timestamp': timestamp
            }
            count += 1
            max_power_list.append(dict)
        return max_power_list
