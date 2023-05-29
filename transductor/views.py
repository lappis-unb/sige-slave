from django.shortcuts import get_object_or_404
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from data_collector.modbus.settings import CSV_DIR_PATH
from data_collector.serializers import MemoryMapSerializer
from measurement.models import MinutelyMeasurement, QuarterlyMeasurement
from measurement.serializers import (
    MinutelyMeasurementSerializer,
    MonthlyListMeasurementSerializer,
    QuarterlyListMeasurementSerializer,
)
from measurement.views import MonthlyMeasurementViewSet
from transductor.models import Transductor
from transductor.serializers import (
    ActiveTransductorsSerializer,
    BrokenTransductorsSerializer,
    TransductorSerializer,
)


class TransductorViewSet(viewsets.ModelViewSet):
    queryset = Transductor.objects.all().order_by("-id")
    serializer_class = TransductorSerializer

    def create(self, request, *args, **kwargs):
        model = request.data.get("model")

        if not model:
            return Response({"error": "Model field is required"}, status=400)

        csv_filename = request.data.get("model").lower().strip().replace(" ", "_")
        csv_file_path = (CSV_DIR_PATH / csv_filename).with_suffix(".csv")

        if not csv_file_path.exists():
            error_message = f"Memory Map CSV file not found for '{model}' model at path: '{csv_file_path}'"
            raise serializers.ValidationError({"detail": [error_message]})

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    @action(detail=False, methods=["get"], url_path="broken")
    def broken_transductors(self, request):
        queryset = self.get_queryset().filter(broken=True)
        serializer = BrokenTransductorsSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="active")
    def active_transductors(self, request):
        queryset = self.get_queryset().filter(active=True)
        serializer = ActiveTransductorsSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="memory-map")
    def memorymap(self, request, pk=None):
        transductor = self.get_object()
        serializer = MemoryMapSerializer(transductor.memory_map)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="minutely-measurements")
    def minutely(self, request, pk=None):
        transductor = get_object_or_404(Transductor, pk=pk)
        measurements = MinutelyMeasurement.objects.filter(transductor=transductor)[:100]
        serializer = MinutelyMeasurementSerializer(measurements, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="quarterly-measurements")
    def quarterly(self, request, pk=None):
        transductor = get_object_or_404(Transductor, pk=pk)
        measurements = QuarterlyMeasurement.objects.filter(transductor=transductor)[:100]
        serializer = QuarterlyListMeasurementSerializer(measurements, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="monthly-measurements")
    def monthly(self, request, pk=None):
        transductor = get_object_or_404(Transductor, pk=pk)
        monthly_measurement_view = MonthlyMeasurementViewSet()
        queryset = monthly_measurement_view.get_queryset()
        measurements = queryset.filter(transductor=transductor)
        serializer = MonthlyListMeasurementSerializer(measurements, many=True)
        return Response(serializer.data)


class ActiveTransductorsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transductor.objects.all().order_by("-id")
    serializer_class = ActiveTransductorsSerializer


class BrokenTransductorsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transductor.objects.all().order_by("-id")
    serializer_class = BrokenTransductorsSerializer
