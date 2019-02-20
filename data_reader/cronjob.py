from django_cron import CronJobBase, Schedule

from .utils import DataCollector


class MinutelyCollectCronJob(CronJobBase):
    RUN_EVERY_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'data_reader.cronjob.MinutelyCollectCronJob'

    def do(self):
        data_collector = DataCollector()
        data_collector.perform_all_data_collection('Minutely')


class QuarterlyCollectCronJob(CronJobBase):
    RUN_EVERY_MINS = 15
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'data_reader.cronjob.QuartelyCollectCronJob'

    def do(self):
        data_collector = DataCollector()
        data_collector.perform_all_data_collection('Quarterly')


class MonthlyCollectCronJob(CronJobBase):
    RUN_EVERY_MINS = 0    
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'data_reader.cronjob.MonthlyCollectCronJob'
    
    def do(self):
        data_collector = DataCollector()
        data_collector.perform_all_data_collection('Monthly')


class CorrectDateCronJob(CronJobBase):
    RUN_EVERY_MINS = 0    
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'data_reader.cronjob.CorrectDateCronJob'
    
    def do(self):
        data_collector = DataCollector()
        data_collector.correct_all_transductor_date()
