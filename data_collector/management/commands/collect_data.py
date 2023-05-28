import logging
import multiprocessing
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management import BaseCommand
from django.core.management.base import CommandError, CommandParser

from data_collector.modbus.helpers import get_now
from data_collector.modbus.settings import (
    CONFIG_TRANSDUCTOR,
    DATA_GROUP_MINUTELY,
    DATA_GROUP_MONTHLY,
    DATA_GROUP_QUARTERLY,
    DATA_GROUPS,
)
from measurement.serializers import (
    MinutelyMeasurementSerializer,
    MonthlyMeasurementSerializer,
    QuarterlyMeasurementSerializer,
)
from transductor.models import Transductor

logger = logging.getLogger("tasks")


class Command(BaseCommand):
    """
    This class defines a Django management command for collecting and saving data from a transductor.
    It inherits from Django's BaseCommand class for managing command-line arguments and output.
    """

    help = "This command collects and saves data from a transductor"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("data_group", type=str)

    def handle(self, data_group, *args, **options):
        start_time = time.perf_counter()
        logger.info("-" * 70)
        logger.info(f"Command collect data from transducers  -  {data_group.upper()}")

        active = Transductor.objects.filter(active=True).count()
        msg = f"Start Collection - Active Transductors: {active}" if active else "No active Transductors in database"
        logger.error(msg)
        # raise CommandError(msg)

        collect = self.collect_data(data_group)

        elapsed_time = time.perf_counter() - start_time
        logger.info(f"[{collect}/{active}] Collects completed and saved database.")
        logger.info(f"Command execution time: {elapsed_time:0.2f} seconds.")

    def collect_data(self, data_group: str) -> int:
        """
        Collect data from active transductors and save it to the database.
        """
        if data_group not in DATA_GROUPS:
            logger.error(f"Unknown data_group: {data_group}")
            raise CommandError(f"Unknown data_group: {data_group}")

        transductors = Transductor.objects.filter(active=True)

        modbus_data = self.get_data_from_transductors_threads(transductors, data_group)
        self.save_data_to_database(modbus_data, data_group)

        return len(modbus_data)

    def get_data_from_transductors_threads(self, transductors, data_group):
        """
        Collect data from each transductor in parallel using multiple processes.
        """
        modbus_data = []  # TODO: Teste in server perforance num thread in cpu
        with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() * 4) as executor:
            future_list = []
            for transductor in transductors:
                model_transductor = transductor.model.lower().strip().replace(" ", "_")
                slave_id = CONFIG_TRANSDUCTOR.get(model_transductor, {}).get("slave_id", 1)

                future = executor.submit(transductor.collect_data, data_group, slave_id)
                future_list.append(future)

            for future in as_completed(future_list):
                try:
                    result = future.result()
                    if result["broken"]:
                        logger.warning(f"{result['errors']} - set to broken")
                    else:
                        modbus_data.append(result["collected"])

                except Exception as e:
                    logger.error(f"ThreadPoolExecutor Error: {e}")
                    raise CommandError(f"{get_now()}  -  ThreadPoolExecutor Error: {e}")

        return modbus_data

    def save_data_to_database(self, modbus_data, data_group) -> None:
        """
        Save the provided modbus_data to the database using the provided serializer class.
        """
        serializer_class = self.get_serializer_class(data_group)
        serializer = serializer_class(data=modbus_data, many=True)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            valid_data = []

            for error, data in zip(serializer.errors, serializer.initial_data):
                if not error:
                    valid_data.append(data)
                else:
                    logger.info(self.style.ERROR(f"{get_now()} - {error}"))

            if not valid_data:
                logger.info(self.style.ERROR(f"{get_now()}  -  No collection with valid data to save in the database"))
                return

            serializer = serializer_class(data=valid_data, many=True)
            serializer.is_valid(raise_exception=True)

        serializer.save()

    def get_serializer_class(self, data_group: str):
        serializer_dict = {
            DATA_GROUP_MINUTELY: MinutelyMeasurementSerializer,
            DATA_GROUP_QUARTERLY: QuarterlyMeasurementSerializer,
            DATA_GROUP_MONTHLY: MonthlyMeasurementSerializer,
        }

        try:
            return serializer_dict[data_group]
        except KeyError:
            raise Exception(f"{get_now()}  -  Unknown serializer data_group")
