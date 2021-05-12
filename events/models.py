from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from polymorphic.models import PolymorphicModel

from transductor.models import EnergyTransductor


class Event(PolymorphicModel):
    """
    Defines a new event object
    """

    created_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    transductor = models.ForeignKey(
        EnergyTransductor,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    data = JSONField(default=dict)

    def __str__(self):
        return "%s@%s" % (self.__class__.__name__, self.created_at)

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
        base_manager_name = "non_polymorphic"

    def save_event(self, transductor, list_data=[]):
        self.transductor = transductor
        self.data = dict()

        for phase in list_data:
            self.data[phase[0]] = phase[1]

        self.save()
        return self

    def all_phases_are_none(self):
        for phase_name, phase_value in self.data.items():
            if phase_value:
                return False
        return True


class FailedConnectionTransductorEvent(Event):
    """
    Defines a new event related to a failed connection with a transductor
    """

    def save_event(self, transductor, list_data=[]):
        self.transductor = transductor
        self.data = dict()
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
