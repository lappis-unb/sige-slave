from collections import OrderedDict
from csv import DictReader

try:
    from modbus_reader.utils.constants import (
        COLLECTION_TYPE_DATETIME,
        COLLECTION_TYPE_MINUTELY,
    )
    from modbus_reader.utils.utils import ModbusTypeDecoder, str_bool, type_modbus
except ImportError:
    from utils.constants import COLLECTION_TYPE_DATETIME, COLLECTION_TYPE_MINUTELY
    from utils.utils import ModbusTypeDecoder, str_bool, type_modbus


class RegisterCSV(object):
    def __init__(self, path_file, REGISTER_MAP_COLUMNS):
        self.path_file = path_file
        self.csv_map_columns = REGISTER_MAP_COLUMNS

    def filter_registers_by_collection_type_and_get_requests_blocks(
        self, collection_type, max_reg_request
    ):
        """
        filter the registers by collection_type and build contiguous blocks with
        fields: initial_address, num_reg, type to be requested
        """
        registers_collection_type = self.get_registers_by_collection_type(collection_type)

        for line in registers_collection_type:
            del line["group"]

        collection_type_request = self._build_contiguous_blocks_requests_to_device(
            registers_collection_type, max_reg_request
        )

        return self._build_registers_data_according_modbus_decoder(collection_type_request)

    def get_registers_by_collection_type(self, collection_type):
        """
        list registers with the columns defined in the map_columns
        filtered by collection_type (example: collection_type = "minutely")
        each line is a register (ordered dict)
        """

        valid_block = self.get_full_registers_according_defined_columns()
        return self._filter_registers_by_collection_type(valid_block, collection_type)

    def get_full_registers_according_defined_columns(self):
        """
        list registers with the columns defined in the map_columns
        filtered by collection_type (example: collection_type = "minutely")
        each line is a register (ordered dict)
        """
        raw_block = self._parser_csv_file(self.path_file)
        return self._filter_valid_block_by_column_active(raw_block)

    def _filter_valid_block_by_column_active(self, raw_block: list):
        """
        filter the valid registers (colomn active) from the raw registers,
            convert the type registers to the correct type for the modbus device
            convert str to bool and str to int
        """
        valid_map_block: list[dict[str, str | int]] = []

        for line in raw_block:
            line["address"] = int(line["address"])
            line["size"] = int(line["size"])
            line["active"] = str_bool(line["active"])
            line["type"] = type_modbus(line["type"])

            if line["active"]:
                valid_line = {
                    column: line[column] for column in line if column in self.csv_map_columns
                }
                valid_map_block.append(valid_line)
        return valid_map_block

    def _parser_csv_file(self, path_file: str):
        """
        read the csv file and return a list of dictionaries
        """
        raw_map_block = []

        with open(path_file, "r", encoding="utf8") as file_handle:
            csv_reader = DictReader(file_handle, delimiter=",", skipinitialspace=True)

            for line in csv_reader:
                raw_line = {key.lower().strip(): value.strip() for key, value in line.items()}
                raw_map_block.append(raw_line)
        return raw_map_block

    def _build_contiguous_blocks_requests_to_device(self, registers, max_reg_request):
        """
        build contiguous block of the same type to better reduce the
        number of requests to the device.

        params:
            registers: list of tuples (address, size, type) - each tuple one register
            max_reg_request: maximum number of registers in contiguous block
                to be requested.

        return: list of tuples (initial_address, num_reg, type)
            initial_address: initial address of block
            num_reg: the number of registers to read
            type: type of registers in the block
        """

        sequential_blocks = []
        current_line = registers[0]
        current_addr: int = current_line["address"]
        current_size: int = current_line["size"]
        current_type: str = current_line["type"]

        start_address: int = current_addr
        size_request: int = current_size
        name_registers: list[str] = [current_line["register"]]
        register_counter: int = 0

        for next_line in registers[1:]:
            is_continuous = next_line["address"] == current_addr + current_size
            is_same_type = next_line["type"].lower() == current_type.lower()
            is_same_size = next_line["size"] == current_size
            is_low_max_size = register_counter < max_reg_request - 1

            if all([is_continuous, is_same_type, is_same_size, is_low_max_size]):
                size_request += next_line["size"]
                register_counter += 1

            else:
                sequential_blocks.append(
                    OrderedDict(
                        start_address=start_address,
                        size=size_request,
                        type=current_type,
                        byteorder=next_line["byteorder"],
                        datamodel=next_line["datamodel"],
                        name_registers=name_registers,
                    )
                )

                start_address = next_line["address"]
                size_request = next_line["size"]
                register_counter = 0
                name_registers = []

            current_addr = next_line["address"]
            current_size = next_line["size"]
            current_type = next_line["type"]
            current_byteorder = next_line["byteorder"]
            current_datamodel = next_line["datamodel"]
            name_registers.append(next_line["register"])

        sequential_blocks.append(
            OrderedDict(
                start_address=start_address,
                size=size_request,
                type=current_type,
                byteorder=current_byteorder,
                datamodel=current_datamodel,
                name_registers=name_registers,
            )
        )
        return sequential_blocks

    def _filter_registers_by_collection_type(self, registers_block, collection_type: str):
        """
        filter a block valid registers by collection_type
        example: collection_type = "minutely"
        """
        registers_collection_type = []

        for line in registers_block:
            if line["group"].lower() in [collection_type, COLLECTION_TYPE_DATETIME]:
                registers_collection_type.append(line)
        return registers_collection_type

    def _build_registers_data_according_modbus_decoder(self, request_blocks):
        """
        build the registers data to be requested to the device whith function
        decode by type defined in the request_blocks
        """

        for block in request_blocks:
            block.func_decode = ModbusTypeDecoder().parsers[block["type"]]

        return request_blocks
