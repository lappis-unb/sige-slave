import sys
import socket
import struct
import importlib

from abc import ABCMeta
from abc import abstractmethod
from threading import Thread

from .exceptions import NumberOfAttempsReachedException
from .exceptions import RegisterAddressException
from .exceptions import CRCInvalidException

from .transport import *
from .communication import *

from transductor.models import *
from measurement.models import *
from transductor_model.models import *


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
        self.functions_dict = self.build_functions_dict()

    def build_functions_dict(self):
        return {
            "Minutely": self.minutely_data_collection,
            "Quarterly": self.quarterly_data_collection,
            "Monthly": self.monthly_data_collection
        }

    def build_registers(self, transductor):
        return {
            "Minutely": transductor.model.minutely_register_addresses,
            "Quarterly": transductor.model.quarterly_register_addresses,
            "Monthly": transductor.model.monthly_register_addresses
        }

    def single_data_collection(self, transductor, collection_type):
        """
        Thread method responsible to handle all the communication used
        by a transductor and save the measurements collected.

        Args:
            transductor (Transductor): The transductor used.

        Returns:
            None
        """

        serial_protocol_instance, \
            transport_protocol_instance = self.get_protocols(transductor)

        messages, transductor = self.create_communication(
            (serial_protocol_instance, transport_protocol_instance),
            transductor,
            collection_type
        )

        measurements = []

        for message in messages:
            measurements.append(
                serial_protocol_instance
                .get_measurement_value_from_response(message)
            )

        self.functions_dict[collection_type](measurements, transductor)

    def minutely_data_collection(self, measurements, transductor):
        if transductor.model.name == "TR4020":
            MinutelyMeasurement.save_measurements(measurements, transductor)
        else:
            pass

    def quarterly_data_collection(self, measurements, transductor):
        if transductor.model.name == "TR4020":
            QuarterlyMeasurement.save_measurements(measurements, transductor)
        else:
            pass

    def monthly_data_collection(self, measurements, transductor):

        if transductor.model.name == "TR4020":
            MonthlyMeasurement.save_measurements(measurements, transductor)
        else:
            pass

    def get_protocols(self, transductor):
        # Creating instances of the serial and transport protocol used
        # by the transductor
        serial_protocol_instance = globals()[
            transductor.model.serial_protocol
        ](transductor)
        transport_protocol_instance = globals()[
            transductor.model.transport_protocol
        ](serial_protocol_instance)

        return (serial_protocol_instance, transport_protocol_instance)

    def create_communication(self, protocols, transductor, collection_type):

        serial_protocol_instance, \
            transport_protocol_instance = protocols

        registers = self.build_registers(transductor)[collection_type]

        messages = []

        try:
            messages = \
                transport_protocol_instance.start_communication(
                    registers
                )
        except (NumberOfAttempsReachedException, CRCInvalidException) as e:
            if not transductor.broken:
                transductor.set_broken(True)
            return None

        if transductor.broken:
            transductor.set_broken(False)

        return (messages, transductor)

    def perform_all_data_collection(self, collection_type):
        """
        Method responsible to start all transductors data collection
        simultaneously.

        Returns:
            None
        """
        threads = []

        for transductor in self.transductors:
            collection_thread = Thread(
                target=self.single_data_collection,
                args=(transductor, collection_type)
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

    # TODO Separate communication and transport classes
    # and methods from data_reader module
    def set_correct_date(self, transductor):

        serial_protocol_instance = globals()[
            transductor.model.serial_protocol
        ](transductor)
        transport_protocol_instance = globals()[
            transductor.model.transport_protocol
        ](serial_protocol_instance)

        try:
            messages = transport_protocol_instance.data_sender()
        except (NumberOfAttempsReachedException, CRCInvalidException) as e:
            if not transductor.broken:
                transductor.set_broken(True)
            return None

        if transductor.broken:
            transductor.set_broken(False)
