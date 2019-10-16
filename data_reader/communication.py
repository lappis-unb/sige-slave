from .exceptions import CRCInvalidException
import importlib
import struct
import sys
import math

from abc import ABCMeta, abstractmethod
from django.utils import timezone

from .exceptions import RegisterAddressException
from .exceptions import CRCInvalidException
from .exceptions import NotANumberException


class SerialProtocol(metaclass=ABCMeta):
    """
    Base class for serial protocols.

    Attributes:
        transductor (Transductor): The transductor which will
        hold communication.
    """

    def __init__(self, transductor, transductor_model):
        self.transductor = transductor
        self.transductor_model = transductor_model

    @abstractmethod
    def create_messages(self):
        """
        Abstract method responsible to create messages
        following the header patterns of the serial protocol used.
        """
        pass

    @abstractmethod
    def get_content_from_message(self, message, message_type):
        """
        Abstract method responsible for read an value of
        a message sent by transductor.

        Args:
            message_received_data (str): The data from received message.
        """
        pass


class ModbusRTU(SerialProtocol):
    """
    Class responsible to represent the communication protocol
    Modbus in RTU mode.

    The RTU format follows the commands/data with a cyclic
    redundancy check checksum as an error check mechanism to
    ensure the reliability of data

    This protocol will be encapsulated in the data field of
    an transport protocol header.

    `Modbus reference guide <http://modbus.org/docs/PI_MBUS_300.pdf>`_
    """

    def __init__(self, transductor, transductor_model):
        super(ModbusRTU, self).__init__(transductor, transductor_model)

    def create_get_message(self, register):

        address_value = 0
        address_type = 1

        packaged_message = struct.pack(
            "2B", 0x01, 0x03
        ) + \
            struct.pack(
                ">2H", register[address_value], (register[address_type]))

        return packaged_message

    def create_messages(self, collection_type, date=None):
        request = self.transductor_model.data_collection(
            collection_type, date)
        messages = []

        if(request.__len__() == 2):
            for register in request[1]:
                message = self.int_to_bytes(1, 1) 
                message += self.int_to_bytes(request[0], 1) 
                message += self.int_to_bytes(register[0], 2)
                aux = register[1]
                message += self.int_to_bytes(aux, 2)
                aux = self._computate_crc(message)
                message += self.int_to_bytes(aux, 2, 'little')
                messages.append(message)
        else:
            messages_bodies = zip(request[1], request[2])    
            for message_body in messages_bodies:
                message = self.int_to_bytes(1, 1) 
                message += self.int_to_bytes(request[0], 1)
                message += self.int_to_bytes(message_body[0][0], 2)
                aux = message_body[0][1]
                message += self.int_to_bytes(aux, 2)
                message += self.int_to_bytes(aux * 2, 1)
                message += self.int_to_bytes(message_body[1], aux * 2)
                aux = self._computate_crc(message)
                message += self.int_to_bytes(aux, 2, 'little')
                messages.append(message)

        return messages    

    def get_content_from_messages(self, collection_type, recived_messages,
                                  date=None):
        request = \
            self.transductor_model.data_collection(
                collection_type, date)
        messages_registers = zip(recived_messages, request[1])    
        messages_content = []
        for message_register in messages_registers:
            messages_content.append(self.get_content_from_message(
                message_register[0],
                message_register[1][1]
            ))
        return messages_content

    def get_content_from_message(self, message, message_type):
        message = message[3:-2]            
        if(message_type == 1):
            message_content = self.bytes_to_int(message)
        elif(message_type == 2):
            message_content = self.bytes_to_float(message)
        elif(message_type == 4):
            message_content = self.bytes_to_int(message)
        elif(message_type == 22):
            message_content = []
            message_content.append(
                self.bytes_to_timestamp_to_datetime(message[0:8]))
            for i in range(8, 44, 4):
                message_content.append(
                    self._unpack_float_response(message[i:i + 4]))

        return message_content

    def _check_crc(self, packaged_message):
        """
        Method responsible to verify if a CRC is valid.

        Args:
            packaged_message (str): The packaged message ready
            to be sent/received.

        Returns:
            bool: True if CRC is valid, False otherwise.
        """            
        crc = struct.pack("<H", self._computate_crc(packaged_message[:-2]))

        return (crc == packaged_message[-2:])

    @staticmethod
    def _computate_crc(packaged_message):
        """
        Method responsible to computate the crc from a packaged message.

        A cyclic redundancy check (CRC) is an error-detecting code
        commonly used in digital networks and storage devices to
        detect accidental changes to raw data.

        `Modbus CRC documentation:
        <http://www.modbustools.com/modbus.html#crc>`_

        Args:
            packaged_message (str): The packaged message ready to
            be sent/received.

        Returns:
            int: The CRC generated.
        """
        crc = 0xFFFF
        for index, item in enumerate((packaged_message)):
            next_byte = item
            crc ^= next_byte
            for i in range(8):
                lsb = crc & 1
                crc >>= 1
                if lsb:
                    crc ^= 0xA001

        return crc

    # TODO Change communication to use this methods
    @staticmethod
    def bytes_to_int(x):
        number = int.from_bytes(x, byteorder='big')
        if(math.isnan(number)):
            raise NotANumberException(
                "The bytestring can't be conveted to a integer")
        else:
            return number

    @staticmethod
    def _unpack_float_response(msg):
        number = struct.unpack('>f', msg)
        if(math.isnan(number[0])):
            raise NotANumberException(
                "The bytestring can't be conveted to a float")
        else:
            return number[0]

    @staticmethod
    def bytes_to_float(msg):
        """
        Args:
            message_received_data (str): The data from received message.

        Returns:
            float: The value from response.
        """
        new_message = bytearray()

        if sys.byteorder == "little":
            msb = msg[0]
            new_message.append(msg[1])
            new_message.append(msb)

            msb = msg[2]
            new_message.append(msg[3])
            new_message.append(msb)

        value = struct.unpack("1f", new_message)[0]
        if(math.isnan(value)):
            raise NotANumberException(
                "The bytestring can't be conveted to a float")
        else:
            return value

    @staticmethod
    def bytes_to_timestamp_to_datetime(x):
        timestamp = ModbusRTU.bytes_to_int(x)
        return timezone.datetime.fromtimestamp(timestamp)

    @staticmethod
    def int_to_bytes(x, size=None, encryption='big'):
        if(size is None):
            return x.to_bytes((x.bit_length() + 7) // 8, encryption)
        return x.to_bytes(size, encryption)
