import struct

from django.utils import timezone

from data_collector.modbus.constants import ON_PEAK_TIME_END, ON_PEAK_TIME_START


class ModbusTypeDecoder(object):
    """
    Parsing different data types commonly used in Modbus communication. Use dictionary to
    mapping the data type string names to their corresponding parsing methods.
    """

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

    @staticmethod
    def parse_bits():
        return lambda d: d.decode_bits()

    @staticmethod
    def parse_8bit_uint():
        return lambda d: d.decode_8bit_uint()

    @staticmethod
    def parse_16bit_uint():
        return lambda d: d.decode_16bit_uint()

    @staticmethod
    def parse_32bit_uint():
        return lambda d: d.decode_32bit_uint()

    @staticmethod
    def parse_64bit_uint():
        return lambda d: d.decode_64bit_uint()

    @staticmethod
    def parse_8bit_int():
        return lambda d: d.decode_8bit_int()

    @staticmethod
    def parse_16bit_int():
        return lambda d: d.decode_16bit_int()

    @staticmethod
    def parse_32bit_int():
        return lambda d: d.decode_32bit_int()

    @staticmethod
    def parse_64bit_int():
        return lambda d: d.decode_64bit_int()

    @staticmethod
    def parse_16bit_float():
        return lambda d: d.decode_16bit_float()

    @staticmethod
    def parse_32bit_float():
        return lambda d: d.decode_32bit_float()

    @staticmethod
    def parse_64bit_float():
        return lambda d: d.decode_64bit_float()


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
    clean_format = data_type.replace(" ", "").strip("-").lower()

    uint8 = {"u8", "ui8", "uint8"}
    uint16 = {"u16", "ui16", "uint", "word", "uint16", "s16", "short"}
    uint32 = {"ui32", "u32", "uint32", "dword", "ul32", "ulong"}
    uint64 = {"uint64", "u64", "ui64", "ulong64", "ulonglong"}
    int8 = {"int8", "i8", "integer8"}
    int16 = {"int", "i16", "int16", "int16bit", "integer", "integer16"}
    int32 = {"int32", "i32", "integer32", "l32", "long", "long32", "li32"}
    int64 = {"int64", "i64", "integer64", "longlong", "longint64"}
    float16 = {"float16", "f16", "fp16", "half"}
    float32 = {"f32", "fp32", "float", "float32", "real", "single"}
    float64 = {"f64", "fp64", "float64", "lreal", "double"}
    bits = {"bit", "bits", "b"}

    if clean_format in uint8:
        data_type = "uint8"
    elif clean_format in uint16:
        data_type = "uint16"
    elif clean_format in uint32:
        data_type = "uint32"
    elif clean_format in uint64:
        data_type = "uint64"
    elif clean_format in int8:
        data_type = "int8"
    elif clean_format in int16:
        data_type = "int16"
    elif clean_format in int32:
        data_type = "int32"
    elif clean_format in int64:
        data_type = "int64"
    elif clean_format in float16:
        data_type = "float16"
    elif clean_format in float32:
        data_type = "float32"
    elif clean_format in float64:
        data_type = "float64"
    elif clean_format in bits:
        data_type = "bits"
    else:
        raise ValueError(f"Unsupported type: {data_type}")

    return data_type


def is_weekday_interval():
    current_datetime = timezone.now()
    return (
        current_datetime.time() > ON_PEAK_TIME_START
        and current_datetime.time() < ON_PEAK_TIME_END
    )


def map_registers_to_model(register_blocks, model):
    mapping = {
        block["register_name"]: block["model_attribute"] for block in register_blocks
    }
    setattr(model, "register_mapping", mapping)
