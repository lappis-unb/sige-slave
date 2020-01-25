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
        self.transductor = EnergyTransductor.objects.create(
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

    def test_create_failed_connection_event(self):
        before = len(FailedConnectionTransductorEvent.objects.all())

        self.transductor.set_broken(True)
        event = FailedConnectionTransductorEvent.objects.last()

        self.assertEqual(
            before + 1, len(FailedConnectionTransductorEvent.objects.all())
        )
        self.assertEqual(
            self.transductor.ip_address, event.transductor.ip_address
        )

    def test_voltage_debouncer(self):
        '''
        Test responsible for the voltage event debouncer class.
        It both tests its creation as well as its functionalities.
        '''
        from events.models import VoltageEventDebouncer
        deb = VoltageEventDebouncer.get_voltage_debouncer(
            self.transductor, 'voltage_a')
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
        deb.populate_voltage_event_lists(voltage_parameters)
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

        deb.populate_voltage_event_lists(voltage_parameters)
        events_list = VoltageEventDebouncer.get_event_lists(deb.id)

        self.assertEqual(len(events_list), 5)
        self.assertEqual(len(events_list[0]), 1)
        self.assertEqual(len(events_list[1]), 0)
        self.assertEqual(len(events_list[2]), 0)
        self.assertEqual(len(events_list[3]), 0)
        self.assertEqual(len(events_list[4]), 0)

    def test_create_critical_voltage_event(self):
        before = len(CriticalVoltageEvent.objects.all())

        a = MinutelyMeasurement()
        a.voltage_a = 220
        a.voltage_b = 400
        a.voltage_c = 200
        a.transductor = self.transductor
        a.reset_filter()
        a.check_measurements()

        b = MinutelyMeasurement()
        b.voltage_a = 220
        b.voltage_b = 180
        b.voltage_c = 200
        b.transductor = self.transductor
        b.reset_filter()
        b.check_measurements()

        self.assertEqual(before + 2, len(CriticalVoltageEvent.objects.all()))

    def test_create_precarious_voltage_event(self):
        before = len(PrecariousVoltageEvent.objects.all())

        a = MinutelyMeasurement()
        a.voltage_a = 220
        a.voltage_b = 220
        a.voltage_c = 199
        a.transductor = self.transductor
        a.reset_filter()
        a.check_measurements()

        b = MinutelyMeasurement()
        b.voltage_a = 220
        b.voltage_b = 230
        b.voltage_c = 220
        b.transductor = self.transductor
        b.reset_filter()
        b.check_measurements()

        self.assertEqual(before + 2, len(PrecariousVoltageEvent.objects.all()))

    def test_create_phase_drop_event(self):
        before = len(PhaseDropEvent.objects.all())

        a = MinutelyMeasurement()
        a.voltage_a = 220
        a.voltage_b = 220
        a.voltage_c = 50
        a.transductor = self.transductor
        a.reset_filter()
        a.check_measurements()

        self.assertEqual(before + 1, len(PhaseDropEvent.objects.all()))
