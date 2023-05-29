from rest_framework import routers

from measurement.views import (
    MinutelyMeasurementViewSet,
    MonthlyMeasurementViewSet,
    QuarterlyMeasurementViewSet,
    RealTimeMeasurementViewSet,
)

app_name = "minutely_measurements"

router = routers.DefaultRouter()
router.register(r"minutely-measurements", MinutelyMeasurementViewSet, basename="minutely")
router.register(r"quarterly-measurements", QuarterlyMeasurementViewSet, basename="quarterly")
router.register(r"monthly-measurements", MonthlyMeasurementViewSet, basename="monthly")
router.register(r"realtime-measurements", RealTimeMeasurementViewSet, basename="realtime")
