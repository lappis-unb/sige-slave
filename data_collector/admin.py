from django.contrib import admin

from data_collector.models import MemoryMap


@admin.register(MemoryMap)
class MemoryMapAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "model",
        "minutely",
        "quarterly",
        "monthly",
        "created_at",
        "updated_at",
    ]
