from django.urls import include, path
from rest_framework import routers

from data_collector.views import MemoryMapViewSet

app_name = "memory_map"

router = routers.DefaultRouter()
router.register(r"memory-map", MemoryMapViewSet, basename="memorymap")

urlpatterns = [
    path("", include(router.urls)),
]
