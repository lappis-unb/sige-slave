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
    measures = JSONField()

    transductor = models.ForeignKey(
        EnergyTransductor,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )

    def __str__(self):
        return '%s@%s' % (self.__class__.__name__, self.created_at)

    def save_event(self):
        """
        Saves the event.
        """
        raise NotImplementedError


class FailedConnectionEvent(Event):
    """
    Defines a new event related to a failed connection with a transductor
    """

    def save_event(self, transductor):
        """
        Saves a failed connection event related to a transductor
        """
        new_event = FailedConnectionEvent()
        new_event.transductor = transductor
        new_event.measures = {}

        new_event.save()
        return new_event


class CriticalVoltageEvent(Event):
    """
    Defines a new event related to a critical voltage measurement
    """

    def save_event(self, transductor, list_critical_phases):
        new_event = CriticalVoltageEvent()
        new_event.transductor = transductor
        new_event.measures = {}

        for phase in list_critical_phases:
            new_event.measures[phase[0]] = phase[1]

        new_event.save()
        return new_event


class PrecariousVoltageEvent(Event):
    """
    Defines a new event related to a precarious voltage measurement
    """

    def save_event(self, transductor, list_precarious_phases):
        new_event = PrecariousVoltageEvent()
        new_event.transductor = transductor
        new_event.measures = {}

        for phase in list_precarious_phases:
            new_event.measures[phase[0]] = phase[1]

        new_event.save()
        return new_event


class PhaseDropEvent(Event):
    """
    Defines a new event related to a drop on the triphasic voltage measurement
    """

    def save_event(self, transductor, list_down_phases):
        new_event = PhaseDropEvent()
        new_event.transductor = transductor
        new_event.measures = {}

        for phase in list_down_phases:
            new_event.measures[phase[0]] = phase[1]

        new_event.save()
        return new_event
