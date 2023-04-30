from pymodbus.client.tcp import ModbusTcpClient
from pymodbus.client.udp import ModbusUdpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ModbusException
from pymodbus.payload import BinaryPayloadDecoder

from data_collector.modbus.helpers import ModbusTypeDecoder


class ModbusDataReader:
    def __init__(self, ip_address, port, slave_id, method="tcp"):
        self.ip_address = ip_address
        self.port = port
        self.method = method
        self.slave_id = slave_id
        self.client = None

    def read_datagroup_blocks(self, register_blocks):
        """
        Reads data from multiple register blocks using Modbus protocol, decodes the data.
        """

        self._start_modbus_client()
        collected_data = {}

        for register_block in register_blocks:
            byte_order = (
                Endian.Little
                if register_block["byteorder"].startswith(("msb", "f2"))
                else Endian.Big
            )

            payload = self._read_registers_block(register_block)
            if payload is None:
                continue

            decoder = BinaryPayloadDecoder.fromRegisters(
                registers=payload,
                byteorder=byte_order,
                wordorder=Endian.Little,
            )

            decoded_data = self._decode_response_message(decoder, register_block)
            collected_data |= decoded_data
        self._stop_client()

        return collected_data

    def _setup_client(self):
        """Create a client instance"""

        if self.method == "tcp":
            client = ModbusTcpClient(self.ip_address, self.port)
        elif self.method == "udp":
            client = ModbusUdpClient(self.ip_address, self.port)
        else:
            raise ModbusException("Invalid Protocol Comunication")
        return client

    def _start_modbus_client(self):
        self.client = self._setup_client()
        self.client.connect()

        if not self.client.connected:
            raise Exception(f"Connection failure with client: {self.ip_address}")

    def _stop_client(self):
        self.client.close()

    def _read_registers_block(self, register_block):
        """
        Reads the contents of a contiguous block of registers from modbus device
        """

        starting_address = register_block["start_address"]
        size = register_block["size"]
        _function = register_block["function"]

        if _function == "read_input_register":
            response = self.client.read_input_registers(
                address=starting_address,
                count=size,
                slave=self.slave_id,
            )

        elif _function == "read_holding_register":
            response = self.client.read_holding_registers(
                address=starting_address,
                count=size,
                slave=self.slave_id,
            )

        else:
            raise NotImplementedError(
                f"function modbus: {register_block['datamodel']} not implemented!"
            )

        if response.isError():
            raise ModbusException(
                f"{self.ip_address} => Error reading holding registers"
            )

        return response.registers

    def _decode_response_message(self, decoder, register_block):
        """
        decode payload message from a modbus response message into data components to their
        respective values which are stored in a dictionary
        """
        parse_function = ModbusTypeDecoder().parsers[register_block["type"]]

        decoded_value = {}
        for attribute in register_block["attributes"]:
            decoded_value[attribute] = round(parse_function(decoder), 2)

        return decoded_value
