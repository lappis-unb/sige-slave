import logging

from pymodbus.client.tcp import ModbusTcpClient
from pymodbus.client.udp import ModbusUdpClient
from pymodbus.constants import Defaults
from pymodbus.exceptions import ModbusException, NotImplementedException

logger = logging.getLogger(__name__)


class ModbusDataCollector:
    def __init__(self, ip_address, port, slave_id, method="tcp"):
        self.ip_address = ip_address
        self.port = port
        self.method = method
        self.slave_id = slave_id
        self.client = None

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

    def read_holding_registers(self, address, count: int, unit: int = 1):
        """
        Reads the contents of a contiguous block of holding registers in a remote device

        Args:
            unit(int):  Arguments
            address: The starting address to read from
            count (int): The number of registers to read
            count: The slave unit this request is targeting
        Returns:
            Read Holding Registers Response
        """

        payload = {}
        try:
            response = self.client.read_holding_registers(
                address=address,
                count=count,
                slave=self.slave_id,
            )

            payload = response.registers
            logger.info(f"payload: {payload}")

        except ModbusExceptions as e:
            logger.error(e)

        return payload

    def read_input_registers(self, address, count: int, unit: int = 1):
        """
        Reads the contents of a contiguous block of input registers in a remote device

        Args:
            unit(int):  Arguments
            address: The starting address to read from
            count (int): The number of registers to read
            count: The slave unit this request is targeting
        Returns:
            Read input Registers Response
        """
        payload = {}

        try:
            response = self.client.read_input_registers(
                address=address, count=count, slave=self.slave_id
            )
            payload = response.registers
            logger.info(f"payload: {payload}")

        except ModbusException as e:
            logger.error(e)

        return payload

    def read_discrete_inputs(self, address, count, unit):
        raise NotImplementedException("Method not implemented")

    def read_coils(self, address, size):
        raise NotImplementedException("Method not implemented")

    def write_single_coil(self, address, value):
        raise NotImplementedException("Method not implemented")

    def write_single_register(self, address, value):
        raise NotImplementedException("Method not implemented")

    def write_multiple_coils(self, address, values):
        raise NotImplementedException("Method not implemented")

    def write_multiple_registers(self, address, values):
        raise NotImplementedException("Method not implemented")
