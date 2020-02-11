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

    # TODO Change communication to use this methods
    @staticmethod
    def bytes_to_unsigned(x):
        """
        Conversion method responsible for convert an unsigned number in
        hexadecimal representation to a decimal representation.
        Args:
            x: an unsigned in hexadecimal.

        Returns:
            an unsigned in decimal.
        """
        number = int.from_bytes(x, byteorder='big')
        if(math.isnan(number)):
            raise NotANumberException(
                "The bytestring can't be conveted to a integer")
        return number

    @staticmethod
    def bytes_to_float(x):
        """
        Conversion method responsible for convert a floating point (32 bits) in
        hexadecimal representation to decimal representation.
        Args:
            x: a floating point number in hexadecimal.

        Returns:
            a floating point number in decimal.
        """
        value = struct.unpack("!f", x)[0]
        if (math.isnan(value)):
            raise NotANumberException(
                "The bytestring can't be conveted to a float")
        return value

    @staticmethod
    def bytes_to_binary(nmbr_hex):
        '''
        Converts data in hexadecimal representation to binary representation as
        a string of zeros and ones.
        Args:
            nmbr_hex: Data in hexadecimal

        Returns:
            Converted data as a string in binary
        '''
        return bin(int(nmbr_hex.hex(), base=16))[2:]

    @staticmethod
    def datetime_to_timestamp_to_bytes(x):
        timestamp = int(timezone.datetime.timestamp(x))
        return SerialProtocol.unsigned_to_bytes(timestamp)

    @staticmethod
    def bytes_to_timestamp_to_datetime(x):
        """
        Converts data in hexadecimal representation to datetime.
        Args:
            x: Data in hexadecimal

        Returns:
            Converted data as datetime.
        """
        timestamp = SerialProtocol.bytes_to_unsigned(x)
        return timezone.datetime.fromtimestamp(timestamp)

    @staticmethod
    def binary_to_bytes(str_bin):
        '''
        Convert data represented in binary as a string to hexadecimal
        Args:
            str_bin: A string of zeros and ones.

        Returns:
            Data represented in hexadecimal.
        '''
        return SerialProtocol.unsigned_to_bytes(int(str_bin, base=2))

    @staticmethod
    def float_to_bytes(x):
        '''
        Convert a floating point number to hexadecimal representation.
        Args:
            x: A floating point number.

        Returns:
            The floating point number converted to hexadecimal in 4 bytes.
        '''
        if (math.isnan(x)):
            raise NotANumberException(
                "The floating point number can't be conveted to a bytestring")
        return SerialProtocol.binary_to_bytes(
            SerialProtocol.float_to_binary(x))

    @staticmethod
    def float_to_binary(nmbr, size_expoent=8, size_mantissa=23):
        """
        Converts data in floating point to binary as a string of zeros and ones.
        Args:
            nmbr: The floating point number.
            size_expoent: The number of bits used to represent the expoent.
            size_mantissa: The number of bits used to represent the mantissa.

        Returns:
            Returns the floating point in binary as a string of zeros and ones.
        """

        # Calculate bias
        bias_value = 2 ** (size_expoent - 1) - 1
        # Obtain sign bit
        sign_bit = ''
        if (nmbr >= 0):
            sign_bit = '0'
        else:
            sign_bit = '1'
        # Convert integer part to binary
        integer = math.floor(abs(nmbr))
        bin_integer = SerialProtocol.bytes_to_binary(
            SerialProtocol.unsigned_to_bytes(integer))
        bin_integer_size = len(bin_integer)

        # Convert decimal part to binary
        dec = abs(nmbr) - integer
        bin_dec = ''
        for i in range(8 * size_mantissa):
            dec = dec * 2
            if (dec >= 1):
                bin_dec = bin_dec + '1'
                dec = dec - 1
            else:
                bin_dec = bin_dec + '0'

        # Obtain number of bits in expoent
        exp_value = 0
        bin_expdec = ''
        if nmbr == 0:
            exp_value = -bias_value
            for i in range(size_mantissa + size_expoent + 1):
                bin_expdec = bin_expdec + '0'
        elif bin_integer[0] == '1':
            exp_value = bin_integer_size - 1
        else:
            j = 0
            for i in range(5 * size_mantissa):
                exp_value = exp_value - 1
                if bin_dec[i] != '0':
                    break
                j += 1
            bin_expdec = bin_dec[(j + 0):(5 * size_mantissa)]

        # Convert expoent to binary
        exp_value = exp_value + bias_value
        bin_exp = SerialProtocol.bytes_to_binary(
            SerialProtocol.unsigned_to_bytes(exp_value))
        nb_exp = len(bin_exp)
        for i in range(size_expoent):
            if nb_exp < size_expoent:
                bin_exp = '0' + bin_exp
                nb_exp = len(bin_exp)

        # Merge bits
        bits = ''
        if (abs(nmbr) >= 1):
            bits = sign_bit + bin_exp + \
                bin_integer[1:bin_integer_size] + bin_dec
        else:
            bits = sign_bit + bin_exp + bin_expdec

        return bits[0:size_expoent + size_mantissa + 1]

    @staticmethod
    def unsigned_to_bytes(x, size=None, encryption='big'):
        """
        Converts an unsigned number to bytes representation.
        Args:
            x: The unsigned number.
            size: The number of bits used for the conversion.
            encryption: The encryption type used, respectively, 'big' or
            'little'.

        Returns:
            The converted unsigned number in bytes.
        """
        if(size is None):
            if (x == 0):
                return b'\x00'
            else:
                return x.to_bytes((x.bit_length() + 7) // 8, encryption)
        return x.to_bytes(size, encryption)

    def _check_crc(self, packaged_message):
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

    def create_messages(self, collection_type, date=None):
        request = self.transductor_model.data_collection(
            collection_type, date)
        messages = []
        if(request[0] == "ReadHoldingRegisters"):
            for register in request[1]:
                message = self.create_read_holding_registers_message(register)
                full_message = self.add_complement(message)
                messages.append(full_message)
        elif(request[0] == "PresetMultipleRegisters"):
            messages_bodies = zip(request[1], request[2])
            for message_body in messages_bodies:
                message = self.create_preset_multiple_registers_message(
                    message_body)
                full_message = self.add_complement(message)
                messages.append(full_message)
        return messages

    @abstractmethod
    def add_complement(self, message):
        pass

    @abstractmethod
    def remove_complement(self, message):
        pass

    def create_read_holding_registers_message(self, register):
        # this line adds the slave id, in the TR4020 and MD30 is always 0x01
        message = self.unsigned_to_bytes(1, 1)

        # this line adds function code, in this case 0x03, the read holding
        # registers code
        message += self.unsigned_to_bytes(3, 1)

        # this line adds two bytes that inform the starting register to be read
        message += self.unsigned_to_bytes(register[0], 2)

        # this line adds two bytes that inform how many bytes should be read
        # from the starting register
        message += self.unsigned_to_bytes(register[1], 2)

        return message

    def create_preset_multiple_registers_message(self, message_body):
        # this line adds the slave id, in the TR4020 and MD30 is always 0x01.
        message = self.unsigned_to_bytes(1, 1)

        # this line adds function code, in this case 0x10, the set multiple
        # registers code.
        message += self.unsigned_to_bytes(16, 1)

        # this line adds two bytes that inform the starting register to be
        # writen.
        message += self.unsigned_to_bytes(message_body[0][0], 2)

        # this line adds two bytes that inform how many 16 bits(2 bytes)
        # registers should be written.
        message += self.unsigned_to_bytes(message_body[0][1], 2)

        # this line adds one bytes that inform size of the "payload" of the
        # message (its the double of the number of registers)
        message += self.unsigned_to_bytes(message_body[0][1] * 2, 1)

        # this line adds the payload of the message, in other words the data
        # that will be written in the registers
        message += self.unsigned_to_bytes(message_body[1],
                                          message_body[0][1] * 2)

        return message

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
        message = self.remove_complement(message)
        if(message_type == 1):
            message_content = self.bytes_to_unsigned(message)
        elif(message_type == 2):
            message_content = self.bytes_to_float(message)
        elif(message_type == 4):
            message_content = self.bytes_to_unsigned(message)
        elif(message_type == 22):
            message_content = []
            message_content.append(
                self.bytes_to_timestamp_to_datetime(message[0:8]))
            for i in range(8, 44, 4):
                message_content.append(
                    self.bytes_to_float(message[i:i + 4]))

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

    def __init__(self, transductor, transductor_model):
        super(ModbusRTU, self).__init__(transductor, transductor_model)

    def add_complement(self, message):
        aux = self._computate_crc(message)
        message += self.unsigned_to_bytes(aux, 2, 'little')
        return message

    def remove_complement(self, message):
        return message[3:-2]

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


class ModbusTCP(Modbus):
    def __init__(self, transductor, transductor_model):
        super(ModbusTCP, self).__init__(transductor, transductor_model)

    def add_complement(self, message):
        timestamp = timezone.datetime.now().timestamp()
        timestamp = str(timestamp).split('.')
        trasaction_id = int(timestamp[1]) % 65535
        full_message = self.unsigned_to_bytes(trasaction_id, 2)
        protocol_identifier = 0
        full_message += self.unsigned_to_bytes(protocol_identifier, 2)
        message_length = message.__len__()
        full_message += self.unsigned_to_bytes(message_length, 2)
        full_message += message
        return full_message

    def remove_complement(self, message):
        return message[9:]
