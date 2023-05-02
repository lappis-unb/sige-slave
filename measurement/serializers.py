from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.db.models import Max, Q, Sum
from django.utils import timezone
from rest_framework import serializers

from data_collector.modbus.helpers import is_peak_time
from data_collector.modbus.settings import (
    ON_PEAK_TIME_END,
    ON_PEAK_TIME_START,
    DataGroups,
)
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
            "transductor_collection_date",
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
            "transductor_collection_date",
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
        last_measurement = measurements.order_by("-transductor_collection_date").first()
        return last_measurement.transductor_collection_date if last_measurement else None

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
            key: value - getattr(reference, key)
            for key, value in validated_data.items()
            if key not in ["transductor", "transductor_collection_date", "slave_collection_date"]
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
        collection_date = attrs.get("transductor_collection_date")
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

        if not self.has_reference(data_group, validated_data):
            return self.create_reference(data_group, validated_data)

        transductor = validated_data.get("transductor")
        current_collection_date = validated_data["transductor_collection_date"]

        reference_measurement = self.get_reference(data_group, transductor)
        reference_collection_date = reference_measurement.transductor_collection_date
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
        validate_data.pop("transductor_collection_date")
        instances = []

        for i in range(chunks):
            data_chunk = {key: round(value / chunks, 2) for key, value in validate_data.items()}
            data_chunk["transductor_collection_date"] = ref_collection_date + timedelta(minutes=15 * (i + 1))
            data_chunk["transductor"] = transductor
            data_chunk["reference_measurement"] = reference
            data_chunk["is_calculated"] = True
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

        if not self.has_reference(data_group, validated_data):
            return self.create_reference(data_group, validated_data)

        reference_measurement = self.get_reference(data_group, validated_data.get("transductor"))
        self.update_reference_measurement(reference_measurement, validated_data)
        return super().create(validated_data)


class QuarterlyListMeasurementSerializer(serializers.ModelSerializer):
    ip_address = serializers.CharField(source="transductor.ip_address")
    model = serializers.CharField(source="transductor.model")
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
            "ip_address",
            "model",
            "is_calculated",
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
        date_time = obj.transductor_collection_date
        measurement_value = getattr(obj, measurement_type)

        if is_peak_time(date_time):
            return measurement_value if is_peak else None
        else:
            return None if is_peak else measurement_value

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


class MonthlyListMeasurementSerializer(serializers.ModelSerializer):
    ip_address = serializers.CharField(source="transductor.ip_address")
    model = serializers.CharField(source="transductor.model")
    active_consumption_peak = serializers.SerializerMethodField()
    active_consumption_off_peak = serializers.SerializerMethodField()
    active_generated_peak = serializers.SerializerMethodField()
    active_generated_off_peak = serializers.SerializerMethodField()
    reactive_inductive_peak = serializers.SerializerMethodField()
    reactive_inductive_off_peak = serializers.SerializerMethodField()
    reactive_capacitive_peak = serializers.SerializerMethodField()
    reactive_capacitive_off_peak = serializers.SerializerMethodField()
    active_max_power_peak_time = serializers.SerializerMethodField()
    active_max_power_off_peak_time = serializers.SerializerMethodField()
    reactive_max_power_peak_time = serializers.SerializerMethodField()
    reactive_max_power_off_peak_time = serializers.SerializerMethodField()
    active_max_power_list_peak = serializers.SerializerMethodField()
    active_max_power_list_peak_time = serializers.SerializerMethodField()
    active_max_power_list_off_peak = serializers.SerializerMethodField()
    active_max_power_list_off_peak_time = serializers.SerializerMethodField()
    reactive_max_power_list_peak = serializers.SerializerMethodField()
    reactive_max_power_list_peak_time = serializers.SerializerMethodField()
    reactive_max_power_list_off_peak = serializers.SerializerMethodField()
    reactive_max_power_list_off_peak_time = serializers.SerializerMethodField()
    transductor_collection_date = serializers.DateTimeField(default=timezone.now)

    class Meta:
        model = MonthlyMeasurement
        fields = (
            "id",
            "transductor",
            "ip_address",
            "model",
            "active_consumption_peak",
            "active_consumption_off_peak",
            "active_generated_peak",
            "active_generated_off_peak",
            "reactive_inductive_peak",
            "reactive_inductive_off_peak",
            "reactive_capacitive_peak",
            "reactive_capacitive_off_peak",
            "active_max_power_peak_time",
            "active_max_power_off_peak_time",
            "reactive_max_power_peak_time",
            "reactive_max_power_off_peak_time",
            "active_max_power_list_peak",
            "active_max_power_list_peak_time",
            "active_max_power_list_off_peak",
            "active_max_power_list_off_peak_time",
            "reactive_max_power_list_peak",
            "reactive_max_power_list_peak_time",
            "reactive_max_power_list_off_peak",
            "reactive_max_power_list_off_peak_time",
            "transductor_collection_date",
        )

    def get_quarterly_measurements(self, obj, is_peak_time=True):
        start_date = (obj.transductor_collection_date - timedelta(days=1)).replace(day=1)
        end_date = start_date + relativedelta(months=1)

        queryset = QuarterlyMeasurement.objects.filter(
            transductor=obj.transductor,
            transductor_collection_date__gte=start_date,
            transductor_collection_date__lt=end_date,
        )

        if is_peak_time:  # Filtrar para horario de pico (18h-21h em dias da semana)
            queryset = queryset.filter(
                transductor_collection_date__time__gte=ON_PEAK_TIME_START,
                transductor_collection_date__time__lt=ON_PEAK_TIME_END,
            )

        else:
            queryset = queryset.exclude(
                transductor_collection_date__time__gte=ON_PEAK_TIME_START,
                transductor_collection_date__time__lt=ON_PEAK_TIME_END,
            )

        return queryset

    def get_active_consumption_peak(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=True)
        return quarterly_measurements.aggregate(Sum("active_consumption"))["active_consumption__sum"] or 0

    def get_active_consumption_off_peak(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=False)
        return quarterly_measurements.aggregate(Sum("active_consumption"))["active_consumption__sum"] or 0

    def get_active_generated_peak(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=True)
        return quarterly_measurements.aggregate(Sum("active_generated"))["active_generated__sum"] or 0

    def get_active_generated_off_peak(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=False)
        return quarterly_measurements.aggregate(Sum("active_generated"))["active_generated__sum"] or 0

    def get_reactive_inductive_peak(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=True)
        return quarterly_measurements.aggregate(Sum("reactive_inductive"))["reactive_inductive__sum"] or 0

    def get_reactive_inductive_off_peak(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=False)
        return quarterly_measurements.aggregate(Sum("reactive_inductive"))["reactive_inductive__sum"] or 0

    def get_reactive_capacitive_peak(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=True)
        return quarterly_measurements.aggregate(Sum("reactive_capacitive"))["reactive_capacitive__sum"] or 0

    def get_reactive_capacitive_off_peak(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=False)
        return quarterly_measurements.aggregate(Sum("reactive_capacitive"))["reactive_capacitive__sum"] or 0

    # -------------------------------------------------------------------------------------------------------------------------
    def get_active_max_power_peak_time(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=True)
        return quarterly_measurements.aggregate(Max("active_consumption"))["active_consumption__max"] or 0

    def get_active_max_power_off_peak_time(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=False)
        return quarterly_measurements.aggregate(Max("active_consumption"))["active_consumption__max"] or 0

    def get_reactive_max_power_peak_time(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=True)
        return quarterly_measurements.aggregate(Max("reactive_capacitive"))["reactive_capacitive__max"] or 0

    def get_reactive_max_power_off_peak_time(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=False)
        return quarterly_measurements.aggregate(Max("reactive_capacitive"))["reactive_capacitive__max"] or 0

    # -------------------------------------------------------------------------------------------------------------------------
    def get_active_max_power_list_peak(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=True)
        return quarterly_measurements.order_by("-active_consumption").values_list("active_consumption", flat=True)[:4]

    def get_active_max_power_list_peak_time(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=True)
        return quarterly_measurements.order_by("-active_consumption").values_list("active_consumption", flat=True)[:4]

    def get_active_max_power_list_off_peak(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=False)
        return quarterly_measurements.order_by("-active_consumption").values_list("active_consumption", flat=True)[:4]

    def get_active_max_power_list_off_peak_time(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=False)
        return quarterly_measurements.order_by("-active_consumption").values_list("active_consumption", flat=True)[:4]

    def get_reactive_max_power_list_peak(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=True)
        return quarterly_measurements.order_by("-reactive_capacitive").values_list("reactive_capacitive", flat=True)[:4]

    def get_reactive_max_power_list_peak_time(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=True)
        return quarterly_measurements.order_by("-reactive_capacitive").values_list("reactive_capacitive", flat=True)[:4]

    def get_reactive_max_power_list_off_peak(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=False)
        return quarterly_measurements.order_by("-reactive_capacitive").values_list("reactive_capacitive", flat=True)[:4]

    def get_reactive_max_power_list_off_peak_time(self, obj):
        quarterly_measurements = self.get_quarterly_measurements(obj, is_peak_time=False)
        return quarterly_measurements.order_by("-reactive_capacitive").values_list("reactive_capacitive", flat=True)[:4]
