from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from data_collector.modbus.helpers import reader_csv_file
from data_collector.modbus.settings import CSV_DIR_PATH
from data_collector.models import MemoryMap
from transductor.models import Transductor
from transductor.validators import validate_csv_file


class TransductorSerializer(serializers.ModelSerializer):
    memory_map_url = serializers.SerializerMethodField()
    minutely_measurement_url = serializers.SerializerMethodField()
    quarterly_measurement_url = serializers.SerializerMethodField()
    monthly_measurement_url = serializers.SerializerMethodField()

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
            "minutely_measurement_url",
            "quarterly_measurement_url",
            "monthly_measurement_url",
        )

    def get_memory_map_url(self, obj):
        return self._get_reverse_url("transductor-memorymap", obj)

    def get_minutely_measurement_url(self, obj):
        return self._get_reverse_url("transductor-minutely", obj)

    def get_quarterly_measurement_url(self, obj):
        return self._get_reverse_url("transductor-quarterly", obj)

    def get_monthly_measurement_url(self, obj):
        return self._get_reverse_url("transductor-monthly", obj)

    def _get_reverse_url(self, name, obj):
        request = self.context.get("request")
        if request is not None:
            return reverse(name, kwargs={"pk": obj.pk}, request=request)
        return None

    def validate(self, attrs):
        csv_filename = attrs.get("model").lower().strip().replace(" ", "_")

        csv_file_path = (CSV_DIR_PATH / csv_filename).with_suffix(".csv")
        csv_data = reader_csv_file(csv_file_path)

        validate_csv_file(csv_data)

        attrs["csv_data"] = csv_data
        return super().validate(attrs)

    def create(self, validated_data):
        id = validated_data.get("id")  # SINCRONIZAR ID DO MASTER
        if Transductor.objects.filter(id=id).exists():  # SINCRONIZAR ID DO MASTER
            raise ValidationError({"id": "Um objeto com este ID já existe."})  # SINCRONIZAR ID DO MASTER

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
