from .views import MinutelyMeasurementViewSet
from .views import QuarterlyMeasurementViewSet
from .views import MonthlyMeasurementViewSet
from .views import RealTimeMeasurementViewSet

from rest_framework import routers


app_name = "minutely_measurements"

router = routers.DefaultRouter()
router.register(
    r'minutely_measurements', 
    MinutelyMeasurementViewSet)
router.register(
    r'quarterly_measurements', 
    QuarterlyMeasurementViewSet)
router.register(
    r'monthly_measurements', 
    MonthlyMeasurementViewSet)
router.register(
    r'realtime_measurements', 
    RealTimeMeasurementViewSet)
