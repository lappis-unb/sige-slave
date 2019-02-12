import pytest
from django.test import TestCase
from django.conf import settings
from django.db import IntegrityError
from django.db.utils import DataError
from transductor_model.models import TransductorModel
from transductor.models import EnergyTransductor
from measurement.models import EnergyMeasurement
from measurement.models import MinutelyMeasurement
from measurement.models import QuarterlyMeasurement
from measurement.models import MonthlyMeasurement
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime


class EnergyMeasurementTestCase(TestCase):

    def setUp(self):
        self.trans_model = TransductorModel.objects.create(
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
        self.transductor = EnergyTransductor.objects.create(
            serial_number='87654321',
            ip_address='111.111.111.11',
            broken=False,
            active=True,
            model=self.trans_model,
            firmware_version='12.1.3215',
            physical_location='predio 2 sala 44',
            geolocation_longitude=-24.4556,
            geolocation_latitude=-24.45996
        )
        self.energy_measurement = MinutelyMeasurement.objects.create(
            transductor=self.transductor,
            frequency_a=8,
            voltage_a=8,
            voltage_b=8,
            voltage_c=8,
            current_a=8,
            current_b=8,
            current_c=8,
            active_power_a=8,
            active_power_b=8,
            active_power_c=8,
            total_active_power=8,
            reactive_power_a=8,
            reactive_power_b=8,
            reactive_power_c=8,
            total_reactive_power=8,
            apparent_power_a=8,
            apparent_power_b=8,
            apparent_power_c=8,
            total_apparent_power=8,
            power_factor_a=8,
            power_factor_b=8,
            power_factor_c=8,
            total_power_factor=8,
            dht_voltage_a=8,
            dht_voltage_b=8,
            dht_voltage_c=8,
            dht_current_a=8,
            dht_current_b=8,
            dht_current_c=8,
        )

    '''
    MinutelyMeasurementTests
    '''

    def test_create_minutely_energy_measurement_with_defaults(self):
        size = len(MinutelyMeasurement.objects.all())

        minutely_en_measurement = MinutelyMeasurement()
        minutely_en_measurement.transductor = self.transductor

        self.assertIsNone(minutely_en_measurement.save())
        self.assertEqual(size + 1, len(MinutelyMeasurement.objects.all()))

    def test_create_minutely_energy_measurement(self):
        size = len(MinutelyMeasurement.objects.all())

        minutely_en_measurement = MinutelyMeasurement()
        minutely_en_measurement.transductor = self.transductor
        minutely_en_measurement.frequency_a = 666
        minutely_en_measurement.voltage_a = 666
        minutely_en_measurement.voltage_b = 666
        minutely_en_measurement.voltage_c = 666
        minutely_en_measurement.current_a = 666
        minutely_en_measurement.current_b = 666
        minutely_en_measurement.current_c = 666
        minutely_en_measurement.active_power_a = 666
        minutely_en_measurement.active_power_b = 666
        minutely_en_measurement.active_power_c = 666
        minutely_en_measurement.total_active_power = 666
        minutely_en_measurement.reactive_power_a = 666
        minutely_en_measurement.reactive_power_b = 666
        minutely_en_measurement.reactive_power_c = 666
        minutely_en_measurement.total_reactive_power = 666
        minutely_en_measurement.apparent_power_a = 666
        minutely_en_measurement.apparent_power_b = 666
        minutely_en_measurement.apparent_power_c = 666
        minutely_en_measurement.total_apparent_power = 666
        minutely_en_measurement.power_factor_a = 666
        minutely_en_measurement.power_factor_b = 666
        minutely_en_measurement.power_factor_c = 666
        minutely_en_measurement.total_power_factor = 666
        minutely_en_measurement.dht_voltage_a = 666
        minutely_en_measurement.dht_voltage_b = 666
        minutely_en_measurement.dht_voltage_c = 666
        minutely_en_measurement.dht_current_a = 666
        minutely_en_measurement.dht_current_b = 666
        minutely_en_measurement.dht_current_c = 666

        self.assertIsNone(minutely_en_measurement.save())
        self.assertEqual(size + 1, len(MinutelyMeasurement.objects.all()))

    def test_not_create_minutely_energy_measurement_empty_transductor(self):
        size = len(EnergyTransductor.objects.all())

        en_measurement = EnergyMeasurement()

        with self.assertRaises(IntegrityError):
            en_measurement.save()

    def test_update_minutely_energy_measurement(self):
        minutely_energy_measurement = MinutelyMeasurement()
        minutely_energy_measurement.transductor = \
            EnergyTransductor.objects.get(
                serial_number=87654321
            )
        minutely_energy_measurement.save()

        minutely_energy_measurement.total_power_factor = 100

        self.assertEquals(
            None,
            minutely_energy_measurement.save(
                update_fields=['total_power_factor']
            )
        )

        self.assertTrue(100, minutely_energy_measurement.total_power_factor)

    def test_delete_minutely_measurement(self):
        size = len(MinutelyMeasurement.objects.all())
        MinutelyMeasurement.objects.filter(total_power_factor='8').delete()

        self.assertEqual(size - 1, len(MinutelyMeasurement.objects.all()))

    def test_not_delete_inexistent_transductor_minutely_measures(self):
        size = len(MinutelyMeasurement.objects.all())
        value = '8'

        MinutelyMeasurement.objects.get(
            total_power_factor=8
        ).delete()

        self.assertEqual(size - 1, len(MinutelyMeasurement.objects.all()))

        with self.assertRaises(MinutelyMeasurement.DoesNotExist):
            MinutelyMeasurement.objects.get(
                total_power_factor=8
            ).delete()

    def test_save_measurements(self):
        before_count = EnergyMeasurement.objects.all().__len__()

        values_list = [2019, 2, 5, 14, 0, 0, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                       15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28,
                       29, 30, 31, 32, 33, 34, 35, 36, 37, 38]

        EnergyMeasurement.save_measurements(values_list, self.transductor)

        after_count = EnergyMeasurement.objects.all().__len__()

        self.assertEqual(after_count - 1, before_count)

        measurement = EnergyMeasurement.objects.last()

        hour_with_timezone = values_list[3] + 2

        self.assertEqual(measurement.collection_date.year, values_list[0])
        self.assertEqual(measurement.collection_date.month, values_list[1])
        self.assertEqual(measurement.collection_date.day, values_list[2])
        self.assertEqual(measurement.collection_date.hour, hour_with_timezone)
        self.assertEqual(measurement.collection_date.minute, values_list[4])
        self.assertEqual(measurement.collection_date.second, values_list[5])
        self.assertEqual(measurement.frequency_a, values_list[6])
        self.assertEqual(measurement.voltage_a, values_list[7])
        self.assertEqual(measurement.voltage_b, values_list[8])
        self.assertEqual(measurement.voltage_c, values_list[9])
        self.assertEqual(measurement.current_a, values_list[10])
        self.assertEqual(measurement.current_b, values_list[11])
        self.assertEqual(measurement.current_c, values_list[12])
        self.assertEqual(measurement.active_power_a, values_list[13])
        self.assertEqual(measurement.active_power_b, values_list[14])
        self.assertEqual(measurement.active_power_c, values_list[15])
        self.assertEqual(measurement.total_active_power, values_list[16])
        self.assertEqual(measurement.reactive_power_a, values_list[17])
        self.assertEqual(measurement.reactive_power_b, values_list[18])
        self.assertEqual(measurement.reactive_power_c, values_list[19])
        self.assertEqual(measurement.total_reactive_power, values_list[20])
        self.assertEqual(measurement.apparent_power_a, values_list[21])
        self.assertEqual(measurement.apparent_power_b, values_list[22])
        self.assertEqual(measurement.apparent_power_c, values_list[23])
        self.assertEqual(measurement.total_apparent_power, values_list[24])
        self.assertEqual(measurement.power_factor_a, values_list[25])
        self.assertEqual(measurement.power_factor_b, values_list[26])
        self.assertEqual(measurement.power_factor_c, values_list[27])
        self.assertEqual(measurement.total_power_factor, values_list[28])
        self.assertEqual(measurement.dht_voltage_a, values_list[29])
        self.assertEqual(measurement.dht_voltage_b, values_list[30])
        self.assertEqual(measurement.dht_voltage_c, values_list[31])
        self.assertEqual(measurement.dht_current_a, values_list[32])
        self.assertEqual(measurement.dht_current_b, values_list[33])
        self.assertEqual(measurement.dht_current_c, values_list[34])
        self.assertEqual(measurement.consumption_a, values_list[35])
        self.assertEqual(measurement.consumption_b, values_list[36])
        self.assertEqual(measurement.consumption_c, values_list[37])
        self.assertEqual(measurement.total_consumption, values_list[38])
