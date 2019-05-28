from rest_framework import serializers, viewsets, mixins

from .models import Measurement
from .models import MinutelyMeasurement
from .models import QuarterlyMeasurement
from .models import MonthlyMeasurement
from .serializers import MinutelyMeasurementSerializer
from .serializers import QuarterlyMeasurementSerializer
from .serializers import MonthlyMeasurementSerializer


#  this viewset don't inherits from viewsets.ModelViewSet because it 
#  can't have update and create methods so it only inherits from parts of it 
class MinutelyMeasurementViewSet(mixins.RetrieveModelMixin,
                                 mixins.DestroyModelMixin,
                                 mixins.ListModelMixin,
                                 viewsets.GenericViewSet):
        serializer_class = MinutelyMeasurementSerializer
        def get_queryset(self):
            queryset = MinutelyMeasurement.objects.all()
            start_date = self.request.query_params.get('start_date', None)
            end_date = self.request.query_params.get('end_date', None)
            if((start_date is not None) and (end_date is not None)):
                queryset = queryset.filter(collection_date__gte=start_date)
                queryset = queryset.filter(collection_date__lte=end_date)
            return queryset


class QuarterlyMeasurementViewSet(mixins.RetrieveModelMixin,
                                  mixins.DestroyModelMixin,
                                  mixins.ListModelMixin,
                                  viewsets.GenericViewSet):
    serializer_class = QuarterlyMeasurementSerializer
    def get_queryset(self):
        queryset = QuarterlyMeasurement.objects.all()
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if((start_date is not None) and (end_date is not None)):
            queryset = queryset.filter(collection_date__gte=start_date)
            queryset = queryset.filter(collection_date__lte=end_date)
        return queryset

class MonthlyMeasurementViewSet(mixins.RetrieveModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    serializer_class = MonthlyMeasurementSerializer
    def get_queryset(self):
        queryset = MonthlyMeasurement.objects.all()
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if((start_date is not None) and (end_date is not None)):
            queryset = queryset.filter(collection_date__gte=start_date)
            queryset = queryset.filter(collection_date__lte=end_date)
        return queryset