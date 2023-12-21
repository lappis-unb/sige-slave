from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from data_collector.modbus.settings import ON_PEAK_TIME_END, ON_PEAK_TIME_START
from measurement.filters import MinutelyMeasurementFilter, QuarterlyMeasurementFilter
from measurement.models import MinutelyMeasurement, QuarterlyMeasurement, Transductor
from measurement.serializers import (
    MinutelyMeasurementSerializer,
    MonthlyListMeasurementSerializer,
    QuarterlyListMeasurementSerializer,
    QuarterlyMeasurementSerializer,
    RealTimeMeasurementSerializer,
)


class MinutelyMeasurementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MinutelyMeasurementSerializer
    queryset = MinutelyMeasurement.objects.all().order_by("-id")
    filter_backends = [DjangoFilterBackend]
    filterset_class = MinutelyMeasurementFilter
    pagination_class = PageNumberPagination


class QuarterlyMeasurementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QuarterlyMeasurement.objects.all().order_by("-id")
    filter_backends = [DjangoFilterBackend]
    pagination_class = PageNumberPagination
    filterset_class = QuarterlyMeasurementFilter

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return QuarterlyListMeasurementSerializer
        return QuarterlyMeasurementSerializer

    @action(detail=True, methods=["get"])
    def transductor_measurements(self, request, pk=None):
        transductor = get_object_or_404(Transductor, pk=pk)
        measurements = QuarterlyMeasurement.objects.filter(transductor=transductor)
        serializer = QuarterlyListMeasurementSerializer(measurements, many=True)
        return Response(serializer.data)


class MonthlyMeasurementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MonthlyListMeasurementSerializer
    pagination_class = PageNumberPagination

    def list(self, request):
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)
        queryset = self.filter_queryset(self.get_queryset(start_date, end_date))

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
                context={"start_date": start_date, "end_date": end_date},
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset,
            many=True,
            context={"start_date": start_date, "end_date": end_date},
        )
        return Response(serializer.data)

    def get_queryset(self, start_date=None, end_date=None):
        peak_time_start = self.request.query_params.get("peak_time_start", None)
        peak_time_end = self.request.query_params.get("peak_time_end", None)

        peak_time_end = peak_time_end or ON_PEAK_TIME_END
        peak_time_start = peak_time_start or ON_PEAK_TIME_START

        peak_time = (
            Q(collection_date__time__gte=peak_time_start)
            & Q(collection_date__time__lt=peak_time_start)
            & Q(collection_date__week_day__in=[0, 1, 2, 3, 4])
        )

        if start_date is not None:
            end_date = end_date or timezone.now()
            qs = QuarterlyMeasurement.objects.filter(collection_date__range=[start_date, end_date])
            qs = qs.values("transductor")

        else:
            qs = QuarterlyMeasurement.objects.annotate(month=TruncMonth("collection_date"))
            qs = qs.values("month", "transductor")

        qs = qs.annotate(
            consumption_peak_time=Sum("active_consumption", filter=peak_time),
            consumption_off_peak_time=Sum("active_consumption", filter=~peak_time),
            generated_energy_peak_time=Sum("active_generated", filter=peak_time),
            generated_energy_off_peak_time=Sum("active_generated", filter=~peak_time),
            inductive_power_peak_time=Sum("reactive_inductive", filter=peak_time),
            inductive_power_off_peak_time=Sum("reactive_inductive", filter=~peak_time),
            capacitive_power_peak_time=Sum("reactive_capacitive", filter=peak_time),
            capacitive_power_off_peak_time=Sum("reactive_capacitive", filter=~peak_time),
        )
        return qs


# TODO: Acredito que seria mais coerente essa viewset na API  Master.
class RealTimeMeasurementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RealTimeMeasurementSerializer

    def get_queryset(self):
        latest_measurements = []
        transductors = Transductor.objects.all()

        for transductor in transductors:
            latest_measurement = MinutelyMeasurement.objects.filter(transductor=transductor).order_by("-id").first()

            if latest_measurement:
                latest_measurements.append(latest_measurement)

        return latest_measurements
