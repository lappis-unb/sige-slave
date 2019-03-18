from django.contrib import admin
from .models import MinutelyMeasurement
from .models import QuarterlyMeasurement
from .models import MonthlyMeasurement


admin.site.register(MinutelyMeasurement)
admin.site.register(QuarterlyMeasurement)
admin.site.register(MonthlyMeasurement)
