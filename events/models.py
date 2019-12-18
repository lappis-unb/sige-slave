from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from transductor.models import EnergyTransductor


class Event(models.Model):
    """
    Defines a new event object
    """
    settings.USE_TZ = False
    created_at = models.DateTimeField(default=timezone.now)

    def __format_data(self, data):
        """
        Takes the data of what created the event and saves it in a dict.
        """
        formatted_data = dict(

        )
        return formatted_data

    def __str__(self):
        return '%s - %s' % (self.__class__.__name__, self.created_at)

    def save_event(self):
        """
        Saves the event
        """
        raise NotImplementedError


class VoltageRelatedEvent(Event):

    class Meta:
        abstract = True

    phase_a = models.FloatField(default=0)
    phase_b = models.FloatField(default=0)
    phase_c = models.FloatField(default=0)


class FailedConnectionEvent(Event):
    """
    Defines a new event related to a failed connection with a transductor
    """
    transductor_ip = models.CharField(
        max_length=15,
        unique=True,
        default="0.0.0.0",
        validators=[
            RegexValidator(
                regex='^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$',
                message='Incorrect IP address format',
                code='invalid_ip_address'
            ),
        ])

    transductor = models.ForeignKey(
        EnergyTransductor,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )

    @staticmethod
    def save_event(transductor):
        """
        Saves a failed connection event related to a transductor
        """
        new_event = FailedConnectionEvent()
        new_event.transductor = transductor
        new_event.transductor_ip = new_event.transductor.ip_address

        new_event.save()

        return new_event


class CriticalVoltageEvent(VoltageRelatedEvent):
    """
    Defines a new event related to a critical voltage measurement
    """

    @staticmethod
    def save_event(measurement):
        event = CriticalVoltageEvent()
        event.phase_a = measurement.voltage_a
        event.phase_b = measurement.voltage_b
        event.phase_c = measurement.voltage_c

        event.save()
        return event


class PrecariousVoltageEvent(VoltageRelatedEvent):
    """
    Defines a new event related to a precarious voltage measurement
    """

    @staticmethod
    def save_event(measurement):
        event = PrecariousVoltageEvent()
        event.phase_a = measurement.voltage_a
        event.phase_b = measurement.voltage_b
        event.phase_c = measurement.voltage_c

        event.save()
        return event


class PhaseDropEvent(VoltageRelatedEvent):
    """
    Defines a new event related to a drop on the triphasic voltage measurement
    """

    @staticmethod
    def save_event(measurement):
        event = PhaseDropEvent()
        event.phase_a = measurement.voltage_a
        event.phase_b = measurement.voltage_b
        event.phase_c = measurement.voltage_c

        event.save()
        return event


class MaximumConsumptionReachedEvent(Event):
    """
    Defines a new event related to maximum energy consumption
    """

    from measurement.models import QuarterlyMeasurement
    measurement = models.ForeignKey(
        QuarterlyMeasurement,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )

    @staticmethod
    def save_event(measurement):
        pass
