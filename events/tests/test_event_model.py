from datetime import datetime

from django.test import TestCase

from events.models import Event, FailedConnectionTransductorEvent
from transductor.models import Transductor
from data_collector.models import MemoryMap


class EventTestCase(TestCase):
    def setUp(self):
        minutely = [
                {
                    "size": 6,
                    "type": "float32",
                    "function": "read_input_register",
                    "byteorder": "f2_f1_f0_exp",
                    "attributes": [
                        "voltage_a",
                        "voltage_b",
                        "voltage_c"
                    ],
                    "start_address": 10
                }
        ]
        quarterly = [
            {
                    "size": 8,
                    "type": "float32",
                    "function": "read_input_register",
                    "byteorder": "f2_f1_f0_exp",
                    "attributes": [
                        "active_consumption",
                        "reactive_inductive",
                        "active_generated",
                        "reactive_capacitive"
                    ],
                    "start_address": 200
                }
        ]
        monthly = [
                {
                    "size": 8,
                    "type": "float32",
                    "function": "read_input_register",
                    "byteorder": "f2_f1_f0_exp",
                    "attributes": [
                        "active_consumption",
                        "reactive_inductive",
                        "active_generated",
                        "reactive_capacitive"
                    ],
                    "start_address": 200
                }
        ]

        self.memory_map = MemoryMap.objects.create(
            id=1,
            model_transductor='TR4020',
            minutely=minutely,
            quarterly=quarterly,
            monthly=monthly
        )

        self.transductor = Transductor.objects.create(
            id=1,
            serial_number="8764321",
            ip_address="111.101.111.11",
            port='1234',
            broken=False,
            active=True,
            model="TR4020",
            firmware_version="12.1.3215",
            physical_location="predio 2 sala 44",
            geolocation_longitude=-24.4556,
            geolocation_latitude=-24.45996,
            installation_date=datetime.now(),
            memory_map=self.memory_map
        )
        self.transductor2 = Transductor.objects.create(
            id=2,
            serial_number="8764322",
            ip_address="111.101.111.12",
            port='1234',
            broken=False,
            active=True,
            model="TR4020",
            firmware_version="12.1.3215",
            physical_location="predio 2 sala 45",
            geolocation_longitude=-24.4557,
            geolocation_latitude=-24.45997,
            installation_date=datetime.now(),
            memory_map=self.memory_map
        )

    def test_event_behavior(self):
        event = Event.objects.create(transductor=self.transductor)

        self.assertIsNotNone(
            event.created_at,
            msg="An event was created with a start date set to None.",
        )

        self.assertIsNone(
            event.ended_at,
            msg=("A connection failure event has been created with an end date other " "than None."),
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
            msg=("A connection failure event has been created with an end date other " "than None."),
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
