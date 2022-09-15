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
        MinutelyMeasurement.objects.create(
            transductor_collection_date=data.get("transductor_collection_date"),
            slave_collection_date=data.get("transductor_collection_date"),
            transductor=transductor,
            frequency_a=data.get("frequency_a"),
            voltage_a=data.get("voltage_a"),
            voltage_b=data.get("voltage_b"),
            voltage_c=data.get("voltage_c"),
            current_a=data.get("current_a"),
            current_b=data.get("current_b"),
            current_c=data.get("current_c"),
            active_power_a=data.get("active_power_a"),
            active_power_b=data.get("active_power_b"),
            active_power_c=data.get("active_power_c"),
            total_active_power=data.get("total_active_power"),
            reactive_power_a=data.get("reactive_power_a"),
            reactive_power_b=data.get("reactive_power_b"),
            reactive_power_c=data.get("reactive_power_c"),
            total_reactive_power=data.get("total_reactive_power"),
            apparent_power_a=data.get("apparent_power_a"),
            apparent_power_b=data.get("apparent_power_b"),
            apparent_power_c=data.get("apparent_power_c"),
            total_apparent_power=data.get("total_apparent_power"),
            power_factor_a=data.get("power_factor_a"),
            power_factor_b=data.get("power_factor_b"),
            power_factor_c=data.get("power_factor_c"),
            total_power_factor=data.get("total_power_factor"),
            dht_voltage_a=data.get("dht_voltage_a"),
            dht_voltage_b=data.get("dht_voltage_b"),
            dht_voltage_c=data.get("dht_voltage_c"),
            dht_current_a=data.get("dht_current_a"),
            dht_current_b=data.get("dht_current_b"),
            dht_current_c=data.get("dht_current_c"),
        )

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
            capacitive_power_off_peak_time=data.get("capacitive_power_off_peak_time")
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
            active_max_power_list_peak=data.get("")
        )
