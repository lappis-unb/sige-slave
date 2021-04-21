from rest_framework import routers

from .views import (MinutelyMeasurementViewSet, MonthlyMeasurementViewSet,
                    QuarterlyMeasurementViewSet, RealTimeMeasurementViewSet)

app_name = "minutely_measurements"

router = routers.DefaultRouter()
router.register(r'minutely-measurements', MinutelyMeasurementViewSet)
router.register(r'quarterly-measurements', QuarterlyMeasurementViewSet)
router.register(r'monthly-measurements', MonthlyMeasurementViewSet)
router.register(r'realtime-measurements', RealTimeMeasurementViewSet)
