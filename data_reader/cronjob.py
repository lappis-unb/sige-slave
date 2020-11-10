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


class MinutelyDataRescueCronJob(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'data_reader.cronjob.MinutelyDataRescueCronJob'

    def do(self):
        perform_all_data_rescue('Minutely')


class QuarterlyDataRescueCronJob(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'data_reader.cronjob.QuarterlyDataRescueCronJob'

    def do(self):
        perform_all_data_rescue('Quarterly')


class MonthlyDataRescueCronJob(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'data_reader.cronjob.MonthlyDataRescueCronJob'

    def do(self):
        perform_all_data_rescue('Monthly')
