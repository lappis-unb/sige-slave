from datetime import datetime

from django.db import IntegrityError
from django.db.utils import DataError
from django.test import TestCase

from events.models import FailedConnectionTransductorEvent
from measurement.models import (
    MinutelyMeasurement,
    MonthlyMeasurement,
    QuarterlyMeasurement,
)
from transductor.models import Transductor


class TransductorTestCase(TestCase):
    def setUp(self):
        self.transductor = Transductor.objects.create(
            serial_number="87654321",
            ip_address="192.168.10.3",
            broken=False,
            active=True,
            model="Transductor",
            firmware_version="12.1.3215",
            physical_location="predio 2 sala 44",
            geolocation_longitude=-24.4556,
            geolocation_latitude=-24.45996,
            installation_date=datetime.now(),
        )

    def test_create_energy_transductor(self):
        size = len(Transductor.objects.all())

        energy_transductor = Transductor()
        energy_transductor.serial_number = "12345678"
        energy_transductor.ip_address = "1.1.1.1"
        energy_transductor.broken = False
        energy_transductor.active = True
        energy_transductor.model = "Transductor"
        energy_transductor.firmware_version = "12.1.3215"
        energy_transductor.physical_location = "predio 2 sala 44"
        energy_transductor.geolocation_longitude = -24.4556
        energy_transductor.geolocation_latitude = -24.45996
        energy_transductor.installation_date = datetime.now()

        self.assertIsNone(energy_transductor.save())
        self.assertEqual(size + 1, len(Transductor.objects.all()))

    def test_not_create_energy_transductor_no_firmware(self):
        size = len(Transductor.objects.all())

        transductor = Transductor()
        transductor.serial_number = "123456789"
        transductor.ip_address = "1.1.1.1"
        transductor.broken = False
        transductor.active = True
        transductor.model = "Transductor"
        transductor.physical_location = "predio 2 sala 44"
        transductor.geolocation_longitude = -24.4556
        transductor.geolocation_latitude = -24.45996
        transductor.installation_date = datetime.now()

        with self.assertRaises(DataError):
            transductor.save()

    def test_not_create_energy_transductor_no_geolocation_latitude(self):
        size = len(Transductor.objects.all())

        transductor = Transductor()
        transductor.serial_number = "123456789"
        transductor.ip_address = "1.1.1.1"
        transductor.broken = False
        transductor.active = True
        transductor.model = "Transductor"
        transductor.firmware_version = "12.1.3215"
        transductor.physical_location = "predio 2 sala 44"
        transductor.geolocation_longitude = -24.4556
        transductor.installation_date = datetime.now()

        with self.assertRaises(DataError):
            transductor.save()

    def test_not_create_energy_transductor_no_geolocation_longitude(self):
        size = len(Transductor.objects.all())

        transductor = Transductor()
        transductor.serial_number = "123456789"
        transductor.ip_address = "1.1.1.1"
        transductor.broken = False
        transductor.active = True
        transductor.model = "Transductor"
        transductor.firmware_version = "12.1.3215"
        transductor.physical_location = "predio 2 sala 44"
        transductor.geolocation_latitude = -24.4556
        transductor.installation_date = datetime.now()

        with self.assertRaises(DataError):
            transductor.save()

    def test_not_create_energy_transductor_wrong_serial_number(self):
        size = len(Transductor.objects.all())

        transductor = Transductor()
        transductor.serial_number = "123456789"
        transductor.ip_address = "1.1.1.1"
        transductor.broken = False
        transductor.active = True
        transductor.model = "Transductor"
        transductor.installation_date = datetime.now()

        with self.assertRaises(DataError):
            transductor.save()

    def test_not_create_energy_transductor_empty_serial_number(self):
        size = len(Transductor.objects.all())

        transductor = Transductor()
        transductor.serial_number = ""
        transductor.ip_address = "1.1.1.1"
        transductor.broken = False
        transductor.active = True
        transductor.model = "Transductor"
        transductor.installation_date = datetime.now()

        with self.assertRaises(IntegrityError):
            transductor.save()

    def test_not_create_energy_transductor_no_transductor_model(self):
        size = len(Transductor.objects.all())

        energy_transductor = Transductor()
        energy_transductor.serial_number = "12345678"
        energy_transductor.ip_address = ""
        energy_transductor.broken = False
        energy_transductor.active = True
        energy_transductor.installation_date = datetime.now()
        energy_transductor.serial_number = "12345677777"

        with self.assertRaises(DataError):
            energy_transductor.save()

    def test_update_transductor_ip_address(self):
        energy_transductor = Transductor.objects.get(serial_number="87654321")

        energy_transductor.ip_address = "111.111.111.111"

        self.assertIsNone(energy_transductor.save())

    def test_set_broken_method(self):
        self.transductor.broken = False

        # false to false
        self.assertFalse(self.transductor.set_broken(False))
        self.assertFalse(self.transductor.broken)

        qs = FailedConnectionTransductorEvent.objects.all()

        self.assertFalse(
            qs.exists(),
            msg="False to false must not create connection failure events",
        )

        self.assertFalse(
            self.transductor.timeintervals.exists(),
            msg="False to false must not create timeintervals",
        )

        # false to true
        self.assertTrue(self.transductor.set_broken(True))
        self.assertTrue(self.transductor.broken)

        qs = FailedConnectionTransductorEvent.objects.all()

        self.assertTrue(
            qs.exists(),
            msg=("Toggle broken attribute to True must create a " "FailedConnectionTransductorEvent"),
        )

        self.assertEqual(
            qs.count(),
            1,
            msg=("Toggle broken attribute to True must create only one " "FailedConnectionTransductorEvent"),
        )

        self.assertIsNone(
            qs.last().ended_at,
            msg=(
                "Toggle broken attribute to True must create a "
                "FailedConnectionTransductorEvent with ended_at attribute "
                "equals to None"
            ),
        )

        self.assertEqual(
            self.transductor.timeintervals.count(),
            1,
            msg=("Toggle broken attribute to True must create only one " "timeinterval"),
        )

        self.assertTrue(
            self.transductor.timeintervals.exists(),
            msg="Toggle broken attribute to True must create an timeinterval",
        )

        self.assertIsNone(
            self.transductor.timeintervals.last().end,
            msg=("Toggle broken attribute to True must create an timeinterval " "with end attribute equals to None"),
        )

        # true to true
        self.assertTrue(self.transductor.set_broken(True))
        self.assertTrue(self.transductor.broken)

        qs = FailedConnectionTransductorEvent.objects.all()

        self.assertEqual(
            qs.count(),
            1,
            msg=("True to True must not create a " "FailedConnectionTransductorEvent"),
        )

        self.assertEqual(
            self.transductor.timeintervals.count(),
            1,
            msg="True to True must not create a timeintervals",
        )

        self.assertIsNone(
            qs.last().ended_at,
            msg=("True to True must not modify the ended_at attribute of " "FailedConnectionTransductorEvent"),
        )

        self.assertIsNone(
            self.transductor.timeintervals.last().end,
            msg=("True to True must not modify the end attribute of " "timeinterval"),
        )

        # true to false
        self.assertFalse(self.transductor.set_broken(False))
        self.assertFalse(self.transductor.broken)

        qs = FailedConnectionTransductorEvent.objects.all()

        self.assertEqual(
            qs.count(),
            1,
            msg=(
                "Toggle broken attribute to False must create must not modify "
                "the number of FailedConnectionTransductorEvent"
            ),
        )

        self.assertEqual(
            self.transductor.timeintervals.count(),
            1,
            msg=("Toggle broken attribute to False must create must not modify " "the number of timeintervals"),
        )

        self.assertIsNotNone(
            qs.last().ended_at,
            msg=(
                "Toggle broken attribute to False must modify the ended_at "
                "attribute of an existing FailedConnectionTransductorEvent"
            ),
        )

        self.assertIsNotNone(
            self.transductor.timeintervals.last().end,
            msg=("Toggle broken attribute to False must modify the end " "attribute of an existing timeinterval"),
        )

    def test_delete_transductor(self):
        size = len(Transductor.objects.all())
        Transductor.objects.get(serial_number="87654321").delete()

        self.assertEqual(size - 1, len(Transductor.objects.all()))

    def test_not_delete_nonexistent_transductor(self):
        size = len(Transductor.objects.all())
        transductor_serial = "87654321"

        Transductor.objects.get(serial_number=transductor_serial).delete()

        self.assertEqual(size - 1, len(Transductor.objects.all()))

        with self.assertRaises(Transductor.DoesNotExist):
            Transductor.objects.get(serial_number=transductor_serial).delete()

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
            datetime(2019, 1, 3, 15, 00, 00, 188939),
        ]

        for date in datetimes:
            MinutelyMeasurement.objects.create(
                collection_date=date,
                slave_collection_date=date,
                transductor=energy_transductor,
            )

            QuarterlyMeasurement.objects.create(collection_date=date, transductor=energy_transductor)

            MonthlyMeasurement.objects.create(
                collection_date=date,
                transductor=energy_transductor,
                active_max_power_list_peak_time=[],
                active_max_power_list_off_peak_time=[],
                reactive_max_power_list_peak_time=[],
                reactive_max_power_list_off_peak_time=[],
            )
