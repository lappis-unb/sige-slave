import logging

from pymodbus.client.sync import ModbusTcpClient, ModbusUdpClient
from pymodbus.exceptions import ModbusException, NotImplementedException

logger = logging.getLogger(__name__)


class ModbusClient:
    """
    provides additional factory methods to create instances of the client and
    methods for all the current modbus methods.
    """

    def __init__(self, ip_address: str, port: int = 502, protocol: int = 0):
        self.ip_address = ip_address
        self.port = port
        self.protocol = protocol
        self.client = self.create_modbus_client()

    def create_modbus_client(self):
        """Initialize a client instance"""
        if self.protocol == 0:
            logger.info(f"cliente tcp, host: {self.ip_address}, port: {self.port}")
            client = ModbusTcpClient(self.ip_address, self.port)
            client.connect()

        elif self.protocol == 1:
            logger.info(f"cliente udp, host: {self.ip_address},port: {self.port}")
            client = ModbusUdpClient(self.ip_address, self.port)
            client.connect()

        else:
            client = None
            logger.error("protocol not implemented")

        return client

    def disconnect(self) -> None:
        """Closes the underlying socket connection"""
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
            response = self.client.read_holding_registers(address, count, unit=1)
            payload = response.registers
            logger.info(f"payload: {payload}")
        
        except ModbusException as e:
            logger.error(e)

        return payload

    def read_discrete_inputs(self, address, count, unit):
        raise NotImplementedException("Method not implemented")

    def read_input_registers(self, address, count, unit):
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
