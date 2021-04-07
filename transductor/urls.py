from rest_framework import routers

from .views import (ActiveTransductorsViewSet, BrokenTransductorsViewSet,
                    EnergyTransductorViewSet)

app_name = "transductors"

router = routers.DefaultRouter()
router.register(r'energy-transductors', EnergyTransductorViewSet)
router.register(r'active-transductors', ActiveTransductorsViewSet)
router.register(r'broken-transductors', BrokenTransductorsViewSet)

urlpatterns = []
