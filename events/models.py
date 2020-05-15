from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from transductor.models import EnergyTransductor
from polymorphic.models import PolymorphicModel
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.fields import ArrayField


class Event(PolymorphicModel):
    """
    Defines a new event object
    """
    settings.USE_TZ = False
    created_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    transductor = models.ForeignKey(
        EnergyTransductor,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    data = JSONField()

    def __str__(self):
        return '%s@%s' % (self.__class__.__name__, self.created_at)

    def save_event(self):
        """
        Saves the event.
        """
        raise NotImplementedError


class VoltageRelatedEvent(Event):
    """
    Defines a new event related to a voltage metric
    """

    non_polymorphic = models.Manager()

    class Meta:
        base_manager_name = 'non_polymorphic'

    def save_event(self, transductor, list_data=[]):
        self.transductor = transductor
        self.data = {}

        for phase in list_data:
            self.data[phase[0]] = phase[1]

        self.save()
        return self


class FailedConnectionTransductorEvent(Event):
    """
    Defines a new event related to a failed connection with a transductor
    """

    def save_event(self, transductor, list_data=[]):
        self.transductor = transductor
        self.data = {}
        self.save()
        return self


class CriticalVoltageEvent(VoltageRelatedEvent):
    """
    Defines a new event related to a critical voltage measurement
    """


class PrecariousVoltageEvent(VoltageRelatedEvent):
    """
    Defines a new event related to a precarious voltage measurement
    """


class PhaseDropEvent(VoltageRelatedEvent):
    """
    Defines a new event related to a drop on the triphasic voltage measurement
    """


class RaisedVoltageEventData():
    """
    Defines a copy for the data related to a voltage event.
    """

    # Holds a dictionary of available active/de-activated events
    available_raised_events = dict()

    def __init__(self):
        self.raised_event = None
        self.event_data = {'voltage_a': None,
                           'voltage_b': None,
                           'voltage_c': None}

    @staticmethod
    def initialize_transductor_events(transductor):
        """
        Initializes the available events related to a certain transductor.
        Each transductor holds three possible events related to critical,
        precarious, or phase drop events.
        In turn each one of these events may rise depending on the possible
        three signal phases.
        Args:
            transductor: The used transductor.

        Returns:

        """
        if RaisedVoltageEventData.available_raised_events.get(
                transductor.serial_number) is None:
            RaisedVoltageEventData.available_raised_events[
                transductor.serial_number] = {
                CriticalVoltageEvent.__name__: RaisedVoltageEventData(),
                PrecariousVoltageEvent.__name__: RaisedVoltageEventData(),
                PhaseDropEvent.__name__: RaisedVoltageEventData(),
            }

    @staticmethod
    def reset_transductor_events(transductor):
        """
        Re-initialize the events related to a transductor, see also
        initialize_transductor_events
        Args:
            transductor: The used transductor.

        Returns:

        """
        RaisedVoltageEventData.available_raised_events[
            transductor.serial_number] = \
            {CriticalVoltageEvent.__name__: RaisedVoltageEventData(),
             PrecariousVoltageEvent.__name__: RaisedVoltageEventData(),
             PhaseDropEvent.__name__: RaisedVoltageEventData(),
             }

    @staticmethod
    def finish_transductor_event(transductor,
                                 event_type_name,
                                 measurement_phase):
        """
        Finishes an event related to a transductor and phase.
        It may either finishes the event if there are no data related to it
        (i.e. no phase currently in the event), or
        update the active event by removing the phase that no longer active in
        that event.
        Args:
            transductor: The used transductor.
            event_type_name: The event type it may vary from Critical,
            Precarious or Phase Drop events.
            measurement_phase: The phase of the finished event.

        Returns:

        """
        if event_type_name is None:
            return

        RaisedVoltageEventData.available_raised_events[
            transductor.serial_number][
            event_type_name].event_data[measurement_phase] = None
        if RaisedVoltageEventData.available_raised_events[
            transductor.serial_number][
                event_type_name].raised_event is None:
            return

        are_all_phases_none = True
        for phase, data in RaisedVoltageEventData.available_raised_events[
                transductor.serial_number][event_type_name].event_data.items():
            if data is not None:
                are_all_phases_none = False
                break
        if are_all_phases_none:
            RaisedVoltageEventData.available_raised_events[
                transductor.serial_number][
                event_type_name].raised_event.ended_at = \
                timezone.datetime.now()
            RaisedVoltageEventData.available_raised_events[
                transductor.serial_number][
                event_type_name].raised_event.save_event(transductor)
            RaisedVoltageEventData.available_raised_events[
                transductor.serial_number][
                event_type_name].raised_event = None
        else:
            data = RaisedVoltageEventData.available_raised_events[
                transductor.serial_number][
                event_type_name].get_raised_event_data_as_list()
            RaisedVoltageEventData.available_raised_events[
                transductor.serial_number][
                event_type_name].raised_event.save_event(transductor, data)

    @staticmethod
    def update_transductor_event_data(transductor,
                                      event_type_name,
                                      measurement_phase,
                                      measurement_value):
        if event_type_name is None:
            return

        RaisedVoltageEventData.available_raised_events[
            transductor.serial_number][
            event_type_name].event_data[measurement_phase] = measurement_value
        if RaisedVoltageEventData.available_raised_events[
            transductor.serial_number][
                event_type_name].raised_event is None:
            if event_type_name == CriticalVoltageEvent.__name__:
                RaisedVoltageEventData.available_raised_events[
                    transductor.serial_number][
                    event_type_name].raised_event = CriticalVoltageEvent()
            elif event_type_name == PrecariousVoltageEvent.__name__:
                RaisedVoltageEventData.available_raised_events[
                    transductor.serial_number][
                    event_type_name].raised_event = PrecariousVoltageEvent()
            elif event_type_name == PhaseDropEvent.__name__:
                RaisedVoltageEventData.available_raised_events[
                    transductor.serial_number][
                    event_type_name].raised_event = PhaseDropEvent()
            data = RaisedVoltageEventData.available_raised_events[
                transductor.serial_number][
                event_type_name].get_raised_event_data_as_list()
            RaisedVoltageEventData.available_raised_events[
                transductor.serial_number][
                event_type_name].raised_event.save_event(transductor, data)
        else:
            data = RaisedVoltageEventData.available_raised_events[
                transductor.serial_number][
                event_type_name].get_raised_event_data_as_list()
            RaisedVoltageEventData.available_raised_events[
                transductor.serial_number][
                event_type_name].raised_event.ended_at = None
            RaisedVoltageEventData.available_raised_events[
                transductor.serial_number][
                event_type_name].raised_event.save_event(transductor, data)

    def get_raised_event_data_as_list(self):
        """
        Obtains the data of an event as a list.

        """
        data_as_list = []
        for measurement_phase, data_value in self.event_data.items():
            if data_value is not None:
                data_as_list.append([measurement_phase, data_value])
        return data_as_list


class VoltageEventDebouncer():
    '''
    Defines a debouncer for voltage related events.
    It works as FSM that changes its states due to a combination of an average
    filter with histeresis of voltage readings
    '''

    '''
    Voltage Threshold for the Debouncer to consider phase down
    '''
    PHASE_DOWN_THRESHOLD_RATE = 0.5

    '''
    List of available event status
    '''
    EVENT_STATE_NORMAL = 'Normal'
    EVENT_STATE_CRITICAL_LOWER = 'CriticalLow'
    EVENT_STATE_CRITICAL_UPPER = 'CriticalHigh'
    EVENT_STATE_PRECARIOUS_LOWER = 'PrecariousLow'
    EVENT_STATE_PRECARIOUS_UPPER = 'PrecariousHigh'
    EVENT_STATE_PHASE_DOWN = 'PhaseDown'

    '''
    Holds a dictionary of available debouncers
    '''
    available_debouncers_dictionary = dict()

    def __init__(self, unique_id, measurement_phase,
                 normal_voltage=220,
                 lower_precarious_voltage=200.2,
                 upper_precarious_voltage=228.2,
                 critical_lower_voltage=189.2,
                 critical_upper_voltage=233.2,
                 history_size=15):
        # Holds parameters
        self.unique_id = unique_id
        self.normal_voltage = normal_voltage
        self.precarious_lower_voltage = lower_precarious_voltage
        self.precarious_upper_voltage = upper_precarious_voltage
        self.critical_lower_voltage = critical_lower_voltage
        self.critical_upper_voltage = critical_upper_voltage
        self.measurement_phase = measurement_phase

        # Holds average filter parameters and data
        self.history_size = history_size
        self.data_history = []
        self.avg_filter = 0
        self.last_measurement = 0

        # Holds current event status
        self.current_event_state = VoltageEventDebouncer.EVENT_STATE_NORMAL
        # Holds last event status transition
        self.last_event_state_transition = \
            (VoltageEventDebouncer.EVENT_STATE_NORMAL,
             VoltageEventDebouncer.EVENT_STATE_NORMAL)

    def reset(self):
        """
        Resets the debouncer to an initial state.
        """
        self.current_event_state = VoltageEventDebouncer.EVENT_STATE_NORMAL
        self.last_event_state_transition = \
            (VoltageEventDebouncer.EVENT_STATE_NORMAL,
             VoltageEventDebouncer.EVENT_STATE_NORMAL)
        self.data_history = []

    def add_new_measurement(self, measurement_phase, measurement_value):
        """
        Adds data from a new measurement to the event debouncer and updates
        the debouncer state
        Args:
            measurement_phase: The signal phase type. For example, if the data
            comes from phase A then type='voltage_a'
            measurement_value: The last measurement value.
        """
        if self.measurement_phase != measurement_phase:
            raise Exception('Measurement has a different phase than the one '
                            'expected for this VoltageEventDebouncer')
        while len(self.data_history) >= self.history_size:
            self.data_history.pop(0)
        self.data_history.append(measurement_value)
        self.last_measurement = measurement_value
        self.avg_filter = sum(self.data_history) / len(self.data_history)
        self.update_current_state()

    def update_current_state(self):
        """
        Updates the current state for the debouncer given a list of possible
        state transitions.
        It works as a FSM.

        Returns:
            The updated current event state.

        """
        # Checks if the phase dropped
        previous_state = self.current_event_state
        if self.check_phase_down():
            self.current_event_state = \
                VoltageEventDebouncer.EVENT_STATE_PHASE_DOWN
        else:
            # Check event transitions
            if self.current_event_state == \
                    VoltageEventDebouncer.EVENT_STATE_CRITICAL_UPPER:
                if not self.check_critical_upper_voltage_with_hysteresis():
                    self.current_event_state = \
                        VoltageEventDebouncer.EVENT_STATE_PRECARIOUS_UPPER
            elif self.current_event_state == \
                    VoltageEventDebouncer.EVENT_STATE_PRECARIOUS_UPPER:
                if self.check_critical_upper_voltage_with_hysteresis():
                    self.current_event_state = \
                        VoltageEventDebouncer.EVENT_STATE_CRITICAL_UPPER
                elif not self.check_precarious_upper_voltage_with_hysteresis():
                    self.current_event_state = \
                        VoltageEventDebouncer.EVENT_STATE_NORMAL
            elif self.current_event_state == VoltageEventDebouncer.\
                    EVENT_STATE_NORMAL:
                if self.check_precarious_upper_voltage_with_hysteresis():
                    self.current_event_state = \
                        VoltageEventDebouncer.EVENT_STATE_PRECARIOUS_UPPER
                elif self.check_precarious_lower_voltage_with_hysteresis():
                    self.current_event_state = \
                        VoltageEventDebouncer.EVENT_STATE_PRECARIOUS_LOWER
            elif self.current_event_state == VoltageEventDebouncer.\
                    EVENT_STATE_PRECARIOUS_LOWER:
                if self.check_critical_lower_voltage_with_hysteresis():
                    self.current_event_state = \
                        VoltageEventDebouncer.EVENT_STATE_CRITICAL_LOWER
                elif not self.check_precarious_lower_voltage_with_hysteresis():
                    self.current_event_state = \
                        VoltageEventDebouncer.EVENT_STATE_NORMAL
            elif self.current_event_state == VoltageEventDebouncer.\
                    EVENT_STATE_CRITICAL_LOWER:
                if not self.check_precarious_lower_voltage_with_hysteresis():
                    self.current_event_state = \
                        VoltageEventDebouncer.EVENT_STATE_PRECARIOUS_LOWER
            else:  # Phase Down State -> Critical Lower
                self.current_event_state = \
                    VoltageEventDebouncer.EVENT_STATE_CRITICAL_LOWER

        self.last_event_state_transition = \
            (previous_state, self.current_event_state)
        return self.current_event_state

    def check_phase_down(self):
        """
        Checks whether the phase signal is current down (not enough voltage
        amplitude).

        Returns: True if the phase is down, False otherwise.

        """
        is_phase_down = False
        if self.last_measurement < (
                VoltageEventDebouncer.
                PHASE_DOWN_THRESHOLD_RATE * self.normal_voltage):
            is_phase_down = True
        return is_phase_down

    def check_critical_lower_voltage_with_hysteresis(
            self, hysteresis_rate=0.03):
        """
        Checks whether the phase is current below a critical level.
        Args:
            hysteresis_rate: The rate for the hysteresis.

        Returns: True if critical, False otherwise.

        """
        hysteresis_threshold = \
            self.critical_lower_voltage * (1 + hysteresis_rate)
        is_in_critical_lower_state = (
            self.current_event_state == VoltageEventDebouncer.
            EVENT_STATE_CRITICAL_LOWER)

        if is_in_critical_lower_state:
            if self.avg_filter > hysteresis_threshold and \
                    self.last_measurement > hysteresis_threshold:
                return False
            else:
                return True
        else:
            if self.last_measurement < self.critical_lower_voltage:
                return True
            else:
                return False

    def check_critical_upper_voltage_with_hysteresis(
            self, hysteresis_rate=0.03):
        """
        Checks whether the phase is currently above the critical level using
        hysteresis.
        Args:
            hysteresis_rate: The rate for hysteresis.

        Returns: True if it is above upper critical level, False otherwise.
        """
        hysteresis_threshold = \
            self.critical_upper_voltage * (1 - hysteresis_rate)
        is_in_critical_upper_state = (
            self.current_event_state == VoltageEventDebouncer.
            EVENT_STATE_CRITICAL_UPPER)
        if is_in_critical_upper_state:
            if self.avg_filter < hysteresis_threshold and \
                    self.last_measurement < hysteresis_threshold:
                return False
            else:
                return True
        else:
            if self.last_measurement > self.critical_upper_voltage:
                return True
            else:
                return False

    def check_precarious_upper_voltage_with_hysteresis(
            self, hysteresis_rate=0.03):
        """
        Checks whether the phase is current above a precarious level
        Args:
            hysteresis_rate: The rate for the hysteresis.

        Returns: True if precarious, False otherwise.

        """
        hysteresis_threshold = \
            self.precarious_upper_voltage * (1 - hysteresis_rate)
        is_in_precarious_upper_state = (
            self.current_event_state == VoltageEventDebouncer.
            EVENT_STATE_PRECARIOUS_UPPER)
        if is_in_precarious_upper_state:
            if self.avg_filter < hysteresis_threshold and \
                    self.last_measurement < hysteresis_threshold:
                return False
            else:
                return True
        else:
            if self.last_measurement > self.precarious_upper_voltage:
                return True
            else:
                return False

    def check_precarious_lower_voltage_with_hysteresis(
            self, hysteresis_rate=0.03):
        """
        Checks whether the phase is below a precarious level.
        Args:
            hysteresis_rate: The rate for the hysteresis.

        Returns: True if precarious, False otherwise.

        """
        hysteresis_threshold = \
            self.precarious_lower_voltage * (1 + hysteresis_rate)
        is_in_precarious_lower_state = (
            self.current_event_state == VoltageEventDebouncer.
            EVENT_STATE_PRECARIOUS_LOWER)
        if is_in_precarious_lower_state:
            if self.avg_filter > hysteresis_threshold and \
                    self.last_measurement > hysteresis_threshold:
                return False
            else:
                return True
        else:
            if self.last_measurement < self.precarious_lower_voltage:
                return True
            else:
                return False

    @staticmethod
    def get_target_event_name(event_state):
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
        if (event_state == VoltageEventDebouncer.
            EVENT_STATE_CRITICAL_UPPER) or \
            (event_state == VoltageEventDebouncer.
                EVENT_STATE_CRITICAL_LOWER):
            return CriticalVoltageEvent.__name__
        elif (event_state == VoltageEventDebouncer.
                EVENT_STATE_PRECARIOUS_UPPER) or \
                (event_state == VoltageEventDebouncer.
                    EVENT_STATE_PRECARIOUS_LOWER):
            return PrecariousVoltageEvent.__name__
        elif event_state == VoltageEventDebouncer.EVENT_STATE_PHASE_DOWN:
            return PhaseDropEvent.__name__
        else:  # Does nothing when its normal state
            return None

    @staticmethod
    def get_voltage_debouncer(transductor, measurement_phase):
        """
        Getter to the voltage debouncer mapped to a transductor and a phase.
        Args:
            transductor: The used transductor.
            measurement_phase:  The phase used.

        Returns: The voltage event debouncer.

        """
        if VoltageEventDebouncer.available_debouncers_dictionary.get(
                transductor.serial_number + measurement_phase) is None:
            VoltageEventDebouncer.available_debouncers_dictionary[
                transductor.serial_number + measurement_phase] = \
                VoltageEventDebouncer(
                    transductor.serial_number + measurement_phase,
                    measurement_phase)

        return VoltageEventDebouncer.available_debouncers_dictionary.get(
            transductor.serial_number + measurement_phase)

    def raise_event(self, transductor):
        RaisedVoltageEventData.initialize_transductor_events(transductor)

        if self.last_event_state_transition[0] != \
                self.last_event_state_transition[1]:
            RaisedVoltageEventData.finish_transductor_event(
                transductor,
                self.get_target_event_name(self.last_event_state_transition[0]),
                self.measurement_phase)
        if self.current_event_state != VoltageEventDebouncer.EVENT_STATE_NORMAL:
            RaisedVoltageEventData.update_transductor_event_data(
                transductor,
                self.get_target_event_name(self.current_event_state),
                self.measurement_phase, self.last_measurement)
