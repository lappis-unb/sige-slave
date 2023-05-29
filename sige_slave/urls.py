from debug_toolbar import urls as debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from events import urls as events_routes
from measurement import urls as measurements_routes
from transductor import urls as transductors_routes

router = DefaultRouter()

router.registry.extend(measurements_routes.router.registry)
router.registry.extend(transductors_routes.router.registry)
router.registry.extend(events_routes.router.registry)

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", admin.site.urls),
    path("schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs"),
]

if settings.DEBUG:
    urlpatterns += [path("__debug__/", include(debug_toolbar_urls))]
