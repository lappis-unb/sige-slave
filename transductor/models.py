from django.db import models
from datetime import datetime
from django.core.validators import RegexValidator
from django.contrib.postgres.fields import ArrayField
from transductor_model.models import TransductorModel
import json
from boogie.rest import rest_api
from itertools import chain


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
    model = models.ForeignKey(TransductorModel, on_delete=models.DO_NOTHING)
    serial_number = models.CharField(
        max_length=8,
        unique=True,
        primary_key=True
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
    broken = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    firmware_version = models.CharField(max_length=20)
    installation_date = models.DateTimeField(auto_now=True)
    physical_location = models.CharField(max_length=30, default='')
    geolocation_longitude = models.DecimalField(
        max_digits=15,
        decimal_places=10
    )
    geolocation_latitude = models.DecimalField(max_digits=15, decimal_places=10)
    last_clock_battery_change = models.DateTimeField(auto_now=True)

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

    def get_measurements(self, start_date, final_date):
        """
        Method responsible to retrieve all measurements from
        a specific transductor within a time window.

        Args:
            start_date (datetime): Collections time window start date.
            final_date (datetime): Collections time window final date.

        Returns:
            list: List of all measurements
        """
        raise NotImplementedError


@rest_api()
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

    def set_broken(self, broken):
        self.broken = broken
        self.save()

    def get_minutely_measurements_by_datetime(self, start_date, final_date):
        # dates must match 'yyyy-mm-dd'
        return self.minutely_measurements.filter(
            collection_date__range=[start_date, final_date]
        )

    def get_quartely_measurements_by_datetime(self, start_date, final_date):
        # dates must match 'yyyy-mm-dd'
        return self.quartely_measurements.filter(
            collection_date__range=[start_date, final_date]
        )
    
    def get_monthly_measurements_by_datetime(self, start_date, final_date):
        # dates must match 'yyyy-mm-dd'
        return self.monthly_measurements.filter(
            collection_date__range=[start_date, final_date]
        )

    def get_minutely_measurements(self):
        return self.minutely_measurements.all()
    
    def get_quartely_measurements(self):
        return self.quartely_measurements.all()

    def get_monthly_measurements(self):
        return self.monthly_measurements.all()
