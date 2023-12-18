from django.test import TestCase
from dataclasses import asdict

from debouncers.data_classes import VoltageBounds, VoltageState
from debouncers.debouncers import VoltageEventDebouncer
from events.models import (
    CriticalVoltageEvent,
    PrecariousVoltageEvent,
    PhaseDropEvent,
)


class VoltageEventDebouncerTestCase(TestCase):
    def setUp(self) -> None:
        phase = "voltage_a"
        self.debouncer = VoltageEventDebouncer(
            measurement_phase=phase, contracted_voltage=220
        )

    def test_debouncer_initialization(self):
        self.assertIsNotNone(
            self.debouncer.PHASE_DOWN_THRESHOLD_RATE,
            msg="A debouncer was instantiated without a threshold rate",
        )

        self.assertIsNotNone(
            self.debouncer.normal_voltage,
            msg="A debouncer was instantiated without a normal voltage",
        )

        self.assertTrue(
            len(self.debouncer.data_history) == 0,
            msg="The debouncer was instantiated with the measurement history not reset",
        )

        self.assertTrue(
            hasattr(self.debouncer, "avg_filter"),
            msg="The debouncer was instantiated without the avg_filter attribute",
        )

        self.assertTrue(
            hasattr(self.debouncer, "last_voltage_state_transition"),
            msg=(
                "The debouncer was instantiated without the "
                "last_voltage_state_transition attribute"
            ),
        )

        self.assertTrue(
            self.debouncer.phase_down_voltage
            < self.debouncer.critical_lower_voltage
            < self.debouncer.precarious_lower_voltage
            < self.debouncer.normal_voltage
            < self.debouncer.precarious_upper_voltage
            < self.debouncer.critical_upper_voltage,
            msg="The values of the intervals for each state should be increasing",
        )

    def test_add_new_measurement(self):
        measurement_value = 220
        self.debouncer.add_new_measurement(measurement_value)

        self.assertEqual(
            first=self.debouncer.data_history[-1],
            second=measurement_value,
            msg=(
                "The measurement passed as a parameter was not added in the last "
                "measurement list"
            ),
        )

        self.assertEqual(
            first=self.debouncer.last_measurement,
            second=measurement_value,
            msg=(
                "The measurement passed as a parameter was not saved as in the "
                "`last_measurement` attribute"
            ),
        )

        measurement_value = 210
        self.debouncer.add_new_measurement(measurement_value)
        avg = (220 + 210) / 2

        self.assertEqual(
            first=self.debouncer.avg_filter,
            second=avg,
            msg=(
                "The `avg_filter` variable is not being updated with the new "
                "measurements"
            ),
        )

        self.assertEqual(
            first=self.debouncer.current_voltage_state,
            second=VoltageState.NORMAL.value,
            msg=(
                "A measurement has been added within the range of the normal state "
                "and a non-normal state has been defined"
            ),
        )

    def test_all_possible_states(self):
        self.debouncer.add_new_measurement(measurement_value=220)
        self.assertEqual(
            self.debouncer.current_voltage_state, VoltageState.NORMAL.value
        )

        while self.debouncer.avg_filter >= self.debouncer.precarious_lower_voltage:
            self.debouncer.add_new_measurement(measurement_value=190)

        self.assertEqual(
            self.debouncer.current_voltage_state, VoltageState.PRECARIOUS_LOWER.value
        )

        while self.debouncer.avg_filter >= self.debouncer.critical_lower_voltage:
            self.debouncer.add_new_measurement(measurement_value=150)

        self.assertEqual(
            self.debouncer.current_voltage_state, VoltageState.CRITICAL_LOWER.value
        )

        while self.debouncer.avg_filter >= self.debouncer.phase_down_voltage:
            self.debouncer.add_new_measurement(measurement_value=50)

        self.assertEqual(
            self.debouncer.current_voltage_state, VoltageState.PHASE_DOWN.value
        )

        while self.debouncer.avg_filter <= self.debouncer.precarious_upper_voltage:
            self.debouncer.add_new_measurement(measurement_value=230)

        self.assertEqual(
            self.debouncer.current_voltage_state, VoltageState.PRECARIOUS_UPPER.value
        )

        for i in range(10):
            self.debouncer.add_new_measurement(measurement_value=260)

        self.assertEqual(
            self.debouncer.current_voltage_state, VoltageState.CRITICAL_UPPER.value
        )

    def test_update_current_state(self):
        last_voltage_state_transition = self.debouncer.add_new_measurement(
            measurement_value=220
        )

        # b_ -> before
        b_previous_state, b_current_state = last_voltage_state_transition

        last_voltage_state_transition = self.debouncer.add_new_measurement(
            measurement_value=110
        )

        # a_ -> after
        a_previous_state, a_current_state = last_voltage_state_transition

        self.assertEqual(
            first=b_current_state,
            second=a_previous_state,
            msg=(
                "The state before the insertion of the new measurement is not being "
                "saved in the last transaction tuple"
            ),
        )

        current_voltage_state = self.debouncer.update_current_state()
        valid_states = (state.value for state in VoltageState)

        self.assertIn(
            current_voltage_state,
            valid_states,
            msg="The update_current_state method should have returned a valid state",
        )

    def test_get_state_ranges(self):
        # normal measurement
        self.debouncer.add_new_measurement(measurement_value=220)

        # b_ -> before
        b_state_ranges = self.debouncer.get_state_ranges()

        self.debouncer.add_new_measurement(measurement_value=110)

        # a_ -> after
        a_state_ranges = self.debouncer.get_state_ranges()

        self.assertGreater(
            b_state_ranges[VoltageState.NORMAL.value].upper_bound,
            a_state_ranges[VoltageState.NORMAL.value].upper_bound,
            msg="The threshold constant is not being applied in the current phase",
        )

        self.assertLess(
            b_state_ranges[VoltageState.NORMAL.value].lower_bound,
            a_state_ranges[VoltageState.NORMAL.value].lower_bound,
            msg="The threshold constant is not being applied in the current phase",
        )

        state_ranges = self.debouncer.get_state_ranges()
        valid_states = (state.value for state in VoltageState)

        for state in state_ranges.keys():
            self.assertIn(
                member=state,
                container=valid_states,
                msg=(
                    "The state_ranges dictionary keys must belong to the Enum "
                    "VoltageState"
                ),
            )

        self.assertEqual(
            first=state_ranges[VoltageState.CRITICAL_UPPER.value].upper_bound,
            second=float("inf"),
            msg=(
                "The upper limit of the state with the highest threshold must be "
                "positive infinite"
            ),
        )

        self.assertEqual(
            first=state_ranges[VoltageState.PHASE_DOWN.value].lower_bound,
            second=float("-inf"),
            msg=(
                "The lower limit of the state with the lowest threshold must be "
                "negative infinite"
            ),
        )

    def test_threshold_application_in_the_current_phase(self):
        previous_state, current_state = self.debouncer.add_new_measurement(
            measurement_value=220
        )

        self.assertEqual(
            first=current_state,
            second=VoltageState.NORMAL.value,
        )

        previous_state, current_state = self.debouncer.add_new_measurement(
            measurement_value=228.8
        )

        self.assertEqual(
            first=current_state,
            second=VoltageState.PRECARIOUS_UPPER.value,
        )

        previous_state, current_state = self.debouncer.add_new_measurement(
            measurement_value=228.7
        )

        self.assertEqual(
            first=current_state,
            second=VoltageState.PRECARIOUS_UPPER.value,
            msg=(
                "The lower_bound of the current phase should have changed, thus "
                "preventing a small variation in the measure from changing the "
                "current state"
            ),
        )
    
    def test_empty_history(self):
        self.assertEqual(len(self.debouncer.data_history), 0)
        self.assertEqual(self.debouncer.avg_filter, 0)
        self.assertEqual(self.debouncer.last_measurement, 0)
        self.assertEqual(self.debouncer.current_voltage_state, VoltageState.NORMAL.value)

    def test_full_history(self):
        for _ in range(self.debouncer.history_size):
            self.debouncer.add_new_measurement(220)

    def test_extreme_values(self):
        self.debouncer.add_new_measurement(1e10)
        self.assertEqual(self.debouncer.current_voltage_state, VoltageState.CRITICAL_UPPER.value)
    
    def test_continuous_measurements(self):
        for _ in range(20):
            self.debouncer.add_new_measurement(220)

    def test_history_size_limit(self):
        for _ in range(self.debouncer.history_size):
            self.debouncer.add_new_measurement(220)
        self.assertEqual(len(self.debouncer.data_history), self.debouncer.history_size)
        expected_data_history = [220] * self.debouncer.history_size
        self.assertListEqual(self.debouncer.data_history, expected_data_history)
    
    def test_get_target_event_class(self):
       
        self.assertEqual(
            VoltageState.get_target_event_class(VoltageState.CRITICAL_UPPER.value),
            CriticalVoltageEvent,
        )
        self.assertEqual(
            VoltageState.get_target_event_class(VoltageState.CRITICAL_LOWER.value),
            CriticalVoltageEvent,
        )
        self.assertEqual(
            VoltageState.get_target_event_class(VoltageState.PRECARIOUS_UPPER.value),
            PrecariousVoltageEvent,
        )
        self.assertEqual(
            VoltageState.get_target_event_class(VoltageState.PRECARIOUS_LOWER.value),
            PrecariousVoltageEvent,
        )
        self.assertEqual(
            VoltageState.get_target_event_class(VoltageState.PHASE_DOWN.value),
            PhaseDropEvent,
        )

    def test_voltage_bounds_creation(self):
       
        upper_bound = 100.0
        lower_bound = 50.0
        voltage_bounds = VoltageBounds(upper_bound, lower_bound)
        
        self.assertEqual(voltage_bounds.upper_bound, upper_bound)
        self.assertEqual(voltage_bounds.lower_bound, lower_bound)

    def test_voltage_bounds_as_dict(self):
       
        voltage_bounds = VoltageBounds(100.0, 50.0)
        expected_dict = {"upper_bound": 100.0, "lower_bound": 50.0}

        self.assertDictEqual(asdict(voltage_bounds), expected_dict)
    
    def test_hysteresis_application(self):

        self.debouncer.add_new_measurement(measurement_value=220)
        state_ranges_before = self.debouncer.get_state_ranges()
        self.debouncer.add_new_measurement(
            measurement_value=self.debouncer.avg_filter + 0.5
        )

        state_ranges_after = self.debouncer.get_state_ranges()

        for state in VoltageState:
            if state != VoltageState.PHASE_DOWN:
                if state_ranges_before[state.value].upper_bound != float('inf'):
                    self.assertAlmostEqual(
                        state_ranges_before[state.value].upper_bound,
                        state_ranges_after[state.value].upper_bound,
                        places=2,
                        msg="The upper bound should have increased due to hysteresis",
                    )

            if state != VoltageState.CRITICAL_UPPER:
                if state_ranges_before[state.value].lower_bound != float('-inf'):
                    self.assertAlmostEqual(
                        state_ranges_before[state.value].lower_bound,
                        state_ranges_after[state.value].lower_bound,
                        places=2,
                        msg="The lower bound should have decreased due to hysteresis",
                    )
