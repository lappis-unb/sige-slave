import importlib
import socket
import struct
import sys

from abc import ABCMeta, abstractmethod
from threading import Thread

from .exceptions import NumberOfAttempsReachedException, \
    RegisterAddressException, \
    CRCInvalidException

from .transport import *
from .communication import *

from transductor.models import *
from transductor_model.models import *
from measurement.models import *


class DataCollector(object):
    """
    Class responsible to handle all transductor measurements collect.

    Attributes:
        transductors (Transductor): The existing active transductors.
        transductor_module (module): The module that contains the
        transductor models.
    """

    def __init__(self):
        # self.transductors = Transductor.objects.filter(active=True)
        self.transductors = EnergyTransductor.objects.all()

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
                transductor.set_broken(True)
            return None

        if transductor.broken:
            transductor.set_broken(False)

        measurements = []

        for message in messages:
            measurements.append(
                serial_protocol_instance
                .get_measurement_value_from_response(message)
            )

        if transductor.model.name == "TR4020":
            EnergyMeasurement.save_measurements(measurements, transductor)
        else:
            pass

    def perform_data_collection(self):
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

    

    def correct_all_transductor_date(self):
        """
        Method responsible to correct the date and time of all transductors.

        Returns:
            None
        """
        threads = []

        for transductor in self.transductors:
            correct_date_thread = Thread(
                target=self.set_correct_date, args=(transductor,)
            )
        
            correct_date_thread.start()

            threads.append(correct_date_thread)
        
        for thread in threads:
            thread.join()

    #TODO Separate communication and transport classes and methods from data_reader module

    def set_correct_date(self, transductor):
        
        print("********************* Set Corret Date Method *********************")

        serial_protocol_instance = globals()[
            transductor.model.serial_protocol
        ](transductor)
        tranport_protocol_instance = globals()[
            transductor.model.transport_protocol
        ](serial_protocol_instance)
        
        try:
            messages = tranport_protocol_instance.data_sender()
        except (NumberOfAttempsReachedException, CRCInvalidException) as e:
            if not transductor.broken:
                transductor.set_broken(True)
            return None

        if transductor.broken:
            transductor.set_broken(False)
        