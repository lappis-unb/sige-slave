import pytest
from django.test import TestCase
from django.conf import settings
from django.db import IntegrityError
from django.db.utils import DataError
from transductor_model.models import TransductorModel
from transductor.models import EnergyTransductor
from measurement.models import EnergyMeasurement
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime


class EnergyMeasurementTestCase(TestCase):

    def setUp(self):
        self.trans_model = TransductorModel.objects.create(
            name='TR4020',
            transport_protocol='UDP',
            serial_protocol='ModbusRTU',
            register_addresses=[[68, 0], [70, 1]],
        )
        self.transductor = EnergyTransductor.objects.create(
            serial_number= '87654321',
            ip_address='111.111.111.11',
            broken=False,
            active=True,
            model=self.trans_model,
            firmware_version='12.1.3215',
            physical_location='predio 2 sala 44',
            geolocation_longitude=-24.4556,
            geolocation_latitude=-24.45996
        )
        self.measurement = EnergyMeasurement.objects.create(
            transductor=self.transductor,
            frequency_a = 8,
            voltage_a = 8,
            voltage_b = 8,
            voltage_c = 8,
            current_a = 8,
            current_b = 8,
            current_c = 8,
            active_power_a = 8,
            active_power_b = 8,
            active_power_c = 8,
            total_active_power = 8,
            reactive_power_a = 8,
            reactive_power_b = 8,
            reactive_power_c = 8,
            total_reactive_power = 8,
            apparent_power_a = 8,
            apparent_power_b = 8,
            apparent_power_c = 8,
            total_apparent_power = 8,
            power_factor_a = 8,
            power_factor_b = 8,
            power_factor_c = 8,
            total_power_factor = 8,
            dht_voltage_a = 8,
            dht_voltage_b = 8,
            dht_voltage_c = 8,
            dht_current_a = 8,
            dht_current_b = 8,
            dht_current_c = 8,
            consumption_a = 8,
            consumption_b = 8,
            consumption_c = 8,
            total_consumption = 8,
        )

    def test_create_energy_measurement_with_defaults(self):
        size = len(EnergyMeasurement.objects.all())

        en_measurement = EnergyMeasurement()
        en_measurement.transductor = self.transductor

        self.assertIsNone(en_measurement.save())
        self.assertEqual(size+1, len(EnergyMeasurement.objects.all()))

    def test_create_energy_measurement(self):
        size = len(EnergyMeasurement.objects.all())

        en_measurement = EnergyMeasurement()
        en_measurement.transductor = self.transductor
        en_measurement.frequency_a = 666
        en_measurement.voltage_a = 666
        en_measurement.voltage_b = 666
        en_measurement.voltage_c = 666
        en_measurement.current_a = 666
        en_measurement.current_b = 666
        en_measurement.current_c = 666
        en_measurement.active_power_a = 666
        en_measurement.active_power_b = 666
        en_measurement.active_power_c = 666
        en_measurement.total_active_power = 666
        en_measurement.reactive_power_a = 666
        en_measurement.reactive_power_b = 666
        en_measurement.reactive_power_c = 666
        en_measurement.total_reactive_power = 666
        en_measurement.apparent_power_a = 666
        en_measurement.apparent_power_b = 666
        en_measurement.apparent_power_c = 666
        en_measurement.total_apparent_power = 666
        en_measurement.power_factor_a = 666
        en_measurement.power_factor_b = 666
        en_measurement.power_factor_c = 666
        en_measurement.total_power_factor = 666
        en_measurement.dht_voltage_a = 666
        en_measurement.dht_voltage_b = 666
        en_measurement.dht_voltage_c = 666
        en_measurement.dht_current_a = 666
        en_measurement.dht_current_b = 666
        en_measurement.dht_current_c = 666
        en_measurement.consumption_a = 666
        en_measurement.consumption_b = 666
        en_measurement.consumption_c = 666
        en_measurement.total_consumption = 666

        self.assertIsNone(en_measurement.save())
        self.assertEqual(size+1, len(EnergyMeasurement.objects.all()))

    def test_not_create_energy_measurement_empty_transductor(self):
        size = len(EnergyTransductor.objects.all())

        en_measurement = EnergyMeasurement()

        with self.assertRaises(IntegrityError):
            en_measurement.save()

    def test_update_energy_measurement(self):
        energy_measurement = EnergyMeasurement()
        energy_measurement.transductor = EnergyTransductor.objects.get(
            serial_number=87654321
        )
        energy_measurement.save()

        energy_measurement.total_consumption = 100

        self.assertEquals(
            None,
            energy_measurement.save(update_fields=['total_consumption'])
        )

        self.assertTrue(100, energy_measurement.total_consumption)

    def test_delete_measurement(self):
        size = len(EnergyMeasurement.objects.all())
        EnergyMeasurement.objects.filter(consumption_a='8').delete()

        self.assertEqual(size-1, len(EnergyMeasurement.objects.all()))

    def test_not_delete_nonexistent_transductor(self):
        size = len(EnergyMeasurement.objects.all())
        value = '8'

        EnergyMeasurement.objects.get(
            total_consumption=8
        ).delete()

        self.assertEqual(size-1, len(EnergyMeasurement.objects.all()))

        with self.assertRaises(EnergyMeasurement.DoesNotExist):
            EnergyMeasurement.objects.get(
                total_consumption=8
            ).delete()
