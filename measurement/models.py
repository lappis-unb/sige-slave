from django.db import models
from django.utils import timezone

from data_collector.modbus.settings import DataGroups
from debouncers.debouncers import VoltageEventDebouncer
from transductor.models import Transductor


class MinutelyMeasurement(models.Model):
    transductor = models.ForeignKey(Transductor, related_name="minutelys", on_delete=models.CASCADE)
    frequency_a = models.FloatField(default=None, null=True, blank=True)
    frequency_b = models.FloatField(default=None, null=True, blank=True)
    frequency_c = models.FloatField(default=None, null=True, blank=True)
    frequency_iec = models.FloatField(default=None, null=True, blank=True)
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
    slave_collection_date = models.DateTimeField(default=timezone.now, blank=True)
    collection_date = models.DateTimeField(default=timezone.now, blank=True)

    class Meta:
        verbose_name = "Minutely Measurement"
        verbose_name_plural = "Minutely Measurements"

    def __str__(self):
        return f"{self.slave_collection_date} - {self.transductor}"

    def check_measurements(self):
        measurements = [
            ["voltage_a", self.voltage_a],
            ["voltage_b", self.voltage_b],
            ["voltage_c", self.voltage_c],
        ]

        for measurement_phase, measurements_value in measurements:
            transductor: Transductor = self.transductor

            debouncer: VoltageEventDebouncer
            debouncer = transductor.get_voltage_debouncer(measurement_phase)

            voltage_state_transition = debouncer.add_new_measurement(measurements_value)

            transductor.check_voltage_events(
                voltage_state_transition,
                measurement_phase,
                measurements_value,
            )


class BaseMeasurement(models.Model):
    transductor = models.ForeignKey(Transductor, on_delete=models.CASCADE)
    active_consumption = models.FloatField(null=True, blank=True)
    active_generated = models.FloatField(null=True, blank=True)
    reactive_inductive = models.FloatField(null=True, blank=True)
    reactive_capacitive = models.FloatField(null=True, blank=True)
    slave_collection_date = models.DateTimeField(default=timezone.now, blank=True)
    collection_date = models.DateTimeField(default=timezone.now, blank=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"


class ReferenceMeasurement(BaseMeasurement):
    data_group = models.IntegerField(choices=DataGroups.choices)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["transductor", "data_group"], name="unique_ref")]
        verbose_name = "Reference Measurement"
        verbose_name_plural = "Reference Measurements"


class QuarterlyMeasurement(BaseMeasurement):
    is_calculated = models.BooleanField(default=False)
    reference_measurement = models.ForeignKey(
        ReferenceMeasurement,
        related_name="+",
        on_delete=models.CASCADE,
        blank=True,
    )

    class Meta:
        verbose_name = "Quarterly Measurement"
        verbose_name_plural = "Quarterly Measurements"


class MonthlyMeasurement(BaseMeasurement):
    active_max_power_peak_time = models.FloatField(default=None, null=True, blank=True)
    active_max_power_off_peak_time = models.FloatField(default=None, null=True, blank=True)
    reactive_max_power_peak_time = models.FloatField(default=None, null=True, blank=True)
    reactive_max_power_off_peak_time = models.FloatField(default=None, null=True, blank=True)
    reference_measurement = models.ForeignKey(
        ReferenceMeasurement,
        related_name="+",
        on_delete=models.DO_NOTHING,
        blank=True,
    )

    class Meta:
        verbose_name = "Monthly Measurement"
        verbose_name_plural = "Monthly Measurements"
