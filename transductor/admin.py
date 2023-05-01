from django.contrib import admin

from transductor.models import TimeInterval, Transductor, TransductorVoltageState


@admin.register(TransductorVoltageState)
class TransductorVoltageStateAdmin(admin.ModelAdmin):
    list_display = (
        "transductor",
        "current_voltage_state",
        "phase",
    )


@admin.register(Transductor)
class TransductorAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "model",
        "serial_number",
        "ip_address",
        "port",
        "installation_date",
        "active",
        "broken",
    ]
    list_display_links = ("id", "model")
    search_fields = ("id", "model", "serial_number", "ip_address")
    list_filter = ("ip_address", "model", "active", "broken")


admin.site.register(TimeInterval)
