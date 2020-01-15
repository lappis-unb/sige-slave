from rest_framework import serializers, viewsets, mixins
from .models import Measurement
from .models import MinutelyMeasurement
from .models import QuarterlyMeasurement
from .models import MonthlyMeasurement
from .models import EnergyTransductor
from .serializers import MinutelyMeasurementSerializer
from .serializers import QuarterlyMeasurementSerializer
from .serializers import MonthlyMeasurementSerializer
from .serializers import RealTimeMeasurementSerializer

from .pagination import PostLimitOffsetPagination
from .pagination import PostPageNumberPagination


#  this viewset don't inherits from viewsets.ModelViewSet because it
#  can't have update and create methods so it only inherits from parts of it
class MeasurementViewSet(mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = None
    model = None

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        serial_number = self.request.query_params.get('serial_number', None)
        self.queryset = self.model.objects

        if serial_number:
            try:
                transductor = EnergyTransductor.objects.get(
                    serial_number=serial_number
                )
                self.queryset = self.queryset.objects.filter(
                    transductor=transductor
                )
            except EnergyTransductor.DoesNotExist:
                transductor = None

        if start_date and end_date:
            self.queryset = self.queryset.filter(
                collection_date__gte=start_date,
                collection_date__lte=end_date
            )

        return self.queryset.reverse()


class MinutelyMeasurementViewSet(MeasurementViewSet):
    model = MinutelyMeasurement
    serializer_class = MinutelyMeasurementSerializer
    pagination_class = PostLimitOffsetPagination
    queryset = MinutelyMeasurement.objects.select_related('transductor').none()


class QuarterlyMeasurementViewSet(MeasurementViewSet):
    model = QuarterlyMeasurement
    serializer_class = QuarterlyMeasurementSerializer
    pagination_class = PostLimitOffsetPagination
    queryset = QuarterlyMeasurement.objects.select_related('transductor').none()


class MonthlyMeasurementViewSet(MeasurementViewSet):
    model = MonthlyMeasurement
    serializer_class = MonthlyMeasurementSerializer
    pagination_class = PostLimitOffsetPagination
    queryset = MonthlyMeasurement.objects.select_related('transductor').none()


class RealTimeMeasurementViewSet(MeasurementViewSet):
    model = MinutelyMeasurement
    serializer_class = RealTimeMeasurementSerializer
    queryset = MonthlyMeasurement.objects.select_related('transductor').none()

    def get_queryset(self):
        last_measurements = []

        transductors = EnergyTransductor.objects.all()

        for transductor in transductors:
            measurement = MinutelyMeasurement.objects.filter(
                transductor=transductor
            ).order_by('collection_date').last()
            if measurement:
                last_measurements.append(measurement)

        return last_measurements
