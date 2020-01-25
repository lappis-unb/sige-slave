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

    def reset_filter(self):
        self.is_phase_down = False
        self.is_above_upper_critical_level = False
        self.is_above_upper_precarious_level = False
        self.is_below_lower_critical_level = False
        self.is_below_lower_precarious_level = False
        self.data_history = []

    def add_data(self, type, last_measurement):
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

    def check_phase_down(self, normal_measurement, phase_down_rate=0.8):
        if self.last_measurement < normal_measurement * phase_down_rate:
            self.is_phase_down = True
        else:
            self.is_phase_down = False
        return self.is_phase_down

    def check_critical_upper_voltage_with_hysteresis(
            self, critical_upper_boundary, hysteresis_rate=0.04):
        hysteresis_threshold = critical_upper_boundary * (1 - hysteresis_rate)
        if self.last_measurement > critical_upper_boundary or \
                self.avg_filter > critical_upper_boundary:
            self.is_above_upper_critical_level = True
        elif self.avg_filter < hysteresis_threshold and \
                self.last_measurement < hysteresis_threshold:
            self.is_above_upper_critical_level = False
        return self.is_above_upper_critical_level

    def check_precarious_upper_voltage_with_hysteresis(
            self, precarious_upper_boundary, hysteresis_rate=0.04):
        hysteresis_threshold = precarious_upper_boundary * (1 - hysteresis_rate)
        if self.last_measurement > precarious_upper_boundary or \
                self.avg_filter > precarious_upper_boundary:
            self.is_above_upper_precarious_level = True
        elif self.avg_filter < hysteresis_threshold and \
                self.last_measurement < hysteresis_threshold:
            self.is_above_upper_precarious_level = False
        return self.is_above_upper_precarious_level

    def check_critical_lower_voltage_with_hysteresis(
            self, critical_lower_boundary, hysteresis_rate=0.04):
        hysteresis_threshold = critical_lower_boundary * (1 + hysteresis_rate)
        if self.last_measurement < critical_lower_boundary or \
                self.avg_filter < critical_lower_boundary:
            self.is_below_lower_critical_level = True
        elif self.avg_filter > hysteresis_threshold and \
                self.last_measurement > hysteresis_threshold:
            self.is_below_lower_critical_level = False
        return self.is_below_lower_critical_level

    def check_precarious_lower_voltage_with_hysteresis(
            self, precarious_lower_boundary, histeresis_rate=0.04):
        hysteresis_threshold = \
            precarious_lower_boundary * (1 + histeresis_rate)
        if self.last_measurement < precarious_lower_boundary or \
                self.avg_filter < precarious_lower_boundary:
            self.is_below_lower_precarious_level = True
        elif self.avg_filter > hysteresis_threshold and \
                self.last_measurement > hysteresis_threshold:
            self.is_below_lower_precarious_level = False
        return self.is_below_lower_precarious_level

    def get_average_filter_value(self):
        return self.avg_filter

    @staticmethod
    def remove_entries_in_event_lists(debouncer_id):
        if VoltageEventDebouncer.event_lists_dictionary.get(
                debouncer_id) is not None:
            del VoltageEventDebouncer.event_lists_dictionary[debouncer_id]
        VoltageEventDebouncer.event_lists_dictionary[debouncer_id] = \
            [[], [], [], [], []]

    @staticmethod
    def get_event_lists(debouncer_id):
        if VoltageEventDebouncer.event_lists_dictionary.get(
                debouncer_id) is None:
            VoltageEventDebouncer.event_lists_dictionary[debouncer_id] = \
                [[], [], [], [], []]
        return VoltageEventDebouncer.event_lists_dictionary.get(debouncer_id)

    @staticmethod
    def get_voltage_debouncer(transductor, measurement_phase):
        if VoltageEventDebouncer.debouncers_dictionary.get(
                transductor.serial_number + measurement_phase) is None:

            VoltageEventDebouncer.debouncers_dictionary[
                transductor.serial_number + measurement_phase] = \
                VoltageEventDebouncer(
                    transductor.serial_number + measurement_phase)

        return VoltageEventDebouncer.debouncers_dictionary.get(
            transductor.serial_number + measurement_phase)

    def populate_voltage_event_lists(self, voltage_parameters):
        '''
        Identify and raise "unique" events in which the voltage is in
        critical/precarious levels. It uses an Average Filter with a
        Default period of 45 minutes as a "debouncer" to the voltage signal.
        '''
        event_lists = VoltageEventDebouncer.get_event_lists(self.id)

        used_voltage = voltage_parameters[0]
        precary_lower_boundary = voltage_parameters[1]
        precary_upper_boundary = voltage_parameters[2]
        critical_lower_boundary = voltage_parameters[3]
        critical_upper_boundary = voltage_parameters[4]

        if self.check_phase_down(used_voltage):
            if event_lists[0] == []:
                VoltageEventDebouncer.remove_entries_in_event_lists(self.id)
                VoltageEventDebouncer.event_lists_dictionary[self.id][0].append(
                    [self.measurement_type, self.last_measurement])
            self.is_below_lower_precarious_level = False
            self.is_below_lower_critical_level = False
            self.is_above_upper_precarious_level = False
            self.is_above_upper_critical_level = False
        elif self.check_critical_lower_voltage_with_hysteresis(
                critical_lower_boundary):
            if event_lists[1] == []:
                VoltageEventDebouncer.remove_entries_in_event_lists(self.id)
                VoltageEventDebouncer.event_lists_dictionary[self.id][1].append(
                    [self.measurement_type, self.last_measurement])
            self.is_below_lower_precarious_level = False
            self.is_phase_down = False
            self.is_above_upper_precarious_level = False
            self.is_above_upper_critical_level = False
        elif self.check_critical_upper_voltage_with_hysteresis(
                critical_upper_boundary):
            if event_lists[2] == []:
                VoltageEventDebouncer.remove_entries_in_event_lists(self.id)
                VoltageEventDebouncer.event_lists_dictionary[self.id][2].append(
                    [self.measurement_type, self.last_measurement])
            self.is_below_lower_precarious_level = False
            self.is_below_lower_critical_level = False
            self.is_above_upper_precarious_level = False
            self.is_phase_down = False
        elif self.check_precarious_lower_voltage_with_hysteresis(
                precary_lower_boundary):
            if event_lists[3] == []:
                VoltageEventDebouncer.remove_entries_in_event_lists(self.id)
                VoltageEventDebouncer.event_lists_dictionary[self.id][3].append(
                    [self.measurement_type, self.last_measurement])
            self.is_phase_down = False
            self.is_below_lower_critical_level = False
            self.is_above_upper_precarious_level = False
            self.is_above_upper_critical_level = False
        elif self.check_precarious_upper_voltage_with_hysteresis(
                precary_upper_boundary):
            if event_lists[4] == []:
                VoltageEventDebouncer.remove_entries_in_event_lists(self.id)
                VoltageEventDebouncer.event_lists_dictionary[self.id][4].append(
                    [self.measurement_type, self.last_measurement])
            self.is_below_lower_precarious_level = False
            self.is_below_lower_critical_level = False
            self.is_phase_down = False
            self.is_above_upper_critical_level = False
        else:
            self.is_phase_down = False
            self.is_below_lower_precarious_level = False
            self.is_below_lower_critical_level = False
            self.is_above_upper_precarious_level = False
            self.is_above_upper_critical_level = False
            VoltageEventDebouncer.remove_entries_in_event_lists(self.id)
