from django.core.validators import MaxValueValidator
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.reverse import reverse

from data_collector.modbus.helpers import reader_csv_file
from data_collector.modbus.settings import CSV_DIR_PATH
from data_collector.models import MemoryMap
from transductor.validators import (
    latitude_validator,
    longitude_validator,
    validate_csv_file,
)

from .models import Transductor


class TransductorSerializer(serializers.ModelSerializer):
    geolocation_latitude = serializers.FloatField(validators=[latitude_validator])
    geolocation_longitude = serializers.FloatField(validators=[longitude_validator])
    port = serializers.IntegerField(validators=[MaxValueValidator(65535)])
    memory_map_url = serializers.SerializerMethodField()

    class Meta:
        model = Transductor
        fields = (
            "id",
            "model",
            "serial_number",
            "ip_address",
            "port",
            "physical_location",
            "geolocation_latitude",
            "geolocation_longitude",
            "broken",
            "active",
            "firmware_version",
            "installation_date",
            "last_clock_battery_change",
            "memory_map_url",
        )

    def get_memory_map_url(self, obj):
        request = self.context.get("request")
        if request is not None:
            return reverse("transductor-memorymap", kwargs={"pk": obj.pk}, request=request)
        return None

    def validate(self, attrs):
        csv_filename = attrs.get("model").lower().strip().replace(" ", "_")

        csv_file_path = (CSV_DIR_PATH / csv_filename).with_suffix(".csv")
        csv_data = reader_csv_file(csv_file_path)

        validate_csv_file(csv_data)

        attrs["csv_data"] = csv_data
        return super().validate(attrs)

    def create(self, validated_data):
        model = validated_data.get("model")
        csv_data = validated_data.pop("csv_data")

        try:
            memory_map, created = MemoryMap.get_or_create_by_csv(
                model_transductor=model,
                csv_data=csv_data,
            )

        except (IntegrityError, ValueError) as e:
            raise ValueError(f"An exception of type {type(e).__name__} occurred: {e}")

        validated_data["memory_map"] = memory_map
        return super().create(validated_data)


class ActiveTransductorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transductor
        fields = (
            "id",
            "active",
        )


class BrokenTransductorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transductor
        fields = (
            "id",
            "broken",
        )
