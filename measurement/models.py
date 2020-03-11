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

    def get_avg_filters_values(self):
        from events.models import VoltageEventDebouncer
        from events.models import VoltageEventDebouncer
        debouncer_a = VoltageEventDebouncer.get_voltage_debouncer(
            self.transductor, 'voltage_a')
        debouncer_a.reset_filter()
        debouncer_b = VoltageEventDebouncer.get_voltage_debouncer(
            self.transductor, 'voltage_b')
        debouncer_b.reset_filter()
        debouncer_c = VoltageEventDebouncer.get_voltage_debouncer(
            self.transductor, 'voltage_c')
        return (debouncer_a.get_average_filter_value(),
                debouncer_b.get_average_filter_value(),
                debouncer_c.get_average_filter_value())

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

        from events.models import CriticalVoltageEvent
        from events.models import PhaseDropEvent
        from events.models import PrecariousVoltageEvent
        from events.models import VoltageEventDebouncer

        # Create a voltage event debouncer per phase
        debouncers = []
        debouncers.append(VoltageEventDebouncer.get_voltage_debouncer(
            self.transductor, measurements[0][0]))
        debouncers.append(VoltageEventDebouncer.get_voltage_debouncer(
            self.transductor, measurements[1][0]))
        debouncers.append(VoltageEventDebouncer.get_voltage_debouncer(
            self.transductor, measurements[2][0]))

        voltage_parameters = [used_voltage,
                              precary_lower_boundary,
                              precary_upper_boundary,
                              critical_lower_boundary,
                              critical_upper_boundary]

        index = 0
        for debouncer in debouncers:
            debouncer.add_data(measurements[index][0], measurements[index][1])
            index += 1

        prev_evts = []
        cur_evts = []
        event_indices = []
        for debouncer in debouncers:
            (event_index, prev, cur) = debouncer.raise_event(voltage_parameters,
                                                             self.transductor)
            prev_evts.append(prev)
            cur_evts.append(cur)
            event_indices.append(event_index)

        # Raise Previous Events
        # TODO Encapsulate this code snippet in a private method
        for prev_evt in prev_evts:
            if prev_evt is not None:
                data = []
                for key, value in prev_evt.data.items():
                    data.append(key)
                    data.append(value)
                prev_evt.save_event(self.transductor,
                                    [data])

        # Raise Current Events and Suppress repeated
        # TODO Refactor this code snippet for maintenance
        # TODO Encapsulate this code snippet in a private method
        if event_indices[0] > -1:
            cur_evts[0].data = []
            cur_evts[0].data.append(
                VoltageEventDebouncer.event_lists_dictionary[
                    debouncers[0].id][event_indices[0]][0]
            )
            if event_indices[0] == event_indices[1]:
                key = VoltageEventDebouncer.event_lists_dictionary[
                    debouncers[1].id][event_indices[1]][0][0]
                value = VoltageEventDebouncer.event_lists_dictionary[
                    debouncers[1].id][event_indices[1]][0][1]
                cur_evts[0].data.append([key, value])

                cur_evts[1] = None
                event_indices[1] = -1
            if event_indices[0] == event_indices[2]:
                key = VoltageEventDebouncer.event_lists_dictionary[
                    debouncers[2].id][event_indices[2]][0][0]
                value = VoltageEventDebouncer.event_lists_dictionary[
                    debouncers[2].id][event_indices[2]][0][1]
                cur_evts[0].data.append([key, value])

                cur_evts[2] = None
                event_indices[2] = -1
        if event_indices[1] > -1:
            cur_evts[1].data = []
            cur_evts[1].data.append(
                VoltageEventDebouncer.event_lists_dictionary[
                    debouncers[1].id][event_indices[1]][0])
            if event_indices[1] == event_indices[2]:
                key = VoltageEventDebouncer.event_lists_dictionary[
                    debouncers[2].id][event_indices[2]][0][0]
                value = VoltageEventDebouncer.event_lists_dictionary[
                    debouncers[2].id][event_indices[2]][0][1]
                cur_evts[1].data.append([key, value])

                cur_evts[2] = None
                event_indices[2] = -1
        if event_indices[2] > -1:
            cur_evts[2].data = []
            cur_evts[2].data.append(
                VoltageEventDebouncer.event_lists_dictionary[
                    debouncers[2].id][event_indices[2]][0])

        for i in range(len(debouncers)):
            if cur_evts[i] is not None:
                # TODO Refactor this code snippet!!!
                # TODO Investigate the reason why it changes data type between
                #  measurements!!!
                if type(cur_evts[i].data) is dict:
                    aux_list = []
                    for key, value in cur_evts[i].data.items():
                        aux_list.append([key, value])
                    cur_evts[i].save_event(self.transductor, aux_list)
                elif type(cur_evts[i].data) is not list:
                    cur_evts[i].save_event(self.transductor)
                else:
                    cur_evts[i].save_event(self.transductor, cur_evts[i].data)

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
