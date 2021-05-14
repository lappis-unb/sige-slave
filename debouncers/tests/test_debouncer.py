from django.test import TestCase

from debouncers.debouncers import VoltageEventDebouncer
from debouncers.data_classes import VoltageState


class VoltageEventDebouncerTestCase(TestCase):

    def test_debouncer_initialization(self):
        phase = "voltage_a"
        debouncer = VoltageEventDebouncer(measurement_phase=phase)

        self.assertIsNotNone(
            debouncer.PHASE_DOWN_THRESHOLD_RATE,
            msg="A debouncer was instantiated without a threshold rate"
        )

        self.assertIsNotNone(
            debouncer.normal_voltage,
            msg="A debouncer was instantiated without a normal voltage"
        )

        self.assertTrue(
            len(debouncer.data_history) == 0,
            msg="The debouncer was instantiated with the measurement history not reset"
        )

        self.assertTrue(
            hasattr(debouncer, 'avg_filter'),
            msg="The debouncer was instantiated without the avg_filter attribute"
        )

        self.assertTrue(
            hasattr(debouncer, 'last_event_state_transition'),
            msg=(
                "The debouncer was instantiated without the "
                "last_event_state_transition attribute"
            )
        )

    def test_add_new_measurement(self):
        phase = "voltage_a"
        debouncer = VoltageEventDebouncer(measurement_phase=phase)

        measurement_value = 220
        debouncer.add_new_measurement(measurement_value)

        self.assertEqual(
            first=debouncer.data_history[-1],
            second=measurement_value,
            msg=(
                "The measurement passed as a parameter was not added in the last "
                "measurement list"
            )
        )

        self.assertEqual(
            first=debouncer.last_measurement,
            second=measurement_value,
            msg=(
                "The measurement passed as a parameter was not saved as in the "
                "`last_measurement` attribute"
            )
        )

        measurement_value = 210
        debouncer.add_new_measurement(measurement_value)
        avg = (220 + 210) / 2

        self.assertEqual(
            first=debouncer.avg_filter,
            second=avg,
            msg=(
                "The `avg_filter` variable is not being updated with the new "
                "measurements"
            )
        )
