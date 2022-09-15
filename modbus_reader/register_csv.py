from collections import OrderedDict
from csv import DictReader
from typing import List, Tuple, Union

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

    def get_request_blocks(self, collection_type, max_reg_request):
        """
        filter the registers by collection_type and build contiguous blocks with
        fields: initial_address, num_reg, type to be requested
        """

        registers_collection_type = self.get_registers_collection_type(collection_type)
        registers_data_size = [(line["address"], line["size"], line["type"], line["register"]) for line in registers_collection_type]
        collection_type_request = self._build_contiguous_blocks_requests_to_device(registers_data_size, max_reg_request)
        return self._build_registers_data(collection_type_request)

    def get_registers_collection_type(self, collection_type):
        """
        list registers with the columns defined in the map_columns
        filtered by collection_type (example: collection_type = "minutely")
        each line is a register (ordered dict)
        """
        valid_block = self.get_full_registers()
        return self._filter_registers_collection_type(valid_block, collection_type)

    def get_full_registers(self):
        """
        list registers with the columns defined in the map_columns
        each line is a register (ordered dict)
        """
        raw_block = self._parser_csv_file(self.path_file)
        return self._filter_valid_block(raw_block, self.csv_map_columns)

    def _parser_csv_file(self, path_file):
        """
        read the csv file and return a list of dictionaries
        """
        raw_map_block: List[OrderedDict[str, str]] = []

        with open(path_file, "r", encoding="utf8") as file_handle:
            csv_reader = DictReader(file_handle, delimiter=",", skipinitialspace=True)

            for line in csv_reader:
                raw_line = OrderedDict()
                for key, value in line.items():
                    raw_line[key.lower()] = value
                raw_map_block.append(raw_line)
        return raw_map_block

    def _filter_valid_block(self, raw_block, csv_map_columns):
        """
        filter the valid registers (colomn active) from the raw registers,
            convert the type registers to the correct type for the modbus device
            convert str to bool and str to int
        """
        valid_map_block: List[OrderedDict[str, Union[str, int]]] = []

        for line in raw_block:
            line["address"] = int(line["address"])
            line["size"] = int(line["size"])
            line["active"] = str_bool(line["active"])
            line["type"] = type_modbus(line["type"])

            if line["active"]:
                valid_line = OrderedDict()
                for column in line:
                    if column in csv_map_columns:
                        valid_line[column] = line[column]
                valid_map_block.append(valid_line)
        return valid_map_block

    def _build_contiguous_blocks_requests_to_device(self, registers: List[Tuple[int, int, str]], max_reg_request: int=100) -> List[OrderedDict]:
        sequential_blocks = []

        current_addr, current_size, current_type, current_name = registers[0]
        start_address: int = current_addr
        size_request: int = current_size
        register_counter: int = 0
        name_registers: list[str] = [current_name]

        for next_addr, next_size, next_type, next_name in registers[1:]:
            continuous = next_addr == current_addr + current_size
            same_type = next_type.lower() == current_type.lower()
            same_size = next_size == current_size
            max_size = register_counter < max_reg_request - 1

            if continuous and max_size and same_type and same_size:
                size_request += next_size
                register_counter += 1

            else:
                sequential_blocks.append(
                    OrderedDict(
                        start_address=start_address,
                        size=size_request,
                        type=current_type,
                        name_registers=name_registers
                    )
                )

                start_address = next_addr
                size_request = next_size
                register_counter = 0
                name_registers = []

            current_addr = next_addr
            current_size = next_size
            current_type = next_type
            name_registers.append(next_name)

        sequential_blocks.append(
            OrderedDict(
                start_address=start_address,
                size=size_request,
                type=current_type,
                name_registers=name_registers
            )
        )
        return sequential_blocks

    def _filter_registers_collection_type(self, registers_block, collection_type: str):
        # sourcery skip: for-append-to-extend, identity-comprehension, inline-immediately-returned-variable, list-comprehension, remove-redundant-if
        """
        filter a block valid registers by collection_type
        example: collection_type = "minutely"
        """
        registers_collection_type: List[OrderedDict[str, Union[str, int]]] = []

        for line in registers_block:
            if line["group"].lower() in [collection_type, COLLECTION_TYPE_DATETIME, COLLECTION_TYPE_MINUTELY]:
                registers_collection_type.append(line)
        return registers_collection_type

    def _build_registers_data(self, request_blocks):
        """
        build the registers data to be requested to the device whith function
        decode by type defined in the request_blocks
        """

        for block in request_blocks:
            block.func_decode = ModbusTypeDecoder().parsers[block['type']]

        return request_blocks
