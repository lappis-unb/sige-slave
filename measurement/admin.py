from django.contrib import admin

from measurement.models import (
    MinutelyMeasurement,
    MonthlyMeasurement,
    QuarterlyMeasurement,
    ReferenceMeasurement,
)


@admin.register(ReferenceMeasurement)
class ReferenceMeasurementAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "transductor",
        "data_group",
        "active_consumption",
        "active_generated",
        "reactive_inductive",
        "reactive_capacitive",
        "slave_collection_date",
    ]
    list_display_links = ("id", "transductor")
    list_filter = (
        "transductor",
        "data_group",
    )


@admin.register(MinutelyMeasurement)
class MinutelyMeasurementAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "transductor",
        "frequency_a",
        "voltage_a",
        "current_a",
        "active_power_a",
    ]
    list_display_links = ("id", "transductor")
    list_filter = ("transductor",)


@admin.register(QuarterlyMeasurement)
class QuarterlyMeasurementAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "transductor",
        "active_consumption",
        "active_generated",
        "reactive_inductive",
        "reactive_capacitive",
        "slave_collection_date",
    ]
    list_display_links = ("id", "transductor")
    list_filter = ("transductor",)


@admin.register(MonthlyMeasurement)
class MonthlyMeasurementAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "transductor",
        "active_consumption",
        "active_generated",
        "reactive_inductive",
        "reactive_capacitive",
        "slave_collection_date",
    ]
    list_display_links = ("id", "transductor")
    list_filter = ("transductor",)
