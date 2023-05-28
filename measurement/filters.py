from django_filters import rest_framework as filters

from measurement.models import MinutelyMeasurement, QuarterlyMeasurement


class MeasurementFilter(filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Meta.model = self.model

    transductor = filters.CharFilter(field_name="transductor")
    start_date = filters.IsoDateTimeFilter(field_name="collection_date", lookup_expr="gte")
    end_date = filters.IsoDateTimeFilter(field_name="collection_date", lookup_expr="lte")

    class Meta:
        fields = ["transductor", "start_date", "end_date"]


class MinutelyMeasurementFilter(MeasurementFilter):
    model = MinutelyMeasurement


class QuarterlyMeasurementFilter(MeasurementFilter):
    model = QuarterlyMeasurement
