from rest_framework import serializers, viewsets, mixins
from django.utils import timezone

from .models import Measurement
from .models import MinutelyMeasurement
from .models import QuarterlyMeasurement
from .models import MonthlyMeasurement
from .models import EnergyTransductor
from .serializers import MinutelyMeasurementSerializer
from .serializers import QuarterlyMeasurementSerializer
from .serializers import MonthlyMeasurementSerializer
from .serializers import RealTimeMeasurementSerializer
from .utils import MeasurementParamsValidator

#  this viewset don't inherits from viewsets.ModelViewSet because it
#  can't have update and create methods so it only inherits from parts of it


class MeasurementViewSet(mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = None
    model = None

    def get_queryset(self):
        params = {}
        start_date = self.request.query_params.get('start_date')
        if start_date:
            params['start_date'] = start_date
        end_date = self.request.query_params.get('end_date', None)
        if end_date:
            params['end_date'] = end_date
        else:
            end_date = timezone.now()
            end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")
            params['end_date'] = str(end_date)
        transductor_id = self.request.query_params.get('id')
        if transductor_id:
            params['id'] = transductor_id
        self.queryset = self.model.objects

        MeasurementParamsValidator.validate_query_params(params)

        if transductor_id:
            transductor = EnergyTransductor.objects.get(
                id=transductor_id
            )

            if start_date:
                self.queryset = self.queryset.filter(
                    transductor=transductor,
                    slave_collection_date__gte=start_date,
                    slave_collection_date__lte=end_date
                )

            else:
                self.queryset = self.queryset.filter(
                    transductor=transductor
                )

        elif start_date:
            self.queryset = self.queryset.filter(
                slave_collection_date__gte=start_date,
                slave_collection_date__lte=end_date
            )

        else:
            self.queryset = self.queryset.all()

        return self.queryset


class MinutelyMeasurementViewSet(MeasurementViewSet):
    model = MinutelyMeasurement
    serializer_class = MinutelyMeasurementSerializer
    queryset = MinutelyMeasurement.objects.none()


class QuarterlyMeasurementViewSet(MeasurementViewSet):
    model = QuarterlyMeasurement
    serializer_class = QuarterlyMeasurementSerializer
    queryset = QuarterlyMeasurement.objects.none()


class MonthlyMeasurementViewSet(MeasurementViewSet):
    model = MonthlyMeasurement
    serializer_class = MonthlyMeasurementSerializer
    queryset = MonthlyMeasurement.objects.none()


class RealTimeMeasurementViewSet(MeasurementViewSet):
    model = MinutelyMeasurement
    serializer_class = RealTimeMeasurementSerializer
    queryset = MinutelyMeasurement.objects.none()

    def get_queryset(self):
        last_measurements = []

        transductors = EnergyTransductor.objects.all()

        for transductor in transductors:
            measurement = MinutelyMeasurement.objects.filter(
                transductor=transductor
            ).order_by('slave_collection_date').last()
            if measurement:
                last_measurements.append(measurement)

        return last_measurements
