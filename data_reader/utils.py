import importlib
import socket
import struct
import sys
from . import communication
from . import transport

from abc import ABCMeta, abstractmethod
from threading import Thread

from .exceptions import NumberOfAttempsReachedException, \
    RegisterAddressException, \
    CRCInvalidException

# importar Transductor e EnergyMeasurements model

class DataCollector(object):
    """
    Class responsible to handle all transductor measurements collect.

    Attributes:
        transductors (Transductor): The existing active transductors.
        transductor_module (module): The module that contains the
        transductor models.
    """

    def __init__(self):
        self.transductors = Transductor.objects.filter(active=True)

    def single_data_collection(self, transductor):
        """
        Thread method responsible to handle all the communication used
        by a transductor and save the measurements collected.

        Args:
            transductor (Transductor): The transductor used.

        Returns:
            None
        """

        # Creating instances of the serial and transport protocol used
        # by the transductor
        serial_protocol_instance = globals()[
            transductor.model.serial_protocol
        ](transductor)
        tranport_protocol_instance = globals()[
            transductor.model.transport_protocol
        ](serial_protocol_instance)

        try:
            messages = tranport_protocol_instance.start_communication()
        except (NumberOfAttempsReachedException, CRCInvalidException) as e:
            if not transductor.broken:
                transductor.set_transductor_broken(True)
            return None

        if transductor.broken:
            transductor.set_transductor_broken(False)

        measurements = []

        for message in messages:
            measurements.append(
                serial_protocol_instance
                .get_measurement_value_from_response(message)
            )

        if transductor.model.name == "TR4020":
            EnergyMeasurements.save_measurements(measurements)
        else:
            pass

    def perform_all_data_collection(self):
        """
        Method responsible to start all transductors data collection
        simultaneously.

        Returns:
            None
        """
        threads = []

        for transductor in self.transductors:
            collection_thread = Thread(
                target=self.single_data_collection, args=(transductor,)
            )
            collection_thread.start()
            threads.append(collection_thread)
        for thread in threads:
            thread.join()
