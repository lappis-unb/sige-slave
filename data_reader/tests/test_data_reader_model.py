import socket

from freezegun import freeze_time

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
            register_addresses=[[4, 1], [68, 2]],
        )

        self.transductor = EnergyTransductor.objects.create(
            model=self.t_model,
            serial_number="12345678",
            ip_address=HOST,
            firmware_version='12.1.3215',
            physical_location='predio 2 sala 44',
            geolocation_longitude=-24.4556,
            geolocation_latitude=-24.45996
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
        messages = self.modbus_rtu.create_messages()

        int_message = messages[0]

        float_message = messages[1]

        self.assertEqual(b'\x01\x03\x00\x04\x00\x01\xc5\xcb', int_message)
        self.assertEqual(b'\x01\x03\x00D\x00\x02\x84\x1e', float_message)

    def test_create_date_send_message(self):

        messsage_a = b'\x01\x10\x00\n\x00\x08\x10\x07'
        messsage_b = b'\xe3\x00\x02\x00$\x00\x02\x00'
        messsage_c = b'\x05\x00\x0e\x00\x00\x00\x00\xfc\x0e'

        with freeze_time("2019-02-05 14:00:00"):
            data_send = self.modbus_rtu.create_date_send_message()

        correct_messsage = messsage_a + messsage_b + messsage_c
        self.assertEqual(data_send[0], correct_messsage)

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
