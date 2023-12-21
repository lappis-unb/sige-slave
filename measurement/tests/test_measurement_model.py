from datetime import datetime

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from events.models import (
    CriticalVoltageEvent,
    Event,
    PhaseDropEvent,
    PrecariousVoltageEvent,
)
from measurement.models import (
    MinutelyMeasurement,
    MonthlyMeasurement,
    QuarterlyMeasurement,
    ReferenceMeasurement
)
from data_collector.modbus.settings import DataGroups
from transductor.models import Transductor
from data_collector.models import MemoryMap


class EnergyMeasurementTestCase(TestCase):
    def setUp(self):
        self.memory_map = MemoryMap.objects.create(
            id=1,
            model_transductor='TR4020',
            minutely=[],
            quarterly=[],
            monthly=[]
        )

        self.transductor = Transductor.objects.create(
            id=1,
            serial_number="87654321",
            ip_address="111.111.111.11",
            port='1234',
            broken=False,
            active=True,
            model="Transductor",
            firmware_version="12.1.3215",
            physical_location="predio 2 sala 44",
            geolocation_longitude=-24.4556,
            geolocation_latitude=-24.45996,
            installation_date=datetime.now(),
            memory_map=self.memory_map
        )
        self.minutely_measurement = MinutelyMeasurement.objects.create(
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

        self.quarterly_reference = ReferenceMeasurement.objects.create(
            collection_date=timezone.datetime(2019, 2, 5, 14, 0, 0),
            slave_collection_date=timezone.datetime(2019, 2, 5, 14, 0, 0),
            transductor=self.transductor,
            data_group=DataGroups.QUARTERLY
        )

        self.quarterly_measurement = QuarterlyMeasurement.objects.create(
            collection_date=timezone.datetime(2019, 2, 5, 14, 0, 0),
            slave_collection_date=timezone.datetime(2019, 2, 5, 14, 0, 0),
            transductor=self.transductor,
            reference_measurement = self.quarterly_reference
        )

        self.monthly_reference = ReferenceMeasurement.objects.create(
            collection_date=timezone.datetime(2019, 2, 5, 14, 0, 0),
            slave_collection_date=timezone.datetime(2019, 2, 5, 14, 0, 0),
            transductor=self.transductor,
            data_group=DataGroups.MONTHLY
        )

        self.monthly_measurement = MonthlyMeasurement.objects.create(
            collection_date=timezone.datetime(2019, 2, 5, 14, 0, 0),
            slave_collection_date=timezone.datetime(2019, 2, 5, 14, 0, 0),
            transductor=self.transductor,
            active_max_power_peak_time=8,
            active_max_power_off_peak_time=8,
            reactive_max_power_peak_time=8,
            reactive_max_power_off_peak_time=8,
            reference_measurement=self.monthly_reference
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
        minutely_en_measurement.slave_collection_date = timezone.datetime(2019, 2, 5, 14, 0, 0)
        minutely_en_measurement.collection_date = timezone.datetime(2019, 2, 5, 14, 0, 0)
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
        minutely_energy_measurement.transductor = Transductor.objects.get(serial_number=87654321)
        minutely_energy_measurement.save()

        minutely_energy_measurement.total_power_factor = 100

        self.assertEqual(None, minutely_energy_measurement.save(update_fields=["total_power_factor"]))

        self.assertTrue(100, minutely_energy_measurement.total_power_factor)

    def test_delete_minutely_measurement(self):
        size = len(MinutelyMeasurement.objects.all())
        value = "8"
        MinutelyMeasurement.objects.filter(total_power_factor=value).delete()

        self.assertEqual(size - 1, len(MinutelyMeasurement.objects.all()))

    def test_not_delete_inexistent_transductor_minutely_measures(self):
        size = len(MinutelyMeasurement.objects.all())
        value = "8"

        MinutelyMeasurement.objects.get(total_power_factor=value).delete()

        self.assertEqual(size - 1, len(MinutelyMeasurement.objects.all()))

        with self.assertRaises(MinutelyMeasurement.DoesNotExist):
            MinutelyMeasurement.objects.get(total_power_factor=value).delete()

    # def test_check_measurements(self):
    #     measurement = MinutelyMeasurement.objects.create(
    #         transductor=self.transductor,
    #         voltage_a=220,
    #         voltage_b=220,
    #         voltage_c=220,
    #     )

    #     # b_ -> before
    #     b_event_qty = Event.objects.count()

    #     measurement.check_measurements()

    #     # a_ -> after
    #     a_event_qty = Event.objects.count()

    #     self.assertEqual(
    #         b_event_qty,
    #         a_event_qty,
    #         msg="The voltage measurements created should not have created an event",
    #     )

    #     measurement = MinutelyMeasurement.objects.create(
    #         transductor=self.transductor,
    #         voltage_a=195,
    #         voltage_b=195,
    #         voltage_c=195,
    #     )
    #     measurement.check_measurements()

    #     # a_ -> after
    #     a_event_qty = Event.objects.count()

    #     self.assertEqual(
    #         b_event_qty + 1,
    #         a_event_qty,
    #         msg="The voltage measurements created should have created an event",
    #     )

    #     last_event = Event.objects.last()

    #     self.assertIsInstance(
    #         last_event,
    #         PrecariousVoltageEvent,
    #         msg=("The event created should have been of the type " "`PrecariousVoltageEvent`"),
    #     )

    #     measurement = MinutelyMeasurement.objects.create(
    #         transductor=self.transductor,
    #         voltage_a=180,
    #         voltage_b=180,
    #         voltage_c=180,
    #     )

    #     measurement.check_measurements()

    #     last_precarious_event = PrecariousVoltageEvent.objects.last()

    #     self.assertIsNotNone(
    #         last_precarious_event.ended_at,
    #         msg="The last open event should have been closed after the change of state",
    #     )

    #     last_event = Event.objects.last()

    #     self.assertIsInstance(
    #         last_event,
    #         CriticalVoltageEvent,
    #         msg=("The event created should have been of the type " "`CriticalVoltageEvent`"),
    #     )

    #     measurement = MinutelyMeasurement.objects.create(
    #         transductor=self.transductor,
    #         voltage_a=100,
    #         voltage_b=100,
    #         voltage_c=100,
    #     )

    #     measurement.check_measurements()

    #     last_critical_event = CriticalVoltageEvent.objects.last()

    #     self.assertIsNotNone(
    #         last_critical_event.ended_at,
    #         msg="The last open event should have been closed after the change of state",
    #     )

    #     last_event = Event.objects.last()

    #     self.assertIsInstance(
    #         last_event,
    #         PhaseDropEvent,
    #         msg=("The event created should have been of the type " "`PhaseDropEvent`"),
    #     )

    #     measurement = MinutelyMeasurement.objects.create(
    #         transductor=self.transductor,
    #         voltage_a=230,
    #         voltage_b=230,
    #         voltage_c=230,
    #     )

    #     measurement.check_measurements()

    #     last_phase_drop_event = PhaseDropEvent.objects.last()

    #     self.assertIsNotNone(
    #         last_phase_drop_event.ended_at,
    #         msg="The last open event should have been closed after the change of state",
    #     )

    #     last_event = Event.objects.last()

    #     self.assertIsInstance(
    #         last_event,
    #         PrecariousVoltageEvent,
    #         msg=("The event created should have been of the type " "`PrecariousVoltageEvent`"),
    #     )

    #     measurement = MinutelyMeasurement.objects.create(
    #         transductor=self.transductor,
    #         voltage_a=250,
    #         voltage_b=250,
    #         voltage_c=250,
    #     )

    #     measurement.check_measurements()

    #     last_precarious_event = PrecariousVoltageEvent.objects.last()

    #     self.assertIsNotNone(
    #         last_precarious_event.ended_at,
    #         msg="The last open event should have been closed after the change of state",
    #     )

    #     last_event = Event.objects.last()

    #     self.assertIsInstance(
    #         last_event,
    #         CriticalVoltageEvent,
    #         msg=("The event created should have been of the type " "`CriticalVoltageEvent`"),
    #     )

    #     measurement = MinutelyMeasurement.objects.create(
    #         transductor=self.transductor,
    #         voltage_a=220,
    #         voltage_b=220,
    #         voltage_c=220,
    #     )
    #     measurement.check_measurements()

    #     all_open_events = Event.objects.filter(ended_at=None)

    #     self.assertTrue(
    #         len(all_open_events) == 0,
    #         msg=("After the last measurement, with normal values, there should be no " "open events"),
    #     )

    """
    QuarterlyMeasurementTests
    """

    def test_create_quarterly_energy_measurement_with_defaults(self):
        size = len(QuarterlyMeasurement.objects.all())

        quarterly_en_measurement = QuarterlyMeasurement()
        quarterly_en_measurement.transductor = self.transductor
        quarterly_en_measurement.reference_measurement = self.quarterly_reference

        self.assertIsNone(quarterly_en_measurement.save())
        self.assertEqual(size + 1, len(QuarterlyMeasurement.objects.all()))

    def test_create_quarterly_energy_measurement(self):
        size = len(QuarterlyMeasurement.objects.all())

        quarterly_en_measurement = QuarterlyMeasurement()
        quarterly_en_measurement.slave_collection_date = timezone.datetime(2019, 2, 5, 14, 0, 0)
        quarterly_en_measurement.collection_date = timezone.datetime(2019, 2, 5, 14, 0, 0)
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
        quarterly_en_measurement.reference_measurement = self.quarterly_reference

        self.assertIsNone(quarterly_en_measurement.save())
        self.assertEqual(size + 1, len(QuarterlyMeasurement.objects.all()))

    def test_not_create_quarterly_energy_measurement_empty_transductor(self):
        en_measurement = QuarterlyMeasurement()

        with self.assertRaises(IntegrityError):
            en_measurement.save()

    def test_update_quarterly_energy_measurement(self):
        quarterly_energy_measurement = QuarterlyMeasurement()
        quarterly_energy_measurement.transductor = Transductor.objects.get(serial_number=87654321)
        quarterly_energy_measurement.reference_measurement = self.quarterly_reference
        quarterly_energy_measurement.save()

        quarterly_energy_measurement.is_calculated = True

        self.assertEqual(
            None,
            quarterly_energy_measurement.save(update_fields=["is_calculated"]),
        )

        self.assertEqual(True, quarterly_energy_measurement.is_calculated)

    def test_delete_quarterly_measurement(self):
        size = len(QuarterlyMeasurement.objects.all())
        value = timezone.datetime(2019, 2, 5, 14, 0, 0)
        QuarterlyMeasurement.objects.filter(collection_date=value).delete()

        self.assertEqual(size - 1, len(QuarterlyMeasurement.objects.all()))

    def test_not_delete_inexistent_transductor_quarterly_measures(self):
        size = len(QuarterlyMeasurement.objects.all())
        value = timezone.datetime(2019, 2, 5, 14, 0, 0)

        QuarterlyMeasurement.objects.get(collection_date=value).delete()

        self.assertEqual(size - 1, len(QuarterlyMeasurement.objects.all()))

        with self.assertRaises(QuarterlyMeasurement.DoesNotExist):
            QuarterlyMeasurement.objects.get(collection_date=value).delete()

    """
    MonthlyMeasurementTests
    """

    def test_create_monthly_energy_measurement_with_defaults(self):
        size = len(MonthlyMeasurement.objects.all())

        monthly_en_measurement = MonthlyMeasurement()
        monthly_en_measurement.slave_collection_date = timezone.datetime(2019, 2, 5, 14, 0, 0)
        monthly_en_measurement.collection_date = timezone.datetime(2019, 2, 5, 14, 0, 0)
        monthly_en_measurement.transductor = self.transductor
        monthly_en_measurement.active_max_power_list_peak_time = []
        monthly_en_measurement.active_max_power_list_peak = []
        monthly_en_measurement.active_max_power_list_off_peak_time = []
        monthly_en_measurement.active_max_power_list_off_peak = []
        monthly_en_measurement.reactive_max_power_list_peak_time = []
        monthly_en_measurement.reactive_max_power_list_peak = []
        monthly_en_measurement.reactive_max_power_list_off_peak_time = []
        monthly_en_measurement.reactive_max_power_list_off_peak = []
        monthly_en_measurement.reference_measurement = self.monthly_reference

        self.assertIsNone(monthly_en_measurement.save())
        self.assertEqual(size + 1, len(MonthlyMeasurement.objects.all()))

    def test_create_monthly_energy_measurement(self):
        size = len(MonthlyMeasurement.objects.all())

        monthly_en_measurement = MonthlyMeasurement()
        monthly_en_measurement.slave_collection_date = timezone.datetime(2019, 2, 5, 14, 0, 0)
        monthly_en_measurement.trasnductor_collection_date = timezone.datetime(2019, 2, 5, 14, 0, 0)
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
        monthly_en_measurement.reference_measurement = self.monthly_reference

        self.assertIsNone(monthly_en_measurement.save())
        self.assertEqual(size + 1, len(MonthlyMeasurement.objects.all()))

    def test_not_create_monthly_energy_measurement_empty_transductor(self):
        en_measurement = MonthlyMeasurement()

        with self.assertRaises(IntegrityError):
            en_measurement.save()

    def test_update_monthly_energy_measurement(self):
        monthly_energy_measurement = MonthlyMeasurement()
        monthly_energy_measurement.transductor = Transductor.objects.get(serial_number=87654321)
        monthly_energy_measurement.active_max_power_list_peak_time = []
        monthly_energy_measurement.active_max_power_list_peak = []
        monthly_energy_measurement.active_max_power_list_off_peak_time = []
        monthly_energy_measurement.active_max_power_list_off_peak = []
        monthly_energy_measurement.reactive_max_power_list_peak_time = []
        monthly_energy_measurement.reactive_max_power_list_peak = []
        monthly_energy_measurement.reactive_max_power_list_off_peak_time = []
        monthly_energy_measurement.reactive_max_power_list_off_peak = []
        monthly_energy_measurement.reference_measurement = self.monthly_reference
        monthly_energy_measurement.save()

        monthly_energy_measurement.active_max_power_peak_time = 9

        self.assertEqual(
            None,
            monthly_energy_measurement.save(update_fields=["active_max_power_peak_time"]),
        )

        self.assertEqual(9, monthly_energy_measurement.active_max_power_peak_time)

    def test_delete_monthly_measurement(self):
        size = len(MonthlyMeasurement.objects.all())
        value = 8
        MonthlyMeasurement.objects.filter(active_max_power_peak_time=value).delete()

        self.assertEqual(size - 1, len(MonthlyMeasurement.objects.all()))

    def test_not_delete_inexistent_transductor_monthly_measures(self):
        size = len(MonthlyMeasurement.objects.all())
        value = 8

        MonthlyMeasurement.objects.get(active_max_power_peak_time=value).delete()

        self.assertEqual(size - 1, len(MonthlyMeasurement.objects.all()))

        with self.assertRaises(MonthlyMeasurement.DoesNotExist):
            MonthlyMeasurement.objects.get(active_max_power_peak_time=8).delete()
