import importlib
import struct
import sys

from abc import ABCMeta, abstractmethod

from .exceptions import RegisterAddressException, \
                        CRCInvalidException


class SerialProtocol(metaclass=ABCMeta):
    """
    Base class for serial protocols.

    Attributes:
        transductor (Transductor): The transductor which will
        hold communication.
    """

    def __init__(self, transductor):
        self.transductor = transductor

    @abstractmethod
    def create_messages(self):
        """
        Abstract method responsible to create messages
        following the header patterns of the serial protocol used.
        """
        pass

    @abstractmethod
    def get_measurement_value_from_response(self, message_received_data):
        """
        Abstract method responsible for read an value of
        a message sent by transductor.

        Args:
            message_received_data (str): The data from received message.
        """
        pass

    @abstractmethod
    def check_all_messages_crc(self, messages):
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

    def __init__(self, transductor):
        super(ModbusRTU, self).__init__(transductor)

    def create_messages(self):
        """
        This method creates all messages based on transductor
        model register address that will be sent to a transductor
        seeking out their respective values.

        Returns:
            list: The list with all messages.

        Raises:
            RegisterAddressException: raised if the register
            address from transductor model is in a wrong format.
        """
        registers = self.transductor.model.register_addresses

        messages_to_send = []

        int_addr = 0
        float_addr = 1

        address_value = 0
        address_type = 1

        for register in registers:
            if register[address_type] == int_addr:
                packaged_message = struct.pack(
                    "2B", 0x01, 0x03
                ) + \
                    struct.pack(
                    ">2H", register[address_value], 1
                )
            elif register[address_type] == float_addr:
                packaged_message = struct.pack(
                    "2B", 0x01, 0x03
                ) + \
                    struct.pack(
                    ">2H", register[address_value], 2
                )
            else:
                raise RegisterAddressException("Wrong register address type.")

            crc = struct.pack("<H", self._computate_crc(packaged_message))
            packaged_message = packaged_message + crc

            messages_to_send.append(packaged_message)

        return messages_to_send

    def get_measurement_value_from_response(self, message_received_data):
        """
        Method responsible to read a value (int/float)
        from a Modbus RTU response.

        Args:
            message_received_data: The Modbus RTU response.

        Returns:
            int: if the value on response is an int.
            float: if the value on response is an float.
        """
        n_bytes = message_received_data[2]

        msg = bytearray(message_received_data[3:-2])

        if n_bytes == 2:
            return self._unpack_int_response(n_bytes, msg)
        else:
            return self._unpack_float_response(n_bytes, msg)

    def _unpack_int_response(self, n_bytes, msg):
        """
        Args:
            message_received_data (str): The data from received message.

        Returns:
            int: The value from response.
        """
        new_message = bytearray()

        for i in range(0, n_bytes, 2):
            if sys.byteorder == "little":
                msb = msg[i]
                new_message.append(msg[i + 1])
                new_message.append(msb)

        value = struct.unpack("1h", new_message)[0]
        return value

    def _unpack_float_response(self, n_bytes, msg):
        """
        Args:
            message_received_data (str): The data from received message.

        Returns:
            float: The value from response.
        """
        new_message = bytearray()

        for i in range(0, n_bytes, 4):
            if sys.byteorder == "little":
                msb = msg[i]
                new_message.append(msg[i + 1])
                new_message.append(msb)

                msb = msg[i + 2]
                new_message.append(msg[i + 3])
                new_message.append(msb)

        value = struct.unpack("1f", new_message)[0]
        return value

    def check_all_messages_crc(self, messages):
        all_crc_valid = False

        for message in messages:
            crc = struct.pack("<H", self._computate_crc(message[:-2]))

            if not (message[-2:] == crc):
                raise CRCInvalidException('CRC is invalid!')

        all_crc_valid = True

        return all_crc_valid

    def _check_crc(self, packaged_message):
        """
        Method responsible to verify if a CRC is valid.

        Args:
            packaged_message (str): The packaged message ready
            to be sent/received.

        Returns:
            bool: True if CRC is valid, False otherwise.
        """
        integer_message_array = []

        for unicode_element in packaged_message:
            integer_message_array.append(ord(unicode_element))

        return (self._computate_crc(integer_message_array) == 0)

    def _computate_crc(self, packaged_message):
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
