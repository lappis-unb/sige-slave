from django.core.management.base import BaseCommand
from django.utils import timezone
from measurement.models import MinutelyMeasurement, ReferenceMeasurement, QuarterlyMeasurement, MonthlyMeasurement

class Command(BaseCommand): 
    help = 'Deletes all measurements older than 30 days'

    def handle(self, *args, **options):
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        
        try:
            MinutelyMeasurement.objects.filter(slave_collection_date__lt=thirty_days_ago).delete()
            ReferenceMeasurement.objects.filter(collection_date__lt=thirty_days_ago).delete()
            QuarterlyMeasurement.objects.filter(collection_date__lt=thirty_days_ago).delete()
            MonthlyMeasurement.objects.filter(collection_date__lt=thirty_days_ago).delete()
            self.stdout.write(self.style.SUCCESS('Measurements older than 30 days have been successfully deleted.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Failed to delete measurements: {str(e)}'))
