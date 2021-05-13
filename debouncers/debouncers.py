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
    ):

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
        self.last_event_state_transition = (
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

    @staticmethod
    def get_target_event_class(event_state):
        """
        Obtains the event name generated in a specific state in the list of
        available ones.
        For example, if the event state is CriticalLower the target event name
        should be critical.
        The same applies if the event would be CriticalUpper.

        Args:
            event_state:  The spectif event state in the list of available ones.

        Returns:
            The target event name.
            Note that if the event state is Normal, there are not target event
            so this function return None

        """
        from events.models import (
            CriticalVoltageEvent,
            PhaseDropEvent,
            PrecariousVoltageEvent,
        )

        critical_event_states = [
            VoltageEventDebouncer.EVENT_STATE_CRITICAL_UPPER,
            VoltageEventDebouncer.EVENT_STATE_CRITICAL_LOWER,
        ]

        precarious_event_states = [
            VoltageEventDebouncer.EVENT_STATE_PRECARIOUS_UPPER,
            VoltageEventDebouncer.EVENT_STATE_PRECARIOUS_LOWER,
        ]

        if event_state in critical_event_states:
            return CriticalVoltageEvent
        elif event_state in precarious_event_states:
            return PrecariousVoltageEvent
        elif event_state == VoltageEventDebouncer.EVENT_STATE_PHASE_DOWN:
            return PhaseDropEvent
        else:  # Does nothing when its normal state
            return None

    def finish_transductor_event(self, transductor, event_type_class):
        """
        Finishes an event related to a transductor and phase.
        It may either finishes the event if there are no data related to it
        (i.e. no phase currently in the event), or
        update the active event by removing the phase that no longer active in
        that event.
        Args:
            transductor: The used transductor.
            ## TODO: FIX event_type_name: The event type it may vary from Critical,
            Precarious or Phase Drop events.
            measurement_phase: The phase of the finished event.

        Returns:
        """
        from transductor.models import TransductorVoltageState

        # TODO: POPULAR O BANCO ->
        transductor_voltage_state = TransductorVoltageState.objects.get(
            transductor=transductor,
            phase=self.measurement_phase,
        )
        transductor_voltage_state.current_voltage_state = self.current_voltage_state
        transductor_voltage_state.save()

        # if the is no event to close, just return
        if event_type_class is None:
            return

        # TODO: SEMPRE SÓ 1 -> CRITICAL -> DROP
        transductor_unfinished_events = event_type_class.objects.filter(
            transductor=transductor,
            ended_at=None,
        )
        last_event = transductor_unfinished_events.last()

        # if there is no event opened, just return
        # TODO: BUG
        if not last_event:
            return

        if not last_event.data:
            last_event.data = {
                "voltage_a": None,
                "voltage_b": None,
                "voltage_c": None,
            }

        # when set to None, it is because the event is no longer happening at this phase
        last_event.data[self.measurement_phase] = None

        all_phases_is_none = True
        for measurement_value in last_event.data.values():
            if measurement_value != None:
                all_phases_is_none = False

        # If the event does not occur at any phase, it is because the event is over
        if all_phases_is_none:
            last_event.ended_at = timezone.datetime.now()

        else:
            # ATUALIZANDO A FASE QUE PERMANECE COM O EVENTO ABERTO
            last_event.data[self.measurement_phase] = self.last_measurement

        last_event.save()

    def update_transductor_event_data(self, transductor, event_type_class):
        from transductor.models import TransductorVoltageState

        transductor_voltage_state = TransductorVoltageState.objects.get(
            transductor=transductor,
            phase=self.measurement_phase,
        )

        transductor_voltage_state.current_voltage_state = self.current_voltage_state
        transductor_voltage_state.save()

        if event_type_class is None:
            return

        previous_state, current_state = self.last_event_state_transition

        # Create the event first
        if previous_state != current_state:
            event = event_type_class.objects.create(transductor=transductor)
        else:  # get a existing event
            event = event_type_class.objects.filter(transductor=transductor).last()

        if event:
            data = {
                "voltage_a": None,
                "voltage_b": None,
                "voltage_c": None,
            }
            data[self.measurement_phase] = self.last_measurement
            event.data = data
            event.save()

        return event

    def raise_event(self, transductor):
        previous_state, current_state = self.last_event_state_transition

        # The event is no longer happing at this phase
        # A new event may be occurring or it may have been normalized on all phases
        # The finish_transductor_event will update the phase status and related events
        if previous_state != current_state:
            target_event_class = self.get_target_event_class(previous_state)
            self.finish_transductor_event(transductor, target_event_class)

        """
        In this `if` two different cases are treated

        The first case is when an EVENT_STATE_NORMAL to X transition occurs
        In this case an event is created for the new X state

        The second case is when an X -> Y transition occurs

        If state X is equal to state Y, the event is retrieved and updated
        If state X is different from state Y, an event is created for state Y
        """
        if self.current_voltage_state != VoltageEventDebouncer.EVENT_STATE_NORMAL:
            target_event_class = self.get_target_event_class(current_state)
            self.update_transductor_event_data(transductor, target_event_class)
