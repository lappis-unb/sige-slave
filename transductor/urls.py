from rest_framework import routers

from .views import EnergyTransductorViewSet
from .views import ActiveTransductorsViewSet
from .views import BrokenTransductorsViewSet
from .views import MinutelyVoltageThreePhaseViewSet

app_name = "transductors"

router = routers.DefaultRouter()
router.register(r'energy_transductors', EnergyTransductorViewSet)
router.register(r'active_transductors', ActiveTransductorsViewSet)
router.register(r'broken_transductors', BrokenTransductorsViewSet)

urlpatterns = []
