from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.HyperlinkedModelSerializer):
    measures = serializers.ListField(child=serializers.ListField())
    type = serializers.CharField()

    class Meta:
        model = Event
        fields = (
            'measures',
            'type',
            'created_at'
        )
