import pytest
from django.test import TestCase
from django.conf import settings
from django.db import IntegrityError
from django.db.utils import DataError
from transductor.models import EnergyTransductor
from measurement.models import MinutelyMeasurement
from measurement.models import QuarterlyMeasurement
from measurement.models import MonthlyMeasurement
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.utils import timezone
from data_reader.utils import *

'''
TODO Unit Test Data Reader
'''
# class DataReaderTestCase(TestCase):
#     """
#     Test Data Reader mainly Serial Protocol
#     """
#     def setUp(self):
#         self.transductor = EnergyTransductor.objects.create(
#             serial_number='87654321',
#             ip_address='111.111.111.11',
#             broken=False,
#             active=True,
#             model="EnergyTransductor",
#             firmware_version='12.1.3215',
#             physical_location='predio 2 sala 44',
#             geolocation_longitude=-24.4556,
#             geolocation_latitude=-24.45996,
#             installation_date=datetime.now()
#         )
#         self.minutely_measurement = MinutelyMeasurement.objects.create(
#             collection_date=timezone.datetime(2019, 2, 5, 14, 0, 0),
#             transductor=self.transductor,
#             frequency_a=8,
#             voltage_a=8,
#             voltage_b=8,
#             voltage_c=8,
#             current_a=8,
#             current_b=8,
#             current_c=8,
#             active_power_a=8,
#             active_power_b=8,
#             active_power_c=8,
#             total_active_power=8,
#             reactive_power_a=8,
#             reactive_power_b=8,
#             reactive_power_c=8,
#             total_reactive_power=8,
#             apparent_power_a=8,
#             apparent_power_b=8,
#             apparent_power_c=8,
#             total_apparent_power=8,
#             power_factor_a=8,
#             power_factor_b=8,
#             power_factor_c=8,
#             total_power_factor=8,
#             dht_voltage_a=8,
#             dht_voltage_b=8,
#             dht_voltage_c=8,
#             dht_current_a=8,
#             dht_current_b=8,
#             dht_current_c=8,
#         )
#
#         self.quarterly_measurement = QuarterlyMeasurement.objects.create(
#             collection_date=timezone.datetime(2019, 2, 5, 14, 0, 0),
#             transductor=self.transductor,
#             generated_energy_peak_time=8,
#             generated_energy_off_peak_time=8,
#             consumption_peak_time=8,
#             consumption_off_peak_time=8,
#             inductive_power_peak_time=8,
#             inductive_power_off_peak_time=8,
#             capacitive_power_peak_time=8,
#             capacitive_power_off_peak_time=8
#         )
#
#         self.monthly_measurement = MonthlyMeasurement.objects.create(
#             collection_date=timezone.datetime(2019, 2, 5, 14, 0, 0),
#             transductor=self.transductor,
#             generated_energy_peak_time=8,
#             generated_energy_off_peak_time=8,
#             consumption_peak_time=8,
#             consumption_off_peak_time=8,
#             inductive_power_peak_time=8,
#             inductive_power_off_peak_time=8,
#             capacitive_power_peak_time=8,
#             capacitive_power_off_peak_time=8,
#             active_max_power_peak_time=8,
#             active_max_power_off_peak_time=8,
#             reactive_max_power_peak_time=8,
#             reactive_max_power_off_peak_time=8,
#             active_max_power_list_peak_time=[
#                 {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
#                 {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
#                 {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
#                 {"value": 0.0, "timestamp": "2019-02-05 14:00:00"}
#             ],
#             active_max_power_list_off_peak_time=[
#                 {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
#                 {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
#                 {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
#                 {"value": 0.0, "timestamp": "2019-02-05 14:00:00"}
#             ],
#             reactive_max_power_list_peak_time=[
#                 {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
#                 {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
#                 {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
#                 {"value": 0.0, "timestamp": "2019-02-05 14:00:00"}
#             ],
#             reactive_max_power_list_off_peak_time=[
#                 {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
#                 {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
#                 {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
#                 {"value": 0.0, "timestamp": "2019-02-05 14:00:00"}
#             ]
#         )
#
#
#     def test_data_converter:
#         """
#         TODO
#         Returns:
#
#         """
