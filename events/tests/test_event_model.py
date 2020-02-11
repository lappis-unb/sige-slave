from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.utils import timezone
from measurement.models import (MinutelyMeasurement, MonthlyMeasurement,
                                QuarterlyMeasurement)
from transductor.models import EnergyTransductor
from events.models import *
from datetime import datetime


class EventTestCase(TestCase):

    def setUp(self):
        self.transductor1 = EnergyTransductor.objects.create(
            serial_number='8764321',
            ip_address='111.101.111.11',
            broken=False,
            active=True,
            model='TR4020',
            firmware_version='12.1.3215',
            physical_location='predio 2 sala 44',
            geolocation_longitude=-24.4556,
            geolocation_latitude=-24.45996,
            installation_date=datetime.now()
        )
        self.transductor2 = EnergyTransductor.objects.create(
            serial_number='8764322',
            ip_address='111.101.111.12',
            broken=False,
            active=True,
            model='TR4020',
            firmware_version='12.1.3215',
            physical_location='predio 2 sala 45',
            geolocation_longitude=-24.4557,
            geolocation_latitude=-24.45997,
            installation_date=datetime.now()
        )

    def test_create_failed_connection_event(self):
        before = len(FailedConnectionTransductorEvent.objects.all())

        self.transductor1.set_broken(True)
        event = FailedConnectionTransductorEvent.objects.last()

        self.assertEqual(
            before + 1, len(FailedConnectionTransductorEvent.objects.all())
        )
        self.assertEqual(
            self.transductor1.ip_address, event.transductor.ip_address
        )

    def test_voltage_debouncer(self):
        '''
        Test responsible for the voltage event debouncer class.
        It both tests its creation as well as its functionalities.
        '''
        from events.models import VoltageEventDebouncer
        deb = VoltageEventDebouncer.get_voltage_debouncer(
            self.transductor1, 'voltage_a')
        deb.reset_filter()
        deb.add_data('voltage_a', 220)
        deb.add_data('voltage_a', 230)

        self.assertAlmostEqual(
            deb.get_average_filter_value(),
            (220 + 230) / 2.0)

        deb.add_data('voltage_a', 380)
        deb.add_data('voltage_a', 400)

        self.assertAlmostEqual(
            deb.get_average_filter_value(),
            (220 + 230 + 400 + 380) / 4.0)

        voltage_parameters = [220, 200.2, 228.8, 189.2, 233.2]
        deb.raise_event(voltage_parameters, self.transductor1)
        events_list = VoltageEventDebouncer.get_event_lists(deb.id)

        self.assertEqual(len(events_list), 5)
        self.assertEqual(len(events_list[0]), 0)
        self.assertEqual(len(events_list[1]), 0)
        self.assertEqual(len(events_list[2]), 1)
        self.assertEqual(len(events_list[3]), 0)
        self.assertEqual(len(events_list[4]), 0)
        self.assertAlmostEqual(events_list[2][0][1], 400)

        deb.reset_filter()
        deb.add_data('voltage_a', 50)
        deb.add_data('voltage_a', 60)

        self.assertAlmostEqual(deb.get_average_filter_value(), (50 + 60) / 2.0)

        deb.raise_event(voltage_parameters, self.transductor1)
        events_list = VoltageEventDebouncer.get_event_lists(deb.id)

        self.assertEqual(len(events_list), 5)
        self.assertEqual(len(events_list[0]), 1)
        self.assertEqual(len(events_list[1]), 0)
        self.assertEqual(len(events_list[2]), 0)
        self.assertEqual(len(events_list[3]), 0)
        self.assertEqual(len(events_list[4]), 0)

        deb.reset_filter()
        deb.add_data('voltage_a', 40)

        deb.raise_event(voltage_parameters, self.transductor1)
        self.assertFalse(deb.raised_event is None)
        if deb.raised_event is not None:
            deb.raised_event.ended_at = timezone.datetime.now()
            self.assertFalse(deb.raised_event.ended_at is None)

        deb.reset_filter()

    def test_create_critical_voltage_event(self):
        before = len(CriticalVoltageEvent.objects.all())

        a = MinutelyMeasurement()
        a.voltage_a = 220
        a.voltage_b = 400
        a.voltage_c = 200
        a.transductor = self.transductor1
        a.reset_filter()
        a.check_measurements()
        a.check_measurements()
        a.check_measurements()

        b = MinutelyMeasurement()
        b.voltage_a = 220
        b.voltage_b = 180
        b.voltage_c = 200
        b.transductor = self.transductor2
        b.reset_filter()
        b.check_measurements()
        b.check_measurements()
        b.check_measurements()

        self.assertEqual(before + 2, len(CriticalVoltageEvent.objects.all()))
        for evt in CriticalVoltageEvent.objects.all():
            self.assertTrue(evt.ended_at is None)

        b.voltage_a = 220
        b.voltage_b = 220
        a.voltage_a = 220
        a.voltage_b = 220
        for i in range(16):
            a.check_measurements()
            b.check_measurements()

        for evt in CriticalVoltageEvent.objects.all():
            self.assertFalse(evt.ended_at is None)

    def test_create_precarious_voltage_event(self):
        before = len(PrecariousVoltageEvent.objects.all())

        a = MinutelyMeasurement()
        a.voltage_a = 220
        a.voltage_b = 220
        a.voltage_c = 199
        a.transductor = self.transductor1
        a.reset_filter()
        a.check_measurements()

        b = MinutelyMeasurement()
        b.voltage_a = 220
        b.voltage_b = 230
        b.voltage_c = 220
        b.transductor = self.transductor2
        b.reset_filter()
        b.check_measurements()

        self.assertEqual(before + 2, len(PrecariousVoltageEvent.objects.all()))

    def test_create_phase_drop_event(self):
        before = len(PhaseDropEvent.objects.all())

        a = MinutelyMeasurement()
        a.voltage_a = 50
        a.voltage_b = 220
        a.voltage_c = 220
        a.transductor = self.transductor1
        a.reset_filter()
        a.check_measurements()

        self.assertEqual(before + 1, len(PhaseDropEvent.objects.all()))

    def test_create_multiple_events_in_series(self):
        before = len(VoltageRelatedEvent.objects.all())

        a = MinutelyMeasurement()
        a.transductor = self.transductor1
        a.reset_filter()

        a.voltage_a = 50
        a.voltage_b = 220
        a.voltage_c = 220
        for i in range(2):
            a.check_measurements()
        a.voltage_a = 55
        for i in range(2):
            a.check_measurements()
        a.voltage_a = 60
        for i in range(2):
            a.check_measurements()
        self.assertEqual(before + 1, len(VoltageRelatedEvent.objects.all()))
        for evt in VoltageRelatedEvent.objects.all():
            self.assertEqual(evt.ended_at, None)
        a.voltage_a = 220
        for i in range(20):
            a.check_measurements()
        self.assertEqual(before + 1, len(VoltageRelatedEvent.objects.all()))
        for evt in VoltageRelatedEvent.objects.all():
            self.assertNotEqual(evt.ended_at, None)
        a.voltage_a = 70
        for i in range(20):
            a.check_measurements()
        self.assertEqual(before + 2, len(VoltageRelatedEvent.objects.all()))
        a.voltage_a = 400
        for i in range(2):
            a.check_measurements()
        self.assertEqual(before + 3, len(VoltageRelatedEvent.objects.all()))
        a.voltage_a = 350
        for i in range(2):
            a.check_measurements()
        a.voltage_a = 300
        for i in range(2):
            a.check_measurements()
        a.voltage_a = 260
        for i in range(5):
            a.check_measurements()
        a.voltage_a = 218
        for i in range(15):
            a.check_measurements()
        for evt in VoltageRelatedEvent.objects.all():
            self.assertNotEqual(evt.ended_at, None)
        a.voltage_a = 230
        for i in range(3):
            a.check_measurements()
        a.voltage_a = 218
        for i in range(3):
            a.check_measurements()
        self.assertEqual(before + 4, len(VoltageRelatedEvent.objects.all()))
        a.voltage_a = 175
        for i in range(3):
            a.check_measurements()
        a.voltage_a = 220
        for i in range(3):
            a.check_measurements()
        self.assertEqual(before + 5, len(VoltageRelatedEvent.objects.all()))
        a.voltage_a = 195
        for i in range(3):
            a.check_measurements()
        a.voltage_a = 220
        for i in range(3):
            a.check_measurements()
        self.assertEqual(before + 6, len(VoltageRelatedEvent.objects.all()))
