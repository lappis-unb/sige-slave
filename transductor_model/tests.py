from django.test import TestCase
from .models import TransductorModel
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

class TransductorModelTestCase(TestCase):

    def setUp(self):
        self.transductor_model_example = TransductorModel.objects.create(
            name='TR4020',
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

        self.assertFalse(transductor_model.save())

    def test_not_create_transductor_model(self):
        transductor_model = TransductorModel()
        transductor_model.name = 'TR4020'
        transductor_model.transport_protocol = 'UDP'
        transductor_model.serial_protocol = 'ModbusRTU'
        transductor_model.register_addresses = [[68, 0], [70, 1]]

        self.assertRaises(IntegrityError, transductor_model.save)

    def test_retrieve_transductor_model(self):
        model_name = 'TR4020'
        t_model_retrieved = TransductorModel.objects.get(name=model_name)

        self.assertEqual(self.transductor_model_example, t_model_retrieved)

    def test_not_retrieve_transductor_model(self):
        wrong_model_name = 'TR 4020'

        with self.assertRaises(TransductorModel.DoesNotExist):
            TransductorModel.objects.get(name=wrong_model_name)

    def test_update_transport_protocol_of_transductor_model(self):
        transductor_model = TransductorModel.objects.filter(name='TR4020')

        self.assertTrue(
            transductor_model.update(transport_protocol='TCP')
        )

    def test_update_serial_protocol_of_transductor_model(self):
        transductor_model = TransductorModel.objects.filter(name='TR4020')

        self.assertTrue(
            transductor_model.update(serial_protocol='I2C')
        )

    def test_update_register_address_of_transductor_model(self):
        transductor_model = TransductorModel.objects.filter(name='TR4020')

        self.assertTrue(
            transductor_model.update(register_addresses=[[54, 0],[60, 1]])
        )

    def test_update_name_of_transductor_model(self):
        transductor_model = TransductorModel.objects.filter(name='TR4020')

        self.assertTrue(transductor_model.update(name='SP4000'))

    def test_not_update_transductor_model(self):
        pass


    def test_delete_transductor_model(self):
        pass


    def test_not_delete_transductor_model(self):
        pass
