from django.contrib import admin

from .models import (
    CriticalVoltageEvent,
    Event,
    FailedConnectionTransductorEvent,
    PhaseDropEvent,
    PrecariousVoltageEvent,
)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "created_at",
        "ended_at",
        # "data",
    )
    list_filter = ("ended_at",)


admin.site.register(CriticalVoltageEvent)
admin.site.register(PhaseDropEvent)
admin.site.register(PrecariousVoltageEvent)
admin.site.register(FailedConnectionTransductorEvent)
