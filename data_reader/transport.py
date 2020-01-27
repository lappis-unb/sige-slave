import importlib
import socket
import pickle
import os

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

    def __init__(self, serial_protocol, timeout=10):
        self.serial_protocol = serial_protocol
        self.transductor = serial_protocol.transductor
        self.timeout = timeout
        self.socket = None

        broker_ip = os.environ['BROKER_IP']
        broker_port = os.environ['BROKER_PORT']
        self.broker_address = (broker_ip, int(broker_port))

    def send_message(self, message):
        self.open_socket()
        max_receive_attempts = 3
        receive_attemps = 0
        received_message = None
        crc_errors = 0
        max_crc_erros = max_receive_attempts
        while(
            not received_message and (
                receive_attemps < max_receive_attempts
            ) and (
                crc_errors < max_crc_erros
            )
        ):
            message_to_send = self._create_message(message)
            self.socket.sendto(
                message_to_send,
                self.broker_address
            )

            try:
                MAX_MSG_SIZE = int(os.environ['MAX_MSG_SIZE'])
                received_message = self.socket.recvfrom(MAX_MSG_SIZE)
                unpacked_received_message = pickle.loads(received_message[0])
                if(unpacked_received_message['status'] == 0):
                    raise Exception(unpacked_received_message['content'])
                self._check_all_messages_crc(
                    unpacked_received_message['content'])
            except socket.timeout:
                receive_attemps += 1
                if(receive_attemps == max_receive_attempts):
                    self.socket.close()
                    raise NumberOfAttempsReachedException(
                        "Maximum attempts reached!")
            except CRCInvalidException as e:
                crc_errors += 1
                if(crc_errors == max_crc_erros):
                    self.socket.close()
                    raise e

        self.socket.close()
        return unpacked_received_message['content']

    def open_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(self.timeout)

    def _check_all_messages_crc(self, messages):
        for message in messages:
            if(self.serial_protocol._check_crc(message)):
                pass
            else:
                return False
        return True

    @abstractmethod
    def _create_message(self, message):
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

    def _create_message(self, message):
        real_message = {}
        real_message['content'] = message
        real_message['protocol'] = 'UDP'
        real_message['ip'] = self.transductor.ip_address
        real_message['port'] = self.transductor.port

        real_message = pickle.dumps(real_message)
        return real_message


class TcpProtocol(TransportProtocol):

    def _create_message(self, message):
        real_message = {}
        real_message['content'] = message
        real_message['protocol'] = 'TCP'
        real_message['ip'] = self.transductor.ip_address
        real_message['port'] = self.transductor.port

        real_message = pickle.dumps(real_message)
        return real_message
