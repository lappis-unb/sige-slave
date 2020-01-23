from django.utils import timezone


def is_datetime_similar(date1, date2):
    max_delay_acceptable = 30  # seconds

    time_difference = abs(date1 - date2)

    if(time_difference.seconds < max_delay_acceptable):
        return True
    else:
        return False
