from django.contrib import admin

from .models import EnergyTransductor, TimeInterval, TransductorVoltageState


@admin.register(TransductorVoltageState)
class TransductorVoltageStateAdmin(admin.ModelAdmin):
    list_display = (
        'transductor',
        'current_voltage_state',
        'phase',
    )

admin.site.register(EnergyTransductor)
admin.site.register(TimeInterval)
