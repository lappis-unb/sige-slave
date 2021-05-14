from datetime import datetime

from django.test import TestCase

from events.models import (
    CriticalVoltageEvent,
    Event,
    FailedConnectionTransductorEvent,
    PhaseDropEvent,
    PrecariousVoltageEvent,
    VoltageRelatedEvent,
)
from measurement.models import MinutelyMeasurement
from transductor.models import EnergyTransductor


class EventTestCase(TestCase):
    def setUp(self):
        self.transductor1 = EnergyTransductor.objects.create(
            serial_number="8764321",
            ip_address="111.101.111.11",
            broken=False,
            active=True,
            model="TR4020",
            firmware_version="12.1.3215",
            physical_location="predio 2 sala 44",
            geolocation_longitude=-24.4556,
            geolocation_latitude=-24.45996,
            installation_date=datetime.now(),
        )
        self.transductor2 = EnergyTransductor.objects.create(
            serial_number="8764322",
            ip_address="111.101.111.12",
            broken=False,
            active=True,
            model="TR4020",
            firmware_version="12.1.3215",
            physical_location="predio 2 sala 45",
            geolocation_longitude=-24.4557,
            geolocation_latitude=-24.45997,
            installation_date=datetime.now(),
        )

    def test_connection_event_behavior(self):
        size_before = len(FailedConnectionTransductorEvent.objects.all())

        self.transductor1.set_broken(True)

        size_after = len(FailedConnectionTransductorEvent.objects.all())

        self.assertEqual(
            first=size_before + 1,
            second=size_after,
            msg=(
                "The broken attribute has been toggled to True and a communication "
                "failure event has not been created."
            ),
        )

        event: Event = FailedConnectionTransductorEvent.objects.last()

        self.assertEqual(
            first=self.transductor1.ip_address,
            second=event.transductor.ip_address,
            msg=(
                "The communication failure event created has an IP address different "
                "from the transducer that had the broken attribute modified."
            )
        )

        self.assertIsNone(
            event.ended_at,
            msg=(
                "A connection failure event has been created with an end date other "
                "than None."
            )
        )

        self.transductor1.set_broken(False)

        event = FailedConnectionTransductorEvent.objects.last()

        self.assertIsNone(
            event.ended_at,
            msg=(
                "The broken attribute has been toggled to False and the associated "
                "communication failure event has not been closed."
            )
        )

    # def test_voltage_debouncer(self):
    #     '''
    #     Test responsible for the voltage event debouncer class.
    #     It both tests its creation as well as its functionalities.
    #     '''
    #     deb = VoltageEventDebouncer.get_voltage_debouncer(
    #         self.transductor1, 'voltage_a')
    #     deb.reset()

    #     # Checks avg_filter working
    #     deb.add_new_measurement('voltage_a', 220)
    #     deb.add_new_measurement('voltage_a', 225)
    #     self.assertAlmostEqual(
    #         deb.avg_filter,
    #         (220 + 225) / 2.0)
    #     self.assertEqual(deb.current_event_state,
    #                      VoltageEventDebouncer.EVENT_STATE_NORMAL)
    #     self.assertEqual(deb.last_event_state_transition,
    #                      (VoltageEventDebouncer.EVENT_STATE_NORMAL,
    #                       VoltageEventDebouncer.EVENT_STATE_NORMAL))
    #     deb.add_new_measurement('voltage_a', 380)
    #     self.assertEqual(deb.last_event_state_transition,
    #                      (VoltageEventDebouncer.EVENT_STATE_NORMAL,
    #                       VoltageEventDebouncer.EVENT_STATE_PRECARIOUS_UPPER))
    #     deb.add_new_measurement('voltage_a', 400)
    #     self.assertEqual(deb.last_event_state_transition,
    #                      (VoltageEventDebouncer.EVENT_STATE_PRECARIOUS_UPPER,
    #                       VoltageEventDebouncer.EVENT_STATE_CRITICAL_UPPER))
    #     self.assertAlmostEqual(
    #         deb.avg_filter,
    #         (220 + 225 + 400 + 380) / 4.0)
    #     self.assertEqual(deb.current_event_state,
    #                      VoltageEventDebouncer.EVENT_STATE_CRITICAL_UPPER)

    #     deb.reset()
    #     deb.add_new_measurement('voltage_a', 40)
    #     self.assertEqual(deb.last_event_state_transition,
    #                      (VoltageEventDebouncer.EVENT_STATE_NORMAL,
    #                       VoltageEventDebouncer.EVENT_STATE_PHASE_DOWN))
    #     deb.add_new_measurement('voltage_a', 50)
    #     self.assertEqual(deb.last_event_state_transition,
    #                      (VoltageEventDebouncer.EVENT_STATE_PHASE_DOWN,
    #                       VoltageEventDebouncer.EVENT_STATE_PHASE_DOWN))
    #     self.assertAlmostEqual(deb.avg_filter, (40 + 50) / 2.0)
    #     self.assertEqual(deb.current_event_state,
    #                      VoltageEventDebouncer.EVENT_STATE_PHASE_DOWN)
    #     deb.add_new_measurement('voltage_a', 180)
    #     self.assertEqual(deb.last_event_state_transition,
    #                      (VoltageEventDebouncer.EVENT_STATE_PHASE_DOWN,
    #                       VoltageEventDebouncer.EVENT_STATE_CRITICAL_LOWER))
    #     self.assertAlmostEqual(deb.avg_filter, (40 + 50 + 180) / 3.0)
    #     self.assertEqual(deb.current_event_state,
    #                      VoltageEventDebouncer.EVENT_STATE_CRITICAL_LOWER)
    #     for i in range(5):
    #         deb.add_new_measurement('voltage_a', 230)
    #     self.assertEqual(deb.current_event_state,
    #                      VoltageEventDebouncer.EVENT_STATE_PRECARIOUS_LOWER)
    #     for i in range(5):
    #         deb.add_new_measurement('voltage_a', 300)
    #     self.assertEqual(deb.current_event_state,
    #                      VoltageEventDebouncer.EVENT_STATE_CRITICAL_UPPER)
    #     for i in range(15):
    #         deb.add_new_measurement('voltage_a', 220)
    #     self.assertEqual(deb.current_event_state,
    #                      VoltageEventDebouncer.EVENT_STATE_NORMAL)

    # def test_create_critical_voltage_event(self):
    #     before = len(CriticalVoltageEvent.objects.all())

    #     a = MinutelyMeasurement()
    #     a.voltage_a = 220
    #     a.voltage_b = 400
    #     a.voltage_c = 200
    #     a.transductor = self.transductor1
    #     a.reset_debouncers()
    #     a.reset_events()
    #     a.check_measurements()
    #     a.check_measurements()

    #     b = MinutelyMeasurement()
    #     b.voltage_a = 220
    #     b.voltage_b = 180
    #     b.voltage_c = 200
    #     b.transductor = self.transductor2
    #     b.reset_debouncers()
    #     b.reset_events()
    #     b.check_measurements()
    #     b.check_measurements()
    #     b.check_measurements()

    #     for evt in CriticalVoltageEvent.objects.all():
    #         self.assertTrue(evt.ended_at is None)

    #     self.assertEqual(before + 2, len(CriticalVoltageEvent.objects.all()))

    #     b.voltage_a = 220
    #     b.voltage_b = 220
    #     a.voltage_a = 220
    #     a.voltage_b = 220
    #     for i in range(16):
    #         a.check_measurements()
    #         b.check_measurements()

    #     for evt in CriticalVoltageEvent.objects.all():
    #         self.assertFalse(evt.ended_at is None)

    # def test_create_precarious_voltage_event(self):
    #     before = len(PrecariousVoltageEvent.objects.all())

    #     a = MinutelyMeasurement()
    #     a.voltage_a = 220
    #     a.voltage_b = 220
    #     a.voltage_c = 199
    #     a.transductor = self.transductor1
    #     a.reset_debouncers()
    #     a.reset_events()
    #     a.check_measurements()
    #     a.check_measurements()

    #     b = MinutelyMeasurement()
    #     b.voltage_a = 220
    #     b.voltage_b = 230
    #     b.voltage_c = 220
    #     b.transductor = self.transductor2
    #     b.reset_debouncers()
    #     b.reset_events()
    #     b.check_measurements()
    #     b.check_measurements()

    #     self.assertEqual(before + 2, len(PrecariousVoltageEvent.objects.all()))

    # def test_create_phase_drop_event(self):
    #     before = len(PhaseDropEvent.objects.all())

    #     a = MinutelyMeasurement()
    #     a.voltage_a = 50
    #     a.voltage_b = 220
    #     a.voltage_c = 220
    #     a.transductor = self.transductor1
    #     a.reset_debouncers()
    #     a.reset_events()
    #     a.check_measurements()

    #     self.assertEqual(before + 1, len(PhaseDropEvent.objects.all()))

    # def test_create_repeated_voltage_event(self):
    #     before = len(VoltageRelatedEvent.objects.all())

    #     a = MinutelyMeasurement()
    #     a.voltage_a = 400
    #     a.voltage_b = 999
    #     a.voltage_c = 10
    #     a.transductor = self.transductor1
    #     a.reset_debouncers()
    #     a.reset_events()
    #     a.check_measurements()

    #     self.assertEqual(before + 2, len(VoltageRelatedEvent.objects.all()))

    # def test_create_multiple_events_in_series(self):
    #     before = len(VoltageRelatedEvent.objects.all())

    #     a = MinutelyMeasurement()
    #     a.transductor = self.transductor1
    #     a.reset_debouncers()
    #     a.reset_events()

    #     a.voltage_a = 50
    #     a.voltage_b = 220
    #     a.voltage_c = 220
    #     for i in range(2):
    #         a.check_measurements()
    #     a.voltage_a = 55
    #     for i in range(2):
    #         a.check_measurements()
    #     a.voltage_a = 60
    #     for i in range(2):
    #         a.check_measurements()
    #     self.assertEqual(before + 1, len(VoltageRelatedEvent.objects.all()))
    #     for evt in VoltageRelatedEvent.objects.all():
    #         self.assertEqual(evt.ended_at, None)
    #     a.voltage_a = 220
    #     for i in range(20):
    #         a.check_measurements()
    #     self.assertEqual(before + 3, len(VoltageRelatedEvent.objects.all()))
    #     for evt in VoltageRelatedEvent.objects.all():
    #         self.assertNotEqual(evt.ended_at, None)
    #     a.voltage_a = 90
    #     for i in range(20):
    #         a.check_measurements()
    #     self.assertEqual(before + 4, len(VoltageRelatedEvent.objects.all()))
    #     a.voltage_a = 400
    #     for i in range(5):
    #         a.check_measurements()
    #     self.assertEqual(before + 6, len(VoltageRelatedEvent.objects.all()))
    #     a.voltage_a = 350
    #     for i in range(2):
    #         a.check_measurements()
    #     a.voltage_a = 300
    #     for i in range(2):
    #         a.check_measurements()
    #     a.voltage_a = 260
    #     for i in range(5):
    #         a.check_measurements()
    #     a.voltage_a = 218
    #     for i in range(15):
    #         a.check_measurements()
    #     for evt in VoltageRelatedEvent.objects.all():
    #         self.assertNotEqual(evt.ended_at, None)
    #     a.voltage_a = 230
    #     for i in range(3):
    #         a.check_measurements()
    #     a.voltage_a = 218
    #     for i in range(3):
    #         a.check_measurements()
    #     self.assertEqual(before + 10, len(VoltageRelatedEvent.objects.all()))
    #     a.voltage_a = 175
    #     for i in range(3):
    #         a.check_measurements()
    #     a.voltage_a = 220
    #     for i in range(3):
    #         a.check_measurements()
    #     self.assertEqual(before + 13, len(VoltageRelatedEvent.objects.all()))
    #     a.voltage_a = 195
    #     for i in range(3):
    #         a.check_measurements()
    #     a.voltage_a = 220
    #     for i in range(3):
    #         a.check_measurements()
    #     self.assertEqual(before + 14, len(VoltageRelatedEvent.objects.all()))
