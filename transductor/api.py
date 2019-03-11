from boogie.rest import rest_api
from .models import EnergyTransductor
from json import loads


@rest_api.action('transductor.EnergyTransductor')
def minutely_measurements(energy_transductor):
    return energy_transductor.get_minutely_measurements()


@rest_api.action('transductor.EnergyTransductor')
def quartely_measurements(energy_transductor):
    return energy_transductor.get_quartely_measurements()


@rest_api.action('transductor.EnergyTransductor')
def monthly_measurements(energy_transductor):
    return energy_transductor.get_monthly_measurements()


@rest_api.action('transductor.EnergyTransductor')
def minutely_measurements_by_datetime(request, energy_transductor):
    return energy_transductor.minutely_measurements_by_datetime(
        request.data['start_date'],
        request.data['end_date']
    )


@rest_api.action('transductor.EnergyTransductor')
def quartely_measurements_by_datetime(request, energy_transductor):
    return energy_transductor.quartely_measurements_by_datetime(
        request.data['start_date'],
        request.data['end_date']
    )


@rest_api.action('transductor.EnergyTransductor')
def monthly_measurements_by_datetime(request, energy_transductor):
    return energy_transductor.monthly_measurements_by_datetime(
        request.data['start_date'],
        request.data['end_date']
    )