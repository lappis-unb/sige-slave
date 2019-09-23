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

    def __init__(self, serial_protocol, timeout, port):
        self.serial_protocol = serial_protocol
        self.transductor = serial_protocol.transductor
        self.timeout = timeout
        self.port = port
        self.socket = None

    @abstractmethod
    def send_messages(self, messages):
        """
        Abstract method responsible to start the communication with
        the transductor based on his transport protocol.
        """
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

    def __init__(self, serial_protocol, timeout=2, port=1001):
        super(UdpProtocol, self).__init__(serial_protocol, timeout, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.receive_attempts = 0
        self.max_receive_attempts = 3

    def send_messages(self, messages):
        response_messages = []
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
                pass
            except CRCInvalidException:
                crc_errors += 1
                if(crc_errors == self.max_receive_attempts):
                    raise

        return received_message[0]
