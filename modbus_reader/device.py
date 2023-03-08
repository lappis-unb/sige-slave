from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

try:
    from modbus_reader.client import ModbusClient
    from modbus_reader.utils.utils import ModbusTypeDecoder, remove_format_datetime
except ImportError:
    from client import ModbusClient

    from utils.utils import ModbusTypeDecoder, remove_format_datetime


class TransductorDevice(object):
    """
    Transductor device class for reading registers from modbus device
    """

    def __init__(self, transductor, max_reg_request, file_reader) -> None:
        self.file_reader = file_reader
        self.model = transductor.model
        self.ip_address = transductor.ip_address
        self.port = transductor.port
        self.slave_id = transductor.slave_id
        self.max_reg_request = max_reg_request

    def reset_registers(self) -> None:
        self.register_collection_type = None
        self.registers_data = None

    def get_registers_collection_type(self, collection_type):
        return self.file_reader.get_registers_by_collection_type(collection_type)

    def get_registers_data(self, collection_type, max_reg_request):
        return self.file_reader.filter_registers_by_collection_type_and_get_requests_blocks(
            collection_type, max_reg_request
        )


class DeviceReader(object):
    def __init__(self, collection_type: str, device: TransductorDevice):
        self.device = device
        self.collection_type = collection_type
        self.modbus_decoder = ModbusTypeDecoder()
        self.registers_collection_type = device.get_registers_collection_type(collection_type)
        self.registers_data = device.get_registers_data(collection_type, device.max_reg_request)

    def single_data_collection_type(self):
        """
        read blocks of registers from modbus device
        """

        measurements_data = {}
        for data in self.registers_data:
            byteorder = data["byteorder"].split("_")
            byte_order = Endian.Little if byteorder[0] in ["MSB", "F2"] else Endian.Big
            payload = self._read_registers(
                self.device.ip_address, self.device.port, self.device.slave_id, data
            )
            payload_decoder = BinaryPayloadDecoder.fromRegisters(
                registers=payload,
                byteorder=byte_order,
                wordorder=Endian.Little,
            )
            decoded_data = self._modbus_decoder(payload_decoder, data)
            measurements_data |= decoded_data

        # transductor_collection_date = remove_format_datetime(measurements_data)
        # measurements_data["transductor_collection_date"] = transductor_collection_date

        return measurements_data

    def _read_registers(self, ip_address: str, port: int, slave_id: int, registers_data):
        """
        read registers from modbus device
        """

        address = registers_data["start_address"]
        size = registers_data["size"]

        payload = {}
        modbus = ModbusClient(ip_address, port, slave_id)
        if registers_data["datamodel"] == "read_input_register":
            payload = modbus.read_input_registers(address, size, unit=1)

        elif registers_data["datamodel"] == "read_holding_register":
            payload = modbus.read_holding_registers(address, size, unit=1)

        else:
            print(f"funcion modbus: {registers_data['datamodel']} not implemented!")
        modbus.disconnect()
        return payload

    def _modbus_decoder(self, payload_decoder, registers_data):
        """
        decode registers from modbus device
        """
        decoded_payload = {}
        for name_register in registers_data["name_registers"]:
            decoded_payload[name_register] = round(registers_data.func_decode(payload_decoder), 2)
            # valor arredondado para 2 casas decimais (validar professor)

        return decoded_payload
