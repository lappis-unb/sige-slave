from django.db import models
from django.utils import timezone

from transductor.models import Transductor


class Event(models.Model):
    """
    Defines a new event object
    """

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    transductor = models.ForeignKey(
        Transductor,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    data = models.JSONField()

    def __str__(self):
        return "%s@%s" % (self.__class__.__name__, self.created_at)


class VoltageRelatedEvent(Event):
    """
    Defines a new event related to a voltage metric
    """

    non_polymorphic = models.Manager()

    class Meta:
        base_manager_name = "non_polymorphic"

    def all_phases_are_none(self):
        for phase_name, phase_value in self.data.items():
            if phase_value:
                return False
        return True


class FailedConnectionTransductorEvent(Event):
    """
    Defines a new event related to a failed connection with a transductor
    """


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
