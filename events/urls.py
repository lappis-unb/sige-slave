from rest_framework import routers

from .views import VoltageRelatedEventViewSet
from .views import FailedConnectionTransductorEventViewSet


app_name = "events"

router = routers.DefaultRouter()

router.register(
    r"voltage-events",
    VoltageRelatedEventViewSet,
    basename="voltage-events",
)

router.register(
    r"failed-connection-events",
    FailedConnectionTransductorEventViewSet,
    basename="failed-connection-events",
)
