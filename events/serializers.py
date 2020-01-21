from rest_framework import serializers
from .models import VoltageRelatedEvent
from .models import FailedConnectionTransductorEvent


class VoltageRelatedEventSerializer(serializers.HyperlinkedModelSerializer):
    type = serializers.CharField()
    ip_address = serializers.CharField()

    class Meta:
        model = VoltageRelatedEvent
        fields = (
            'data',
            'type',
            'ip_address',
            'created_at',
            'ended_at'
        )


class FailedConnectionTransductorEventSerializer(
        serializers.HyperlinkedModelSerializer):
    type = serializers.CharField()
    ip_address = serializers.CharField()

    class Meta:
        model = FailedConnectionTransductorEvent
        fields = (
            'data',
            'type',
            'ip_address',
            'created_at',
            'ended_at'
        )
