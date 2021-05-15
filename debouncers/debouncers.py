import statistics
from typing import Dict, Optional, Tuple

from django.conf import settings
from django.utils import timezone

from .data_classes import VoltageBounds, VoltageState


class VoltageEventDebouncer:
    """
    Defines a debouncer for voltage related events.
    It works as FSM that changes its states due to a combination of an average
    filter with histeresis of voltage readings
    """

    # Voltage threshold for the debouncer to consider phase down
    PHASE_DOWN_THRESHOLD_RATE = 0.5

    # TODO: Conversar com o prof. sobre esse número mágico
    HYSTERESIS_RATE = 0.005

    def __init__(
        self,
        measurement_phase: str,
        history_size: Optional[int] = 15,
        contracted_voltage: Optional[float] = 220,
    ):
        if not contracted_voltage:
            contracted_voltage = settings.CONTRACTED_VOLTAGE

        PHASE_DOWN_THRESHOLD_RATE = VoltageEventDebouncer.PHASE_DOWN_THRESHOLD_RATE

        self.critical_upper_voltage = contracted_voltage * 1.06
        self.precarious_upper_voltage = contracted_voltage * 1.04
        self.normal_voltage = contracted_voltage
        self.precarious_lower_voltage = contracted_voltage * 0.91
        self.critical_lower_voltage = contracted_voltage * 0.86
        self.phase_down_voltage = contracted_voltage * PHASE_DOWN_THRESHOLD_RATE

        self.measurement_phase = measurement_phase

        # Holds average filter parameters and data
        self.history_size = history_size

        self.data_history = []
        self.avg_filter = 0
        self.last_measurement = 0

        # Holds current event status
        self.current_voltage_state = VoltageState.NORMAL.value

        # Holds last event status transition
        self.last_voltage_state_transition = (
            VoltageState.NORMAL.value,
            VoltageState.NORMAL.value,
        )

    def add_new_measurement(
        self,
        measurement_value: float,
    ) -> Tuple[VoltageState, VoltageState]:
        """
        Adds data from a new measurement to the event debouncer and updates
        the debouncer state

        Args:
            measurement_value (float): The last measurement value.

        Returns:
            Tuple[VoltageState, VoltageState]: Last state transition of a voltage phase
        """
        self.data_history.append(measurement_value)
        self.last_measurement = measurement_value

        self.avg_filter = statistics.mean(self.data_history)

        current_voltage_state = self.update_current_state()

        return self.last_voltage_state_transition

    def update_current_state(self) -> VoltageState:
        """
        This function checks what interval the phase the debouncer is analyzed at is.
        Once discovered, the phase status in the database is updated. Each interval is
        associated with a state of the voltage phase.

        Returns:
            VoltageState: This function returns the status of the voltage phase analyzed
        """
        previous_state = self.current_voltage_state
        last_measurement = self.last_measurement

        state_ranges: Dict[str, VoltageBounds] = self.get_state_ranges()

        CRITICAL_UPPER = VoltageState.CRITICAL_UPPER.value
        PRECARIOUS_UPPER = VoltageState.PRECARIOUS_UPPER.value
        NORMAL = VoltageState.NORMAL.value
        PRECARIOUS_LOWER = VoltageState.PRECARIOUS_LOWER.value
        CRITICAL_LOWER = VoltageState.CRITICAL_LOWER.value
        PHASE_DOWN = VoltageState.PHASE_DOWN.value

        if (
            state_ranges[CRITICAL_UPPER].lower_bound <= last_measurement
            and state_ranges[CRITICAL_UPPER].upper_bound >= last_measurement
        ):
            current_state = CRITICAL_UPPER

        elif (
            state_ranges[PRECARIOUS_UPPER].lower_bound <= last_measurement
            and state_ranges[PRECARIOUS_UPPER].upper_bound >= last_measurement
        ):
            current_state = PRECARIOUS_UPPER

        elif (
            state_ranges[NORMAL].lower_bound <= last_measurement
            and state_ranges[NORMAL].upper_bound >= last_measurement
        ):
            current_state = NORMAL

        elif (
            state_ranges[PRECARIOUS_LOWER].lower_bound <= last_measurement
            and state_ranges[PRECARIOUS_LOWER].upper_bound >= last_measurement
        ):
            current_state = PRECARIOUS_LOWER

        elif (
            state_ranges[CRITICAL_LOWER].lower_bound <= last_measurement
            and state_ranges[CRITICAL_LOWER].upper_bound >= last_measurement
        ):
            current_state = CRITICAL_LOWER

        elif (
            state_ranges[PHASE_DOWN].lower_bound <= last_measurement
            and state_ranges[PHASE_DOWN].upper_bound >= last_measurement
        ):
            current_state = PHASE_DOWN

        self.last_voltage_state_transition = (previous_state, current_state)
        self.current_voltage_state = current_state

        return self.current_voltage_state

    def get_state_ranges(self) -> Dict[str, VoltageBounds]:
        """
        This function creates a dictionary that associates the voltage status with
        their respective measurement intervals.

        In the interval associated with the current status of the analyzed phase, a
        threshold constant is applied.

        For example, if the current status is NORMAL, and the associated range is:
        >   upper_bound = 228.80
        >   lower_bound = 200.20

        And using the threshold constant equal to 0.05, the interval associated with
        the NORMAL status will be updated as follows:

        >   upper_bound = 228.80 + (228.80 * (1 + threshold))
        >   lower_bound = 200.20 + (200.20 * (1 - threshold))

        Returns:
            Dict[str, VoltageBounds]: Dictionary with keys equal to possible states and
            values equal to associated intervals.
        """

        state_ranges: Dict[str, VoltageBounds] = dict()

        state_ranges[VoltageState.CRITICAL_UPPER.value] = VoltageBounds(
            upper_bound=float("inf"),
            lower_bound=self.critical_upper_voltage,
        )

        state_ranges[VoltageState.PRECARIOUS_UPPER.value] = VoltageBounds(
            upper_bound=self.critical_upper_voltage,
            lower_bound=self.precarious_upper_voltage,
        )

        state_ranges[VoltageState.NORMAL.value] = VoltageBounds(
            upper_bound=self.precarious_upper_voltage,
            lower_bound=self.precarious_lower_voltage,
        )

        state_ranges[VoltageState.PRECARIOUS_LOWER.value] = VoltageBounds(
            upper_bound=self.precarious_lower_voltage,
            lower_bound=self.critical_lower_voltage,
        )

        state_ranges[VoltageState.CRITICAL_LOWER.value] = VoltageBounds(
            upper_bound=self.critical_lower_voltage,
            lower_bound=self.phase_down_voltage,
        )

        state_ranges[VoltageState.PHASE_DOWN.value] = VoltageBounds(
            upper_bound=self.phase_down_voltage,
            lower_bound=float("-inf"),
        )

        # hysteresis applied to the current phase bounds
        hysteresis_rate = VoltageEventDebouncer.HYSTERESIS_RATE
        current_voltage_state = self.current_voltage_state

        state_ranges[current_voltage_state].upper_bound *= 1 + hysteresis_rate
        state_ranges[current_voltage_state].lower_bound *= 1 - hysteresis_rate

        return state_ranges
