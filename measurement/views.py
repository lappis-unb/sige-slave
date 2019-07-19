from rest_framework import serializers, viewsets, mixins

from .models import Measurement
from .models import MinutelyMeasurement
from .models import QuarterlyMeasurement
from .models import MonthlyMeasurement
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
        if((start_date is not None) and (end_date is not None)):
            self.queryset = self.queryset.filter(
                collection_date__gte=start_date
            )
            self.queryset = self.queryset.filter(collection_date__lte=end_date)

            return self.queryset[::-1]
        else:

            return self.queryset[::-1]


class MinutelyMeasurementViewSet(MeasurementViewSet):
    serializer_class = MinutelyMeasurementSerializer
    pagination_class = PostLimitOffsetPagination
    queryset = MinutelyMeasurement.objects.all()


class QuarterlyMeasurementViewSet(MeasurementViewSet):
    serializer_class = QuarterlyMeasurementSerializer
    pagination_class = PostLimitOffsetPagination
    queryset = QuarterlyMeasurement.objects.all()


class MonthlyMeasurementViewSet(MeasurementViewSet):
    serializer_class = MonthlyMeasurementSerializer
    pagination_class = PostLimitOffsetPagination
    queryset = MonthlyMeasurement.objects.all()
