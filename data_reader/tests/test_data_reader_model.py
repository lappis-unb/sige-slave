import pytest
from django.test import TestCase
from django.conf import settings
from django.db import IntegrityError
from django.db.utils import DataError
from transductor.models import EnergyTransductor
from measurement.models import MinutelyMeasurement
from measurement.models import QuarterlyMeasurement
from measurement.models import MonthlyMeasurement
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.utils import timezone
from data_reader.utils import *
from yaml.serializer import Serializer


class DataReaderTestCase(TestCase):
    def setUp(self):
        self.transductor = EnergyTransductor.objects.create(
            serial_number='8764321',
            ip_address='111.101.111.13',
            broken=False,
            active=True,
            model='TR4020',
            firmware_version='12.1.3217',
            physical_location='predio 2 sala 47',
            geolocation_longitude=-24.4558,
            geolocation_latitude=-24.45998,
            installation_date=datetime.now()
        )

    def test_byte_to_binary_conversion(self):
        from data_reader.communication import SerialProtocol

        self.assertEqual(SerialProtocol.bytes_to_binary(b'\x00'b'\x00'), '0')
        self.assertEqual(SerialProtocol.bytes_to_binary(b'\x01'), '1')
        self.assertEqual(SerialProtocol.bytes_to_binary(b'\x07'), '111')
        self.assertEqual(SerialProtocol.bytes_to_binary(b'\x04'b'\x07'),
                         '10000000111')

    def test_binary_to_byte_conversion(self):
        from data_reader.communication import SerialProtocol

        self.assertEqual(SerialProtocol.binary_to_bytes('0'), b'\x00')
        self.assertEqual(SerialProtocol.binary_to_bytes('1'), b'\x01')
        self.assertEqual(SerialProtocol.binary_to_bytes('111'), b'\x07')
        self.assertEqual(SerialProtocol.binary_to_bytes('10000000111'),
                         b'\x04'b'\x07')

    def test_unsigned_to_byte_conversion(self):
        from data_reader.communication import SerialProtocol

        self.assertEqual(SerialProtocol.unsigned_to_bytes(0), b'\x00')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(1), b'\x01')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(2), b'\x02')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(4), b'\x04')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(8), b'\x08')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(15), b'\x0f')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(16), b'\x10')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(31), b'\x1f')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(32), b'\x20')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(33), b'\x21')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(63), b'\x3f')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(64), b'\x40')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(81), b'\x51')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(100), b'\x64')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(127), b'\x7f')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(128), b'\x80')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(200), b'\xc8')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(241), b'\xf1')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(255), b'\xff')

    def test_byte_to_unsigned_conversion(self):
        from data_reader.communication import SerialProtocol

        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\x00'), 0)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\x01'), 1)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\x02'), 2)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\x04'), 4)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\x08'), 8)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\x0f'), 15)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\x10'), 16)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\x1f'), 31)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\x20'), 32)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\x21'), 33)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\x3f'), 63)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\x40'), 64)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\x51'), 81)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\x64'), 100)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\x7f'), 127)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\x80'), 128)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\xc8'), 200)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\xf1'), 241)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\xff'), 255)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\x01\x00'), 256)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\x02\x00'), 512)
        self.assertEqual(SerialProtocol.bytes_to_unsigned(b'\xff\xff'), 65535)

    def test_bytes_to_float_conversion(self):
        from data_reader.communication import SerialProtocol
        # The correct way is the following:
        # 3rdByte-4oByte-1oByte-2oByte
        # MSB...LSB
        self.assertAlmostEqual(
            SerialProtocol.bytes_to_float(b'\x40'b'\x49'b'\x0e'b'\x56'), 3.1415)
        self.assertAlmostEqual(
            SerialProtocol.bytes_to_float(b'\x3f'b'\x80'b'\x03'b'\x47'), 1.0001)
        self.assertAlmostEqual(
            SerialProtocol.bytes_to_float(b'\x41'b'\xda'b'\x0b'b'\x77'),
            27.25559806)
        self.assertAlmostEqual(
            SerialProtocol.bytes_to_float(b'\x3f'b'\x41'b'\x06'b'\x25'), .754)
        self.assertAlmostEqual(
            SerialProtocol.bytes_to_float(b'\x43'b'\x66'b'\x74'b'\xb6'),
            230.4559021)
        self.assertAlmostEqual(
            SerialProtocol.bytes_to_float(b'\x43'b'\x5c'b'\x00'b'\x00'),
            220)
        self.assertAlmostEqual(
            SerialProtocol.bytes_to_float(b'\x43'b'\x55'b'\x24'b'\x39'),
            213.1414948)
        self.assertAlmostEqual(
            SerialProtocol.bytes_to_float(b'\x42'b'\xdd'b'\xf6'b'\xf0'),
            110.9822998)

    def test_float_to_bytes_conversion(self):
        from data_reader.communication import SerialProtocol

        self.assertEqual(SerialProtocol.float_to_bytes(85.125),
                         b'\x42\xAA\x40\x00')
        self.assertEqual(SerialProtocol.float_to_bytes(3.1415),
                         b'\x40'b'\x49'b'\x0e'b'\x56')
        self.assertEqual(SerialProtocol.float_to_bytes(220),
                         b'\x43'b'\x5c'b'\x00'b'\x00')

    def test_bytes_to_timestamp(self):
        from data_reader.communication import SerialProtocol

        self.assertEqual(SerialProtocol.bytes_to_timestamp_to_datetime(
            SerialProtocol.unsigned_to_bytes(1580998727)),
            timezone.datetime(2020, 2, 6, 11, 18, 47))
        self.assertEqual(
            SerialProtocol.bytes_to_timestamp_to_datetime(b'\xff\xff'),
            timezone.datetime(1970, 1, 1, 15, 12, 15))

    def test_timestamp_to_bytes(self):
        from data_reader.communication import SerialProtocol

        self.assertEqual(SerialProtocol.datetime_to_timestamp_to_bytes(
            timezone.datetime(2020, 2, 6, 11, 18, 47)),
            SerialProtocol.unsigned_to_bytes(1580998727))

        self.assertEqual(SerialProtocol.datetime_to_timestamp_to_bytes(
            timezone.datetime(1970, 1, 1, 15, 12, 15)), b'\xff\xff')

    def test_create_messages(self):
        from data_reader.communication import Modbus
        from data_reader.communication import SerialProtocol
        m = ModbusTCP(self.transductor, EnergyTransductorModel)

        # Create reading message
        bytes = m.create_read_holding_registers_message([10, 1])
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[0]), b'\x01')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[1]), b'\x03')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[2]), b'\x00')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[3]), b'\x0a')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[4]), b'\x00')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[5]), b'\x01')

        bytes = m.create_read_holding_registers_message([65535, 63])
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[0]), b'\x01')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[1]), b'\x03')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[2]), b'\xff')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[3]), b'\xff')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[4]), b'\x00')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[5]), b'\x3f')

        bytes = m.create_read_holding_registers_message([255, 26])
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[0]), b'\x01')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[1]), b'\x03')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[2]), b'\x00')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[3]), b'\xff')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[4]), b'\x00')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[5]), b'\x1a')

        # Create preset multiple register messages
        bytes = m.create_preset_multiple_registers_message([[255, 1], 65535])
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[0]), b'\x01')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[1]), b'\x10')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[2]), b'\x00')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[3]), b'\xff')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[4]), b'\x00')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[5]), b'\x01')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[6]), b'\x02')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[7]), b'\xff')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[8]), b'\xff')

        bytes = m.create_preset_multiple_registers_message([[65535, 2], 63])
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[0]), b'\x01')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[1]), b'\x10')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[2]), b'\xff')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[3]), b'\xff')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[4]), b'\x00')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[5]), b'\x02')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[6]), b'\x04')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[7]), b'\x00')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[8]), b'\x00')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[9]), b'\x00')
        self.assertEqual(SerialProtocol.unsigned_to_bytes(bytes[10]), b'\x3f')
