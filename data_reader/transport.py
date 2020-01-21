import importlib
import socket

from abc import ABCMeta, abstractmethod

from .exceptions import NumberOfAttempsReachedException, \
    CRCInvalidException


class TransportProtocol(metaclass=ABCMeta):
    """
    Base class for transport protocols.

    Attributes:
        serial_protocol (SerialProtocol): The serial protocol
        used in communication.
        transductor (Transductor): The transductor which will
        hold communication.
        timeout (float): The serial port used by the transductor.
        port (int): The port used to communication.
        socket (socket._socketobject): The socket used in communication.
    """

    def __init__(self, serial_protocol, timeout=2, port=1001):
        self.serial_protocol = serial_protocol
        self.transductor = serial_protocol.transductor
        self.timeout = timeout
        self.port = port
        self.socket = None

    def send_messages(self, messages):
        response_messages = []
        self.open_socket()
        for message in messages:
            response_messages.append(self.send_message(message))
        self.socket.close()
        return response_messages

    @abstractmethod
    def send_message(self, message):
        pass

    @abstractmethod
    def open_socket(self):
        pass


class UdpProtocol(TransportProtocol):
    """
    Class responsible to represent a UDP protocol and handle all
    the communication.

    Attributes:
        receive_attemps (int): Total attempts to receive a message
        via socket UDP.
        max_receive_attempts (int): Maximum number of attemps to
        receive message via socket UDP.
    """

    def open_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(self.timeout)
        self.receive_attempts = 0
        self.max_receive_attempts = 3

    def send_messages(self, messages):
        response_messages = []
        self.open_socket()
        for message in messages:
            response_messages.append(self.send_message(message))
        return response_messages

    def send_message(self, message):
        receive_attemps = 0
        crc_errors = 0
        received_message = None
        while(
            not received_message and (
                receive_attemps < self.max_receive_attempts
            )
        ):
            self.socket.sendto(
                message,
                (self.transductor.ip_address, self.port)
            )
            try:
                received_message = self.socket.recvfrom(256)
                self.serial_protocol._check_crc(received_message[0])
            except socket.timeout:
                receive_attemps += 1
                if(receive_attemps == self.max_receive_attempts):
                    raise NumberOfAttempsReachedException(
                        "Maximum attempts reached!")
                    self.transductor.set_broken(True)
                    self.transductor.save()
                pass
            except CRCInvalidException as e:
                crc_errors += 1
                if(crc_errors == self.max_receive_attempts):
                    self.socket.close()
                    raise e
        return received_message[0]


class TcpProtocol(TransportProtocol):

    def open_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(1)
        self.socket.connect((self.transductor.ip_address, 1001))

    def send_message(self, message):
        self.socket.send(message)
        received_message = self.socket.recvfrom(1024)
        return received_message[0]
