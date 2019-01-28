from boogie.rest import rest_api
from .models import EnergyTransductor
from json import loads


@rest_api.action('transductor.EnergyTransductor')
def measurements(energy_transductor):
    return energy_transductor.get_measurements()


@rest_api.action('transductor.EnergyTransductor')
def measurements_by_datetime(request, energy_transductor):
    return energy_transductor.get_measurements_by_datetime(
        request.data['start_date'],
        request.data['end_date']
    )
