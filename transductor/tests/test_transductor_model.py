from django.test import TestCase
from django.conf import settings
from django.db import IntegrityError
from django.db.utils import DataError
from transductor.models import EnergyTransductor
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from measurement.models import MinutelyMeasurement
from measurement.models import QuarterlyMeasurement
from measurement.models import MonthlyMeasurement
from django.shortcuts import get_object_or_404


class TransductorTestCase(TestCase):
    def setUp(self):
        self.transductor = EnergyTransductor.objects.create(
            serial_number='87654321',
            ip_address='192.168.10.3',
            broken=False,
            active=True,
            model="EnergyTransductor",
            firmware_version='12.1.3215',
            physical_location='predio 2 sala 44',
            geolocation_longitude=-24.4556,
            geolocation_latitude=-24.45996,
            installation_date=datetime.now()
        )

    def test_create_energy_transductor(self):
        size = len(EnergyTransductor.objects.all())

        energy_transductor = EnergyTransductor()
        energy_transductor.serial_number = '12345678'
        energy_transductor.ip_address = '1.1.1.1'
        energy_transductor.broken = False
        energy_transductor.active = True
        energy_transductor.model = "EnergyTransductor"
        energy_transductor.firmware_version = '12.1.3215'
        energy_transductor.physical_location = 'predio 2 sala 44'
        energy_transductor.geolocation_longitude = -24.4556
        energy_transductor.geolocation_latitude = -24.45996
        energy_transductor.installation_date = datetime.now()

        self.assertIsNone(energy_transductor.save())
        self.assertEqual(size + 1, len(EnergyTransductor.objects.all()))

    def test_not_create_energy_transductor_no_firmware(self):
        size = len(EnergyTransductor.objects.all())

        transductor = EnergyTransductor()
        transductor.serial_number = '123456789'
        transductor.ip_address = '1.1.1.1'
        transductor.broken = False
        transductor.active = True
        transductor.model = "EnergyTransductor"
        transductor.physical_location = 'predio 2 sala 44'
        transductor.geolocation_longitude = -24.4556
        transductor.geolocation_latitude = -24.45996
        transductor.installation_date = datetime.now()

        with self.assertRaises(DataError):
            transductor.save()

    def test_not_create_energy_transductor_no_geolocation_latitude(self):
        size = len(EnergyTransductor.objects.all())

        transductor = EnergyTransductor()
        transductor.serial_number = '123456789'
        transductor.ip_address = '1.1.1.1'
        transductor.broken = False
        transductor.active = True
        transductor.model = "EnergyTransductor"
        transductor.firmware_version = '12.1.3215'
        transductor.physical_location = 'predio 2 sala 44'
        transductor.geolocation_longitude = -24.4556
        transductor.installation_date = datetime.now()

        with self.assertRaises(DataError):
            transductor.save()

    def test_not_create_energy_transductor_no_geolocation_longitude(self):
        size = len(EnergyTransductor.objects.all())

        transductor = EnergyTransductor()
        transductor.serial_number = '123456789'
        transductor.ip_address = '1.1.1.1'
        transductor.broken = False
        transductor.active = True
        transductor.model = "EnergyTransductor"
        transductor.firmware_version = '12.1.3215'
        transductor.physical_location = 'predio 2 sala 44'
        transductor.geolocation_latitude = -24.4556
        transductor.installation_date = datetime.now()

        with self.assertRaises(DataError):
            transductor.save()

    def test_not_create_energy_transductor_wrong_serial_number(self):
        size = len(EnergyTransductor.objects.all())

        transductor = EnergyTransductor()
        transductor.serial_number = '123456789'
        transductor.ip_address = '1.1.1.1'
        transductor.broken = False
        transductor.active = True
        transductor.model = "EnergyTransductor"
        transductor.installation_date = datetime.now()

        with self.assertRaises(DataError):
            transductor.save()

    def test_not_create_energy_transductor_empty_serial_number(self):
        size = len(EnergyTransductor.objects.all())

        transductor = EnergyTransductor()
        transductor.serial_number = ''
        transductor.ip_address = '1.1.1.1'
        transductor.broken = False
        transductor.active = True
        transductor.model = "EnergyTransductor"
        transductor.installation_date = datetime.now()

        with self.assertRaises(IntegrityError):
            transductor.save()

    def test_not_create_energy_transductor_no_transductor_model(self):
        size = len(EnergyTransductor.objects.all())

        energy_transductor = EnergyTransductor()
        energy_transductor.serial_number = '12345678'
        energy_transductor.ip_address = ''
        energy_transductor.broken = False
        energy_transductor.active = True
        energy_transductor.installation_date = datetime.now()

        with self.assertRaises(IntegrityError):
            energy_transductor.save()

    def test_not_update_transductor_wrong_serial_number(self):
        energy_transductor = EnergyTransductor.objects.get(
            serial_number='87654321'
        )

        energy_transductor.serial_number = '12345677777'

        with self.assertRaises(DataError):
            energy_transductor.save()

    def test_update_transductor_ip_address(self):
        energy_transductor = EnergyTransductor.objects.get(
            serial_number='87654321'
        )

        energy_transductor.ip_address = '111.111.111.111'

        self.assertIsNone(
            energy_transductor.save()
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
        EnergyTransductor.objects.get(serial_number='87654321').delete()

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
            MinutelyMeasurement.objects.create(
                transductor_collection_date=date,
                slave_collection_date=date,
                transductor=energy_transductor
            )

            QuarterlyMeasurement.objects.create(
                transductor_collection_date=date,
                transductor=energy_transductor
            )

            MonthlyMeasurement.objects.create(
                transductor_collection_date=date,
                transductor=energy_transductor,
                active_max_power_list_peak_time=[],
                active_max_power_list_off_peak_time=[],
                reactive_max_power_list_peak_time=[],
                reactive_max_power_list_off_peak_time=[]
            )
