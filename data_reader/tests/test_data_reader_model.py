import mock
import socket

from django.test import TestCase
from threading import Thread

from transductor.models import *
from data_reader.exceptions import *
from data_reader.utils import *
from data_reader.communication import *
from data_reader.transport import *


class TestDataReaderModels(TestCase):
    def setUp(self):
        HOST, PORT = "localhost", 9999

        self.t_model = TransductorModel.objects.create(
            name="TR4020",
            transport_protocol="UdpProtocol",
            serial_protocol="ModbusRTU",
            minutely_register_addresses=[
                [10, 1], [11, 1], [14, 1], [15, 1], [16, 1], [17, 1], [66, 2],
                [68, 2], [70, 2], [72, 2], [74, 2], [76, 2], [78, 2], [80, 2],
                [82, 2], [84, 2], [86, 2], [88, 2], [90, 2], [92, 2], [94, 2],
                [96, 2], [98, 2], [100, 2], [102, 2], [104, 2], [106, 2],
                [108, 2], [110, 2], [112, 2], [114, 2], [116, 2], [118, 2],
                [120, 2], [122, 2], [132, 2], [134, 2], [136, 2], [138, 2]
            ],
            quarterly_register_addresses=[
                [10, 1], [11, 1], [14, 1], [15, 1], [16, 1], [17, 1], [264, 2],
                [266, 2], [270, 2], [272, 2], [276, 2], [278, 2], [282, 2],
                [284, 2]
            ],
            monthly_register_addresses=[
                [10, 1], [11, 1], [14, 1], [15, 1], [16, 1], [17, 1],
                [156, 2], [158, 2], [162, 2], [164, 2], [168, 2], [170, 2],
                [174, 2], [176, 2], [180, 2], [182, 2], [186, 2], [188, 2],
                [420, 2], [422, 2], [424, 2], [426, 2], [428, 2], [430, 2],
                [432, 2], [434, 2], [444, 2], [446, 2], [448, 2], [450, 2],
                [452, 2], [454, 2], [456, 2], [458, 2], [516, 1], [517, 1],
                [518, 1], [519, 1], [520, 1], [521, 1], [522, 1], [523, 1],
                [524, 1], [525, 1], [526, 1], [527, 1], [528, 1], [529, 1],
                [530, 1], [531, 1], [540, 1], [541, 1], [542, 1], [543, 1],
                [544, 1], [545, 1], [546, 1], [547, 1], [548, 1], [549, 1],
                [550, 1], [551, 1], [552, 1], [553, 1], [554, 1], [555, 1]
            ]
        )

        self.transductor = EnergyTransductor.objects.create(
            model=self.t_model,
            serial_number="12345678",
            ip_address=HOST
        )

        self.modbus_rtu = ModbusRTU(self.transductor)
        self.udp_protocol = UdpProtocol(
            serial_protocol=self.modbus_rtu,
            timeout=0.5,
            port=PORT
        )

    '''
    SerialProtocol and TransportProtocol Tests
    '''

    def test_abstract_methods_from_serial_protocol(self):
        self.assertEqual(
            None,
            SerialProtocol.create_messages(self.modbus_rtu)
        )
        self.assertEqual(
            None,
            SerialProtocol.get_measurement_value_from_response(
                self.modbus_rtu, 'any message'
            )
        )
        self.assertEqual(
            None,
            SerialProtocol.check_all_messages_crc(
                self.modbus_rtu, 'any messages'
            )
        )

    def test_abstract_methods_from_transport_protocol(self):
        self.assertEqual(
            None,
            TransportProtocol.start_communication(self.udp_protocol)
        )
    '''
    ModbusRTU Tests
    '''

    def test_create_messages(self):
        messages = self.modbus_rtu.create_messages(
            [[4, 1], [68, 2]]
        )

        int_message = messages[0]

        float_message = messages[1]

        self.assertEqual(b'\x01\x03\x00\x04\x00\x01\xc5\xcb', int_message)
        self.assertEqual(b'\x01\x03\x00D\x00\x02\x84\x1e', float_message)

    def test_unpack_int_response(self):
        response = b'\x01\x03\x02\x00\xdc\xb9\xdd'[3:-2]

        int_value = self.modbus_rtu._unpack_int_response(2, response)

        self.assertEqual(int_value, 220)

    def test_unpack_float_response(self):
        response_1 = b'\x01\x03\x04_pC\\\xd8\xf5'[3:-2]
        response_2 = b'\x01\x03\x04dIC\\\x05\xdc'[3:-2]
        response_3 = b'\x01\x03\x04\xa3BCY\x89i'[3:-2]

        float_value_1 = self.modbus_rtu \
                            ._unpack_float_response(4, response_1)
        float_value_2 = self.modbus_rtu \
                            ._unpack_float_response(4, response_2)
        float_value_3 = self.modbus_rtu \
                            ._unpack_float_response(4, response_3)

        self.assertAlmostEqual(
            float_value_1, 220.372802734375, places=7, msg=None, delta=None
        )
        self.assertAlmostEqual(
            float_value_2, 220.39173889160156, places=7, msg=None, delta=None
        )
        self.assertAlmostEqual(
            float_value_3, 217.63772583007812, places=7, msg=None, delta=None
        )

    def test_check_all_messages_crc(self):
        response_1 = b'\x01\x03\x00\x04\x00\x01\xc5\xcb'
        response_2 = b'\x01\x03\x04_pC\\\xd8\xf5'
        response_3 = b'\x01\x03\x04dIC\\\x05\xdc'
        response_4 = b'\x01\x03\x04\xa3BCY\x89i'

        messages = [response_1, response_2, response_3, response_4]

        self.assertTrue(self.modbus_rtu.check_all_messages_crc(messages))

    def test_check_all_messages_crc_with_invalid_crc(self):
        response_1 = b'\x01\x03\x00\x04\x00\x01\xc5\xcb'
        wrong_response_2 = b'\x01\x03\x04_pC\\\x00\x00'
        response_3 = b'\x01\x03\x04dIC\\\x05\xdc'
        response_4 = b'\x01\x03\x04\xa3BCY\x89i'

        messages = [response_1, wrong_response_2, response_3, response_4]

        with self.assertRaises(CRCInvalidException):
            self.modbus_rtu.check_all_messages_crc(messages)

    def test_check_crc_right_response(self):
        response_1 = '\x01\x03\x04\x16@D\xa6L\xd5'
        response_2 = '\x01\x03\x04\x10OC\xb9?\xa6'
        response_3 = '\x01\x03\x04jUD\xe1\x04\xb3'

        self.assertEqual(True, self.modbus_rtu._check_crc(response_1))
        self.assertEqual(True, self.modbus_rtu._check_crc(response_2))
        self.assertEqual(True, self.modbus_rtu._check_crc(response_3))

    def test_check_crc_wrong_response(self):
        response_1 = '\x01\x03\x04\x16@D\xa6L\xd4'
        response_2 = '\x01\x03\x04\x10OC\xb9?\xa5'
        response_3 = '\x01\x03\x04jUD\xe1\x04\xb2'

        self.assertEqual(False, self.modbus_rtu._check_crc(response_1))
        self.assertEqual(False, self.modbus_rtu._check_crc(response_2))
        self.assertEqual(False, self.modbus_rtu._check_crc(response_3))
