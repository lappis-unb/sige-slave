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


class EnergyMeasurementTestCase(TestCase):

    def setUp(self):
        self.transductor = EnergyTransductor.objects.create(
            serial_number='87654321',
            ip_address='111.111.111.11',
            broken=False,
            active=True,
            model="EnergyTransductor",
            firmware_version='12.1.3215',
            physical_location='predio 2 sala 44',
            geolocation_longitude=-24.4556,
            geolocation_latitude=-24.45996,
            installation_date=datetime.now()
        )
        self.minutely_measurement = MinutelyMeasurement.objects.create(
            transductor_collection_date=timezone.datetime(2019, 2, 5, 14, 0, 0),
            slave_collection_date=timezone.datetime(2019, 2, 5, 14, 0, 0),
            transductor=self.transductor,
            frequency_a=8,
            voltage_a=8,
            voltage_b=8,
            voltage_c=8,
            current_a=8,
            current_b=8,
            current_c=8,
            active_power_a=8,
            active_power_b=8,
            active_power_c=8,
            total_active_power=8,
            reactive_power_a=8,
            reactive_power_b=8,
            reactive_power_c=8,
            total_reactive_power=8,
            apparent_power_a=8,
            apparent_power_b=8,
            apparent_power_c=8,
            total_apparent_power=8,
            power_factor_a=8,
            power_factor_b=8,
            power_factor_c=8,
            total_power_factor=8,
            dht_voltage_a=8,
            dht_voltage_b=8,
            dht_voltage_c=8,
            dht_current_a=8,
            dht_current_b=8,
            dht_current_c=8,
        )

        self.quarterly_measurement = QuarterlyMeasurement.objects.create(
            transductor_collection_date=timezone.datetime(2019, 2, 5, 14, 0, 0),
            slave_collection_date=timezone.datetime(2019, 2, 5, 14, 0, 0),
            transductor=self.transductor,
            generated_energy_peak_time=8,
            generated_energy_off_peak_time=8,
            consumption_peak_time=8,
            consumption_off_peak_time=8,
            inductive_power_peak_time=8,
            inductive_power_off_peak_time=8,
            capacitive_power_peak_time=8,
            capacitive_power_off_peak_time=8
        )

        self.monthly_measurement = MonthlyMeasurement.objects.create(
            transductor_collection_date=timezone.datetime(2019, 2, 5, 14, 0, 0),
            slave_collection_date=timezone.datetime(2019, 2, 5, 14, 0, 0),
            transductor=self.transductor,
            generated_energy_peak_time=8,
            generated_energy_off_peak_time=8,
            consumption_peak_time=8,
            consumption_off_peak_time=8,
            inductive_power_peak_time=8,
            inductive_power_off_peak_time=8,
            capacitive_power_peak_time=8,
            capacitive_power_off_peak_time=8,
            active_max_power_peak_time=8,
            active_max_power_off_peak_time=8,
            reactive_max_power_peak_time=8,
            reactive_max_power_off_peak_time=8,
            active_max_power_list_peak=[
                0.0, 0.0, 0.0, 0.0
            ],
            active_max_power_list_peak_time=[
                timezone.datetime(2019, 2, 5, 14, 0, 0),
                timezone.datetime(2019, 2, 5, 14, 0, 0),
                timezone.datetime(2019, 2, 5, 14, 0, 0),
                timezone.datetime(2019, 2, 5, 14, 0, 0)
            ],
            active_max_power_list_off_peak=[
                0.0, 0.0, 0.0, 0.0
            ],
            active_max_power_list_off_peak_time=[
                timezone.datetime(2019, 2, 5, 14, 0, 0),
                timezone.datetime(2019, 2, 5, 14, 0, 0),
                timezone.datetime(2019, 2, 5, 14, 0, 0),
                timezone.datetime(2019, 2, 5, 14, 0, 0)
            ],
            reactive_max_power_list_peak=[
                0.0, 0.0, 0.0, 0.0
            ],
            reactive_max_power_list_peak_time=[
                timezone.datetime(2019, 2, 5, 14, 0, 0),
                timezone.datetime(2019, 2, 5, 14, 0, 0),
                timezone.datetime(2019, 2, 5, 14, 0, 0),
                timezone.datetime(2019, 2, 5, 14, 0, 0)
            ],

            reactive_max_power_list_off_peak=[
                0.0, 0.0, 0.0, 0.0
            ],
            reactive_max_power_list_off_peak_time=[
                timezone.datetime(2019, 2, 5, 14, 0, 0),
                timezone.datetime(2019, 2, 5, 14, 0, 0),
                timezone.datetime(2019, 2, 5, 14, 0, 0),
                timezone.datetime(2019, 2, 5, 14, 0, 0)
            ]
        )

    """
    MinutelyMeasurementTests
    """

    def test_create_minutely_energy_measurement_with_defaults(self):
        size = len(MinutelyMeasurement.objects.all())

        minutely_en_measurement = MinutelyMeasurement()
        minutely_en_measurement.transductor = self.transductor

        self.assertIsNone(minutely_en_measurement.save())
        self.assertEqual(size + 1, len(MinutelyMeasurement.objects.all()))

    def test_create_minutely_energy_measurement(self):
        size = len(MinutelyMeasurement.objects.all())

        minutely_en_measurement = MinutelyMeasurement()
        minutely_en_measurement.slave_collection_date = \
            timezone.datetime(2019, 2, 5, 14, 0, 0)
        minutely_en_measurement.transductor_collection_date = \
            timezone.datetime(2019, 2, 5, 14, 0, 0)
        minutely_en_measurement.transductor = self.transductor
        minutely_en_measurement.frequency_a = 666
        minutely_en_measurement.voltage_a = 666
        minutely_en_measurement.voltage_b = 666
        minutely_en_measurement.voltage_c = 666
        minutely_en_measurement.current_a = 666
        minutely_en_measurement.current_b = 666
        minutely_en_measurement.current_c = 666
        minutely_en_measurement.active_power_a = 666
        minutely_en_measurement.active_power_b = 666
        minutely_en_measurement.active_power_c = 666
        minutely_en_measurement.total_active_power = 666
        minutely_en_measurement.reactive_power_a = 666
        minutely_en_measurement.reactive_power_b = 666
        minutely_en_measurement.reactive_power_c = 666
        minutely_en_measurement.total_reactive_power = 666
        minutely_en_measurement.apparent_power_a = 666
        minutely_en_measurement.apparent_power_b = 666
        minutely_en_measurement.apparent_power_c = 666
        minutely_en_measurement.total_apparent_power = 666
        minutely_en_measurement.power_factor_a = 666
        minutely_en_measurement.power_factor_b = 666
        minutely_en_measurement.power_factor_c = 666
        minutely_en_measurement.total_power_factor = 666
        minutely_en_measurement.dht_voltage_a = 666
        minutely_en_measurement.dht_voltage_b = 666
        minutely_en_measurement.dht_voltage_c = 666
        minutely_en_measurement.dht_current_a = 666
        minutely_en_measurement.dht_current_b = 666
        minutely_en_measurement.dht_current_c = 666

        self.assertIsNone(minutely_en_measurement.save())
        self.assertEqual(size + 1, len(MinutelyMeasurement.objects.all()))

    def test_not_create_minutely_energy_measurement_empty_transductor(self):
        en_measurement = MinutelyMeasurement()

        with self.assertRaises(IntegrityError):
            en_measurement.save()

    def test_update_minutely_energy_measurement(self):
        minutely_energy_measurement = MinutelyMeasurement()
        minutely_energy_measurement.transductor = \
            EnergyTransductor.objects.get(
                serial_number=87654321
            )
        minutely_energy_measurement.save()

        minutely_energy_measurement.total_power_factor = 100

        self.assertEqual(
            None,
            minutely_energy_measurement.save(
                update_fields=['total_power_factor']
            )
        )

        self.assertTrue(100, minutely_energy_measurement.total_power_factor)

    def test_delete_minutely_measurement(self):
        size = len(MinutelyMeasurement.objects.all())
        value = '8'
        MinutelyMeasurement.objects.filter(total_power_factor=value).delete()

        self.assertEqual(size - 1, len(MinutelyMeasurement.objects.all()))

    def test_not_delete_inexistent_transductor_minutely_measures(self):
        size = len(MinutelyMeasurement.objects.all())
        value = '8'

        MinutelyMeasurement.objects.get(
            total_power_factor=value
        ).delete()

        self.assertEqual(size - 1, len(MinutelyMeasurement.objects.all()))

        with self.assertRaises(MinutelyMeasurement.DoesNotExist):
            MinutelyMeasurement.objects.get(
                total_power_factor=value
            ).delete()

    """
    QuarterlyMeasurementTests
    """

    def test_create_quarterly_energy_measurement_with_defaults(self):
        size = len(QuarterlyMeasurement.objects.all())

        quarterly_en_measurement = QuarterlyMeasurement()
        quarterly_en_measurement.transductor = self.transductor

        self.assertIsNone(quarterly_en_measurement.save())
        self.assertEqual(size + 1, len(QuarterlyMeasurement.objects.all()))

    def test_create_quarterly_energy_measurement(self):
        size = len(QuarterlyMeasurement.objects.all())

        quarterly_en_measurement = QuarterlyMeasurement()
        quarterly_en_measurement.slave_collection_date = \
            timezone.datetime(2019, 2, 5, 14, 0, 0)
        quarterly_en_measurement.transductor_collection_date = \
            timezone.datetime(2019, 2, 5, 14, 0, 0)
        quarterly_en_measurement.transductor = self.transductor
        quarterly_en_measurement.generated_energy_peak_time = 31
        quarterly_en_measurement.generated_energy_off_peak_time = 31
        quarterly_en_measurement.consumption_peak_time = 31
        quarterly_en_measurement.consumption_off_peak_time = 31
        quarterly_en_measurement.inductive_power_peak_time = 31
        quarterly_en_measurement.inductive_power_off_peak_time = 31
        quarterly_en_measurement.capacitive_power_peak_time = 31
        quarterly_en_measurement.capacitive_power_off_peak_time = 31
        quarterly_en_measurement.active_max_power_peak_time = 31
        quarterly_en_measurement.active_max_power_off_peak_time = 31
        quarterly_en_measurement.reactive_max_power_peak_time = 31
        quarterly_en_measurement.reactive_max_power_off_peak_time = 31

        self.assertIsNone(quarterly_en_measurement.save())
        self.assertEqual(size + 1, len(QuarterlyMeasurement.objects.all()))

    def test_not_create_quarterly_energy_measurement_empty_transductor(self):
        en_measurement = QuarterlyMeasurement()

        with self.assertRaises(IntegrityError):
            en_measurement.save()

    def test_update_quarterly_energy_measurement(self):
        quarterly_energy_measurement = QuarterlyMeasurement()
        quarterly_energy_measurement.transductor = \
            EnergyTransductor.objects.get(
                serial_number=87654321
            )
        quarterly_energy_measurement.save()

        quarterly_energy_measurement.generated_energy_peak_time = 9

        self.assertEqual(
            None,
            quarterly_energy_measurement.save(
                update_fields=['generated_energy_peak_time']
            )
        )

        self.assertTrue(
            9, quarterly_energy_measurement.generated_energy_peak_time
        )

    def test_delete_quarterly_measurement(self):
        size = len(QuarterlyMeasurement.objects.all())
        value = '8'
        QuarterlyMeasurement.objects.filter(
            generated_energy_peak_time=value
        ).delete()

        self.assertEqual(size - 1, len(QuarterlyMeasurement.objects.all()))

    def test_not_delete_inexistent_transductor_quarterly_measures(self):
        size = len(QuarterlyMeasurement.objects.all())
        value = '8'

        QuarterlyMeasurement.objects.get(
            generated_energy_peak_time=value
        ).delete()

        self.assertEqual(size - 1, len(QuarterlyMeasurement.objects.all()))

        with self.assertRaises(QuarterlyMeasurement.DoesNotExist):
            QuarterlyMeasurement.objects.get(
                generated_energy_peak_time=value
            ).delete()

    """
    MonthlyMeasurementTests
    """

    def test_create_monthly_energy_measurement_with_defaults(self):
        size = len(MonthlyMeasurement.objects.all())

        monthly_en_measurement = MonthlyMeasurement()
        monthly_en_measurement.slave_collection_date = \
            timezone.datetime(2019, 2, 5, 14, 0, 0)
        monthly_en_measurement.transductor_collection_date = \
            timezone.datetime(2019, 2, 5, 14, 0, 0)
        monthly_en_measurement.transductor = self.transductor
        monthly_en_measurement.active_max_power_list_peak_time = []
        monthly_en_measurement.active_max_power_list_peak = []
        monthly_en_measurement.active_max_power_list_off_peak_time = []
        monthly_en_measurement.active_max_power_list_off_peak = []
        monthly_en_measurement.reactive_max_power_list_peak_time = []
        monthly_en_measurement.reactive_max_power_list_peak = []
        monthly_en_measurement.reactive_max_power_list_off_peak_time = []
        monthly_en_measurement.reactive_max_power_list_off_peak = []

        self.assertIsNone(monthly_en_measurement.save())
        self.assertEqual(size + 1, len(MonthlyMeasurement.objects.all()))

    def test_create_monthly_energy_measurement(self):
        size = len(MonthlyMeasurement.objects.all())

        monthly_en_measurement = MonthlyMeasurement()
        monthly_en_measurement.slave_collection_date = \
            timezone.datetime(2019, 2, 5, 14, 0, 0)
        monthly_en_measurement.trasnductor_collection_date = \
            timezone.datetime(2019, 2, 5, 14, 0, 0)
        monthly_en_measurement.transductor = self.transductor
        monthly_en_measurement.generated_energy_peak_time = 9
        monthly_en_measurement.generated_energy_off_peak_time = 9
        monthly_en_measurement.consumption_peak_time = 9
        monthly_en_measurement.consumption_off_peak_time = 9
        monthly_en_measurement.inductive_power_peak_time = 9
        monthly_en_measurement.inductive_power_off_peak_time = 9
        monthly_en_measurement.capacitive_power_peak_time = 9
        monthly_en_measurement.capacitive_power_off_peak_time = 9
        monthly_en_measurement.active_max_power_peak_time = 9
        monthly_en_measurement.active_max_power_off_peak_time = 9
        monthly_en_measurement.reactive_max_power_peak_time = 9
        monthly_en_measurement.reactive_max_power_off_peak_time = 9
        monthly_en_measurement.active_max_power_list_peak_time = []
        monthly_en_measurement.active_max_power_list_peak = []
        monthly_en_measurement.active_max_power_list_off_peak_time = []
        monthly_en_measurement.active_max_power_list_off_peak = []
        monthly_en_measurement.reactive_max_power_list_peak_time = []
        monthly_en_measurement.reactive_max_power_list_peak = []
        monthly_en_measurement.reactive_max_power_list_off_peak_time = []
        monthly_en_measurement.reactive_max_power_list_off_peak = []

        self.assertIsNone(monthly_en_measurement.save())
        self.assertEqual(size + 1, len(MonthlyMeasurement.objects.all()))

    def test_not_create_monthly_energy_measurement_empty_transductor(self):
        en_measurement = MonthlyMeasurement()

        with self.assertRaises(IntegrityError):
            en_measurement.save()

    def test_update_monthly_energy_measurement(self):
        monthly_energy_measurement = MonthlyMeasurement()
        monthly_energy_measurement.transductor = \
            EnergyTransductor.objects.get(
                serial_number=87654321
            )
        monthly_energy_measurement.active_max_power_list_peak_time = []
        monthly_energy_measurement.active_max_power_list_peak = []
        monthly_energy_measurement.active_max_power_list_off_peak_time = []
        monthly_energy_measurement.active_max_power_list_off_peak = []
        monthly_energy_measurement.reactive_max_power_list_peak_time = []
        monthly_energy_measurement.reactive_max_power_list_peak = []
        monthly_energy_measurement.reactive_max_power_list_off_peak_time = []
        monthly_energy_measurement.reactive_max_power_list_off_peak = []
        monthly_energy_measurement.save()

        monthly_energy_measurement.generated_energy_peak_time = 9

        self.assertEqual(
            None,
            monthly_energy_measurement.save(
                update_fields=['generated_energy_peak_time']
            )
        )

        self.assertTrue(
            9, monthly_energy_measurement.generated_energy_peak_time
        )

    def test_delete_monthly_measurement(self):
        size = len(MonthlyMeasurement.objects.all())
        value = '8'
        MonthlyMeasurement.objects.filter(
            generated_energy_peak_time=value
        ).delete()

        self.assertEqual(size - 1, len(MonthlyMeasurement.objects.all()))

    def test_not_delete_inexistent_transductor_monthly_measures(self):
        size = len(MonthlyMeasurement.objects.all())
        value = '8'

        MonthlyMeasurement.objects.get(
            generated_energy_peak_time=value
        ).delete()

        self.assertEqual(size - 1, len(MonthlyMeasurement.objects.all()))

        with self.assertRaises(MonthlyMeasurement.DoesNotExist):
            MonthlyMeasurement.objects.get(
                generated_energy_peak_time=8
            ).delete()
