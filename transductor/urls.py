from rest_framework import routers

from .views import EnergyTransductorViewSet
from .views import ActiveTransductorsViewSet

app_name = "transductors"

router = routers.DefaultRouter()
router.register(r'energy_transductors', EnergyTransductorViewSet)
router.register(r'active_transductors', ActiveTransductorsViewSet, basename='ActiveTransductors')

urlpatterns = []
