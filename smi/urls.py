from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from measurement import urls as measurements_routes
from transductor import urls as transductors_routes
from events      import urls as events_routes

router = DefaultRouter()

router.registry.extend(measurements_routes.router.registry)
router.registry.extend(transductors_routes.router.registry)
router.registry.extend(events_routes.router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
