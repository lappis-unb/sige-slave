import os
import pickle
import socket
from abc import ABCMeta, abstractmethod
from typing import List, Optional

from retrying import retry

from .communication import SerialProtocol
from .exceptions import CRCInvalidException, NumberOfAttempsReachedException


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

    def __init__(self, serial_protocol: SerialProtocol, timeout: Optional[int] = 10):
        self.serial_protocol = serial_protocol
        self.transductor = serial_protocol.transductor
        self.timeout = timeout
        self.socket = None

        broker_ip = os.environ['BROKER_IP']
        broker_port = os.environ['BROKER_PORT']
        self.broker_address = (broker_ip, int(broker_port))

    # stops if pass 30s (30000ms) since the first attempt
    # wait 2.5s (2500ms) between retries
    @retry(stop_max_delay=30000, wait_fixed=2500)
    def socket_communication(
        self,
        message_to_send: bytes,
        MAX_MSG_SIZE: int
    ):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as self.socket:
            self.socket.settimeout(self.timeout)
            self.socket.sendto(message_to_send, self.broker_address)
            received_message = self.socket.recvfrom(MAX_MSG_SIZE)
            unpacked_received_message = pickle.loads(received_message[0])

            if(unpacked_received_message['status'] == 0):
                raise Exception(unpacked_received_message['content'])

            self._check_all_messages_crc(unpacked_received_message['content'])

        return unpacked_received_message['content']

    def send_message(self, message: List[bytes]):
        message_to_send: bytes = self._create_message(message)
        MAX_MSG_SIZE: int = int(os.environ['MAX_MSG_SIZE'])

        try:
            content = self.socket_communication(message_to_send, MAX_MSG_SIZE)
        except socket.timeout:
            raise NumberOfAttempsReachedException

        return content

    def _check_all_messages_crc(self, messages):
        for message in messages:
            if(self.serial_protocol._check_crc(message)):
                continue
            else:
                error_message = 'The received message contains an invalid CRC'
                raise CRCInvalidException(error_message)

    @abstractmethod
    def _create_message(self, message: List[bytes]) -> bytes:
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

    def _create_message(self, message: List[bytes]) -> bytes:
        real_message = {}
        real_message['content'] = message
        real_message['protocol'] = 'UDP'
        real_message['ip'] = self.transductor.ip_address
        real_message['port'] = self.transductor.port

        real_message: bytes = pickle.dumps(real_message)
        return real_message


class TcpProtocol(TransportProtocol):

    def _create_message(self, message: List[bytes]) -> bytes:
        real_message = {}
        real_message['content'] = message
        real_message['protocol'] = 'TCP'
        real_message['ip'] = self.transductor.ip_address
        real_message['port'] = self.transductor.port

        real_message: bytes = pickle.dumps(real_message)
        return real_message
