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
