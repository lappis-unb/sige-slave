import time
from datetime import datetime
from importlib import import_module
from types import ModuleType

from django.utils import timezone
from pymodbus.exceptions import ParameterException

"""
    function utilities:
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

    # These methods create utility functions
    @staticmethod
    def parse_bits():
        """
        Decodes a byte worth of bits number
        """
        return lambda d: d.decode_bits()

    @staticmethod
    def parse_8bit_uint():
        """
        Decodes a 8 bits unsigned integer number
        """
        return lambda d: d.decode_8bit_uint()

    @staticmethod
    def parse_16bit_uint():
        """
        Decodes a 16 bits unsigned integer number
        """
        return lambda d: d.decode_16bit_uint()

    @staticmethod
    def parse_32bit_uint():
        """
        Decodes a 32 bits unsigned integer number
        """
        return lambda d: d.decode_32bit_uint()

    @staticmethod
    def parse_64bit_uint():
        """
        Decodes a 64 bits unsigned integer number
        """
        return lambda d: d.decode_64bit_uint()

    @staticmethod
    def parse_8bit_int():
        """
        Decodes a 8 bits in signed integer number
        """
        return lambda d: d.decode_8bit_int()

    @staticmethod
    def parse_16bit_int():
        """
        Decodes a 16 bits in signed integer number
        """
        return lambda d: d.decode_16bit_int()

    @staticmethod
    def parse_32bit_int():
        """
        Decodes a 32 bits in signed integer number
        """
        return lambda d: d.decode_32bit_int()

    @staticmethod
    def parse_64bit_int():
        """
        Decodes a 64 bits in signed integer number
        """
        return lambda d: d.decode_64bit_int()

    @staticmethod
    def parse_16bit_float():
        """
        Decodes a 16 bits in float number
        """
        return lambda d: d.decode_16bit_float()

    @staticmethod
    def parse_32bit_float():
        """
        Decodes a 32 bits in float number
        """
        return lambda d: d.decode_32bit_float()

    @staticmethod
    def parse_64bit_float():
        """
        Decodes a 64 bits in float number
        """
        return lambda d: d.decode_64bit_float()


def load_handler(path: str, *args, **kwargs):
    """
    Given a path to a handler, return an instance of that handler.
    """
    i: int = path.rfind(".")
    module: str
    attr: str
    module, attr = path[:i], path[i + 1 :]
    try:
        mod: ModuleType = import_module(module)
        cls = getattr(mod, attr)

    except AttributeError as e:
        raise ParameterException(
            'invalid parameter (Module: "%s" or attr: "%s")' % (module, attr)
        ) from e

    return cls(*args, **kwargs)


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
        measurements_copy["second"],
    )


def type_modbus(data_type: str) -> str:
    """
    Changes common data type names to the expected modbus data type name

    Args:
        data_type(str): name of the data in the csv file to be parsed.

    Return:
        str: the correct modbus data type.

    Raises:
        ValueError: if we can't find a Modbus
    """

    clean_format: str = data_type.replace(" ", "").strip("-").lower()
    if clean_format in {
        "u8",
        "ui8",
        "uint8",
    }:
        data_type = "uint8"

    elif clean_format in {
        "u16",
        "ui16",
        "uint",
        "word",
        "uint16",
        "uint16bit",
        "unsignedint16bit",
        "s16",
        "short",
        "short16",
    }:
        data_type = "uint16"

    elif clean_format in {
        "ui32",
        "u32",
        "uint32",
        "dword",
        "unsignedint32bit",
        "ul32",
        "ulong",
        "ulong32",
        "longint32",
    }:
        data_type = "uint32"

    elif clean_format in {
        "uint64",
        "u64",
        "ui64",
        "ull",
        "ulong64",
        "ulonglong",
        "ulonglong64",
    }:
        data_type = "uint64"

    elif clean_format in {"int8", "i8", "integer8"}:
        data_type = "int8"

    elif clean_format in {"int", "i16", "int16", "int16bit", "integer", "integer16"}:
        data_type = "int16"

    elif clean_format in {
        "int32",
        "i32",
        "integer32",
        "l32",
        "long",
        "long32",
        "li32",
        "longint",
        "longint32",
    }:
        data_type = "int32"

    elif clean_format in {
        "int64",
        "i64",
        "unixdatastamp",
        "integer64",
        "longlong",
        "longint64",
    }:
        data_type = "int64"

    # Half-precision floating-point format (2 bytes)
    elif clean_format in {"float16", "f16", "fp16", "half"}:
        data_type = "float16"

    # IEEE 754 single-precision binary floating-point format (4 bytes)
    elif clean_format in {
        "f32",
        "fp32",
        "float",
        "float32",
        "real",
        "single",
        "ieee32bitfloatpoint",
        "ieee32bitfp",
        "ieee32bit",
    }:
        data_type = "float32"

    # IEEE 754 double-precision binary floating-point format (8 bytes)
    elif clean_format in {
        "f64",
        "fp64",
        "float64",
        "lreal",
        "double",
        "ieee64bitfloatpoint",
        "ieee64bitfp",
        "ieee64bit",
    }:
        data_type = "float64"

    elif clean_format in {
        "bit",
        "bits",
        "b",
    }:
        data_type = "bits"

    else:
        raise ValueError(f"Unsupported type: {data_type}")

    return data_type


def str_bool(to_convert: str) -> bool:
    """
    Converts a valid string to a boolean

    Args:
        to_convert(str): string to be converted to boolean

    Return:
        bool: if string matched in group(true or false)
        if not matched raise ValueError
    """

    clean_string: str = to_convert.strip().lower()
    if clean_string in {"t", "y", "true", "yes", "1"}:
        return True
    elif clean_string in {"f", "n", "false", "no", "0", ""}:
        return False
    else:
        raise ValueError(f"Unsupported: {to_convert}")


def unixtime_to_datetime(unix_time: int) -> datetime:
    """
    Converts a unix timestamp to datetime object
    """
    date_time: datetime = datetime.fromtimestamp(unix_time)

    date_time.strftime("%Y-%m-%d %H:%M:%S")
    return date_time


def datetime_to_unixtime(date_time: datetime) -> int:
    """
    Converts a datetime object to unix time stamp

    Example:
        datetime = (2022, 5, 1, 13, 20, 15).
        The year is 2022, the month is 5, the day is 1, the hour is 13,
        the minute is 20 and the second is 15.

    Args:
        date_time (datetime): datetime object to be converted to unix time stamp

    Returns:
        int: unix time stamp
    """
    unix_time: float = time.mktime(date_time.timetuple())

    return int(unix_time)


def datetime_string_to_unixtime(date_time_string: str) -> int:
    """
    Converts a datetime string to unix time stamp

    Example:
        date_time_string = "2021/7/26, 21:20:15"
        The year is 2021, the month is 7, the day is 26, the hour is 21,
        the minute is 20 and the second is 15.
    """
    date_format: datetime = datetime.strptime(date_time_string, "%Y-%m-%d, %H:%M:%S")

    return int(datetime.timestamp(date_format))
