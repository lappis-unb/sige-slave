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


class TransductorTestCase(TestCase):

    def setUp(self):
        self.trans_model = TransductorModel.objects.create(
            name='TR4020',
            transport_protocol='UDP',
            serial_protocol='ModbusRTU',
            register_addresses=[[68, 0], [70, 1]],
        )
        self.transductor = EnergyTransductor.objects.create(
            serial_number='87654321',
            ip_address='192.168.10.3',
            broken=False,
            active=True,
            model=self.trans_model,
            firmware_version='12.1.3215',
            physical_location='predio 2 sala 44',
            geolocation_longitude=-24.4556,
            geolocation_latitude=-24.45996,
        )

    def test_create_energy_transductor(self):
        size = len(EnergyTransductor.objects.all())

        energy_transductor = EnergyTransductor()
        energy_transductor.serial_number = '12345678'
        energy_transductor.ip_address = '1.1.1.1'
        energy_transductor.broken = False
        energy_transductor.active = True
        energy_transductor.model = self.trans_model
        energy_transductor.firmware_version = '12.1.3215'
        energy_transductor.physical_location = 'predio 2 sala 44'
        energy_transductor.geolocation_longitude = -24.4556
        energy_transductor.geolocation_latitude = -24.45996

        self.assertIsNone(energy_transductor.save())
        self.assertEqual(size + 1, len(EnergyTransductor.objects.all()))

    def test_not_create_energy_transductor_no_firmware(self):
        size = len(EnergyTransductor.objects.all())

        transductor = EnergyTransductor()
        transductor.serial_number = '123456789'
        transductor.ip_address = '1.1.1.1'
        transductor.broken = False
        transductor.active = True
        transductor.model = self.trans_model
        transductor.physical_location = 'predio 2 sala 44'
        transductor.geolocation_longitude = -24.4556
        transductor.geolocation_latitude = -24.45996

        with self.assertRaises(DataError):
            transductor.save()

    def test_not_create_energy_transductor_no_geolocation_latitude(self):
        size = len(EnergyTransductor.objects.all())

        transductor = EnergyTransductor()
        transductor.serial_number = '123456789'
        transductor.ip_address = '1.1.1.1'
        transductor.broken = False
        transductor.active = True
        transductor.model = self.trans_model
        transductor.firmware_version = '12.1.3215'
        transductor.physical_location = 'predio 2 sala 44'
        transductor.geolocation_longitude = -24.4556

        with self.assertRaises(DataError):
            transductor.save()

    def test_not_create_energy_transductor_no_geolocation_longitude(self):
        size = len(EnergyTransductor.objects.all())

        transductor = EnergyTransductor()
        transductor.serial_number = '123456789'
        transductor.ip_address = '1.1.1.1'
        transductor.broken = False
        transductor.active = True
        transductor.model = self.trans_model
        transductor.firmware_version = '12.1.3215'
        transductor.physical_location = 'predio 2 sala 44'
        transductor.geolocation_latitude = -24.4556

        with self.assertRaises(DataError):
            transductor.save()

    def test_not_create_energy_transductor_wrong_serial_number(self):
        size = len(EnergyTransductor.objects.all())

        transductor = EnergyTransductor()
        transductor.serial_number = '123456789'
        transductor.ip_address = '1.1.1.1'
        transductor.broken = False
        transductor.active = True
        transductor.model = self.trans_model

        with self.assertRaises(DataError):
            transductor.save()

    def test_not_create_energy_transductor_empty_serial_number(self):
        size = len(EnergyTransductor.objects.all())

        transductor = EnergyTransductor()
        transductor.serial_number = ''
        transductor.ip_address = '1.1.1.1'
        transductor.broken = False
        transductor.active = True
        transductor.model = self.trans_model

        with self.assertRaises(IntegrityError):
            transductor.save()

    def test_not_create_energy_transductor_no_transductor_model(self):
        size = len(EnergyTransductor.objects.all())

        energy_transductor = EnergyTransductor()
        energy_transductor.serial_number = '12345678'
        energy_transductor.ip_address = ''
        energy_transductor.broken = False
        energy_transductor.active = True

        with self.assertRaises(IntegrityError):
            energy_transductor.save()

    def test_update_transductor_serial_number(self):
        energy_transductor = EnergyTransductor.objects.filter(
            serial_number='87654321'
        )

        self.assertTrue(
            energy_transductor.update(serial_number='12345677')
        )

    def test_not_update_transductor_wrong_serial_number(self):
        energy_transductor = EnergyTransductor.objects.filter(
            serial_number='87654321'
        )

        with self.assertRaises(DataError):
            energy_transductor.update(serial_number='12345677777')

    def test_update_transductor_ip_address(self):
        energy_transductor = EnergyTransductor.objects.filter(
            serial_number='87654321'
        )

        self.assertTrue(
            energy_transductor.update(ip_address='111.111.111.111')
        )

    def test_set_transductor_broken_status(self):
        energy_transductor = EnergyTransductor.objects.get(
            serial_number='87654321'
        )

        old_status = energy_transductor.broken

        self.assertEqual(None, energy_transductor.set_broken(not old_status))
        self.assertTrue(energy_transductor.broken != old_status)

    def test_delete_transductor(self):
        size = len(EnergyTransductor.objects.all())
        EnergyTransductor.objects.filter(serial_number='87654321').delete()

        self.assertEqual(size - 1, len(EnergyTransductor.objects.all()))

    def test_not_delete_nonexistent_transductor(self):
        size = len(EnergyTransductor.objects.all())
        transductor_serial = '87654321'

        EnergyTransductor.objects.get(
            serial_number=transductor_serial
        ).delete()

        self.assertEqual(size - 1, len(EnergyTransductor.objects.all()))

        with self.assertRaises(EnergyTransductor.DoesNotExist):
            EnergyTransductor.objects.get(
                serial_number=transductor_serial
            ).delete()

    def test_get_all_transductor_measurements(self):
        energy_transductor = EnergyTransductor.objects.get(
            serial_number='87654321'
        )

        self._set_measurements(energy_transductor)
        self.assertEqual(
            12,
            len(energy_transductor.get_measurements())
        )

    def test_get_transductor_meassurements_by_date(self):
        energy_transductor = EnergyTransductor.objects.get(
            serial_number='87654321'
        )

        start_date = datetime(2019, 1, 1, 00, 00, 00, 188939)
        final_date = datetime(2019, 1, 2, 00, 00, 00, 188939)

        self._set_measurements(energy_transductor)
        self.assertEqual(
            4,
            len(
                energy_transductor.get_measurements_by_datetime(
                    start_date,
                    final_date
                )
            )
        )

    def test_get_transductor_meassurements_by_time(self):
        energy_transductor = EnergyTransductor.objects.get(
            serial_number='87654321'
        )

        start_date = datetime(2019, 1, 1, 12, 00, 00, 188939)
        final_date = datetime(2019, 1, 1, 14, 00, 00, 188939)

        self._set_measurements(energy_transductor)
        self.assertEqual(
            3,
            len(
                energy_transductor.get_measurements_by_datetime(
                    start_date,
                    final_date
                )
            )
        )

    def _set_measurements(self, energy_transductor):
        """
            Creates twelve measurements in three days, four in each day.
        """

        datetimes = [
            datetime(2019, 1, 1, 12, 00, 00, 188939),
            datetime(2019, 1, 1, 13, 00, 00, 188939),
            datetime(2019, 1, 1, 14, 00, 00, 188939),
            datetime(2019, 1, 1, 15, 00, 00, 188939),
            datetime(2019, 1, 2, 12, 00, 00, 188939),
            datetime(2019, 1, 2, 13, 00, 00, 188939),
            datetime(2019, 1, 2, 14, 00, 00, 188939),
            datetime(2019, 1, 2, 15, 00, 00, 188939),
            datetime(2019, 1, 3, 12, 00, 00, 188939),
            datetime(2019, 1, 3, 13, 00, 00, 188939),
            datetime(2019, 1, 3, 14, 00, 00, 188939),
            datetime(2019, 1, 3, 15, 00, 00, 188939)
        ]

        for date in datetimes:
            EnergyMeasurement.objects.create(
                collection_date=date,
                transductor=energy_transductor
            )
