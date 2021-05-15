from datetime import datetime

from django.test import TestCase

from events.models import (
    Event,
    FailedConnectionTransductorEvent,
)
from transductor.models import EnergyTransductor


class EventTestCase(TestCase):
    def setUp(self):
        self.transductor = EnergyTransductor.objects.create(
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

    def test_event_behavior(self):
        event = Event.objects.create(transductor=self.transductor)

        self.assertIsNotNone(
            event.created_at,
            msg="An event was created with a start date set to None.",
        )

        self.assertIsNone(
            event.ended_at,
            msg=(
                "A connection failure event has been created with an end date other "
                "than None."
            ),
        )

    def test_connection_event_behavior(self):
        size_before = len(FailedConnectionTransductorEvent.objects.all())

        self.transductor.set_broken(True)

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
            first=self.transductor.ip_address,
            second=event.transductor.ip_address,
            msg=(
                "The communication failure event created has an IP address different "
                "from the transducer that had the broken attribute modified."
            ),
        )

        self.assertIsNone(
            event.ended_at,
            msg=(
                "A connection failure event has been created with an end date other "
                "than None."
            ),
        )

        self.transductor.set_broken(False)

        event = FailedConnectionTransductorEvent.objects.last()

        self.assertIsNotNone(
            event.ended_at,
            msg=(
                "The broken attribute has been toggled to False and the associated "
                "communication failure event has not been closed."
            ),
        )
