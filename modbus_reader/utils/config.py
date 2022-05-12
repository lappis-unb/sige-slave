devices_config = {
    'MD30': {
        "protocol": 0,
        "max_reg_request": 100,
        "path_file_csv": "modbus_reader/maps/md30_tr4020.csv"
    },
    'TR4020': {
        "protocol": 0,
        "max_reg_request": 100,
        "path_file_csv": "modbus_reader/maps/md30_tr4020.csv"
    },
    'Konect': {
        "protocol": 0,
        "max_reg_request": 8,
        "path_file_csv": "modbus_reader/maps/md30_tr4020.csv"
    },
    'test': {
        "id": 1,
        "model": "MD30",
        "serial_number": "30000484",
        # "ip_address": "172.27.1.74",
        "ip_address": "172.27.1.75",
        "port": 1001,
        "slave_server": "http://sige.unb.br:443/slave/1/",
        "geolocation_latitude": -15.7729,
        "geolocation_longitude": -47.8659,
        "campus": "http://sige.unb.br:443/campi/1/",
        "firmware_version": "1.42",
        "name": "STI 1",
        "broken": "false",
        "active": "true",
        "protocol": 0,
        "max_reg_request": 100,
        "path_file_csv": "maps/md30_tr4020.csv",
    },
}
