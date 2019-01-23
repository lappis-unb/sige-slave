from boogie.rest import rest_api
from .models import EnergyTransductor

@rest_api.action('transductor.EnergyTransductor')
def measurements(energy_transductor):
    return energy_transductor.measurements.all()
