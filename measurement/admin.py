from django.contrib import admin
from .models import EnergyMeasurement
from .models import MinutelyMeasurement
from .models import QuarterlyMeasurement
from .models import MonthlyMeasurement


admin.site.register(EnergyMeasurement)
admin.site.register(MinutelyMeasurement)
admin.site.register(QuarterlyMeasurement)
admin.site.register(MonthlyMeasurement)

# SELECT * FROM pg_catalog.pg_tables;
# SELECT sum(pg_column_size(t.*)) as filesize, count(*) as filerow FROM TABLE_NAME as t;
