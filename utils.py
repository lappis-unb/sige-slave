from django.utils import timezone

def is_datetime_in_sync(collected_date):
    max_delay_acceptable = 30  # seconds
    current_date = timezone.datetime.now()

    time_difference = abs(collected_date - current_date)

    if(time_difference.seconds > max_delay_acceptable):
        return True
    else:
        return False