from rest_framework import serializers

from data_collector.models import MemoryMap


class MemoryMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryMap
        fields = (
            "id",
            "minutely",
            "quarterly",
            "monthly",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {
            "created_at": {"read_only": True},
        }
