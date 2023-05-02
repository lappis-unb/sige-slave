from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.db.models import Max, Sum
from django.utils import timezone
from rest_framework import serializers

from data_collector.modbus.settings import DataGroups
from measurement.models import (
    MinutelyMeasurement,
    MonthlyMeasurement,
    QuarterlyMeasurement,
    ReferenceMeasurement,
)


class RealTimeMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = MinutelyMeasurement
        fields = (
            "id",
            "transductor",
            "transductor_collection_date",
            "voltage_a",
            "voltage_b",
            "voltage_c",
            "current_a",
            "current_b",
            "current_c",
            "total_active_power",
            "total_reactive_power",
            "total_power_factor",
        )


class MinutelyMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = MinutelyMeasurement
        fields = (
            "id",
            "transductor",
            "transductor_collection_date",
            "frequency_a",
            "frequency_b",
            "frequency_c",
            "frequency_iec",
            "voltage_a",
            "voltage_b",
            "voltage_c",
            "current_a",
            "current_b",
            "current_c",
            "active_power_a",
            "active_power_b",
            "active_power_c",
            "total_active_power",
            "reactive_power_a",
            "reactive_power_b",
            "reactive_power_c",
            "total_reactive_power",
            "apparent_power_a",
            "apparent_power_b",
            "apparent_power_c",
            "total_apparent_power",
            "power_factor_a",
            "power_factor_b",
            "power_factor_c",
            "total_power_factor",
            "dht_voltage_a",
            "dht_voltage_b",
            "dht_voltage_c",
            "dht_current_a",
            "dht_current_b",
            "dht_current_c",
        )


class BaseMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True

    def update_reference_measurement(self, data_group, validated_data):
        reference = self._get_reference(data_group, validated_data["transductor"])
        diffs = self._calculate_diffs(reference, validated_data)
        self._update_reference(reference, validated_data)
        self._update_validated_data(validated_data, reference, diffs)

    def has_reference(self, data_group, validated_data):
        return ReferenceMeasurement.objects.filter(
            transductor=validated_data.get("transductor"),
            data_group=data_group,
        ).exists()

    def get_created_last_measurement(self, transductor):
        measurements = self.Meta.model.objects.filter(transductor=transductor)
        last_measurement = measurements.order_by("-transductor_collection_date").first()
        return last_measurement.transductor_collection_date if last_measurement else None

    def create_reference(self, data_group, validated_data):
        reference = ReferenceMeasurement.objects.create(
            **validated_data,
            data_group=data_group,
        )
        validated_data["reference_measurement"] = reference

    def _get_reference(self, data_group, transductor_id):
        return ReferenceMeasurement.objects.get(
            transductor=transductor_id,
            data_group=data_group,
        )

    def _calculate_diffs(self, reference, validated_data):
        return {
            key: value - getattr(reference, key)
            for key, value in validated_data.items()
            if key not in ["transductor", "transductor_collection_date"]
        }

    def _update_reference(self, reference, validated_data):
        for key, value in validated_data.items():
            if key not in ["transductor", "transductor_collection_date"]:
                setattr(reference, key, value)
        reference.save()

    def _update_validated_data(self, validated_data, reference, diffs):
        validated_data.update(diffs)
        validated_data["reference_measurement"] = reference

    def validate_collection_date(self, value):
        if value < timezone.now() - timedelta(seconds=30):
            raise serializers.ValidationError("Error: The creation date is earlier than the current date.")

        return value

    def validate(self, attrs):
        collection_date = attrs.get("collection_date")
        transductor = attrs.get("transductor")

        prev_collection_date = self.get_created_last_measurement(transductor)

        if prev_collection_date and collection_date < prev_collection_date:
            raise serializers.ValidationError(
                "Error: The current creation date is earlier than the previous instance's creation date."
            )

        return super().validate(attrs)


class QuarterlyMeasurementSerializer(BaseMeasurementSerializer):
    transductor_collection_date = serializers.DateTimeField(default=timezone.now)

    class Meta:
        model = QuarterlyMeasurement
        fields = (
            "id",
            "transductor",
            "active_consumption",
            "active_generated",
            "reactive_inductive",
            "reactive_capacitive",
            "transductor_collection_date",
        )

    def create(self, validated_data):
        data_group = DataGroups.QUARTERLY

        if self.has_reference(data_group, validated_data):
            self.update_reference_measurement(data_group, validated_data)

            transductor = validated_data.get("transductor")
            prev_collection_date = self.get_created_last_measurement(transductor)
            chunks = self.calculate_data_chunks(prev_collection_date, validated_data["transductor_collection_date"])

            if chunks > 1:
                instances = self.split_data_create_instances(validated_data, prev_collection_date, chunks)
                self.Meta.model.objects.bulk_create(instances)
                return instances[-1]
        else:
            self.create_reference(data_group, validated_data)

        return super().create(validated_data)

    def calculate_data_chunks(self, prev_collection_date, collection_date) -> int:
        diff_minutes = (collection_date - prev_collection_date) / timedelta(minutes=1)
        intervals = diff_minutes / 15
        return int(intervals)  # number of chunks de 15-minute (intervals)

    def split_data_create_instances(self, validate_data: dict, prev_collection_date, chunks: int):
        transductor = validate_data.pop("transductor")
        reference = validate_data.pop("reference_measurement")
        validate_data.pop("transductor_collection_date")
        instances = []

        for i in range(chunks):
            data_chunk = {key: round(value / chunks, 2) for key, value in validate_data.items()}
            data_chunk["transductor_collection_date"] = prev_collection_date + timedelta(minutes=15 * (i + 1))
            data_chunk["transductor"] = transductor
            data_chunk["reference_measurement"] = reference
            instances.append(self.Meta.model(**data_chunk))
        return instances


class MonthlyMeasurementSerializer(BaseMeasurementSerializer):
    transductor_collection_date = serializers.DateTimeField(default=timezone.now)

    class Meta:
        model = MonthlyMeasurement
        fields = (
            "id",
            "transductor",
            "active_consumption",
            "active_generated",
            "reactive_inductive",
            "reactive_capacitive",
            "transductor_collection_date",
        )

    def create(self, validated_data):
        data_group = DataGroups.MONTHLY

        if self.has_reference(data_group, validated_data):
            self.update_reference_measurement(data_group, validated_data)
        else:
            self.create_reference(data_group, validated_data)

        return super().create(validated_data)


# ================================================================================================================
class QuarterlyListMeasurementSerializer(serializers.ModelSerializer):
    active_consumption_peak = serializers.SerializerMethodField()
    active_consumption_off_peak = serializers.SerializerMethodField()
    active_generated_peak = serializers.SerializerMethodField()
    active_generated_off_peak = serializers.SerializerMethodField()
    reactive_inductive_peak = serializers.SerializerMethodField()
    reactive_inductive_off_peak = serializers.SerializerMethodField()
    reactive_capacitive_peak = serializers.SerializerMethodField()
    reactive_capacitive_off_peak = serializers.SerializerMethodField()
    transductor_collection_date = serializers.DateTimeField(default=timezone.now)

    class Meta:
        model = QuarterlyMeasurement
        fields = (
            "id",
            "transductor",
            "active_consumption_peak",
            "active_consumption_off_peak",
            "active_generated_peak",
            "active_generated_off_peak",
            "reactive_inductive_peak",
            "reactive_inductive_off_peak",
            "reactive_capacitive_peak",
            "reactive_capacitive_off_peak",
            "transductor_collection_date",
        )

    def get_measurement(self, obj, measurement_type, is_peak):
        hour = obj.transductor_collection_date.hour
        measurement_value = getattr(obj, measurement_type)
        if is_peak:
            return measurement_value if 18 <= hour <= 21 else None
        else:
            return None if 18 <= hour <= 21 else measurement_value

    def get_active_consumption_peak(self, obj):
        return self.get_measurement(obj, "active_consumption", True)

    def get_active_consumption_off_peak(self, obj):
        return self.get_measurement(obj, "active_consumption", False)

    def get_active_generated_peak(self, obj):
        return self.get_measurement(obj, "active_generated", True)

    def get_active_generated_off_peak(self, obj):
        return self.get_measurement(obj, "active_generated", False)

    def get_reactive_inductive_peak(self, obj):
        return self.get_measurement(obj, "reactive_inductive", True)

    def get_reactive_inductive_off_peak(self, obj):
        return self.get_measurement(obj, "reactive_inductive", False)

    def get_reactive_capacitive_peak(self, obj):
        return self.get_measurement(obj, "reactive_capacitive", True)

    def get_reactive_capacitive_off_peak(self, obj):
        return self.get_measurement(obj, "reactive_capacitive", False)


# ======================================================================================================


class MonthlyListMeasurementSerializer(serializers.ModelSerializer):
    pass
