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

        self.stdout.write("=" * 70)
        self.stdout.write(f"{get_now()} - Start Collection: {data_group} ")
        self.collect_data(data_group)

        elapsed_time = time.perf_counter() - start_time
        self.stdout.write(f"{get_now()} - Finished Collection and saving in {elapsed_time:0.2f} seconds.")

    def collect_data(self, data_group: str) -> None:
        """
        Collect data from active transductors and save it to the database.
        """

        if data_group not in DATA_GROUPS:
            raise CommandError(f"{get_now()} - Unknown data_group: {data_group}")

        transductors = Transductor.objects.filter(broken=False)
        if not transductors:
            self.stdout.write(self.style.ERROR(f"{get_now()} - No active Transductors in the database"))

        modbus_data = self.get_data_from_transductors_threads(transductors, data_group)
        self.save_data_to_database(modbus_data, data_group)

    def get_data_from_transductors_threads(self, transductors, data_group):
        """
        Collect data from each transductor in parallel using multiple processes.
        """
        modbus_data = []
        with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() * 2) as executor:
            future_list = []
            for transductor in transductors:
                model_transductor = transductor.model.lower().strip().replace(" ", "_")
                slave_id = CONFIG_TRANSDUCTOR.get(model_transductor, {}).get("slave_id", 1)

                future = executor.submit(transductor.collect_data, data_group, slave_id)
                future_list.append(future)

            for future in as_completed(future_list):
                try:
                    result = future.result()
                    modbus_data.append(result)
                except Exception as e:
                    raise CommandError(f"{get_now()} - Error: {e}")
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
                    self.stdout.write(self.style.ERROR(f"{get_now()} - {error}"))
                    self.stdout.write(self.style.ERROR(f"\t\t- data: {data} - Set to broken"))

            if not valid_data:
                self.stdout.write(
                    self.style.ERROR(f"{get_now()} - No collection with valid data to save in the database")
                )
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
            raise Exception(f"{get_now()} - Unknown serializer data_group")
