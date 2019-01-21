from django.db import models
from boogie.rest import rest_api
from django.contrib.postgres.fields import ArrayField

@rest_api()
class TransductorModel(models.Model):
    """
    """

    name = models.CharField(max_length=50, unique=True)
    transport_protocol = models.CharField(max_length=50)
    serial_protocol = models.CharField(max_length=50)
    register_addresses = ArrayField(ArrayField(models.IntegerField()))

    def __str__(self):
        return self.name
