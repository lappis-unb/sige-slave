from django.contrib import admin

from .models import (Event,
                    CriticalVoltageEvent,
                    PrecariousVoltageEvent,
                    PhaseDropEvent)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'created_at',
        'ended_at',
        'data',
    )
    list_filter = ('ended_at',)


admin.site.register(CriticalVoltageEvent)
admin.site.register(PrecariousVoltageEvent)
admin.site.register(PhaseDropEvent)
