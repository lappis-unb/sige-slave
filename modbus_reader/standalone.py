from collections import namedtuple
from time import time

from device import DeviceReader, TransductorDevice
from register_csv import RegisterCSV
from tabulate import tabulate

from utils.config import devices_config
from utils.constants import REGISTER_MAP_COLUMNS


def test_without_django(config_file, collection_type):
    """Function aims to perform tests without the need to upload the entire djando system

        The transductor data will not be fetched in the database, but in a configuration 
        file (utils.config.py)

        Run standalone: python3 <name_of_this_file>.py
        Obs: required pymodbus installed on SO or in virtual environment
    """
    start = time()
    # Fake transductor (dados do config_file)
    Device = namedtuple('Device', ["ip_address", "port", "model"])
    transductor = Device(config_file['ip_address'], config_file['port'], config_file['model'])
    # max_request = config_file["max_reg_request"]
    
    max_request = 100

    file_reader = RegisterCSV(config_file["path_file_csv"], REGISTER_MAP_COLUMNS)
    transductor_device = TransductorDevice(transductor, max_request, file_reader)
    transductor_reader = DeviceReader(collection_type, transductor_device)

    measurements_data = transductor_reader.single_data_collection_type()
    stop = time()


    print("<>" * 30)
    print("\n")
    z = [
        ["Transductor:", f"{transductor.model}"],
        ["Serial:", config_file['serial_number']],
        ["IP:", f"{transductor.ip_address}"],
        ["Port:", f"{transductor.port}"],
        ["Max_reg_request:", config_file['max_reg_request']],
        ["Path_file_csv:", config_file['path_file_csv']],
    ]
    
    print(tabulate(z, headers=["Atribute", "value"]))
    
    print("\n")
    print("<>" * 30)

    print("")
    print(f" => collection_type: {collection_type}")
    print("")
    
    p = []
    for measurement, valor in measurements_data.items():
        p.append([measurement, valor])
    
    print(tabulate(p, headers=["Measurement", "value"]))
    print("")
    print("<>" * 30)

    print("*>-<*" * 12)
    print("")
    
    print(f" => bloclos: {len(transductor_reader.registers_data)}")
    print(f" => time   : {round(stop - start, 2)} seconds")
    print("")
    print("*>-<*" * 12)


if __name__ == "__main__":
    config_file = devices_config["test"]
    
    collection_type = {0: "minutely", 1: "quartely", 2: "monthly"}
    test_without_django(config_file, collection_type[1])
