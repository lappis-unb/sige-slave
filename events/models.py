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


class VoltageEventDebouncer():
    '''
    Defines a debouncer for voltage related events
    '''
    debouncers_dictionary = dict()
    event_lists_dictionary = dict()

    def __init__(self, id, history_size=15):
        self.history_size = history_size
        self.data_history = []
        self.avg_filter = 0
        self.measurement_type = ''
        self.last_measurement = 0
        self.is_phase_down = False
        self.is_above_upper_critical_level = False
        self.is_above_upper_precarious_level = False
        self.is_below_lower_critical_level = False
        self.is_below_lower_precarious_level = False
        self.id = id
        self.raised_event = None

    def reset_filter(self):
        """
        Resets the filter to an initial state.
        """
        self.is_phase_down = False
        self.is_above_upper_critical_level = False
        self.is_above_upper_precarious_level = False
        self.is_below_lower_critical_level = False
        self.is_below_lower_precarious_level = False
        self.data_history = []
        VoltageEventDebouncer.remove_entries_in_event_lists(self.id)
        self.raised_event = None

    def add_data(self, type, last_measurement):
        """
        Adds data to the event debouncer, It is expected that the data added
        is obtained through a new measurement.
        Args:
            type: The signal phase type. For example, if the data comes from
            phase A then type='voltage_a'
            last_measurement: The last measurement value.
        """
        if self.measurement_type == '':
            self.measurement_type = type
        elif self.measurement_type != type:
            raise Exception('Measurement has a different phase than the one '
                            'expected for this VoltageEventDebouncer')

        while len(self.data_history) >= self.history_size:
            self.data_history.pop(0)
        self.data_history.append(last_measurement)
        self.last_measurement = last_measurement

        self.avg_filter = 0
        for measurement_data in self.data_history:
            self.avg_filter += measurement_data
        self.avg_filter /= len(self.data_history)

    def check_phase_down(self, normal_measurement, phase_down_rate=0.5):
        """
        Checks whether the phase signal is current down (not enough voltage
        amplitude).
        Args:
            normal_measurement: The expected voltage level for a normal
            measurement.
            phase_down_rate: The rate of a normal measurement for a phase
            start to be considered down.

        Returns: True if the phase is down, False otherwise.
        """
        threshold = normal_measurement * phase_down_rate
        if self.last_measurement < threshold or self.avg_filter < threshold:
            self.is_phase_down = True
        else:
            self.is_phase_down = False
        return self.is_phase_down

    def check_critical_upper_voltage_with_hysteresis(
            self, critical_upper_boundary, hysteresis_rate=0.03):
        """
        Checks whether the phase is currently above the critical level using
        hysteresis.
        Args:
            critical_upper_boundary: The voltage level for the signal start to
            be considered above upper critical level.
            hysteresis_rate: The rate for hysteresis.

        Returns: True if it is above upper critical level, False otherwise.

        """
        hysteresis_threshold = critical_upper_boundary * (1 - hysteresis_rate)
        lm_above_bound = self.last_measurement > critical_upper_boundary
        af_above_bound = self.avg_filter > critical_upper_boundary
        if lm_above_bound or (af_above_bound and lm_above_bound):
            self.is_above_upper_critical_level = True
        elif self.avg_filter < hysteresis_threshold and \
                self.last_measurement < hysteresis_threshold:
            self.is_above_upper_critical_level = False
        return self.is_above_upper_critical_level

    def check_precarious_upper_voltage_with_hysteresis(
            self, precarious_upper_boundary, hysteresis_rate=0.03):
        """
        Checks whether the phase is current above a precarious level
        Args:
            precarious_upper_boundary: The voltage level in which the phase is
            considered precarious.
            hysteresis_rate: The rate for the hysteresis.

        Returns: True if precarious, False otherwise.

        """
        hysteresis_threshold = precarious_upper_boundary * (1 - hysteresis_rate)
        lm_above_bound = self.last_measurement > precarious_upper_boundary
        af_above_bound = self.avg_filter > precarious_upper_boundary
        if lm_above_bound or (lm_above_bound and af_above_bound):
            self.is_above_upper_precarious_level = True
        elif self.avg_filter < hysteresis_threshold and \
                self.last_measurement < hysteresis_threshold:
            self.is_above_upper_precarious_level = False
        return self.is_above_upper_precarious_level

    def check_critical_lower_voltage_with_hysteresis(
            self, critical_lower_boundary, hysteresis_rate=0.03):
        """
        Checks whether the phase is current below a critical level.
        Args:
            critical_lower_boundary: The voltage level in which the phase is
            considered critical.
            hysteresis_rate: The rate for the hysteresis.

        Returns: True if critical, False otherwise.

        """
        hysteresis_threshold = critical_lower_boundary * (1 + hysteresis_rate)
        lm_below_bound = self.last_measurement < critical_lower_boundary
        af_below_bound = self.avg_filter < critical_lower_boundary
        if lm_below_bound or (lm_below_bound and af_below_bound):
            self.is_below_lower_critical_level = True
        elif self.avg_filter > hysteresis_threshold and \
                self.last_measurement > hysteresis_threshold:
            self.is_below_lower_critical_level = False
        return self.is_below_lower_critical_level

    def check_precarious_lower_voltage_with_hysteresis(
            self, precarious_lower_boundary, hysteresis_rate=0.03):
        """
        Checks whether the phase is below a precarious level.
        Args:
            precarious_lower_boundary: The voltage level in which the phase
            starts to be considered precarious.
            hysteresis_rate: The rate for the hysteresis.

        Returns: True if precarious, False otherwise.

        """
        hysteresis_threshold = \
            precarious_lower_boundary * (1 + hysteresis_rate)
        lm_below_bound = self.last_measurement < precarious_lower_boundary
        af_below_bound = self.avg_filter < precarious_lower_boundary
        if lm_below_bound or (lm_below_bound and af_below_bound):
            self.is_below_lower_precarious_level = True
        elif self.avg_filter > hysteresis_threshold and \
                self.last_measurement > hysteresis_threshold:
            self.is_below_lower_precarious_level = False
        return self.is_below_lower_precarious_level

    def get_average_filter_value(self):
        """
        Getter to the debouncer average filter current value.
        Returns: The average filter value.

        """
        return self.avg_filter

    def get_event_checking_states(self):
        """
        Getter to the debouncer checking current states.
        Returns: True if there are a event happening, False otherwise.

        """
        return self.is_below_lower_precarious_level or \
            self.is_below_lower_critical_level or \
            self.is_above_upper_precarious_level or \
            self.is_above_upper_critical_level or \
            self.is_phase_down

    @staticmethod
    def remove_entries_in_event_lists(debouncer_id):
        """
        Removes any entries for the event list mapped to this debouncer.
        Args:
            debouncer_id: The debouncer id.

        Returns:

        """
        if VoltageEventDebouncer.event_lists_dictionary.get(
                debouncer_id) is not None:
            del VoltageEventDebouncer.event_lists_dictionary[debouncer_id]
        VoltageEventDebouncer.event_lists_dictionary[debouncer_id] = \
            [[], [], [], [], []]

    @staticmethod
    def get_event_lists(debouncer_id):
        """
        Getter to the event list attached to a specific debouncer.
        Args:
            debouncer_id: The deboncer id.

        Returns: The event lists.

        """
        if VoltageEventDebouncer.event_lists_dictionary.get(
                debouncer_id) is None:
            VoltageEventDebouncer.event_lists_dictionary[debouncer_id] = \
                [[], [], [], [], []]
        return VoltageEventDebouncer.event_lists_dictionary.get(debouncer_id)

    @staticmethod
    def get_voltage_debouncer(transductor, measurement_phase):
        """
        Getter to the voltage debouncer mapped to a transductor and a phase.
        Args:
            transductor: The used transductor.
            measurement_phase:  The phase used.

        Returns: The voltage event debouncer.

        """
        if VoltageEventDebouncer.debouncers_dictionary.get(
                transductor.serial_number + measurement_phase) is None:

            VoltageEventDebouncer.debouncers_dictionary[
                transductor.serial_number + measurement_phase] = \
                VoltageEventDebouncer(
                    transductor.serial_number + measurement_phase)

        return VoltageEventDebouncer.debouncers_dictionary.get(
            transductor.serial_number + measurement_phase)

    def raise_event(self, voltage_parameters, transductor):
        """
        Raises a event depending on the last measurement added to the debouncer.
        Args:
            voltage_parameters: The voltage parameters, respectively,
            the used standard voltage,
            the lower precary voltage level,
            the upper precary voltage level,
            the lower critical voltage level,
            and the upper critical voltage level.
            transductor: The transductor in which the measurements were read
            from.

        Returns:

        """
        used_voltage = voltage_parameters[0]
        precary_lower_boundary = voltage_parameters[1]
        precary_upper_boundary = voltage_parameters[2]
        critical_lower_boundary = voltage_parameters[3]
        critical_upper_boundary = voltage_parameters[4]

        if self.check_phase_down(used_voltage):
            if VoltageEventDebouncer.event_lists_dictionary[self.id][0] == []:
                VoltageEventDebouncer.remove_entries_in_event_lists(self.id)
                VoltageEventDebouncer.event_lists_dictionary[self.id][0].append(
                    [self.measurement_type, self.last_measurement])
                if self.raised_event is not None:
                    self.raised_event.ended_at = timezone.datetime.now()
                    self.raised_event.save()
                    self.raised_event = None
                self.raised_event = PhaseDropEvent()
                self.raised_event.save_event(
                    transductor, VoltageEventDebouncer.event_lists_dictionary[
                        self.id][0])
            self.is_below_lower_precarious_level = False
            self.is_below_lower_critical_level = False
            self.is_above_upper_precarious_level = False
            self.is_above_upper_critical_level = False
        elif self.check_critical_upper_voltage_with_hysteresis(
                critical_upper_boundary):
            if VoltageEventDebouncer.event_lists_dictionary[self.id][2] == []:
                VoltageEventDebouncer.remove_entries_in_event_lists(self.id)
                VoltageEventDebouncer.event_lists_dictionary[self.id][2].append(
                    [self.measurement_type, self.last_measurement])
                if self.raised_event is not None:
                    self.raised_event.ended_at = timezone.datetime.now()
                    self.raised_event.save()
                    self.raised_event = None
                self.raised_event = CriticalVoltageEvent()
                self.raised_event.save_event(
                    transductor, VoltageEventDebouncer.event_lists_dictionary[
                        self.id][2])
            self.is_below_lower_precarious_level = False
            self.is_below_lower_critical_level = False
            self.is_above_upper_precarious_level = False
            self.is_phase_down = False
        elif self.check_critical_lower_voltage_with_hysteresis(
                critical_lower_boundary):
            if VoltageEventDebouncer.event_lists_dictionary[self.id][1] == []:
                VoltageEventDebouncer.remove_entries_in_event_lists(self.id)
                VoltageEventDebouncer.event_lists_dictionary[self.id][1].append(
                    [self.measurement_type, self.last_measurement])
                if self.raised_event is not None:
                    self.raised_event.ended_at = timezone.datetime.now()
                    self.raised_event.save()
                    self.raised_event = None
                self.raised_event = CriticalVoltageEvent()
                self.raised_event.save_event(
                    transductor, VoltageEventDebouncer.event_lists_dictionary[
                        self.id][1])
            self.is_below_lower_precarious_level = False
            self.is_phase_down = False
            self.is_above_upper_precarious_level = False
            self.is_above_upper_critical_level = False
        elif self.check_precarious_upper_voltage_with_hysteresis(
                precary_upper_boundary):
            if VoltageEventDebouncer.event_lists_dictionary[self.id][
                    4] == [] and self.raised_event is None:
                VoltageEventDebouncer.remove_entries_in_event_lists(self.id)
                VoltageEventDebouncer.event_lists_dictionary[self.id][4].append(
                    [self.measurement_type, self.last_measurement])
                if self.raised_event is not None:
                    self.raised_event.ended_at = timezone.datetime.now()
                    self.raised_event.save()
                    self.raised_event = None
                self.raised_event = PrecariousVoltageEvent()
                self.raised_event.save_event(
                    transductor, VoltageEventDebouncer.event_lists_dictionary[
                        self.id][4])
            self.is_below_lower_precarious_level = False
            self.is_below_lower_critical_level = False
            self.is_phase_down = False
            self.is_above_upper_critical_level = False
        elif self.check_precarious_lower_voltage_with_hysteresis(
                precary_lower_boundary):
            if VoltageEventDebouncer.event_lists_dictionary[self.id][
                    3] == [] and (
                    self.is_phase_down or self.raised_event is None):
                VoltageEventDebouncer.remove_entries_in_event_lists(self.id)
                VoltageEventDebouncer.event_lists_dictionary[self.id][3].append(
                    [self.measurement_type, self.last_measurement])
                if self.raised_event is not None:
                    self.raised_event.ended_at = timezone.datetime.now()
                    self.raised_event.save()
                    self.raised_event = None
                self.raised_event = PrecariousVoltageEvent()
                self.raised_event.save_event(
                    transductor, VoltageEventDebouncer.event_lists_dictionary[
                        self.id][3])
            self.is_phase_down = False
            self.is_below_lower_critical_level = False
            self.is_above_upper_precarious_level = False
            self.is_above_upper_critical_level = False
        else:
            if self.raised_event is not None:
                self.raised_event.ended_at = timezone.datetime.now()
                self.raised_event.save()
                self.raised_event = None
            self.is_phase_down = False
            self.is_below_lower_precarious_level = False
            self.is_below_lower_critical_level = False
            self.is_above_upper_precarious_level = False
            self.is_above_upper_critical_level = False
            VoltageEventDebouncer.remove_entries_in_event_lists(self.id)
