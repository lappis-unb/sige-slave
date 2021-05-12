from debouncers.debouncers import VoltageEventDebouncer
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from transductor.models import EnergyTransductor


class Measurement(models.Model):
    """
    Abstract class responsible to create a base for measurements and optimize
    performance from queries.

    Attributes:
        collection_date (datetime): The exactly collection time.

    """

    slave_collection_date = models.DateTimeField(default=timezone.now)
    transductor_collection_date = models.DateTimeField(default=timezone.now)

    transductor = models.ForeignKey(
        EnergyTransductor,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
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
    class Meta:
        default_related_name = "minutely_measurements"

    def __str__(self):
        return "%s" % self.transductor_collection_date

    frequency_a = models.FloatField(default=None, null=True, blank=True)

    voltage_a = models.FloatField(default=None, null=True, blank=True)
    voltage_b = models.FloatField(default=None, null=True, blank=True)
    voltage_c = models.FloatField(default=None, null=True, blank=True)

    current_a = models.FloatField(default=None, null=True, blank=True)
    current_b = models.FloatField(default=None, null=True, blank=True)
    current_c = models.FloatField(default=None, null=True, blank=True)

    active_power_a = models.FloatField(default=None, null=True, blank=True)
    active_power_b = models.FloatField(default=None, null=True, blank=True)
    active_power_c = models.FloatField(default=None, null=True, blank=True)
    total_active_power = models.FloatField(default=None, null=True, blank=True)

    reactive_power_a = models.FloatField(default=None, null=True, blank=True)
    reactive_power_b = models.FloatField(default=None, null=True, blank=True)
    reactive_power_c = models.FloatField(default=None, null=True, blank=True)
    total_reactive_power = models.FloatField(default=None, null=True, blank=True)

    apparent_power_a = models.FloatField(default=None, null=True, blank=True)
    apparent_power_b = models.FloatField(default=None, null=True, blank=True)
    apparent_power_c = models.FloatField(default=None, null=True, blank=True)
    total_apparent_power = models.FloatField(default=None, null=True, blank=True)

    power_factor_a = models.FloatField(default=None, null=True, blank=True)
    power_factor_b = models.FloatField(default=None, null=True, blank=True)
    power_factor_c = models.FloatField(default=None, null=True, blank=True)
    total_power_factor = models.FloatField(default=None, null=True, blank=True)

    dht_voltage_a = models.FloatField(default=None, null=True, blank=True)
    dht_voltage_b = models.FloatField(default=None, null=True, blank=True)
    dht_voltage_c = models.FloatField(default=None, null=True, blank=True)

    dht_current_a = models.FloatField(default=None, null=True, blank=True)
    dht_current_b = models.FloatField(default=None, null=True, blank=True)
    dht_current_c = models.FloatField(default=None, null=True, blank=True)

    def check_measurements(self):
        measurements = [
            ["voltage_a", self.voltage_a],
            ["voltage_b", self.voltage_b],
            ["voltage_c", self.voltage_c],
        ]

        for measurement_phase, measurements_value in measurements:
            transductor: EnergyTransductor = self.transductor

            debouncer: VoltageEventDebouncer
            debouncer = transductor.get_voltage_debouncer(measurement_phase)

            voltage_state_transition = debouncer.add_new_measurement(measurements_value)

            transductor.check_voltage_events(
                voltage_state_transition,
                measurement_phase,
                measurements_value,
            )


class QuarterlyMeasurement(Measurement):
    def __str__(self):
        return "%s" % self.transductor_collection_date

    generated_energy_peak_time = models.FloatField(default=None, null=True, blank=True)
    generated_energy_off_peak_time = models.FloatField(
        default=None, null=True, blank=True
    )

    consumption_peak_time = models.FloatField(default=None, null=True, blank=True)
    consumption_off_peak_time = models.FloatField(default=None, null=True, blank=True)

    inductive_power_peak_time = models.FloatField(default=None, null=True, blank=True)
    inductive_power_off_peak_time = models.FloatField(
        default=None, null=True, blank=True
    )

    capacitive_power_peak_time = models.FloatField(default=None, null=True, blank=True)
    capacitive_power_off_peak_time = models.FloatField(
        default=None, null=True, blank=True
    )

    # TODO
    def check_measurements(self):
        pass

    def reset_measurement_filter(self):
        pass


class MonthlyMeasurement(Measurement):
    def __str__(self):
        return "%s" % self.transductor_collection_date

    generated_energy_peak_time = models.FloatField(default=None, null=True, blank=True)
    generated_energy_off_peak_time = models.FloatField(
        default=None, null=True, blank=True
    )

    consumption_peak_time = models.FloatField(default=None, null=True, blank=True)
    consumption_off_peak_time = models.FloatField(default=None, null=True, blank=True)

    inductive_power_peak_time = models.FloatField(default=None, null=True, blank=True)
    inductive_power_off_peak_time = models.FloatField(
        default=None, null=True, blank=True
    )

    capacitive_power_peak_time = models.FloatField(default=None, null=True, blank=True)
    capacitive_power_off_peak_time = models.FloatField(
        default=None, null=True, blank=True
    )

    active_max_power_peak_time = models.FloatField(default=None, null=True, blank=True)
    active_max_power_off_peak_time = models.FloatField(
        default=None, null=True, blank=True
    )

    reactive_max_power_peak_time = models.FloatField(
        default=None, null=True, blank=True
    )
    reactive_max_power_off_peak_time = models.FloatField(
        default=None, null=True, blank=True
    )

    active_max_power_list_peak = ArrayField(
        models.FloatField(), default=None, null=True, blank=True
    )
    active_max_power_list_peak_time = ArrayField(
        models.DateTimeField(), default=None, null=True, blank=True
    )

    active_max_power_list_off_peak = ArrayField(
        models.FloatField(), default=None, null=True, blank=True
    )

    active_max_power_list_off_peak_time = ArrayField(
        models.DateTimeField(), default=None, null=True, blank=True
    )

    reactive_max_power_list_peak = ArrayField(
        models.FloatField(), default=None, null=True, blank=True
    )

    reactive_max_power_list_peak_time = ArrayField(
        models.DateTimeField(), default=None, null=True, blank=True
    )

    reactive_max_power_list_off_peak = ArrayField(
        models.FloatField(), default=None, null=True, blank=True
    )
    reactive_max_power_list_off_peak_time = ArrayField(
        models.DateTimeField(), default=None, null=True, blank=True
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
                    values_list[initial_date_position + 1][1 + i],
                )
            else:
                value_result = values_list[value + count]
                timestamp = timezone.datetime(1900, 1, 1, 1, 1)

            dict = {"value": value_result, "timestamp": timestamp}
            count += 1
            max_power_list.append(dict)
        return max_power_list
