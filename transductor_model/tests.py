from django.test import TestCase
from .models import TransductorModel
from django.db import IntegrityError


class TransductorModelTestCase(TestCase):

    def setUp(self):
        self.transductor_example = TransductorModel.objects.create(
            name='TR 4020',
            transport_protocol='UDP',
            serial_protocol='ModbusRTU',
            register_addresses=[[68, 0], [70, 1]],
        )

    def test_create_transductor_model(self):
        transductor_model = TransductorModel()
        transductor_model.name = 'transductor_example_1'
        transductor_model.transport_protocol = 'UDP'
        transductor_model.serial_protocol = 'ModbusRTU'
        transductor_model.register_addresses = [[68, 0], [70, 1]]

        self.assertEqual(None, transductor_model.save())

    def test_not_create_transductor_model(self):
        transductor_model = TransductorModel()
        transductor_model.name = 'TR 4020'
        transductor_model.transport_protocol = 'UDP'
        transductor_model.serial_protocol = 'ModbusRTU'
        transductor_model.register_addresses = [[68, 0], [70, 1]]

        self.assertRaises(IntegrityError, transductor_model.save)

    def test_retrieve_transductor_model(self):
        pass


    def test_not_retrieve_transductor_model(self):
        pass


    def test_update_transductor_model(self):
        pass


    def test_not_update_transductor_model(self):
        pass


    def test_delete_transductor_model(self):
        pass


    def test_not_delete_transductor_model(self):
        pass
