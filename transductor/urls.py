from rest_framework import routers

from .views import (
    ActiveTransductorsViewSet,
    BrokenTransductorsViewSet,
    TransductorViewSet,
)

app_name = "transductors"

router = routers.DefaultRouter()

router.register(r"energy-transductors", TransductorViewSet, basename="transductor")
router.register(r"active-transductors", ActiveTransductorsViewSet, basename="active_transductor")
router.register(r"broken-transductors", BrokenTransductorsViewSet, basename="broken_transductor")
