import socket
import time
import struct

UDP_IP = "164.41.86.43"
UDP_PORT = 1001
MESSAGE = b'0x010300440008841E'

print("UDP target IP:", UDP_IP)
 
sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM,
                      socket.IPPROTO_UDP) # UDP
while True:
    b = sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

    message, addr = sock.recvfrom(256)
    print("sfsdafdsaf")
    print(message)

sock.close()
