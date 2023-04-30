# flake8: noqa
from datetime import time
from enum import Enum

# These names must be used in the CSV map file in the `group` column
DATA_GROUPS = ["datetime", "minutely", "quarterly", "monthly"]
DATA_GROUP_DATETIME = "datetime"
DATA_GROUP_MINUTELY = "minutely"
DATA_GROUP_QUARTERLY = "quarterly"
DATA_GROUP_MONTHLY = "monthly"

REQUIRED_HEADERS = [
    "register",
    "address",
    "size",
    "type",
    "group",
    "byteorder",
    "datamodel",
]

# Modbus reads and writes in "registers". Our registers have 16 bytes
MODBUS_REGISTER_SIZE: int = 2
MODBUS_READ_MAX: int = 125

# Format characters have the python struct module;


# type - format - size
class DATATYPE(Enum):
    UINT8 = ("B", 1)
    UINT16 = ("H", 2)
    UINT32 = ("I", 4)
    UINT64 = ("Q", 8)
    INT8 = ("b", 1)
    INT16 = ("h", 2)
    INT32 = ("i", 4)
    INT64 = ("q", 8)
    FLOAT16 = ("e", 2)
    FLOAT32 = ("f", 4)
    FLOAT64 = ("d", 4)


class Endian:
    """
    Big: This indicates that the bytes are in big endian format
    Little: This indicates that the bytes are in little endian format
    """

    Auto = "@"
    Big = ">"
    Little = "<"


# Endianness definitions
Auto = "@"
BIG_ENDIAN: str = ">"
LITTLE_ENDIAN: str = "<"

TABLE_EXCEPTION_CODE: dict[str, str] = {
    "1": "ILLEGAL FUNCTION",
    "2": "ILLEGAL DATA ADDRESS",
    "3": "ILLEGAL DATA VALUE",
    "4": "SLAVE DEVICE FAILURE",
    "5": "COMMAND ACKNOWLEDGE",
    "6": "SLAVE DEVICE BUSY",
    "8": "MEMORY PARITY ERROR",
}

dir_type_map: dict[str, str] = {
    "csv_dir": "CSV Config Directory",
    "config_dir": "Diver Config Directory",
}

ON_PEAK_TIME_START = time(18, 00, 00)
ON_PEAK_TIME_END = time(20, 59, 59)

INTERMEDIATE_TIME_START = time(17, 0, 0)
INTERMEDIATE_TIME_END = time(21, 59, 59)

OFF_PEAK_TIME_START = time(22, 0, 0)
OFF_PEAK_TIME_END = time(16, 59, 59)
