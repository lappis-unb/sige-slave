from collections import OrderedDict
from csv import DictReader

from modbus_reader.utils.constants import DATA_GROUPS, REQUIRED_HEADERS
from modbus_reader.utils.helpers import ModbusTypeDecoder, type_modbus


class MemoryMapModbus:
    minutely = {}
    quarterly = {}
    monthly = {}

    # @classmethod
    def getitem(self, transductor, atribute):
        dictionary = getattr(self, atribute)
        return dictionary.get(transductor)

    # @classmethod
    def setitem(self, attribute, transductor, memory_map):
        dictionary = getattr(self, attribute)
        dictionary[transductor] = memory_map

    def create_store_memory_map(self, transductor, path_csv, len_max_block, data_group):
        raw_registers = self._reader_csv_file(path_csv)
        valid_registers = self._filter_valid_block_by_column_active(raw_registers)
        datagroup_registers = self._filter_registers_by_data_group(
            valid_registers, data_group
        )
        register_blocks = self._build_contiguous_blocks(
            datagroup_registers, len_max_block
        )
        request_blocks = self._build_requests_blocks_modbus(register_blocks)

        memory_map = {
            "total_register": len(datagroup_registers),
            "total_blocks": len(request_blocks),
            "request_blocks": request_blocks,
        }

        self.setitem(data_group, transductor, memory_map)

    def update_store_memory_map(self, transductor, path_csv, len_max_block):
        for data_group in DATA_GROUPS:
            self.create_store_memory_map(
                transductor, path_csv, len_max_block, data_group
            )

    def _filter_valid_block_by_column_active(self, raw_block: list):
        """
        filter the required columns from the raw registers,
            convert the type registers to the correct type for the modbus device
            convert str to bool and str to int
        """
        valid_map_block: list[dict[str, str | int]] = []

        for line in raw_block:
            line["address"] = int(line["address"])
            line["size"] = int(line["size"])
            line["type"] = type_modbus(line["type"])

            valid_line = {
                column: line[column] for column in line if column in REQUIRED_HEADERS
            }
            valid_map_block.append(valid_line)

        return valid_map_block

    def _reader_csv_file(self, path_file: str):
        """
        read the csv file and return a list of dictionaries
        keys and values converted to lowercase letters and whitespace stripped,
        only rows with key "active" = "true" are appended to the list of dictionaries.
        """
        data = []
        with open(path_file, "r", encoding="utf8") as file_handle:
            csv_reader = DictReader(file_handle, delimiter=",", skipinitialspace=True)

            for row in csv_reader:
                row = {
                    key.lower().strip(): value.lower().strip()
                    for key, value in row.items()
                }
                if row.get("active") in ["t", "y", "true", "yes", "1"]:
                    data.append(row)
        return data

    def _build_contiguous_blocks(self, registers, len_max_block):
        """
        Build contiguous blocks of the same type to better reduce the number
        of requests to the device.

        Arguments:
        registers -- a list of registers to build contiguous blocks from.
        len_max_block -- the maximum number of registers in a block.

        Return:
        A list of contiguous blocks of registers.
        """

        sequential_blocks = []
        current_line = registers[0]
        current_addr: int = current_line["address"]
        current_size: int = current_line["size"]
        current_type: str = current_line["type"]
        current_byteorder: int = current_line["byteorder"]
        current_datamodel: int = current_line["datamodel"]

        start_address: int = current_addr
        size_request: int = current_size
        name_registers: list[str] = [current_line["register"]]
        register_counter: int = 0

        for next_line in registers[1:]:
            is_continuous = next_line["address"] == current_addr + current_size
            is_same_type = next_line["type"].lower() == current_type.lower()
            is_same_size = next_line["size"] == current_size
            is_low_max_size = register_counter < len_max_block - 1

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

    def _filter_registers_by_data_group(self, registers_block, data_group: str):
        """
        filter a block valid registers by data_group
        example: data_group = "minutely"
        """
        reg_data_group = []
        for line in registers_block:
            if line["group"].lower() in data_group:
                reg_data_group.append(line)

        return reg_data_group

    def _build_requests_blocks_modbus(self, request_blocks):
        """
        build the registers data to be requested to the device whith function
        decode by type defined in the request_blocks
        """

        for block in request_blocks:
            block.func_decode = ModbusTypeDecoder().parsers[block["type"]]

        return request_blocks
