from django_cron import CronJobBase, Schedule

from .utils import perform_all_data_collection
from .utils import perform_all_data_rescue


class MinutelyCollectCronJob(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'data_reader.cronjob.MinutelyCollectCronJob'

    def do(self):
        perform_all_data_collection('Minutely')


class QuarterlyCollectCronJob(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'data_reader.cronjob.QuartelyCollectCronJob'

    def do(self):
        perform_all_data_collection('Quarterly')


class MonthlyCollectCronJob(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'data_reader.cronjob.MonthlyCollectCronJob'

    def do(self):
        perform_all_data_collection('Monthly')


class DataRescueCronJob(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'data_reader.cronjob.DataRescueCronJob'

    def do(self):
        perform_all_data_rescue('Minutely')
        perform_all_data_rescue('Monthly')
        perform_all_data_rescue('Quarterly')
