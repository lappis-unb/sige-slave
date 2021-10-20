from django.contrib import admin
from django.urls import include, path

from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls

from events import urls as events_routes
from measurement import urls as measurements_routes
from transductor import urls as transductors_routes

router = DefaultRouter()

router.registry.extend(measurements_routes.router.registry)
router.registry.extend(transductors_routes.router.registry)
router.registry.extend(events_routes.router.registry)

urlpatterns = [
    path("docs/", include_docs_urls(title="Slave")),
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
]
