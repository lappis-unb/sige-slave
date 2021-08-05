from django.contrib import admin

from .models import MinutelyMeasurement, MonthlyMeasurement, QuarterlyMeasurement

admin.site.register(MinutelyMeasurement)
admin.site.register(QuarterlyMeasurement)
admin.site.register(MonthlyMeasurement)
