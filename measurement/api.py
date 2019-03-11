from boogie.rest import rest_api
from .models import EnergyMeasurement


@rest_api.action('measurement.EnergyMeasurement')
def minutely_measurements(energy_measurements):
    return energy_measurements.get_minutely_measurements()


@rest_api.action('measurement.EnergyMeasurement')
def quartely_measurements(energy_measurements):
    return energy_measurements.get_quartely_measurements()


@rest_api.action('measurement.EnergyMeasurement')
def monthly_measurements(energy_measurements):
    return energy_measurements.get_monthly_measurements()
