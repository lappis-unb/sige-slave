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
from django.urls import path, include
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from django.urls import path, include
from django.conf.urls import url    

from transductor import views as energy_transductor_views
from measurement import views as measurements_views


router = DefaultRouter()

router.register(
    r'energy_transductors',
    energy_transductor_views.EnergyTransductorViewSet,
    basename='energytransductor',

)
router.register(
    r'active_transductors',
    energy_transductor_views.ActiveTransductorsViewSet,
    basename='active_transductor',
)
router.register(
    r'broken_transductors',
    energy_transductor_views.BrokenTransductorsViewSet,
    basename='broken_transductor',
)
router.register(
    r'minutely_measurements',
    measurements_views.MinutelyMeasurementViewSet,
    basename='minutelymeasurement',
)
router.register(
    r'quarterly_measurements',
    measurements_views.QuarterlyMeasurementViewSet,
    basename='quarterlymeasurement',
)

router.register(
    r'monthly_measurements',
    measurements_views.MonthlyMeasurementViewSet,
    basename='monthlymeasurement',
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
