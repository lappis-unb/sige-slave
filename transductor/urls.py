from rest_framework import routers

from .views import (
    ActiveTransductorsViewSet,
    BrokenTransductorsViewSet,
    EnergyTransductorViewSet,
)

app_name = "transductors"

router = routers.DefaultRouter()

router.register(
    r"energy-transductors",
    EnergyTransductorViewSet,
    basename="energytransductor",
)

router.register(
    r"active-transductors",
    ActiveTransductorsViewSet,
    basename="active_transductor",
)

router.register(
    r"broken-transductors",
    BrokenTransductorsViewSet,
    basename="broken_transductor",
)
