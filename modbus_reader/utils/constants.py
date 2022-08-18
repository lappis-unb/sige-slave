# flake8: noqa
# --------------------------------------------------------------------------- #
# Define some constants
# --------------------------------------------------------------------------- #

# Esse padão de nomenclatura deve ser utilizada no arquivo do mapa csv (coluna group)
COLLECTION_TYPE_DATETIME = "datetime"
COLLECTION_TYPE_MINUTELY = "minutely"
COLLECTION_TYPE_QUARTERLY = "quarterly"
COLLECTION_TYPE_MONTHLY = "monthly"

# Atenção se o nome do arquivo, nome da classe ou diretório for alterado
# você deve alterar o nome da constante abaixo
PATH_REGISTER_CSV = "modbus_reader.register_csv.RegisterCSV"
PATH_TRANSDUCTOR_DEVICE = "modbus_reader.device.TransductorDevice"
PATH_TRANSDUCTOR_READER = "modbus_reader.device.DeviceReader"

REGISTER_MAP_COLUMNS = ["register", "address", "size", "type", "group"]

# Modbus data is read and written as "registers" which are 16 bits (1 byte) chunks of data.
# SIZE = size in bytes for type
# lenght = number of registers for size()

MODBUS_REGISTER_SIZE = 2   # 2 bytes(16 bits) 
MODBUS_READ_MAX = 100

SIZE, LENGTH = 0, 1
UINT8   = (1, 1) 
UINT16  = (2, 1)  # UINT16.SIZE = 2, UINT16.LENGTH = 1
UINT32  = (4, 2)
UINT64  = (8, 4)
INT8    = (1, 1)
INT16   = (2, 1)
INT32   = (4, 2)
INT64   = (8, 4)
FLOAT16 = (2, 1)
FLOAT32 = (4, 2)
FLOAT64 = (8, 4)  


# BYTE Ordering
BIG = "big"
BIG_ENDIAN = ">"
LITTLE_ENDIAN = "<"

TABLE_EXCEPTION_CODE = {
    "1": "ILLEGAL FUNCTION",
    "2": "ILLEGAL DATA ADDRESS",
    "3": "ILLEGAL DATA VALUE",
    "4": "SLAVE DEVICE FAILURE",
    "5": "COMMAND ACKNOWLEDGE",
    "6": "SLAVE DEVICE BUSY",
    "8": "MEMORY PARITY ERROR",
}

dir_type_map = {
    "csv_dir": "CSV Config Directory",
    "config_dir": "Diver Config Directory",
}

