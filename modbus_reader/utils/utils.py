import time
from datetime import date, datetime
from importlib import import_module

from django.utils import timezone
from pymodbus.exceptions import ParameterException

"""
    function utilitys:
        function to convert a string to a boolean.
        function to convert type/format to their corresponding size and type modbus.
    class parser to parse the modbus response.
"""

class ModbusTypeDecoder(object):
    def __init__(self):
        self.parsers = {
            "uint8": self.parse_8bit_uint(),
            "uint16": self.parse_16bit_uint(),
            "uint32": self.parse_32bit_uint(),
            "uint64": self.parse_64bit_uint(),
            "int8": self.parse_8bit_int(),
            "int16": self.parse_16bit_int(),
            "int32": self.parse_32bit_int(),
            "int64": self.parse_64bit_int(),
            "float16": self.parse_16bit_float(),
            "float32": self.parse_32bit_float(),
            "float64": self.parse_64bit_float(),
            "bits": self.parse_bits(),
        }

#  métodos estáticos para criar funções utilitárias.
    @staticmethod
    def parse_bits():
        """ Decodes a byte worth of bits number
        """
        return lambda d: d.decode_bits()

    @staticmethod
    def parse_8bit_uint():
        """ Decodes a 8 bits unsigned integer number
        """
        return lambda d: d.decode_8bit_uint()

    @staticmethod
    def parse_16bit_uint():
        """ Decodes a 16 bits unsigned integer number
        """
        return lambda d: d.decode_16bit_uint()

    @staticmethod
    def parse_32bit_uint():
        """ Decodes a 32 bits unsigned integer number
        """
        return lambda d: d.decode_32bit_uint()

    @staticmethod
    def parse_64bit_uint():
        """ Decodes a 64 bits unsigned integer number
        """
        return lambda d: d.decode_64bit_uint()

    @staticmethod
    def parse_8bit_int():
        """ Decodes a 8 bits in signed integer number
        """
        return lambda d: d.decode_8bit_int()

    @staticmethod
    def parse_16bit_int():
        """ Decodes a 16 bits in signed integer number
        """
        return lambda d: d.decode_16bit_int()

    @staticmethod
    def parse_32bit_int():
        """ Decodes a 32 bits in signed integer number
        """
        return lambda d: d.decode_32bit_int()

    @staticmethod
    def parse_64bit_int():
        """ Decodes a 64 bits in signed integer number
        """
        return lambda d: d.decode_64bit_int()

    @staticmethod
    def parse_16bit_float():
        """ Decodes a 16 bits in float number
        """
        return lambda d: d.decode_16bit_float()
    
    @staticmethod
    def parse_32bit_float():
        """ Decodes a 32 bits in float number
        """
        return lambda d: d.decode_32bit_float()

    @staticmethod
    def parse_64bit_float():
        """ Decodes a 64 bits in float number
        """
        return lambda d: d.decode_64bit_float()

# ==================================================================================================
def load_handler(path, *args, **kwargs):
    """
    Given a path to a handler, return an instance of that handler.

    """
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        mod = import_module(module)
        cls = getattr(mod, attr)

    except AttributeError as e:
        raise ParameterException('invalid parameter (Module: "%s" or attr: "%s")' % (module, attr)) from e


    return cls(*args, **kwargs) 

# ==================================================================================================
def remove_format_datetime(measurements):
    measurements_copy = measurements.copy()
    for measurement, _ in measurements_copy.items():
        if measurement in (
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "second",
            "day_of_the_month",
            "day_of_the_week",
            "day_of_the_year",
        ):
            del measurements[measurement]

    return timezone.datetime(
        measurements_copy["year"],
        measurements_copy["month"],
        measurements_copy["day_of_the_month"],
        measurements_copy["hour"],
        measurements_copy["minute"],
        measurements_copy["second"]
    )
# ==================================================================================================

def type_modbus(format: str) -> str:
    """ Parse the transform type/format to the correct modbus data format
    
    Args:
        format: type of the data in csv file to be parsed.
    
    Return:
        str: the correct modbus data type if not matched raise ValueError
    """
    
    clean_format = format.replace(" ", "").strip("-").lower()
    if clean_format in {"u8", "ui8", "uint8", }:
        format = "uint8" # 1 byte
    
    elif clean_format in {"u16", "ui16", "uint", "word", "uint16", "uint16bit", "unsignedint16bit", "s16", "short", "short16"}:
        format = "uint16" # 2 bytes
    
    elif clean_format in {"ui32", "u32", "uint32", "dword", "unsignedint32bit", "ul32", "ulong", "ulong32", "longint32"}:
        format = "uint32" # 4 bytes
    
    elif clean_format in {"uint64", "u64", "ui64", "ull", "ulong64", "ulonglong", "ulonglong64"}:
        format = "uint64" # 8 bytes
    
    elif clean_format in {"int8", "i8", "integer8"}:
        format = "int8" # 1 byte
    
    elif clean_format in {"int", "i16", "int16", "int16bit", "integer", "integer16"}:
        format = "int16" # 2 bytes
    
    elif clean_format in {"int32", "i32", "integer32", "l32", "long", "long32", "li32", "longint", "longint32"}:
        format = "int32" # 4 bytes
    
    elif clean_format in {"int64", "i64", "unixdatastamp", "integer64", "longlong", "longint64"}:
        format = "int64" # 8 bytes
    
    # Half-precision floating-point format
    elif clean_format in {"float16", "f16", "fp16","half"}:
        format = "float16" # 2 bytes
    
    # IEEE 754 single-precision binary floating-point format
    elif clean_format in {"f32", "fp32", "float", "float32", "real", "single", "ieee32bitfloatpoint", "ieee32bitfp", "ieee32bit"}:
        format = "float32" # 4 bytes
    
    # IEEE 754 double-precision binary floating-point format
    elif clean_format in {"f64", "fp64", "float64", "lreal", "double", "ieee64bitfloatpoint", "ieee64bitfp", "ieee64bit"}:
        format = "float64" # 8 bytes
    
    elif clean_format in {"bit", "bits", "b", }:
        format = "bits" # 1 bit
    
    else:
        raise ValueError(f"Unsupported type: {format}")

    return format
# ==================================================================================================

def str_bool(str_bool: str) -> bool:
    """ converts valids string to a boolean
    
    Args:
        str_bool: string to be converted to boolean
    
    Return: 
        bool: if string matched in group(true or false)
        if not matched raise ValueError
    """
    
    clean_string = str_bool.strip().lower()
    if clean_string in {"t", "y", "true", "yes", "1"}:
        return True
    elif clean_string in {"f", "n", "false", "no", "0", ""}:
        return False
    else:
        raise ValueError(f"Unsupported: {str_bool}")
# ==================================================================================================
def unixtime_to_datetime(unix_time: int) -> datetime:
    """ Converts a unix time stamp to datetime object
    """
    date_time = datetime.fromtimestamp(unix_time)
    
    date_time.strftime("%Y-%m-%d %H:%M:%S")
    return date_time
# ==================================================================================================
def datetime_to_unixtime(date_time: datetime) -> int:
    """ Converts a datetime object to unix time stamp
    
    Example: 
        datetime = (2022, 5, 1, 13, 20, 15). 
        The year is 2022, the month is 5, the day is 1, the hour is 13,
        the minute is 20 and the second is 15.

    Args:
        date_time (datetime): datetime object to be converted to unix time stamp

    Returns:
        int: unix time stamp
    """
    unix_time = time.mktime(date_time.timetuple())
    # unix_time = int(date_time.timestamp())
    
    return int(unix_time)
# ==================================================================================================
def datetime_string_to_unixtime(date_time_string: str) -> int:
    """ Converts a datetime string to unix time stamp
    
    Example:
        date_time_string = "2021/7/26, 21:20:15"
        The year is 2021, the month is 7, the day is 26, the hour is 21,
        the minute is 20 and the second is 15.
    """
    date_format = datetime.strptime(date_time_string, "%Y-%m-%d, %H:%M:%S")
    
    return int(datetime.timestamp(date_format))

# ==================================================================================================
