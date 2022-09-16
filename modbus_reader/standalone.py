from collections import namedtuple
from datetime import datetime
from time import time
from typing import Type

from device import TransductorDevice, DeviceReader
from register_csv import RegisterCSV
from tabulate import tabulate

from utils.config import devices_config
from utils.constants import (
    REGISTER_MAP_COLUMNS,
    TRANSDUCTOR_COLLECTION_TYPE_MINUTELY,
    TRANSDUCTOR_COLLECTION_TYPE_QUARTERLY,
    TRANSDUCTOR_COLLECTION_TYPE_MONTHLY,
)


def test_without_django(configuration, collection_to_perform: str) -> None:
    """
    Performs a data collection from a transductor without the Django framework or a database. It also prints the
    transductor configurations, the obtained data and the time elapsed to perform the collection.

    Args:
        configuration: dictionary with transductor configuration
        collection_to_perform(str): the type of the collection to be performed.

    Returns:
        None
    """
    print("")

    start: float = time()

    Device: Type[tuple] = namedtuple("Device", ["ip_address", "port", "model"])
    transductor = Device(
        configuration["ip_address"], configuration["port"], configuration["model"]
    )
    max_request = config_file["max_reg_request"]

    file_reader: RegisterCSV = RegisterCSV(
        configuration["path_file_csv"], REGISTER_MAP_COLUMNS
    )
    transductor_device: TransductorDevice = TransductorDevice(
        transductor, max_request, file_reader
    )
    transductor_reader: DeviceReader = DeviceReader(
        collection_to_perform, transductor_device
    )

    measurements_data: dict[
        str, datetime
    ] = transductor_reader.single_data_collection_type()
    stop: float = time()

    print("Transductor information")
    transductor_info = [
        ["Transductor:", f"{transductor.model}"],
        ["Serial:", configuration["serial_number"]],
        ["IP:", f"{transductor.ip_address}"],
        ["Port:", f"{transductor.port}"],
        ["Max_reg_request:", configuration["max_reg_request"]],
        ["Path_file_csv:", configuration["path_file_csv"]],
    ]

    print(tabulate(transductor_info, headers=["Attribute", "value"]))

    print("Collection type information")
    print(f" => collection_type: {collection_to_perform}", "")

    print("Collection Data")
    collection_data = []
    for measurement, valor in measurements_data.items():
        collection_data.append([measurement, valor])

    print(tabulate(collection_data, headers=["Measurement", "value"]))

    print("Transductor registers read")
    print(f" => blocks: {len(transductor_reader.registers_data)}")

    print("Time elapsed to perform collection")
    print(f" => time: {round(stop - start, 2)} seconds", "")


if __name__ == "__main__":
    # configuration dictionary
    config_file = devices_config["test-lappis"]

    test_without_django(config_file, TRANSDUCTOR_COLLECTION_TYPE_MINUTELY)
    test_without_django(config_file, TRANSDUCTOR_COLLECTION_TYPE_QUARTERLY)
    test_without_django(config_file, TRANSDUCTOR_COLLECTION_TYPE_MONTHLY)
