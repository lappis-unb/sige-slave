import importlib
import socket
import struct
import sys
import socket

result = []
hexa = []

for x in range(960, 1080, 2):
    registers = [[x,1]]

    messages_to_send = []

    int_addr = 0
    float_addr = 1
    address_value = 0
    address_type = 1
    for register in registers:
        if register[address_type] == int_addr:
            packaged_message = struct.pack(
                                   "2B", 0x01, 0x03
                               ) + \
                               struct.pack(
                                   ">2H", register[address_value], 1
                               )
        elif register[address_type] == float_addr:
            packaged_message = struct.pack(
                                   "2B", 0x01, 0x03
                               ) + \
                               struct.pack(
                                   ">2H", register[address_value], 2
                               )
        else:
            raise RegisterAddressException("Wrong register address type.")

        crc = 0xFFFF
        for index, item in enumerate((packaged_message)):
            next_byte = item
            crc ^= next_byte
            for i in range(8):
                lsb = crc & 1
                crc >>= 1
                if lsb:
                    crc ^= 0xA001

        crc = struct.pack("<H", crc)
        packaged_message = packaged_message + crc
        messages_to_send.append(packaged_message)
    
    UDP_IP = "164.41.86.43"
    UDP_PORT = 1001

    print(messages_to_send)
    
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.sendto(messages_to_send[0], (UDP_IP, UDP_PORT))

    try:
        message_received = sock.recvfrom(256)
    except socket.timeout:
        raise


    new_fucking_message = message_received[0]
    
    hexa.append(new_fucking_message)
    print("New Fucking Message: ",new_fucking_message)


    for x in new_fucking_message:
        print(x)


    n_bytes = new_fucking_message[2]
    print("nbytes: ",n_bytes)
    msg = bytearray(new_fucking_message[3:-2])
    print("MSG: ", msg)
    # byte_range = bytearray(message_received[0])
    # if n_bytes == 2:
    #     return self._unpack_int_response(n_bytes, msg)
    # else:

    # new_message = bytearray()

    # for i in range(0, n_bytes, 2):
    #     if sys.byteorder == "little":
    #         msb = msg[i]
    #         new_message.append(msg[i + 1])
    #         new_message.append(msb)

    # value = struct.unpack("1f", message_received[0])

    # byte_range = bytearray()
    # date_header, timestamp = struct.unpack('>BL', byte_range)

    new_message = bytearray()


    if n_bytes == 2:
        for i in range(0, n_bytes, 2):
            if sys.byteorder == "little":
                msb = msg[i]
                new_message.append(msg[i + 1])
                new_message.append(msb)
        value = struct.unpack("1h", new_message)[0]
    else:
        for i in range(0, n_bytes, 4):
            if sys.byteorder == "little":
                msb = msg[i]
                new_message.append(msg[i + 1])
                new_message.append(msb)
                msb = msg[i + 2]
                new_message.append(msg[i + 3])
                new_message.append(msb)
        value = struct.unpack("1f", new_message)[0]
        print("new message: ", new_message)

    result.append(value)
print(hexa)
print(result)