from django_cron import CronJobBase, Schedule

from .utils import perform_all_data_rescue
from modbus_reader.main import perform_all_data_collection
from modbus_reader.utils.constants import (
    MONTH_TO_MINUTES,
    TRANSDUCTOR_COLLECTION_TYPE_MINUTELY,
    TRANSDUCTOR_COLLECTION_TYPE_QUARTERLY,
    TRANSDUCTOR_COLLECTION_TYPE_MONTHLY
)


class MinutelyCollectCronJob(CronJobBase):
    RUN_EVERY_MINS: int = 1
    schedule: Schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code: str = "data_reader.cronjob.MinutelyCollectCronJob"
    collection_type: str = TRANSDUCTOR_COLLECTION_TYPE_MINUTELY

    def do(self) -> None:
        perform_all_data_collection(self.collection_type)


class QuarterlyCollectCronJob(CronJobBase):
    RUN_EVERY_MINS: int = 15
    schedule: Schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code: str = "data_reader.cronjob.QuarterlyCollectCronJob"
    collection_type: str = TRANSDUCTOR_COLLECTION_TYPE_QUARTERLY

    def do(self) -> None:
        perform_all_data_collection(self.collection_type)


class MonthlyCollectCronJob(CronJobBase):
    RUN_EVERY_MINS: int = MONTH_TO_MINUTES
    schedule: Schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code: str = "data_reader.cronjob.MonthlyCollectCronJob"
    collection_type: str = TRANSDUCTOR_COLLECTION_TYPE_MONTHLY

    def do(self) -> None:
        perform_all_data_collection(self.collection_type)


class MinutelyDataRescueCronJob(CronJobBase):
    RUN_EVERY_MINS: int = 1
    schedule: Schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code: str = "data_reader.cronjob.MinutelyDataRescueCronJob"
    collection_type: str = TRANSDUCTOR_COLLECTION_TYPE_MINUTELY

    def do(self) -> None:
        perform_all_data_rescue(self.collection_type)


class QuarterlyDataRescueCronJob(CronJobBase):
    RUN_EVERY_MINS: int = 15
    schedule: Schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code: str = "data_reader.cronjob.QuarterlyDataRescueCronJob"
    collection_type: str = TRANSDUCTOR_COLLECTION_TYPE_QUARTERLY

    def do(self) -> None:
        perform_all_data_rescue(self.collection_type)


class MonthlyDataRescueCronJob(CronJobBase):
    RUN_EVERY_MINS: int = MONTH_TO_MINUTES
    schedule: Schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code: str = "data_reader.cronjob.MonthlyDataRescueCronJob"
    collection_type: str = TRANSDUCTOR_COLLECTION_TYPE_MONTHLY

    def do(self) -> None:
        perform_all_data_rescue(self.collection_type)
