from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from data_collector.modbus.helpers import is_peak_time
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
            "voltage_a",
            "voltage_b",
            "voltage_c",
            "current_a",
            "current_b",
            "current_c",
            "total_active_power",
            "total_reactive_power",
            "total_power_factor",
            "collection_date",
        )


class MinutelyMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = MinutelyMeasurement
        fields = (
            "id",
            "transductor",
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
            "collection_date",
        )


class BaseMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True

    def update_reference_measurement(self, reference_measurement, validated_data):
        diffs = self._calculate_diffs(reference_measurement, validated_data)
        self._update_reference(reference_measurement, validated_data)
        self._update_validated_data(validated_data, reference_measurement, diffs)

    def has_reference(self, data_group, validated_data):
        return ReferenceMeasurement.objects.filter(
            transductor=validated_data.get("transductor"),
            data_group=data_group,
        ).exists()

    def get_created_last_measurement(self, transductor):
        measurements = self.Meta.model.objects.filter(transductor=transductor)
        last_measurement = measurements.order_by("-collection_date").first()
        return last_measurement.collection_date if last_measurement else None

    def create_reference(self, data_group, validated_data):
        return ReferenceMeasurement.objects.create(
            **validated_data,
            data_group=data_group,
        )

    def get_reference(self, data_group, transductor_id):
        return ReferenceMeasurement.objects.get(
            transductor=transductor_id,
            data_group=data_group,
        )

    def _calculate_diffs(self, reference, validated_data):
        return {
            key: round(value - getattr(reference, key), 2)
            for key, value in validated_data.items()
            if key not in ["transductor", "collection_date", "slave_collection_date"]
        }

    def _update_reference(self, reference, validated_data):
        for key, value in validated_data.items():
            if key not in ["transductor", "slave_collection_date"]:
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
    collection_date = serializers.DateTimeField(default=timezone.now)

    class Meta:
        model = QuarterlyMeasurement
        fields = (
            "id",
            "transductor",
            "active_consumption",
            "active_generated",
            "reactive_inductive",
            "reactive_capacitive",
            "collection_date",
        )

    def create(self, validated_data):
        data_group = DataGroups.QUARTERLY

        if not self.has_reference(data_group, validated_data):
            return self.create_reference(data_group, validated_data)

        transductor = validated_data.get("transductor")
        current_collection_date = validated_data["collection_date"]

        reference_measurement = self.get_reference(data_group, transductor)
        reference_collection_date = reference_measurement.collection_date
        self.update_reference_measurement(reference_measurement, validated_data)

        chunks = self.calculate_data_chunks(reference_collection_date, current_collection_date)

        if chunks <= 1:
            return super().create(validated_data)

        instances = self.split_data_create_instances(validated_data, reference_collection_date, chunks)
        self.Meta.model.objects.bulk_create(instances)
        return instances[-1]

    def calculate_data_chunks(self, ref_collection_date, collection_date) -> int:
        diff_minutes = (collection_date - ref_collection_date) / timedelta(minutes=1)
        intervals = diff_minutes / 15
        return int(intervals)  # number of chunks de 15-minute (intervals)

    def split_data_create_instances(self, validate_data, ref_collection_date, chunks: int):
        transductor = validate_data.pop("transductor")
        reference = validate_data.pop("reference_measurement")
        validate_data.pop("collection_date")
        instances = []

        for i in range(chunks):
            data_chunk = {key: round(value / chunks, 2) for key, value in validate_data.items()}
            data_chunk["collection_date"] = ref_collection_date + timedelta(minutes=15 * (i + 1))
            data_chunk["transductor"] = transductor
            data_chunk["reference_measurement"] = reference
            data_chunk["is_calculated"] = True
            instances.append(self.Meta.model(**data_chunk))
        return instances


class MonthlyMeasurementSerializer(BaseMeasurementSerializer):
    collection_date = serializers.DateTimeField(default=timezone.now)

    class Meta:
        model = MonthlyMeasurement
        fields = (
            "id",
            "transductor",
            "active_consumption",
            "active_generated",
            "reactive_inductive",
            "reactive_capacitive",
            "collection_date",
        )

    def create(self, validated_data):
        data_group = DataGroups.MONTHLY

        if not self.has_reference(data_group, validated_data):
            return self.create_reference(data_group, validated_data)

        reference_measurement = self.get_reference(data_group, validated_data.get("transductor"))
        self.update_reference_measurement(reference_measurement, validated_data)
        return super().create(validated_data)


class QuarterlyListMeasurementSerializer(serializers.ModelSerializer):
    consumption_peak_time = serializers.SerializerMethodField()
    consumption_off_peak_time = serializers.SerializerMethodField()
    generated_energy_peak_time = serializers.SerializerMethodField()
    generated_energy_off_peak_time = serializers.SerializerMethodField()
    inductive_power_peak_time = serializers.SerializerMethodField()
    inductive_power_off_peak_time = serializers.SerializerMethodField()
    capacitive_power_peak_time = serializers.SerializerMethodField()
    capacitive_power_off_peak_time = serializers.SerializerMethodField()
    collection_date = serializers.DateTimeField(default=timezone.now)

    class Meta:
        model = QuarterlyMeasurement
        fields = (
            "id",
            "transductor",
            "is_calculated",
            "consumption_peak_time",
            "consumption_off_peak_time",
            "generated_energy_peak_time",
            "generated_energy_off_peak_time",
            "inductive_power_peak_time",
            "inductive_power_off_peak_time",
            "capacitive_power_peak_time",
            "capacitive_power_off_peak_time",
            "collection_date",
        )

    def get_measurement(self, obj, measurement_type, is_peak):
        date_time = obj.collection_date
        measurement_value = getattr(obj, measurement_type)

        if is_peak_time(date_time):
            return measurement_value if is_peak else None
        else:
            return None if is_peak else measurement_value

    def get_consumption_peak_time(self, obj):
        return self.get_measurement(obj, "active_consumption", True)

    def get_consumption_off_peak_time(self, obj):
        return self.get_measurement(obj, "active_consumption", False)

    def get_generated_energy_peak_time(self, obj):
        return self.get_measurement(obj, "active_generated", True)

    def get_generated_energy_off_peak_time(self, obj):
        return self.get_measurement(obj, "active_generated", False)

    def get_inductive_power_peak_time(self, obj):
        return self.get_measurement(obj, "reactive_inductive", True)

    def get_inductive_power_off_peak_time(self, obj):
        return self.get_measurement(obj, "reactive_inductive", False)

    def get_capacitive_power_peak_time(self, obj):
        return self.get_measurement(obj, "reactive_capacitive", True)

    def get_capacitive_power_off_peak_time(self, obj):
        return self.get_measurement(obj, "reactive_capacitive", False)


class MonthlyListMeasurementSerializer(serializers.Serializer):
    transductor = serializers.IntegerField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    consumption_peak_time = serializers.FloatField()
    consumption_off_peak_time = serializers.FloatField()
    generated_energy_peak_time = serializers.FloatField()
    generated_energy_off_peak_time = serializers.FloatField()
    inductive_power_peak_time = serializers.FloatField()
    inductive_power_off_peak_time = serializers.FloatField()
    capacitive_power_peak_time = serializers.FloatField()
    capacitive_power_off_peak_time = serializers.FloatField()

    def to_representation(self, instance):
        start_date = self.context.get("start_date")
        end_date = self.context.get("end_date")

        if start_date:
            instance["start_date"] = start_date
            instance["end_date"] = end_date
        else:
            fd_month = instance["month"].replace(day=1)
            ld_month = (fd_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            instance["start_date"] = fd_month.strftime("%d-%m-%Y")
            instance["end_date"] = ld_month.strftime("%d-%m-%Y")

        return super().to_representation(instance)
