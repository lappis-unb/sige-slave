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
import time


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

    def update_transductors(self):
        self.transductors = EnergyTransductor.objects.all()        

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
            collection_type (String): The type of collection to be made

        Returns:
            None
        """

        serial_protocol_instance, \
            transport_protocol_instance = self.get_protocols(transductor)

        time = datetime.now()
        try:
            messages, transductor = self.create_communication(
                (serial_protocol_instance, transport_protocol_instance),
                transductor,
                collection_type
            )

            if transductor.broken:
                date = datetime.now()
                self.collect_old_measurements_from_transductor(transductor, 
                                                               date)

            measurements = []

            for message in messages:
                measurements.append(
                    serial_protocol_instance
                    .get_measurement_value_from_response(message)
                )

            self.functions_dict[collection_type](measurements, transductor)

        except(Exception) as e:
            print("Error", 
                  e, 
                  "while performing the ", 
                  collection_type, 
                  " collection in the transductor", 
                  transductor.ip_address, 
                  " at ", 
                  time)
            if not transductor.broken:
                transductor.set_broken(True)
            return

    def minutely_data_collection(self, measurements, transductor):
        if transductor.model.name == "TR4020":
            time = datetime.now()            
            try:
                MinutelyMeasurement.save_measurements(measurements, transductor)
                print("Minutely performed at ", time)
            except (Exception) as exception:
                print("Error", 
                      exception,
                      "while performing the Minutely collection in the",
                      " transductor", 
                      transductor.ip_address, 
                      " at ", 
                      time)            
                if not transductor.broken:
                    transductor.set_broken(True)
        else:
            pass

    def quarterly_data_collection(self, measurements, transductor):
        if transductor.model.name == "TR4020":
            time = datetime.now()                        
            try:
                QuarterlyMeasurement.save_measurements(measurements,
                                                       transductor)
                print("Quarterly performed at ", time)

            except (Exception) as exception:
                print("Error",
                      exception, 
                      "while performing the Minutely collection in the",
                      " transductor", 
                      transductor.ip_address,
                      " at ", 
                      time)            
                if not transductor.broken:
                    transductor.set_broken(True)        
        else:
            pass

    def monthly_data_collection(self, measurements, transductor):

        if transductor.model.name == "TR4020":
            time = datetime.now()            
            try:
                MonthlyMeasurement.save_measurements(measurements, transductor)
                print("Monthly performed at ", time)

            except(Exception) as exception:
                print("Error",
                      exception, 
                      "while performing the Minutely collection in the",
                      "transductor", 
                      transductor.ip_address, 
                      " at ", 
                      time)            
                if not transductor.broken:
                    transductor.set_broken(True)
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

        messages = \
            transport_protocol_instance.start_communication(
                registers
            )

        return (messages, transductor)

    def perform_all_data_collection(self, collection_type):
        """
        Method responsible to start all transductors data collection
        simultaneously.

        Returns:
            None
        """
        threads = []

        self.update_transductors()
        for transductor in self.transductors:
            if(transductor.active):
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
            time = datetime.now()
            print("Error", 
                  e, 
                  "while fixing time of transductor", 
                  transductor.ip_address,
                  " at ", 
                  time)

            return None

        if transductor.broken:
            transductor.set_broken(False)

    def collect_old_measurements(self, end_date):
        transductors = EnergyTransductor.objects.all()
        threads = []
        for transductor in self.transductors:
            collect_old_data_thread = Thread(
                target=self.collect_old_measurements_from_transductor, args=(
                    transductor, end_date)
            )

            collect_old_data_thread.start()

            threads.append(collect_old_data_thread)

        for thread in threads:
            thread.join()

    def collect_old_measurements_from_transductor(self, transductor, end_date):
        last_collection_date = transductor.last_collection
        # date = datetime(2019,6,10,9,0)
        last_collection_date = int(last_collection_date.timestamp())
        end_date = int(end_date.timestamp())
        minute_in_timestamp = 60
        last_collection_date += minute_in_timestamp
        while(last_collection_date < end_date):
            try:
                self.request_old_data_from_mass_memory(transductor,
                                                       last_collection_date)
                time.sleep(30)
                self.get_old_data_from_transductor(transductor)
            except Exception as e:
                print("Exeption:", e)
            last_collection_date += minute_in_timestamp

    def request_old_data_from_mass_memory(self, transductor, timestamp):

        # message = [1,16,0,160,0,4,8,0,0,0,0,0,0,0,0,53,187]
        # for transductor in transductors:
        message = ModbusRTU.int_to_bytes(1)
        message += ModbusRTU.int_to_bytes(16)
        message += ModbusRTU.int_to_bytes(160, 2)
        message += ModbusRTU.int_to_bytes(4, 2)
        message += ModbusRTU.int_to_bytes(8)
        message += ModbusRTU.int_to_bytes(timestamp, 8)
        serial_protocol_instance, \
            transport_protocol_instance = self.get_protocols(transductor)
        a = ModbusRTU.int_to_bytes(
            serial_protocol_instance._computate_crc(message))
        message += ModbusRTU.int_to_bytes(a[1])
        message += ModbusRTU.int_to_bytes(a[0])

        received_messages = \
            transport_protocol_instance.handle_messages_via_socket([message])
        return received_messages

    def get_old_data_from_transductor(self, transductor): 
        serial_protocol_instance, \
            transport_protocol_instance = self.get_protocols(transductor)

        message = ModbusRTU.int_to_bytes(1)
        message += ModbusRTU.int_to_bytes(3)
        message += ModbusRTU.int_to_bytes(200, 2)
        message += ModbusRTU.int_to_bytes(22, 2)
        serial_protocol_instance, \
            transport_protocol_instance = self.get_protocols(transductor)
        a = ModbusRTU.int_to_bytes(
            serial_protocol_instance._computate_crc(message))
        message += ModbusRTU.int_to_bytes(a[1])
        message += ModbusRTU.int_to_bytes(a[0])

        received_messages = \
            transport_protocol_instance.handle_messages_via_socket([message])

        minutely_measurement = MinutelyMeasurement()        
        date = received_messages[0][3:11]
        date = ModbusRTU.bytes_to_timestamp_to_datetime(date)
        minutely_measurement.collection_date = date
        va = received_messages[0][11:15]
        va = ModbusRTU.bytes_to_float(va)[0]
        minutely_measurement.voltage_a = va
        vb = received_messages[0][15:19]
        vb = ModbusRTU.bytes_to_float(vb)[0]
        minutely_measurement.voltage_b = vb
        vc = received_messages[0][19:23]
        vc = ModbusRTU.bytes_to_float(vc)[0]
        minutely_measurement.voltage_c = vc
        ia = received_messages[0][23:27]
        ia = ModbusRTU.bytes_to_float(ia)[0]
        minutely_measurement.current_b = ia
        ib = received_messages[0][27:31]
        ib = ModbusRTU.bytes_to_float(ib)[0]
        minutely_measurement.current_b = ib
        ic = received_messages[0][31:35]
        ic = ModbusRTU.bytes_to_float(ic)[0]
        minutely_measurement.current_c = ic
        pa = received_messages[0][35:39]
        pa = ModbusRTU.bytes_to_float(pa)[0]
        minutely_measurement.total_active_power = pa
        pr = received_messages[0][39:43]
        pr = ModbusRTU.bytes_to_float(pr)[0]
        minutely_measurement.total_reactive_power = pr
        minutely_measurement.transductor = transductor
        minutely_measurement.save()
        transductor.last_collection = minutely_measurement.collection_date
        return minutely_measurement
