"""smi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from events.views import (FailedConnectionTransductorEventViewSet,
                          VoltageRelatedEventViewSet)
from measurement import urls as measurements_routes
from transductor import views as energy_transductor_views

router = DefaultRouter()

router.register(
    r'energy-transductors',
    energy_transductor_views.EnergyTransductorViewSet,
    basename='energytransductor'
)
router.register(
    r'active-transductors',
    energy_transductor_views.ActiveTransductorsViewSet,
    basename='active_transductor',
)
router.register(
    r'broken-transductors',
    energy_transductor_views.BrokenTransductorsViewSet,
    basename='broken_transductor',
)
router.register(
    r'voltage-events',
    VoltageRelatedEventViewSet,
    basename='voltage-events'
)
router.register(
    r'failed-connection-events',
    FailedConnectionTransductorEventViewSet,
    basename='failed-connection-events'
)

router.registry.extend(measurements_routes.router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
