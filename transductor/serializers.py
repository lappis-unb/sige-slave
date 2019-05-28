from rest_framework import serializers

from .models import EnergyTransductor


class EnergyTransductorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnergyTransductor
        fields = (
            'serial_number',
            'ip_address',
            'physical_location',
            'geolocation_latitude',
            'geolocation_longitude',
            'broken',
            'active',
            'firmware_version',
            'installation_date',
            'last_clock_battery_change',
            'measurement_minutelymeasurement',
            'measurement_quarterlymeasurement',
            'measurement_monthlymeasurement',
            'model',
            'url',
        )


class ActiveTransductorsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnergyTransductor
        fields = (
            'serial_number',
            'active',
        )


class BrokenTransductorsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnergyTransductor
        fields = (
            'serial_number',
            'broken',
        )
