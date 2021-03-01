import json

from itertools import chain
from datetime import datetime

from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.postgres.fields import ArrayField

from utils import is_datetime_similar


class Transductor(models.Model):
    """
    Base class responsible to create an abstraction of a transductor.

    Attributes:
        serial_number (int): The serie number.
        ip_address (str): The ip address.
        broken (bool): Tells if the transductor is working correctly.
        active (bool): Tells if the transductor can collect data.
        model (TransductorModel): The transductor model.
        firmware_version (str): Tells the transductor's firmware
            version number.
        installation_date (datetime): Tells the installation date
            of a transductor
        physical_location (str): Tells where the transductor is located
        geolocation_longitude (decimal): Tells geographic location
            for a transductor
        geolocation_latitude (decimal): Tells geographic location
            for a transductor
        last_clock_battery_change (datetime): Stores the latest update for the
            transductor's internal clock.
    """
    # TODO fix default value problem
    serial_number = models.CharField(
        max_length=8,
        unique=True,
    )
    ip_address = models.CharField(
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
    port = models.IntegerField(default=1001)
    model = models.CharField(max_length=50, default="EnergyTransductorModel")
    broken = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    firmware_version = models.CharField(max_length=20)
    installation_date = models.DateTimeField(blank=True, null=True)
    physical_location = models.CharField(max_length=30, default='')
    quarterly_data_rescued = models.BooleanField(default=False)
    monthly_data_rescued = models.BooleanField(default=False)
    geolocation_longitude = models.DecimalField(
        max_digits=15,
        decimal_places=10
    )
    geolocation_latitude = models.DecimalField(
        max_digits=15,
        decimal_places=10
    )
    last_clock_battery_change = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    def get_measurements(self):
        """
        Method responsible to retrieve all measurements from
        a specific transductor.

        Args:
            None

        Returns:
            list: List of all measurements
        """
        raise NotImplementedError


class EnergyTransductor(Transductor):
    """
    Class responsible to represent a Energy Transductor which will
    collect energy measurements.

    Example of use:

    >>> t_model = TransductorModel(name="Test Name",
    transport_protocol="UDP", serial_protocol="Modbus RTU",
    register_addresses=[[68, 0], [70, 1]])
    >>> EnergyTransductor(model=t_model, serie_number=1,
    ip_address="1.1.1.1", description="Energy Transductor Test")
    <EnergyTransductor: Energy Transductor Test>
    """

    def __str__(self):
        return self.serial_number

    def set_broken(self, new_status: bool) -> bool:
        """
        Set the broken atribute's new status to match the param.
        If toggled to True, creates a failed connection event
        If toggled to False, closes the created failed connection event
        """
        from events.models import FailedConnectionTransductorEvent

        if new_status == self.broken:
            return self.broken

        old_status = self.broken
        self.broken = new_status
        self.save(update_fields=['broken'])

        # The transductor was working and is now "broken"
        if old_status is False and new_status is True:
            FailedConnectionTransductorEvent.objects.create(transductor=self)
            TimeInterval.objects.create(
                transductor=self,
                begin=timezone.datetime.now(),
            )

        # The transductor was "broken" and now is working
        elif old_status is True and new_status is False:
            last_open_interval = self.timeintervals.last()

            if not last_open_interval:
                raise Exception(
                    'There are no open time intervals on this transductor!'
                )

            # closing the last open interval
            last_open_interval.end = timezone.datetime.now()
            last_open_interval.save(update_fields=['end'])

            related_event_qs = FailedConnectionTransductorEvent.objects.filter(
                transductor=self,
                ended_at__isnull=True
            )

            # save end time of last connection failure event
            if related_event_qs.last():
                last_open_related_event = related_event_qs.last()
                last_open_related_event.ended_at = timezone.now()
                last_open_related_event.save(
                    update_fields=['ended_at']
                )

            else:
                print('There is no element in queryset filtered.')
                # TODO: send to sentry!!!
                # This is an error, but for now we are ignoring

        return self.broken

    def get_minutely_measurements_by_datetime(self, start_date, final_date):
        # dates must match 'yyyy-mm-dd'
        return self.minutely_measurements.filter(
            collection_date__range=[start_date, final_date]
        )

    def get_quarterly_measurements_by_datetime(self, start_date, final_date):
        # dates must match 'yyyy-mm-dd'
        return self.quarterly_measurements.filter(
            collection_date__range=[start_date, final_date]
        )

    def get_monthly_measurements_by_datetime(self, start_date, final_date):
        # dates must match 'yyyy-mm-dd'
        return self.monthly_measurements.filter(
            collection_date__range=[start_date, final_date]
        )

    def get_minutely_measurements(self):
        return self.minutely_measurements.all()

    def get_quarterly_measurements(self):
        return self.quarterly_measurements.all()

    def get_monthly_measurements(self):
        return self.monthly_measurements.all()


class TimeInterval(models.Model):

    begin = models.DateTimeField(null=False)
    end = models.DateTimeField(null=True)

    # TODO Change related name

    transductor = models.ForeignKey(
        EnergyTransductor,
        models.CASCADE,
        related_name='timeintervals',
    )

    @staticmethod
    def begin_interval(transductor):
        time_interval = TimeInterval()
        time_interval.begin = timezone.datetime.now()
        time_interval.transductor = transductor
        time_interval.save()

    def end_interval(self):
        self.end = timezone.datetime.now()
        self.save(update_fields=['end'])

    def change_interval(self, time):
        self.begin = time + timezone.timedelta(minutes=1)

        # Verifies if collected date is inside the recovery interval
        if self.end < time or is_datetime_similar(self.end, time):
            self.delete()
            return False
        else:
            self.save(update_fields=['begin'])
            return True
