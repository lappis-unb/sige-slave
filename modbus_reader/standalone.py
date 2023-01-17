from collections import namedtuple
from time import time

from device import DeviceReader, TransductorDevice
from register_csv import RegisterCSV
from tabulate import tabulate

from utils.config import devices_config
from utils.constants import (
    REGISTER_MAP_COLUMNS,
    TRANSDUCTOR_COLLECTION_TYPE_MINUTELY,
    TRANSDUCTOR_COLLECTION_TYPE_MONTHLY,
    TRANSDUCTOR_COLLECTION_TYPE_QUARTERLY,
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

    Device = namedtuple("Device", ["ip_address", "port", "model", "slave_id", "max_request"])
    transductor = Device(
        config_file["ip_address"],
        config_file["port"],
        config_file["model"],
        config_file["slave_id"],
        config_file["max_reg_request"],
    )
    max_request = config_file["max_reg_request"]

    file_reader = RegisterCSV(config_file["path_file_csv"], REGISTER_MAP_COLUMNS)
    transductor_device = TransductorDevice(transductor, max_request, file_reader)
    transductor_reader = DeviceReader(collection_to_perform, transductor_device)

    measurements_data = transductor_reader.single_data_collection_type()
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
    collection_data = [[measurement, valor]for measurement, valor in measurements_data.items()]
    
    
    print(tabulate(collection_data, headers=["Measurement", "value"]))

    print("Maximum number of registers in a request")
    print(f" => max_request : {max_request}")

    print("Transductor registers read")
    print(f" =>    mediadas : {len(collection_data)}")

    print("Blocks registers read")
    print(f" => blocks: {len(transductor_reader.registers_data)}")

    print("Time elapsed to perform collection")
    print(f" => time: {round(stop - start, 2)} seconds", "")


if __name__ == "__main__":
    # configuration dictionary
    config_file = devices_config["Konect"]

    test_without_django(config_file, TRANSDUCTOR_COLLECTION_TYPE_MINUTELY)
    # test_without_django(config_file, TRANSDUCTOR_COLLECTION_TYPE_QUARTERLY)
    # test_without_django(config_file, TRANSDUCTOR_COLLECTION_TYPE_MONTHLY)
