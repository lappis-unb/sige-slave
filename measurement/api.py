from boogie.rest import rest_api
from .models import EnergyMeasurement

@rest_api.action('measurement.EnergyMeasurement')
def all_measurements(energy_measurements):
    return energy_measurements.get_time_measurements()
