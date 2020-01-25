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
    transductor_collection_date = models.DateTimeField(default=timezone.now)

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

    def reset_measurement_filter(self):
        """
        Clears any related filter data if deemed necessary
        """
        raise NotImplementedError


class MinutelyMeasurement(Measurement):

    def __str__(self):
        return '%s' % self.transductor_collection_date

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
        from events.models import PhaseDropEvent
        from events.models import PrecariousVoltageEvent
        from events.models import VoltageEventDebouncer

        # Create a voltage event debouncer per phase
        debouncer_a = VoltageEventDebouncer.get_voltage_debouncer(
            self.transductor, measurements[0][0])
        debouncer_b = VoltageEventDebouncer.get_voltage_debouncer(
            self.transductor, measurements[1][0])
        debouncer_c = VoltageEventDebouncer.get_voltage_debouncer(
            self.transductor, measurements[2][0])

        voltage_parameters = [used_voltage,
                              precary_lower_boundary,
                              precary_upper_boundary,
                              critical_lower_boundary,
                              critical_upper_boundary]

        debouncer_a.add_data(measurements[0][0], measurements[0][1])
        debouncer_b.add_data(measurements[1][0], measurements[1][1])
        debouncer_c.add_data(measurements[2][0], measurements[2][1])

        debouncer_a.populate_voltage_event_lists(voltage_parameters)
        debouncer_b.populate_voltage_event_lists(voltage_parameters)
        debouncer_c.populate_voltage_event_lists(voltage_parameters)

        events_lists = [[], [], [], [], []]
        events_from_a = VoltageEventDebouncer.get_event_lists(debouncer_a.id)
        events_from_b = VoltageEventDebouncer.get_event_lists(debouncer_b.id)
        events_from_c = VoltageEventDebouncer.get_event_lists(debouncer_c.id)

        for i in range(len(events_lists)):
            events_lists[i] = \
                events_lists[i] + events_from_a[i] +\
                events_from_b[i] + events_from_c[i]

        if events_lists[0] != []:
            evt = PhaseDropEvent()
            evt.save_event(self.transductor, events_lists[0])

        if events_lists[1] != []:
            evt = CriticalVoltageEvent()
            evt.save_event(self.transductor, events_lists[1])

        if events_lists[2] != []:
            evt = CriticalVoltageEvent()
            evt.save_event(self.transductor, events_lists[2])

        if events_lists[3] != []:
            evt = PrecariousVoltageEvent()
            evt.save_event(self.transductor, events_lists[3])

        if events_lists[4] != []:
            evt = PrecariousVoltageEvent()
            evt.save_event(self.transductor, events_lists[4])

    def reset_filter(self):
        from events.models import VoltageEventDebouncer
        debouncer_a = VoltageEventDebouncer.get_voltage_debouncer(
            self.transductor, 'voltage_a')
        debouncer_a.reset_filter()
        debouncer_b = VoltageEventDebouncer.get_voltage_debouncer(
            self.transductor, 'voltage_b')
        debouncer_b.reset_filter()
        debouncer_c = VoltageEventDebouncer.get_voltage_debouncer(
            self.transductor, 'voltage_c')
        debouncer_c.reset_filter()


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

    def reset_measurement_filter(self):
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
