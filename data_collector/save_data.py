from datetime import datetime

from django.utils import timezone

from measurement.models import (
    MinutelyMeasurement,
    MonthlyMeasurement,
    QuarterlyMeasurement,
)
from modbus_reader.utils.constants import (
    COLLECTION_TYPE_MINUTELY,
    COLLECTION_TYPE_MONTHLY,
    COLLECTION_TYPE_QUARTERLY,
)
from transductor.models import EnergyTransductor


def save_data(data, transductor: EnergyTransductor, collection_type: str) -> None:

    if collection_type == COLLECTION_TYPE_MINUTELY:
        save_minutely_measurement(data, transductor)

    elif collection_type == COLLECTION_TYPE_QUARTERLY:
        QuarterlyMeasurement.objects.create(
            transductor_collection_date=timezone.now(),
            generated_energy_peak_time=data.get("generated_energy_peak_time"),
            generated_energy_off_peak_time=data.get("generated_energy_off_peak_time"),
            consumption_peak_time=data.get("consumption_peak_time"),
            consumption_off_peak_time=data.get("consumption_off_peak_time"),
            inductive_power_peak_time=data.get("inductive_power_peak_time"),
            inductive_power_off_peak_time=data.get("inductive_power_off_peak_time"),
            capacitive_power_peak_time=data.get("capacitive_power_peak_time"),
            capacitive_power_off_peak_time=data.get("capacitive_power_off_peak_time"),
        )

    elif collection_type == COLLECTION_TYPE_MONTHLY:

        MonthlyMeasurement.objects.create(
            transductor_collection_date=timezone.now(),
            generated_energy_peak_time=data.get("generated_energy_peak_monthly"),
            generated_energy_off_peak_time=data.get("generated_energy_off_peak_monthly"),
            consumption_peak_time=data.get("consumption_peak_monthly"),
            consumption_off_peak_time=data.get("consumption_off_peak_monthly"),
            inductive_power_peak_time=data.get("inductive_power_peak_monthly"),
            inductive_power_off_peak_time=data.get("inductive_power_off_peak_monthly"),
            capacitive_power_peak_time=data.get("capacitive_power_peak_monthly"),
            capacitive_power_off_peak_time=data.get("capacitive_power_off_peak_monthly"),
            active_max_power_peak_time=data.get("active_max_power_peak_monthly"),
            active_max_power_off_peaktime=data.get("active_max_power_off_peak_monthly"),
            reactive_max_power_peak_time=data.get("reactive_max_power_peak_monthly"),
            reactive_max_power_off_peaktime=data.get(""),
            active_max_power_list_peak=data.get(""),
        )


# ==========================================================================================================


def verify_collection_date(measurements, transductor: EnergyTransductor):
    from data_reader.utils import single_data_collection

    collected_date = timezone.datetime(
        year=measurements[0],
        month=measurements[1],
        day=measurements[2],
        hour=measurements[3],
        minute=measurements[4],
        second=measurements[5],
    )
    current_date = timezone.datetime.now()

    # If the date the transductor returns is more than acceptable (30s), a new
    # request is sent to reset the meter time
    # if not is_datetime_similar(collected_date, current_date):
    #     single_data_collection(transductor, "CorrectDate")
    #     measurements[0] = current_date.year
    #     measurements[1] = current_date.month
    #     measurements[2] = current_date.day
    #     measurements[3] = current_date.hour
    #     measurements[4] = current_date.minute
    #     measurements[5] = current_date.second


def save_minutely_measurement(data, transductor: EnergyTransductor):

    # verify_collection_date(data, transductor)

    minutely_measurement = MinutelyMeasurement()

    # saving the datetime from transductor
    # date = timezone.datetime(
    #     year=response[0],
    #     month=response[1],
    #     day=response[2],
    #     hour=response[3],
    #     minute=response[4],
    #     second=response[5],
    # )

    minutely_measurement.transductor = transductor
    minutely_measurement.frequency_a = data.get("Freq-IEC")
    minutely_measurement.voltage_a = data.get("U1")
    minutely_measurement.voltage_b = data.get("U2")
    minutely_measurement.voltage_c = data.get("U3")
    minutely_measurement.current_a = data.get("I1")
    minutely_measurement.current_b = data.get("I2")
    minutely_measurement.current_c = data.get("I3")
    minutely_measurement.active_power_a = data.get("P1")
    minutely_measurement.active_power_b = data.get("P2")
    minutely_measurement.active_power_c = data.get("P3")
    minutely_measurement.total_active_power = data.get("P0")
    minutely_measurement.reactive_power_a = data.get("Q1")
    minutely_measurement.reactive_power_b = data.get("Q2")
    minutely_measurement.reactive_power_c = data.get("Q3")
    minutely_measurement.total_reactive_power = data.get("Q0")
    minutely_measurement.apparent_power_a = data.get("S1")
    minutely_measurement.apparent_power_b = data.get("S2")
    minutely_measurement.apparent_power_c = data.get("S3")
    minutely_measurement.total_apparent_power = data.get("S0")
    minutely_measurement.power_factor_a = data.get("FP1")
    minutely_measurement.power_factor_b = data.get("FP2")
    minutely_measurement.power_factor_c = data.get("FP3")
    minutely_measurement.total_power_factor = data.get("FP0")
    minutely_measurement.dht_voltage_a = data.get("UAN-THD")
    minutely_measurement.dht_voltage_b = data.get("UBN-THD")
    minutely_measurement.dht_voltage_c = data.get("UCN-THD")
    minutely_measurement.dht_current_a = data.get("IA-THD")
    minutely_measurement.dht_current_b = data.get("IB-THD")
    minutely_measurement.dht_current_c = data.get("IC-THD")

    # minutely_measurement.transctor_collection_date = date
    minutely_measurement.slave_collection_date = timezone.now()

    # Essas medidas não são do grupo de minutos (validar prof)
    # minutely_measurement.consumption_a = response[35]
    # minutely_measurement.consumption_b = response[36]
    # minutely_measurement.consumption_c = response[37]
    # minutely_measurement.total_consumption = response[38]

    minutely_measurement.check_measurements()
    minutely_measurement.save()
    transductor.set_broken(False)
