# flake8: noqa

# These names must be used in the CSV map file in the `group` column
COLLECTION_TYPE_DATETIME: str = "datetime"
COLLECTION_TYPE_MINUTELY: str = "minutely"
COLLECTION_TYPE_QUARTERLY: str = "quarterly"
COLLECTION_TYPE_MONTHLY: str = "monthly"

# Cronjob definitions
TRANSDUCTOR_COLLECTION_TYPE_MINUTELY: str = "minutely"
TRANSDUCTOR_COLLECTION_TYPE_QUARTERLY: str = "quarterly"
TRANSDUCTOR_COLLECTION_TYPE_MONTHLY: str = "monthly"
MONTH_TO_MINUTES: int = 30 * 24 * 60

# WARNING: these must change if the files, classes or directories are changed
PATH_REGISTER_CSV: str = "modbus_reader.register_csv.RegisterCSV"
PATH_TRANSDUCTOR_DEVICE: str = "modbus_reader.device.TransductorDevice"
PATH_TRANSDUCTOR_READER: str = "modbus_reader.device.DeviceReader"

REGISTER_MAP_COLUMNS = ["register", "address", "size", "type", "group", "byteorder", "datamodel"]

# Modbus reads and writes in "registers". Our registers have 16 bytes
MODBUS_REGISTER_SIZE: int = 2
MODBUS_READ_MAX: int = 125

# Variables with size (bytes) and length (register size)
LENGTH: int
SIZE: int
SIZE, LENGTH = 0, 1
UINT8: tuple[int, int] = (1, 1)
UINT16: tuple[int, int] = (2, 1)
UINT32: tuple[int, int] = (4, 2)
UINT64: tuple[int, int] = (8, 4)
INT8: tuple[int, int] = UINT8
INT16: tuple[int, int] = UINT16
INT32: tuple[int, int] = UINT32
INT64: tuple[int, int] = UINT64
FLOAT16: tuple[int, int] = (2, 1)
FLOAT32: tuple[int, int] = (4, 2)
FLOAT64: tuple[int, int] = (8, 4)


# Endianness definitions
BIG: str = "big"
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
