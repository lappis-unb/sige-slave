from django.utils import timezone
from rest_framework import mixins, pagination, viewsets

from .models import (
    MinutelyMeasurement,
    MonthlyMeasurement,
    QuarterlyMeasurement,
    Transductor,
)
from .serializers import (
    MinutelyMeasurementSerializer,
    MonthlyListMeasurementSerializer,
    MonthlyMeasurementSerializer,
    QuarterlyListMeasurementSerializer,
    QuarterlyMeasurementSerializer,
    RealTimeMeasurementSerializer,
)
from .utils import MeasurementParamsValidator


class MeasurementViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = None
    model = None

    def get_queryset(self):
        params = {}
        start_date = self.request.query_params.get("start_date")
        if start_date:
            params["start_date"] = start_date
        end_date = self.request.query_params.get("end_date", None)
        if end_date:
            params["end_date"] = end_date
        else:
            end_date = timezone.now()
            end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")
            params["end_date"] = str(end_date)
        transductor_id = self.request.query_params.get("id")
        if transductor_id:
            params["id"] = transductor_id
        self.queryset = self.model.objects

        MeasurementParamsValidator.validate_query_params(params)

        if transductor_id:
            transductor = Transductor.objects.get(id=transductor_id)

            if start_date:
                self.queryset = self.queryset.filter(
                    transductor=transductor,
                    slave_collection_date__gte=start_date,
                    slave_collection_date__lte=end_date,
                )

            else:
                self.queryset = self.queryset.filter(transductor=transductor)

        elif start_date:
            self.queryset = self.queryset.filter(
                slave_collection_date__gte=start_date,
                slave_collection_date__lte=end_date,
            )

        else:
            self.queryset = self.queryset.all()

        return self.queryset


class MinutelyMeasurementViewSet(viewsets.ModelViewSet):
    serializer_class = MinutelyMeasurementSerializer
    # pagination_class = pagination.PageNumberPagination
    # page_size = 20

    def get_queryset(self):
        return MinutelyMeasurement.objects.all().order_by("-id")


class QuarterlyMeasurementViewSet(viewsets.ModelViewSet):
    queryset = QuarterlyMeasurement.objects.all().order_by("-id")
    # pagination_class = pagination.PageNumberPagination
    # page_size = 20

    def get_serializer_class(self):
        if self.action in ["list", "retrive"]:
            return QuarterlyListMeasurementSerializer
        return QuarterlyMeasurementSerializer


class MonthlyMeasurementViewSet(viewsets.ModelViewSet):
    queryset = MonthlyMeasurement.objects.all().order_by("-id")
    # pagination_class = pagination.PageNumberPagination
    # page_size = 20

    def get_serializer_class(self):
        if self.action in ["list", "retrive"]:
            return MonthlyListMeasurementSerializer
        return MonthlyMeasurementSerializer


class RealTimeMeasurementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RealTimeMeasurementSerializer

    def get_queryset(self):
        last_measurements = []
        transductors = Transductor.objects.all()

        for transductor in transductors:
            measurement = (
                MinutelyMeasurement.objects.filter(transductor=transductor)
                .order_by("transductor_collection_date")
                .last()
            )
            if measurement:
                last_measurements.append(measurement)

        return last_measurements
