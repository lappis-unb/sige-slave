from django.db import models
from django.utils import timezone

from data_collector.modbus.helpers import type_modbus
from data_collector.modbus.settings import CONFIG_TRANSDUCTOR, CSV_SCHEMA, DATA_GROUPS


class MemoryMap(models.Model):
    id = models.AutoField(primary_key=True)
    model_transductor = models.CharField(max_length=30, unique=True)
    minutely = models.JSONField()
    quarterly = models.JSONField()
    monthly = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.model_transductor

    class Meta:
        verbose_name_plural = "Memory Maps"

    @classmethod
    def get_or_create_by_csv(cls, model_transductor: str, csv_data: list[dict], defaults=None):
        defaults = defaults or {}

        model_transductor = model_transductor.lower().strip().replace(" ", "_")
        max_block = CONFIG_TRANSDUCTOR.get(model_transductor, {}).get("max_block", 1)

        sequential_blocks = cls._process_csv_data(csv_data, max_block)
        defaults.update(sequential_blocks)

        return cls.objects.get_or_create(model_transductor=model_transductor, defaults=defaults)

    @classmethod
    def _process_csv_data(cls, csv_data: list[dict], max_block: int) -> dict:
        """Process CSV data by filtering rows that match a data group,
        and splitting them into sequential blocks no larger than max_block.
        """
        sequential_blocks = {}
        for data_group in DATA_GROUPS:
            datagroup_registers = cls._get_valid_registers_by_group(csv_data, data_group)

            if not datagroup_registers:
                sequential_datagroup = {}
            else:
                sequential_datagroup = cls._build_sequential_blocks(datagroup_registers, max_block)

            sequential_blocks[data_group] = sequential_datagroup

        return sequential_blocks

    @staticmethod
    def _get_valid_registers_by_group(csv_data: list[dict], data_group: str) -> list[dict]:
        """
        filters data for records belonging to a specified group.
        """

        required_headers = CSV_SCHEMA.keys()

        try:
            datagroup_registers = []
            for line in csv_data:
                if line["group"] != data_group:
                    continue

                filtered_line = {column: line[column] for column in line if column in required_headers}
                filtered_line.update(
                    {
                        "address": int(line["address"]),
                        "size": int(line["size"]),
                        "type": type_modbus(line["type"]),
                    }
                )
                datagroup_registers.append(filtered_line)
            return datagroup_registers

        except (TypeError, ValueError, KeyError) as e:
            raise Exception(f"Error occurred while processing data: {e}") from e

    @staticmethod
    def _build_sequential_blocks(registers: list[dict], len_max_block: int) -> list[dict]:
        """
        Group consecutive registers with type and until the `len_max_block` number of registers
        is reached or the next register has a different address or type than the previous one.
        It then adds the block of consecutive registers to a list of sequential blocks.
        """

        sequential_blocks = []

        current_block = {
            "start_address": registers[0]["address"],
            "size": registers[0]["size"],
            "type": registers[0]["type"],
            "byteorder": registers[0]["byteorder"],
            "function": registers[0]["function"],
            "attributes": [registers[0]["attribute"]],
        }

        register_counter = 1
        for i in range(1, len(registers)):
            current_line = registers[i]
            check_conditions = all(
                [
                    current_line["address"] == current_block["start_address"] + current_block["size"],
                    current_line["type"] == current_block["type"],
                    register_counter < len_max_block,
                ]
            )

            if check_conditions:
                current_block["size"] += current_line["size"]
                register_counter += 1
                current_block["attributes"].append(current_line["attribute"])

            else:
                sequential_blocks.append(current_block)
                current_block = {
                    "start_address": current_line["address"],
                    "size": current_line["size"],
                    "type": current_line["type"],
                    "byteorder": current_line["byteorder"],
                    "function": current_line["function"],
                    "attributes": [current_line["attribute"]],
                }
                register_counter = 1

        sequential_blocks.append(current_block)
        return sequential_blocks
