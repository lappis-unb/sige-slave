import os


def populate():
    print('Populating database')
    print('-------------------\n')
    add_transductor_model()
    add_transductor()
    print('Finished database seed')


def add_transductor_model():
    print('Creating TR4020 transductor model')

    name = 'TR4020'
    transport_protocol = 'UdpProtocol'
    serial_protocol = 'ModbusRTU'
    minutely_register_addresses = [
        [10, 1], [11, 1], [14, 1], [15, 1], [16, 1], [17, 1], [66, 2],
        [68, 2], [70, 2], [72, 2], [74, 2], [76, 2], [78, 2], [80, 2],
        [82, 2], [84, 2], [86, 2], [88, 2], [90, 2], [92, 2], [94, 2],
        [96, 2], [98, 2], [100, 2], [102, 2], [104, 2], [106, 2], [108, 2],
        [110, 2], [112, 2], [114, 2], [116, 2], [118, 2], [120, 2], [122, 2],
        [132, 2], [134, 2], [136, 2], [138, 2]
    ]
    quarterly_register_addresses = [
        [10, 1], [11, 1], [14, 1], [15, 1], [16, 1], [17, 1], [264, 2],
        [266, 2], [270, 2], [272, 2], [276, 2], [278, 2], [282, 2], [284, 2]
    ]
    monthly_register_addresses = [
        [10, 1], [11, 1], [14, 1], [15, 1], [16, 1], [17, 1], [156, 2],
        [158, 2], [162, 2], [164, 2], [168, 2], [170, 2], [174, 2], [176, 2],
        [180, 2], [182, 2], [186, 2], [188, 2], [420, 2], [422, 2], [424, 2],
        [426, 2], [428, 2], [430, 2], [432, 2], [434, 2], [444, 2], [446, 2],
        [448, 2], [450, 2], [452, 2], [454, 2], [456, 2], [458, 2], [516, 4],
        [520, 4], [524, 4], [528, 4], [540, 4], [544, 4], [548, 4], [552, 4]
    ]

    model, created = TransductorModel.objects.get_or_create(
        name=name,
        transport_protocol=transport_protocol,
        serial_protocol=serial_protocol,
        minutely_register_addresses=minutely_register_addresses,
        quarterly_register_addresses=quarterly_register_addresses,
        monthly_register_addresses=monthly_register_addresses
    )

    if created:
        print('Created TR4020')
    else:
        print('Transductor Model already existed')


def add_transductor():
    print('Creating transductor #1')
    transductor, created = EnergyTransductor.objects.get_or_create(
        serial_number='12345',
        ip_address='164.41.86.42',
        broken=False,
        active=True,
        model=TransductorModel.objects.get(name='TR4020'),
        firmware_version='12.1.3215',
        physical_location='Faculdade do gama prédio UED',
        geolocation_longitude=-15.989753,
        geolocation_latitude=-48.04542
    )

    if created:
        print('Created transductor #1')
    else:
        print('Transductor #1 already existed')

    print('Creating transductor #2')
    transductor2, created2 = EnergyTransductor.objects.get_or_create(
        serial_number='54321',
        ip_address='164.41.86.43',
        broken=False,
        active=True,
        model=TransductorModel.objects.get(name='TR4020'),
        firmware_version='12.1.3215',
        physical_location='Faculdade do gama prédio UED',
        geolocation_longitude=15.989533,
        geolocation_latitude=-48.04567
    )

    if created2:
        print('Created transductor #2')
    else:
        print('Transductor #2 already existed')


if __name__ == '__main__':
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smi.settings')
    django.setup()

    from transductor.models import EnergyTransductor
    from transductor_model.models import TransductorModel

    populate()

    print('Finished populating DB. YAY')
    print('-------------------\n')
