from rest_framework import serializers
import django.utils.timezone
from datetime import datetime

from .models import EnergyTransductor


class EnergyTransductorSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = EnergyTransductor
        fields = (
            'id',
            'serial_number',
            'ip_address',
            'port',
            'physical_location',
            'geolocation_latitude',
            'geolocation_longitude',
            'broken',
            'active',
            'firmware_version',
            'installation_date',
            'last_clock_battery_change',
            'model',
            'url',
        )

    def create(self, validated_data):
        transductor = EnergyTransductor.objects.create(**validated_data)
        transductor.installation_date = django.utils.timezone.now()
        transductor.last_clock_battery_change = django.utils.timezone.now()
        transductor.save()
        return transductor


class ActiveTransductorsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnergyTransductor
        fields = (
            'id',
            'active',
        )


class BrokenTransductorsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnergyTransductor
        fields = (
            'id',
            'broken',
        )
