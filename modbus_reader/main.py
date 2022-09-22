from datetime import datetime
from threading import Thread
from typing import Optional

from modbus_reader.save_data import save_data
from modbus_reader.utils.config import devices_config
from modbus_reader.utils.constants import (
    PATH_REGISTER_CSV,
    PATH_TRANSDUCTOR_DEVICE,
    PATH_TRANSDUCTOR_READER,
    REGISTER_MAP_COLUMNS,
)
from modbus_reader.utils.utils import load_handler
from transductor.models import EnergyTransductor


def perform_all_data_collection(collection_type: str) -> None:
    """
    Method responsible to start all transductors data collection
    simultaneously.

    Args:
        collection_type : str
        Time interval in which data collection should
        be performed (Minutely, Quarterly, Monthly)

    Returns:
        None
    """
    threads: list = []

    transductor: EnergyTransductor
    for transductor in EnergyTransductor.objects.all():
        collection_thread: Thread = Thread(
            target=single_data_collection,
            args=(transductor, collection_type),
        )

        collection_thread.start()
        threads.append(collection_thread)

    for thread in threads:
        thread.join()


def single_data_collection(
    transductor: EnergyTransductor,
    collection_type: str,
    date: Optional[datetime] = None,
) -> None:
    """
    Function responsible for performing a certain type of data collection for a given
    transductor.

    Args:
        transductor (EnergyTransductor): Transductor that has the desired measurements

        collection_type (str): Desired measurement type. Every transductor, regardless
        of hardware, must support at least the following 4 types of measurement:
        (Minutely, Quarterly, Monthly, CorrectDate,  DataRescueGet). Some transductor
        have other types of data collection, such as the case of the `MD30` which
        expands the types of collection with the following types: (DataRescuePost,
        DataRescueGet)

        date (Optional[datetime]): Specifying a collection date. The
        transductors store past measurements in their internal memory. In this way it
        is possible to make requests for past dates. When this attribute is not
        specified, the most recent measurement is retrieved. Defaults to None.

    TODO: Implement collection by date using PyModbus
    Returns:
        None
    """
    config_file = devices_config[transductor.model]

    max_reg_request = config_file["max_reg_request"]

    file_reader = load_handler(
        PATH_REGISTER_CSV, config_file["path_file_csv"], REGISTER_MAP_COLUMNS
    )
    transductor_device = load_handler(
        PATH_TRANSDUCTOR_DEVICE, transductor, max_reg_request, file_reader
    )
    transductor_reader = load_handler(
        PATH_TRANSDUCTOR_READER, collection_type, transductor_device
    )

    measurements_data = transductor_reader.single_data_collection_type()

    save_data(measurements_data, transductor, collection_type)
