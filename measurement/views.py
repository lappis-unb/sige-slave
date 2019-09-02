from rest_framework import serializers, viewsets, mixins
from .models import Measurement
from .models import MinutelyMeasurement
from .models import QuarterlyMeasurement
from .models import MonthlyMeasurement
from .models import EnergyTransductor
from .serializers import MinutelyMeasurementSerializer
from .serializers import QuarterlyMeasurementSerializer
from .serializers import MonthlyMeasurementSerializer

from .pagination import PostLimitOffsetPagination
from .pagination import PostPageNumberPagination


#  this viewset don't inherits from viewsets.ModelViewSet because it
#  can't have update and create methods so it only inherits from parts of it
class MeasurementViewSet(mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = None

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        serial_number = self.request.query_params.get('serial_number', None)

        if serial_number is not None:
            try:
                transductor = EnergyTransductor.objects.get(
                    serial_number=serial_number
                )
            except EnergyTransductor.DoesNotExist:
                transductor = None

            self.queryset = self.queryset.filter(transductor=transductor)

        if (start_date is not None) and (end_date is not None):
            self.queryset = self.queryset.filter(
                collection_date__gte=start_date
            )
            self.queryset = self.queryset.filter(collection_date__lte=end_date)

        return self.queryset.reverse()


class MinutelyMeasurementViewSet(MeasurementViewSet):
    serializer_class = MinutelyMeasurementSerializer
    pagination_class = PostLimitOffsetPagination
    collect = MinutelyMeasurement.objects.select_related('transductor').all()
    queryset = collect.order_by('id')


class QuarterlyMeasurementViewSet(MeasurementViewSet):
    serializer_class = QuarterlyMeasurementSerializer
    pagination_class = PostLimitOffsetPagination
    collect = QuarterlyMeasurement.objects.select_related('transductor').all()
    queryset = collect.order_by('id')


class MonthlyMeasurementViewSet(MeasurementViewSet):
    serializer_class = MonthlyMeasurementSerializer
    pagination_class = PostLimitOffsetPagination
    collect = MonthlyMeasurement.objects.select_related('transductor').all()
    queryset = collect.order_by('id')
