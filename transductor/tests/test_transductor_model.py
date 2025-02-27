from datetime import datetime

from django.db import IntegrityError
from django.db.utils import DataError
from django.test import TestCase

from events.models import FailedConnectionTransductorEvent
from measurement.models import (
    MinutelyMeasurement,
    MonthlyMeasurement,
    QuarterlyMeasurement,
)
from transductor.models import Transductor
from data_collector.models import MemoryMap
from transductor.validators import validate_csv_file
from rest_framework import serializers


class TransductorTestCase(TestCase):
    def setUp(self):
        minutely = [
                {
                    "size": 6,
                    "type": "float32",
                    "function": "read_input_register",
                    "byteorder": "f2_f1_f0_exp",
                    "attributes": [
                        "voltage_a",
                        "voltage_b",
                        "voltage_c"
                    ],
                    "start_address": 10
                }
        ]
        quarterly = [
            {
                    "size": 8,
                    "type": "float32",
                    "function": "read_input_register",
                    "byteorder": "f2_f1_f0_exp",
                    "attributes": [
                        "active_consumption",
                        "reactive_inductive",
                        "active_generated",
                        "reactive_capacitive"
                    ],
                    "start_address": 200
                }
        ]
        monthly = [
                {
                    "size": 8,
                    "type": "float32",
                    "function": "read_input_register",
                    "byteorder": "f2_f1_f0_exp",
                    "attributes": [
                        "active_consumption",
                        "reactive_inductive",
                        "active_generated",
                        "reactive_capacitive"
                    ],
                    "start_address": 200
                }
        ]

        self.memory_map = MemoryMap.objects.create(
            id=1,
            model_transductor='TR4020',
            minutely=minutely,
            quarterly=quarterly,
            monthly=monthly
        )

        self.transductor = Transductor.objects.create(
            id=1,
            serial_number="87654321",
            ip_address="192.168.10.3",
            port='1234',
            broken=False,
            active=True,
            model="Transductor",
            firmware_version="12.1.3215",
            physical_location="predio 2 sala 44",
            geolocation_longitude=-24.4556,
            geolocation_latitude=-24.45996,
            installation_date=datetime.now(),
            memory_map=self.memory_map
        )

    def test_str_method(self):
        transductor = Transductor(
            id=1,
            serial_number="12345678",
            ip_address="192.168.10.3",
            port='1234',
            broken=False,
            active=True,
            model="Transductor",
            firmware_version="12.1.3215",
            physical_location="predio 2 sala 44",
            geolocation_longitude=-24.4556,
            geolocation_latitude=-24.45996,
            installation_date=datetime.now(),
            memory_map=self.memory_map
        )
        self.assertEqual(str(transductor), "192.168.10.3 - Transductor")

    def test_set_broken_method(self):
            
            transductor = Transductor()
            id=1,
            serial_number="12345678",
            ip_address="192.168.10.1",
            port='1234',
            broken=False,
            active=True,
            model="Transductor",
            firmware_version="12.1.3215",
            physical_location="predio 2 sala 44",
            geolocation_longitude=-24.4556,
            geolocation_latitude=-24.45996,
            installation_date=datetime.now(),
            memory_map=self.memory_map
            transductor.set_broken(True)
            self.assertTrue(transductor.broken)
            
    def test_create_energy_transductor(self):
        size = len(Transductor.objects.all())

        energy_transductor = Transductor()
        energy_transductor.id = 1
        energy_transductor.memory_map = self.memory_map
        energy_transductor.port = '1234'
        energy_transductor.serial_number = "12345678"
        energy_transductor.ip_address = "1.1.1.1"
        energy_transductor.broken = False
        energy_transductor.active = True
        energy_transductor.model = "Transductor"
        energy_transductor.firmware_version = "12.1.3215"
        energy_transductor.physical_location = "predio 2 sala 44"
        energy_transductor.geolocation_longitude = -24.4556
        energy_transductor.geolocation_latitude = -24.45996
        energy_transductor.installation_date = datetime.now()

        self.assertIsNone(energy_transductor.save())
        self.assertEqual(size, len(Transductor.objects.all()))

    def test_not_create_energy_transductor_no_firmware(self):

        transductor = Transductor()
        transductor.serial_number = "123456789"
        transductor.ip_address = "1.1.1.1"
        transductor.broken = False
        transductor.active = True
        transductor.model = "Transductor"
        transductor.physical_location = "predio 2 sala 44"
        transductor.geolocation_longitude = -24.4556
        transductor.geolocation_latitude = -24.45996
        transductor.installation_date = datetime.now()

        with self.assertRaises(DataError):
            transductor.save()

    def test_not_create_energy_transductor_no_geolocation_latitude(self):

        transductor = Transductor()
        transductor.serial_number = "123456789"
        transductor.ip_address = "1.1.1.1"
        transductor.broken = False
        transductor.active = True
        transductor.model = "Transductor"
        transductor.firmware_version = "12.1.3215"
        transductor.physical_location = "predio 2 sala 44"
        transductor.geolocation_longitude = -24.4556
        transductor.installation_date = datetime.now()

        with self.assertRaises(DataError):
            transductor.save()

    def test_not_create_energy_transductor_no_geolocation_longitude(self):

        transductor = Transductor()
        transductor.serial_number = "123456789"
        transductor.ip_address = "1.1.1.1"
        transductor.broken = False
        transductor.active = True
        transductor.model = "Transductor"
        transductor.firmware_version = "12.1.3215"
        transductor.physical_location = "predio 2 sala 44"
        transductor.geolocation_latitude = -24.4556
        transductor.installation_date = datetime.now()

        with self.assertRaises(DataError):
            transductor.save()

    def test_not_create_energy_transductor_wrong_serial_number(self):

        transductor = Transductor()
        transductor.serial_number = "123456789"
        transductor.ip_address = "1.1.1.1"
        transductor.broken = False
        transductor.active = True
        transductor.model = "Transductor"
        transductor.installation_date = datetime.now()

        with self.assertRaises(DataError):
            transductor.save()

    def test_not_create_energy_transductor_empty_serial_number(self):

        transductor = Transductor()
        transductor.serial_number = ""
        transductor.ip_address = "1.1.1.1"
        transductor.broken = False
        transductor.active = True
        transductor.model = "Transductor"
        transductor.installation_date = datetime.now()

        with self.assertRaises(IntegrityError):
            transductor.save()

    def test_not_create_energy_transductor_no_transductor_model(self):

        energy_transductor = Transductor()
        energy_transductor.serial_number = "12345678"
        energy_transductor.ip_address = ""
        energy_transductor.broken = False
        energy_transductor.active = True
        energy_transductor.installation_date = datetime.now()
        energy_transductor.serial_number = "12345677777"

        with self.assertRaises(DataError):
            energy_transductor.save()

    def test_update_transductor_ip_address(self):
        energy_transductor = Transductor.objects.get(serial_number="87654321")

        energy_transductor.ip_address = "111.111.111.111"

        self.assertIsNone(energy_transductor.save())

    def test_set_broken_method(self):
        self.transductor.broken = False

        # false to false
        self.assertFalse(self.transductor.set_broken(False))
        self.assertFalse(self.transductor.broken)

        qs = FailedConnectionTransductorEvent.objects.all()

        self.assertFalse(
            qs.exists(),
            msg="False to false must not create connection failure events",
        )

        self.assertFalse(
            self.transductor.timeintervals.exists(),
            msg="False to false must not create timeintervals",
        )

        # false to true
        self.assertTrue(self.transductor.set_broken(True))
        self.assertTrue(self.transductor.broken)

        qs = FailedConnectionTransductorEvent.objects.all()

        self.assertTrue(
            qs.exists(),
            msg=("Toggle broken attribute to True must create a " "FailedConnectionTransductorEvent"),
        )

        self.assertEqual(
            qs.count(),
            1,
            msg=("Toggle broken attribute to True must create only one " "FailedConnectionTransductorEvent"),
        )

        self.assertIsNone(
            qs.last().ended_at,
            msg=(
                "Toggle broken attribute to True must create a "
                "FailedConnectionTransductorEvent with ended_at attribute "
                "equals to None"
            ),
        )

        self.assertEqual(
            self.transductor.timeintervals.count(),
            1,
            msg=("Toggle broken attribute to True must create only one " "timeinterval"),
        )

        self.assertTrue(
            self.transductor.timeintervals.exists(),
            msg="Toggle broken attribute to True must create an timeinterval",
        )

        self.assertIsNone(
            self.transductor.timeintervals.last().end,
            msg=("Toggle broken attribute to True must create an timeinterval " "with end attribute equals to None"),
        )

        # true to true
        self.assertTrue(self.transductor.set_broken(True))
        self.assertTrue(self.transductor.broken)

        qs = FailedConnectionTransductorEvent.objects.all()

        self.assertEqual(
            qs.count(),
            1,
            msg=("True to True must not create a " "FailedConnectionTransductorEvent"),
        )

        self.assertEqual(
            self.transductor.timeintervals.count(),
            1,
            msg="True to True must not create a timeintervals",
        )

        self.assertIsNone(
            qs.last().ended_at,
            msg=("True to True must not modify the ended_at attribute of " "FailedConnectionTransductorEvent"),
        )

        self.assertIsNone(
            self.transductor.timeintervals.last().end,
            msg=("True to True must not modify the end attribute of " "timeinterval"),
        )

        # true to false
        self.assertFalse(self.transductor.set_broken(False))
        self.assertFalse(self.transductor.broken)

        qs = FailedConnectionTransductorEvent.objects.all()

        self.assertEqual(
            qs.count(),
            1,
            msg=(
                "Toggle broken attribute to False must create must not modify "
                "the number of FailedConnectionTransductorEvent"
            ),
        )

        self.assertEqual(
            self.transductor.timeintervals.count(),
            1,
            msg=("Toggle broken attribute to False must create must not modify " "the number of timeintervals"),
        )

        self.assertIsNotNone(
            qs.last().ended_at,
            msg=(
                "Toggle broken attribute to False must modify the ended_at "
                "attribute of an existing FailedConnectionTransductorEvent"
            ),
        )

        self.assertIsNotNone(
            self.transductor.timeintervals.last().end,
            msg=("Toggle broken attribute to False must modify the end " "attribute of an existing timeinterval"),
        )

    def test_delete_transductor(self):
        size = len(Transductor.objects.all())
        Transductor.objects.get(serial_number="87654321").delete()

        self.assertEqual(size - 1, len(Transductor.objects.all()))

    def test_not_delete_nonexistent_transductor(self):
        size = len(Transductor.objects.all())
        transductor_serial = "87654321"

        Transductor.objects.get(serial_number=transductor_serial).delete()

        self.assertEqual(size - 1, len(Transductor.objects.all()))

        with self.assertRaises(Transductor.DoesNotExist):
            Transductor.objects.get(serial_number=transductor_serial).delete()

    def _set_measurements(self, energy_transductor):
        """
        Creates twelve measurements in three days, four in each day.
        """

        datetimes = [
            datetime(2019, 1, 1, 12, 00, 00, 188939),
            datetime(2019, 1, 1, 13, 00, 00, 188939),
            datetime(2019, 1, 1, 14, 00, 00, 188939),
            datetime(2019, 1, 1, 15, 00, 00, 188939),
            datetime(2019, 1, 2, 12, 00, 00, 188939),
            datetime(2019, 1, 2, 13, 00, 00, 188939),
            datetime(2019, 1, 2, 14, 00, 00, 188939),
            datetime(2019, 1, 2, 15, 00, 00, 188939),
            datetime(2019, 1, 3, 12, 00, 00, 188939),
            datetime(2019, 1, 3, 13, 00, 00, 188939),
            datetime(2019, 1, 3, 14, 00, 00, 188939),
            datetime(2019, 1, 3, 15, 00, 00, 188939),
        ]

        for date in datetimes:
            MinutelyMeasurement.objects.create(
                collection_date=date,
                slave_collection_date=date,
                transductor=energy_transductor,
            )

            QuarterlyMeasurement.objects.create(collection_date=date, transductor=energy_transductor)

            MonthlyMeasurement.objects.create(
                collection_date=date,
                transductor=energy_transductor,
                active_max_power_list_peak_time=[],
                active_max_power_list_off_peak_time=[],
                reactive_max_power_list_peak_time=[],
                reactive_max_power_list_off_peak_time=[],
            )

    def test_update_transductor(self):
        # Test updating a Transductor instance
        transductor = Transductor.objects.create(
            id=2,
            serial_number="32145678",
            ip_address="192.168.1.1",
            port=1234,
            model="TestModel",
            firmware_version="1.0",
            installation_date=datetime.now(),
            physical_location="Test Location",
            geolocation_longitude=0.0,
            geolocation_latitude=0.0,
            memory_map=MemoryMap.objects.create(id=2, model_transductor="TestMap", minutely=[], quarterly=[], monthly=[]),
        )
        transductor.serial_number = "67854321"
        transductor.save()
        updated_transductor = Transductor.objects.get(id=1)
        self.assertEqual(updated_transductor.serial_number, "87654321")

    def test_create_transductor(self):
        # Test creating a Transductor instance
        transductor = Transductor.objects.create(
            id=3,
            serial_number="12345678",
            ip_address="192.168.1.1",
            port=1234,
            model="TestModel",
            firmware_version="1.0",
            installation_date=datetime.now(),
            physical_location="Test Location",
            geolocation_longitude=0.0,
            geolocation_latitude=0.0,
            memory_map=MemoryMap.objects.create(id=2, model_transductor="TestMap", minutely=[], quarterly=[], monthly=[]),
        )
        self.assertEqual(transductor.serial_number, "12345678")

    def test_validate_empty_csv(self):
        csv_data = []
        with self.assertRaises(serializers.ValidationError):
            validate_csv_file(csv_data)

    def test_validate_duplicate_headers(self):
        csv_data = [{"header1": "value1", "header1": "value2"}]
        with self.assertRaises(serializers.ValidationError):
            validate_csv_file(csv_data)

    def test_validate_missing_headers(self):
        csv_data = [{"header1": "value1"}]
        with self.assertRaises(serializers.ValidationError):
            validate_csv_file(csv_data)

    def test_validate_null_value(self):
        csv_data = [{"header1": ""}]
        with self.assertRaises(serializers.ValidationError):
            validate_csv_file(csv_data)
        
    def test_validate_invalid_data_type(self):
        csv_data = [{"header1": "invalid_value"}]
        with self.assertRaises(serializers.ValidationError):
            validate_csv_file(csv_data)

    def test_validate_missing_value(self):
        csv_data = [{"header1": "value1", "header2": ""}]
        with self.assertRaises(serializers.ValidationError):
            validate_csv_file(csv_data)

    def test_validate_valid_csv(self):
        # Teste com um CSV válido
        csv_data = [
            {"header1": "value1", "header2": "value2"},
            {"header1": "value3", "header2": "value4"},
        ]
        with self.assertRaises(serializers.ValidationError) as context:
            validate_csv_file(csv_data)

        # Verificar se o código de erro está presente no detalhe da exceção
        self.assertEqual(context.exception.detail[0].code, 'csv_missing_headers')

    def test_validate_invalid_data_type_multiple_rows(self):
        # Teste com um valor inválido em um campo obrigatório em múltiplas linhas
        csv_data = [
            {"header1": "value1", "header2": "value2"},
            {"header1": "invalid_value", "header2": "value4"},
        ]
        with self.assertRaises(serializers.ValidationError):
            validate_csv_file(csv_data)

    def test_validate_invalid_data_type_single_row(self):
        # Teste com um valor inválido em um campo obrigatório em uma única linha
        csv_data = [{"header1": "value1", "header2": "invalid_value"}]
        with self.assertRaises(serializers.ValidationError):
            validate_csv_file(csv_data)

    def test_validate_missing_value_multiple_rows(self):
        # Teste com valor ausente em um campo obrigatório em múltiplas linhas
        csv_data = [
            {"header1": "value1", "header2": "value2"},
            {"header1": "", "header2": "value4"},
        ]
        with self.assertRaises(serializers.ValidationError):
            validate_csv_file(csv_data)

    def test_validate_missing_value_single_row(self):
        # Teste com valor ausente em um campo obrigatório em uma única linha
        csv_data = [{"header1": "value1", "header2": ""}]
        with self.assertRaises(serializers.ValidationError):
            validate_csv_file(csv_data)

    def test_validate_csv_with_extra_headers(self):
        # Teste com CSV contendo cabeçalhos extras não presentes no esquema
        csv_data = [
            {"header1": "value1", "header2": "value2", "extra_header": "extra_value"},
            {"header1": "value3", "header2": "value4", "extra_header": "extra_value"},
        ]
        with self.assertRaises(serializers.ValidationError):
            validate_csv_file(csv_data)

    def test_validate_csv_no_headers(self):
        csv_data = [{"field1": "value1", "field2": "value2"}]
        with self.assertRaises(serializers.ValidationError) as context:
            validate_csv_file(csv_data)

        self.assertEqual(context.exception.detail[0].code, 'csv_missing_headers')

    