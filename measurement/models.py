from django.db import models
from datetime import datetime
from transductor.models import EnergyTransductor
from boogie.rest import rest_api


class Measurement(models.Model):
    """
    Abstract class responsible to create a base for measurements and optimize
    performance from queries.

    Attributes:
        collection_date (datetime): The exactly collection time.

    """
    collection_date = models.DateTimeField(default=datetime.now)

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


@rest_api()
class EnergyMeasurement(Measurement):
    """
    Class responsible to store energy measurements,
    considering a three-phase energy system.

    Attributes:
        transductor (EnergyTransductor): The transductor which conducted
        measurements.

        consumption_a (float): The total consumption on phase A. (since last reset)
        consumption_b (float): The total consumption on phase B. (since last reset)
        consumption_c (float): The total consumption on phase C. (since last reset)
        total_consumption (float): The total consumption of transductor. (since last reset)
    """
    transductor = models.ForeignKey(
        EnergyTransductor, related_name="measurements", on_delete=models.CASCADE
    )

    def __str__(self):
        return '%s' % self.collection_date

    def get_time_measurements():
        measures = [
            MinuteMeasurement.objects.all(),
            HourMeasurement.objects.all(),
            QuarterMeasurement.objects.all()
        ]
        return measures

    def save_measurements(self, values_list, transductor):
        """
        Method responsible to save measurements based on values
        list received.
        Args:
            values_list (list): The list with all important
                measurements values.
            transductor (Transductor): Related transductor object
        Return:
            None
        """
        raise NotImplementedError


class MinutelyMeasurement(EnergyMeasurement):

    frequency_a = models.FloatField(default=None)

    voltage_a = models.FloatField(default=None)
    voltage_b = models.FloatField(default=None)
    voltage_c = models.FloatField(default=None)

    current_a = models.FloatField(default=None)
    current_b = models.FloatField(default=None)
    current_c = models.FloatField(default=None)

    active_power_a = models.FloatField(default=None)
    active_power_b = models.FloatField(default=None)
    active_power_c = models.FloatField(default=None)
    total_active_power = models.FloatField(default=None)

    reactive_power_a = models.FloatField(default=None)
    reactive_power_b = models.FloatField(default=None)
    reactive_power_c = models.FloatField(default=None)
    total_reactive_power_a = models.FloatField(default=None)

    apparent_power_a = models.FloatField(default=None)
    apparent_power_b = models.FloatField(default=None)
    apparent_power_c = models.FloatField(default=None)
    total_apparent_power = models.FloatField(default=None)

    power_factor_a = models.FloatField(default=None)
    power_factor_b = models.FloatField(default=None)
    power_factor_c = models.FloatField(default=None)
    total_power_factor = models.FloatField(default=None)

    dht_voltage_a = models.FloatField(default=None)
    dht_voltage_b = models.FloatField(default=None)
    dht_voltage_c = models.FloatField(default=None)

    dht_current_a = models.FloatField(default=None)
    dht_current_b = models.FloatField(default=None)
    dht_current_c = models.FloatField(default=None)

    def save_measurements(values_list, transductor):
        """
        Method responsible to save measurements based on values
        list received.
        Args:
            values_list (list): The list with all important
            measurements values.
        Return:
            None
        """
        minutely_measurement = MinutelyMeasurement()
        minutely_measurement.transductor = transductor

        # saving the datetime from transductor
        minutely_measurement.collection_date = datetime(
            values_list[0],
            values_list[1],
            values_list[2],
            values_list[3],
            values_list[4],
            values_list[5]
        )

        minutely_measurement.frequency_a = values_list[6]
        minutely_measurement.voltage_a = values_list[7]
        minutely_measurement.voltage_b = values_list[8]
        minutely_measurement.voltage_c = values_list[9]
        minutely_measurement.current_a = values_list[10]
        minutely_measurement.current_b = values_list[11]
        minutely_measurement.current_c = values_list[12]
        minutely_measurement.active_power_a = values_list[13]
        minutely_measurement.active_power_b = values_list[14]
        minutely_measurement.active_power_c = values_list[15]
        minutely_measurement.total_active_power = values_list[16]
        minutely_measurement.reactive_power_a = values_list[17]
        minutely_measurement.reactive_power_b = values_list[18]
        minutely_measurement.reactive_power_c = values_list[19]
        minutely_measurement.total_reactive_power = values_list[20]
        minutely_measurement.apparent_power_a = values_list[21]
        minutely_measurement.apparent_power_b = values_list[22]
        minutely_measurement.apparent_power_c = values_list[23]
        minutely_measurement.total_apparent_power = values_list[24]
        minutely_measurement.power_factor_a = values_list[25]
        minutely_measurement.power_factor_b = values_list[26]
        minutely_measurement.power_factor_c = values_list[27]
        minutely_measurement.total_power_factor = values_list[28]
        minutely_measurement.dht_voltage_a = values_list[29]
        minutely_measurement.dht_voltage_b = values_list[30]
        minutely_measurement.dht_voltage_c = values_list[31]
        minutely_measurement.dht_current_a = values_list[32]
        minutely_measurement.dht_current_b = values_list[33]
        minutely_measurement.dht_current_c = values_list[34]
        minutely_measurement.consumption_a = values_list[35]
        minutely_measurement.consumption_b = values_list[36]
        minutely_measurement.consumption_c = values_list[37]
        minutely_measurement.total_consumption = values_list[38]

        minutely_measurement.save()


class QuarterlyMeasurement(EnergyMeasurement):

    generated_energy_peak_time = models.FloatField(default=None)
    generated_energy_off_peak_time = models.FloatField(default=None)
    consumption_peak_time = models.FloatField(default=None)
    consumption_off_peak_time = models.FloatField(default=None)
    inductive_power_peak_time = models.FloatField(default=None)
    inductive_power_off_peak_time = models.FloatField(default=None)
    capacitive_power_peak_time = models.FloatField(default=None)
    capacitive_power_off_peak_time = models.FloatField(default=None)

    def save_measurements(self, values_list, transductor):
        """
        Method responsible to save measurements based on values
        list received.
        Args:
            values_list (list): The list with all important
            measurements values.
        Return:
            None
        """
        quartely_measurement = QuarterlyMeasurement()
        quartely_measurement.transductor = transductor

        quartely_measurement.collection_date = datetime(
            values_list[0],
            values_list[1],
            values_list[2],
            values_list[3],
            values_list[4],
            values_list[5]
        )

        quartely_measurement.generated_energy_peak_time = values_list[6]
        quartely_measurement.generated_energy_off_peak_time = values_list[7]

        quartely_measurement.consumption_peak_time = values_list[8]
        quartely_measurement.consumption_off_peak_time = values_list[9]

        quartely_measurement.inductive_power_peak_time = values_list[10]
        quartely_measurement.inductive_power_off_peak_time = values_list[11]

        quartely_measurement.capacitive_power_peak_time = values_list[12]
        quartely_measurement.capacitive_power_off_peak_time = values_list[13]

        quartely_measurement.save()


class MonthlyMeasurement(EnergyMeasurement):

    generated_energy_peak_time = models.FloatField(default=None)
    generated_energy_off_peak_time = models.FloatField(default=None)
    consumption_peak_time = models.FloatField(default=None)
    consumption_off_peak_time = models.FloatField(default=None)
    inductive_power_peak_time = models.FloatField(default=None)
    inductive_power_off_peak_time = models.FloatField(default=None)
    capacitive_power_peak_time = models.FloatField(default=None)
    capacitive_power_off_peak_time = models.FloatField(default=None)
    active_max_power_peak_time = models.FloatField(default=None)
    active_max_power_off_peak_time = models.FloatField(default=None)
    reactive_max_power_peak_time = models.FloatField(default=None)
    reactive_max_power_off_peak_time = models.FloatField(default=None)

    active_max_power_peak_time_list = models.ArrayField(
        models.ArrayField(

        ),
    )

    def save_measurements(self, values_list, transductor):
        """
        Method responsible to save measurements based on values
        list received.

        Args:
            values_list (list): The list with all important
            measurements values.

        Return:
            None
        """
        monthly_measurement = MonthlyMeasurement()
        monthly_measurement.transductor = transductor

        monthly_measurement.collection_date = datetime(
            values_list[0],
            values_list[1],
            values_list[2],
            values_list[3],
            values_list[4],
            values_list[5]
        )

        monthly_measurement.generated_energy_peak_time = values_list[6]
        monthly_measurement.generated_energy_off_peak_time = values_list[7]

        monthly_measurement.consumption_peak_time = values_list[8]
        monthly_measurement.consumption_off_peak_time = values_list[9]

        monthly_measurement.inductive_power_peak_time = values_list[10]
        monthly_measurement.inductive_power_off_peak_time = values_list[11]

        monthly_measurement.capacitive_power_peak_time = values_list[12]
        monthly_measurement.capacitive_power_off_peak_time = values_list[14]

        monthly_measurement.active_max_power_peak_time = values_list[15]
        monthly_measurement.active_max_power_off_peak_time = values_list[16]

        monthly_measurement.reactive_max_power_peak_time = values_list[17]
        monthly_measurement.reactive_max_power_off_peak_time = values_list[18]

        monthly_measurement.active_max_power_peak_time_list = [
            [
                datetime(
                    "ano atual",
                    values_list[20],
                    values_list[21],
                    values_list[22],
                    values_list[23],
                    "segundos"
                ),
                values_list[19]
            ]
        ]

        monthly_measurement.save()
