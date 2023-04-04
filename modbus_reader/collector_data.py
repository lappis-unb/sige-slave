import logging

from pymodbus.client.tcp import ModbusTcpClient
from pymodbus.client.udp import ModbusUdpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ModbusException
from pymodbus.payload import BinaryPayloadDecoder

logger = logging.getLogger(__name__)


class ModbusDataCollector:
    def __init__(self, ip_address, port, slave_id, method="tcp"):
        self.ip_address = ip_address
        self.port = port
        self.method = method
        self.slave_id = slave_id
        self.client = None

    def start_data_collection(self, register_blocks):
        """
        collects data from a Modbus device by reading blocks of registers.
        """

        self._start_modbus_client()
        collected_data = {}

        for register_block in register_blocks:
            byte_order = (
                Endian.Little
                if register_block["byteorder"].startswith(("msb", "f2"))
                else Endian.Big
            )
            print(register_block)
            payload = self._collect_data_block(register_block)
            if payload is None:
                print("payload is None")
                continue

            print(payload)
            decoder = BinaryPayloadDecoder.fromRegisters(
                registers=payload,
                byteorder=byte_order,
                wordorder=Endian.Little,
            )

            decoded_data = self._decode_registers_data(decoder, register_block)
            collected_data |= decoded_data

        self._stop_client()
        return collected_data

    def _setup_client(self):
        """Create a client instance"""

        if self.method == "tcp":
            logger.info(f"cliente tcp, host: {self.ip_address}, port: {self.port}")
            client = ModbusTcpClient(self.ip_address, self.port)

        elif self.method == "udp":
            logger.info(f"cliente udp, host: {self.ip_address},port: {self.port}")
            client = ModbusUdpClient(self.ip_address, self.port)

        else:
            raise ModbusException("Invalid Protocol Comunication")

        return client

    def _start_modbus_client(self):
        print("=" * 60)
        logger.info("Client starting")

        self.client = self._setup_client()
        self.client.connect()

        if not self.client.connected:
            raise ModbusException("Client not connected")

        print(f"{self.client} -> connected: {self.client.connected}")

    def _stop_client(self):
        logger.info("Finished client")
        self.client.close()

    def _collect_data_block(self, register_block):
        """
        Reads the contents of a contiguous block of holding registers from modbus device
        """

        starting_address = register_block["start_address"]
        size = register_block["size"]
        datamodel = register_block["datamodel"]

        if datamodel == "read_input_register":
            response = self.client.read_input_registers(
                address=starting_address,
                count=size,
                slave=self.slave_id,
            )

        elif datamodel == "read_holding_register":
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
            logger.error("Error reading holding registers")
            raise ModbusException("Error reading holding registers")

        return response.registers

    def _decode_registers_data(self, decoder, register_block):
        """
        convert the various binary data components to their respective values which are
        stored in a dictionary

        dictionary with the names of the registers as keys and their respective values
        """
        decoded_payload = {}

        for name_register in register_block["name_registers"]:
            decoded_payload[name_register] = round(
                register_block.func_decode(decoder), 2
            )

        return decoded_payload
