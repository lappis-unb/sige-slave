from django.test import TestCase
from transductor_model.models import TransductorModel
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.test import APIRequestFactory
from django.db.utils import DataError
import pytest
from django.conf import settings


class TransductorModelTestCase(TestCase):

    def setUp(self):
        self.first_transductor = TransductorModel.objects.create(
            model_code='987654321',
            name='TR4020',
            transport_protocol='UDP',
            serial_protocol='ModbusRTU',
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

        self.second_transductor = TransductorModel.objects.create(
            model_code='123456789',
            name='TR4030',
            transport_protocol='UDP',
            serial_protocol='ModbusRTU',
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

    def test_create_transductor_model(self):

        transductor_model = TransductorModel()
        transductor_model.model_code = '999999999'
        transductor_model.name = 'transductor_example_1'
        transductor_model.transport_protocol = 'UDP'
        transductor_model.serial_protocol = 'ModbusRTU'
        transductor_model.minutely_register_addresses = [
            [10, 1], [11, 1], [14, 1], [15, 1], [16, 1], [17, 1], [66, 2],
            [68, 2], [70, 2], [72, 2], [74, 2], [76, 2], [78, 2], [80, 2],
            [82, 2], [84, 2], [86, 2], [88, 2], [90, 2], [92, 2], [94, 2],
            [96, 2], [98, 2], [100, 2], [102, 2], [104, 2], [106, 2],
            [108, 2], [110, 2], [112, 2], [114, 2], [116, 2], [118, 2],
            [120, 2], [122, 2], [132, 2], [134, 2], [136, 2], [138, 2]
        ]
        transductor_model.quarterly_register_addresses = [
            [10, 1], [11, 1], [14, 1], [15, 1], [16, 1], [17, 1], [264, 2],
            [266, 2], [270, 2], [272, 2], [276, 2], [278, 2], [282, 2],
            [284, 2]
        ]
        transductor_model.monthly_register_addresses = [
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

        self.assertIsNone(transductor_model.save())

    def test_not_create_transductor_model(self):
        transductor_model = TransductorModel()
        transductor_model.model_code = '987654321'
        transductor_model.name = 'TR4040'
        transductor_model.transport_protocol = 'UDP'
        transductor_model.serial_protocol = 'ModbusRTU'
        transductor_model.minutely_register_addresses = [
            [10, 1], [11, 1], [14, 1], [15, 1], [16, 1], [17, 1], [66, 2],
            [68, 2], [70, 2], [72, 2], [74, 2], [76, 2], [78, 2], [80, 2],
            [82, 2], [84, 2], [86, 2], [88, 2], [90, 2], [92, 2], [94, 2],
            [96, 2], [98, 2], [100, 2], [102, 2], [104, 2], [106, 2],
            [108, 2], [110, 2], [112, 2], [114, 2], [116, 2], [118, 2],
            [120, 2], [122, 2], [132, 2], [134, 2], [136, 2], [138, 2]
        ]
        transductor_model.quarterly_register_addresses = [
            [10, 1], [11, 1], [14, 1], [15, 1], [16, 1], [17, 1], [264, 2],
            [266, 2], [270, 2], [272, 2], [276, 2], [278, 2], [282, 2],
            [284, 2]
        ]
        transductor_model.monthly_register_addresses = [
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

        with self.assertRaises(ValidationError):
            transductor_model.save()

    def test_retrieve_transductor_model(self):
        model_code = '987654321'
        t_model_retrieved = TransductorModel.objects.get(model_code=model_code)

        self.assertEqual(self.first_transductor, t_model_retrieved)

    def test_not_retrieve_transductor_model(self):
        wrong_model_code = '9'

        with self.assertRaises(TransductorModel.DoesNotExist):
            TransductorModel.objects.get(model_code=wrong_model_code)

    def test_update_transport_protocol_of_transductor_model(self):
        transductor_model = TransductorModel.objects.filter(
            model_code='987654321'
        )

        self.assertTrue(
            transductor_model.update(transport_protocol='TCP')
        )

    def test_update_serial_protocol_of_transductor_model(self):
        transductor_model = TransductorModel.objects.filter(
            model_code='987654321'
        )

        self.assertTrue(
            transductor_model.update(serial_protocol='I2C')
        )

    def test_update_minutely_register_address_of_transductor_model(self):
        transductor_model = TransductorModel.objects.filter(
            model_code='987654321'
        )

        self.assertTrue(
            transductor_model.update(
                minutely_register_addresses=[[54, 0], [60, 1]]
            )
        )

    def test_update_name_of_transductor_model(self):
        transductor_model = TransductorModel.objects.filter(
            model_code='987654321'
        )

        self.assertTrue(transductor_model.update(name='SP4000'))

    def test_not_update_with_invalid_name(self):
        transductor_model = TransductorModel.objects.filter(
            model_code='987654321'
        )

        with self.assertRaises(DataError):
            transductor_model.update(
                name='123456789101112131415161718192021222324252627282930')

    def test_update_with_valid_transport_protocol(self):
        transductor_model = TransductorModel.objects.filter(
            model_code='987654321'
        )

        self.assertTrue(transductor_model.update(transport_protocol='USB-C'))

    def test_not_update_with_invalid_serial_protocol(self):
        transductor_model = TransductorModel.objects.filter(
            model_code='987654321'
        )
        new_serial = '123456789101112131415161718192021222324252627282930'

        with self.assertRaises(DataError):
            transductor_model.update(
                transport_protocol=new_serial)

    def test_delete_transductor_model(self):
        size = len(TransductorModel.objects.all())
        transductor_model = TransductorModel.objects.filter(
            model_code='987654321'
        ).delete()

        self.assertEqual(size - 1, len(TransductorModel.objects.all()))

    def test_not_delete_transductor_model(self):
        original_size = len(TransductorModel.objects.all())
        transductor_model = TransductorModel.objects.filter(
            model_code='123456789'
        ).delete()
        new_size = len(TransductorModel.objects.all())

        self.assertEqual(original_size - 1, new_size)

        wrong_model_code = '123456789'

        with self.assertRaises(TransductorModel.DoesNotExist):
            TransductorModel.objects.get(model_code=wrong_model_code).delete()
