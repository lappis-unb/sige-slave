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
            register_addresses=[[4, 0], [68, 1]],
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

    # def test_raise_exception_on_create_messages_with_wrong_address(self):
    #     wrong_address = [[4, 2]]

    #     t_model = TransductorModel()
    #     t_model.name = "TestModel"
    #     t_model.transport_protocol = "UDP"
    #     t_model.serial_protocol = "Modbus RTU"
    #     t_model.register_addresses = wrong_address
    #     t_model.save()

    #     transductor = EnergyTransductor.objects.create(
    #         model=t_model,
    #         ip_address="2.2.2.2",
    #         serial_number="12345670"
    #     )

    #     modbus = ModbusRTU(transductor)

    #     with self.assertRaises(RegisterAddressException):
    #         modbus.create_messages()

    # @mock.patch.object(
    #     ModbusRTU, '_unpack_int_response',
    #     return_value=1, autospec=True)
    # @mock.patch.object(
    #     ModbusRTU, '_unpack_float_response',
    #     return_value=5.0, autospec=True)
    # def test_modbusrtu_get_measurement_value_from_response(
    #     self, float_mock_method, int_mock_method
    # ):
    #     int_response = b'\x01\x03\x02\x00\xdc\xb9\xdd'
    #     float_response = b'\x01\x03\x04_pC\\\xd8\xf5'

    #     int_value = self.modbus_rtu \
    #                     .get_measurement_value_from_response(int_response)
    #     self.assertEqual(1, int_value)

    #     float_value = self.modbus_rtu \
    #                       .get_measurement_value_from_response(float_response)
    #     self.assertEqual(5.0, float_value)

    # '''
    # DataCollector Tests
    # '''
    # @mock.patch.object(Thread, 'join', return_value=None)
    # @mock.patch.object(Thread, 'start', return_value=None)
    # @mock.patch.object(
    #     DataCollector, 'single_data_collection',
    #     return_value='any return', autospec=True)
    # def test_data_collector_perform_all_data_collection(
    #     self, mock_single_data_collection, mock_start, mock_join
    # ):
    #     data_collector = DataCollector()
    #     data_collector.perform_all_data_collection()

    #     self.assertTrue(mock_start.called)
    #     self.assertTrue(mock_join.called)

    # @mock.patch.object(
    #     UdpProtocol, 'start_communication',
    #     side_effect=NumberOfAttempsReachedException('Attempts Reached!'))
    # def test_single_data_collection_with_transductor_broken_receive_timeout(
    #     self, mock_start_communication
    # ):
    #     self.transductor.broken = True

    #     data_collector = DataCollector()
    #     data_collector.single_data_collection(self.transductor)

    #     self.assertTrue(mock_start_communication.called)

    # @mock.patch.object(
    #     EnergyTransductor, 'set_transductor_broken', return_value=None)
    # @mock.patch.object(
    #     UdpProtocol, 'start_communication',
    #     side_effect=NumberOfAttempsReachedException('Attempts Reached!'))
    # def test_single_data_collection_with_transductor_not_broken_timeout(
    #     self, mock_1, mock_2
    # ):
    #     self.transductor.broken = False

    #     data_collector = DataCollector()
    #     data_collector.single_data_collection(self.transductor)

    #     mock_1.assert_called_with()
    #     mock_2.assert_called_with(True)

    # @mock.patch.object(
    #     EnergyMeasurement, 'save_measurements', return_value=None)
    # @mock.patch.object(
    #     ModbusRTU, 'get_measurement_value_from_response', return_value=1)
    # @mock.patch.object(
    #     EnergyTransductor, 'set_transductor_broken', return_value=None)
    # @mock.patch.object(
    #     UdpProtocol, 'start_communication',
    #     return_value=['Message 1', 'Message 2'])
    # def test_single_data_collection_with_transductor_broken_not_timeout(
    #     self, mock_1, mock_2, mock_3, mock_4
    # ):
    #     self.transductor.broken = True

    #     data_collector = DataCollector()
    #     data_collector.single_data_collection(self.transductor)

    #     mock_1.assert_called_with()
    #     mock_2.assert_called_with(False)

    #     calls = [mock.call('Message 1'), mock.call('Message 2')]
    #     mock_3.assert_has_calls(calls)

    #     mock_4.assert_called_with([1, 1])

    # @mock.patch.object(
    #     EnergyMeasurement, 'save_measurements', return_value=None)
    # @mock.patch.object(
    #     ModbusRTU, 'get_measurement_value_from_response', return_value=1)
    # @mock.patch.object(
    #     UdpProtocol, 'start_communication',
    #     return_value=['Message 1', 'Message 2'])
    # def test_single_data_collection_with_transductor_broken_and_not_timeout(
    #     self, mock_1, mock_2, mock_3
    # ):
    #     data_collector = DataCollector()
    #     data_collector.single_data_collection(self.transductor)

    #     mock_1.assert_called_with()

    #     calls = [mock.call('Message 1'), mock.call('Message 2')]
    #     mock_2.assert_has_calls(calls)

    #     mock_3.assert_called_with([1, 1])

    # '''
    # UdpProtocol Tests
    # '''
    # def test_create_socket(self):
    #     self.assertEqual(socket.AF_INET, self.udp_protocol.socket.family)
    #     self.assertEqual(2050, self.udp_protocol.socket.type)
    #     self.assertEqual(0.5, self.udp_protocol.socket.gettimeout())

    # def test_reset_receive_attempts(self):
    #     self.udp_protocol.receive_attempts += 1
    #     self.assertEqual(1, self.udp_protocol.receive_attempts)

    #     self.udp_protocol.reset_receive_attempts()
    #     self.assertEqual(0, self.udp_protocol.receive_attempts)

    # def test_handle_messages_via_socket(self):
    #     socket.socket.send_to = mock.MagicMock()
    #     socket.socket.recvfrom = mock.MagicMock(
    #         side_effect=(['any recv 1'], ['any recv 2'])
    #     )

    #     request_1 = b'\x01\x03\x00\x04\x00\x01\xc5\xcb'
    #     request_2 = b'\x01\x03\x00D\x00\x02\x84\x1e'

    #     messages_to_send = [
    #         request_1,
    #         request_2
    #     ]

    #     messages = self.udp_protocol \
    #                    .handle_messages_via_socket(messages_to_send)

    #     self.assertEqual(
    #         ['any recv 1', 'any recv 2'],
    #         messages
    #     )

    # def test_handle_messages_via_socket_timeout(self):
    #     socket.socket.recvfrom = mock.MagicMock(side_effect=socket.timeout)

    #     int_request = b'\x01\x03\x00\x04\x00\x01\xc5\xcb'

    #     messages_to_send = [
    #         int_request,
    #     ]

    #     with self.assertRaises(socket.timeout):
    #         self.udp_protocol.handle_messages_via_socket(messages_to_send)

    # @mock.patch.object(
    #     ModbusRTU, 'check_all_messages_crc', return_value=True, autospec=True)
    # @mock.patch.object(
    #     UdpProtocol, 'handle_messages_via_socket',
    #     return_value='any return', autospec=True)
    # @mock.patch.object(
    #     ModbusRTU, 'create_messages', return_value='any messages')
    # @mock.patch.object(
    #     UdpProtocol, 'reset_receive_attempts', return_value=None)
    # def test_start_communication(
    #     self, mock_reset, mock_create_messages, mock_handle, mock_check
    # ):
    #     self.udp_protocol.receive_attempts = 0

    #     self.assertEqual(
    #         'any return',
    #         self.udp_protocol.start_communication()
    #     )

    # @mock.patch.object(
    #     ModbusRTU, 'check_all_messages_crc',
    #     side_effect=CRCInvalidException('CRC is wrong!'), autospec=True)
    # @mock.patch.object(
    #     UdpProtocol, 'handle_messages_via_socket',
    #     return_value='any return', autospec=True)
    # @mock.patch.object(
    #     ModbusRTU, 'create_messages', return_value='any messages')
    # @mock.patch.object(
    #     UdpProtocol, 'reset_receive_attempts', return_value=None)
    # def test_start_communication_crc_wrong(
    #     self, mock_reset, mock_create_messages, mock_handle, mock_check
    # ):
    #     self.udp_protocol.receive_attempts = 0

    #     with self.assertRaises(CRCInvalidException):
    #         self.udp_protocol.start_communication()

    # @mock.patch.object(
    #     UdpProtocol, 'handle_messages_via_socket',
    #     side_effect=socket.timeout, autospec=True)
    # @mock.patch.object(
    #     ModbusRTU, 'create_messages', return_value='any messages')
    # @mock.patch.object(
    #     UdpProtocol, 'reset_receive_attempts', return_value=None)
    # def test_start_communication_maximum_attempts_reached(
    #     self, mock_reset, mock_create_messages, mock_handle
    # ):
    #     self.udp_protocol.receive_attempts = 0

    #     with self.assertRaises(NumberOfAttempsReachedException):
    #         self.udp_protocol.start_communication()
