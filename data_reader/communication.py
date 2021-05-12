import math
import struct
import sys
from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import List, Optional, Union

from django.utils import timezone

from transductor.models import EnergyTransductor
from transductor_model.models import EnergyTransductorModel

from .exceptions import NotANumberException


class SerialProtocol(metaclass=ABCMeta):
    """
    Base class for serial protocols.

    Attributes:
        transductor (Transductor): The transductor which will
        hold communication.
    """

    def __init__(
        self,
        transductor: EnergyTransductor,
        transductor_model: EnergyTransductorModel,
    ) -> None:
        self.transductor = transductor
        self.transductor_model = transductor_model

    @abstractmethod
    def create_messages(
        self,
        collection_type: str,
        date: Optional[datetime] = None,
    ) -> List[bytes]:
        """
        Abstract method responsible to create messages
        following the header patterns of the serial protocol used.
        """
        pass

    @abstractmethod
    def get_content_from_message(self, message: bytes, message_type):
        """
        Abstract method responsible for read an value of
        a message sent by transductor.
        """
        pass

    # TODO Change communication to use this methods
    @staticmethod
    def bytes_to_int(x: bytes) -> Union[int, None]:
        number = int.from_bytes(x, byteorder="big")
        if math.isnan(number):
            return None
        else:
            return number

    @staticmethod
    def _unpack_float_response(msg):
        number = struct.unpack(">f", msg)
        if math.isnan(number[0]):
            raise NotANumberException("The bytestring can't be conveted to a float")
        else:
            return number[0]

    @staticmethod
    def bytes_to_float(msg) -> Union[float, None]:
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

        if math.isnan(value):
            return None
        else:
            return value

    @staticmethod
    def bytes_to_timestamp_to_datetime(x: bytes) -> datetime:
        timestamp: int = ModbusRTU.bytes_to_int(x)
        return timezone.datetime.fromtimestamp(timestamp)

    @staticmethod
    def int_to_bytes(
        x: int,
        size: Optional[int] = None,
        encryption: str = "big",
    ) -> bytes:
        if size is None:
            return x.to_bytes((x.bit_length() + 7) // 8, encryption)
        return x.to_bytes(size, encryption)

    def _check_crc(self, packaged_message) -> bool:
        return True


class Modbus(SerialProtocol):
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

    def create_messages(
        self,
        collection_type: str,
        date: Optional[datetime] = None,
    ) -> List[bytes]:

        request = self.transductor_model.data_collection(collection_type, date)

        messages: List[bytes] = list()

        if request[0] == "ReadHoldingRegisters":
            for register in request[1]:
                message = self.create_read_holding_registers_message(register)
                full_message: bytes = self.add_complement(message)
                messages.append(full_message)

        elif request[0] == "PresetMultipleRegisters":
            messages_bodies = zip(request[1], request[2])

            for message_body in messages_bodies:
                message = self.create_preset_multiple_registers_message(message_body)
                full_message: bytes = self.add_complement(message)
                messages.append(full_message)

        return messages

    @abstractmethod
    def add_complement(self, message: bytes) -> bytes:
        """
        This method should implement how to add the complement to the message given a
        given serial protocol
        """

    @abstractmethod
    def remove_complement(self, message: bytes) -> bytes:
        """
        This method should implement how to remove the complement to the message given
        a given serial protocol
        """

    def create_read_holding_registers_message(self, register):
        # this line adds the slave id, in the TR4020 and MD30 is always 0x01
        message = self.int_to_bytes(1, 1)

        # this line adds function code, in this case 0x03, the read holding
        # registers code
        message += self.int_to_bytes(3, 1)

        # this line adds two bytes that inform the starting register to be read
        message += self.int_to_bytes(register[0], 2)

        # this line adds two bytes that inform how many bytes should be read
        # from the starting register
        message += self.int_to_bytes(register[1], 2)

        return message

    def create_preset_multiple_registers_message(self, message_body):
        # this line adds the slave id, in the TR4020 and MD30 is always 0x01.
        message = self.int_to_bytes(1, 1)

        # this line adds function code, in this case 0x10, the set multiple
        # registers code.
        message += self.int_to_bytes(16, 1)

        # this line adds two bytes that inform the starting register to be
        # writen.
        message += self.int_to_bytes(message_body[0][0], 2)

        # this line adds two bytes that inform how many 16 bits(2 bytes)
        # registers should be written.
        message += self.int_to_bytes(message_body[0][1], 2)

        # this line adds one bytes that inform size of the "payload" of the
        # message (its the double of the number of registers)
        message += self.int_to_bytes(message_body[0][1] * 2, 1)

        # this line adds the payload of the message, in other words the data
        # that will be written in the registers
        message += self.int_to_bytes(message_body[1], message_body[0][1] * 2)

        return message

    def get_content_from_messages(
        self,
        collection_type: str,
        recived_messages,
        date: Optional[datetime] = None,
    ) -> list:
        """[summary]

        Args:
            collection_type (str): Desired measurement type. Every transductor,
            regardless of hardware, must support at least the following 4 types of
            measurement: (Minutely, Quarterly, Monthly, CorrectDate,  DataRescueGet).
            Some transductor have other types of data collection, such as the case of
            the `MD30` which expands the types of collection with the following
            types: (DataRescuePost, DataRescueGet)

            recived_messages ([type]): [description]

            date (Optional[datetime]): Specifying a collection date. The
            transductors store past measurements in their internal memory. In this way
            it is possible to make requests for past dates. When this attribute is not
            specified, the most recent measurement is retrieved. Defaults to None.

        Returns:
            list: [description]
        """
        request = self.transductor_model.data_collection(collection_type, date)
        messages_registers = zip(recived_messages, request[1])
        messages_content = []
        for message_register in messages_registers:
            messages_content.append(
                self.get_content_from_message(
                    message_register[0], message_register[1][1]
                )
            )
        return messages_content

    # TODO: This method returns a strange data structure
    # Abstract the return of this function to a class
    def get_content_from_message(
        self,
        message: bytes,
        message_type,
    ) -> Union[int, float, list]:
        message: bytes = self.remove_complement(message)
        if message_type == 1:
            message_content: int = self.bytes_to_int(message)

        elif message_type == 2:
            message_content: float = self.bytes_to_float(message)

        elif message_type == 4:
            message_content: int = self.bytes_to_int(message)

        elif message_type == 22:
            message_content = []
            date: datetime = self.bytes_to_timestamp_to_datetime(message[0:8])
            message_content.append(date)

            for i in range(8, 44, 4):
                message_content.append(self._unpack_float_response(message[i : i + 4]))

        return message_content


class ModbusRTU(Modbus):
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

    def add_complement(self, message: bytes) -> bytes:
        aux: int = self._computate_crc(message)
        message: bytes = message + self.int_to_bytes(aux, 2, "little")
        return message

    def remove_complement(self, message: bytes) -> bytes:
        return message[3:-2]

    def _check_crc(self, packaged_message) -> bool:
        """
        Method responsible to verify if a CRC is valid.

        Args:
            packaged_message (str): The packaged message ready
            to be sent/received.

        Returns:
            bool: True if CRC is valid, False otherwise.
        """
        crc = struct.pack("<H", self._computate_crc(packaged_message[:-2]))

        return crc == packaged_message[-2:]

    @staticmethod
    def _computate_crc(packaged_message: str) -> int:
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


class ModbusTCP(Modbus):
    def add_complement(self, message: bytes) -> bytes:
        timestamp = timezone.datetime.now().timestamp()
        timestamp = str(timestamp).split(".")
        trasaction_id = int(timestamp[1]) % 65535
        full_message = self.int_to_bytes(trasaction_id, 2)
        protocol_identifier = 0
        full_message += self.int_to_bytes(protocol_identifier, 2)
        message_length = message.__len__()
        full_message += self.int_to_bytes(message_length, 2)
        full_message += message
        return full_message

    def remove_complement(self, message: bytes) -> bytes:
        return message[9:]
