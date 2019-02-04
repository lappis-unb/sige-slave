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
    def start_communication(self):
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

    def __init__(self, serial_protocol, timeout=0.5, port=1001):
        super(UdpProtocol, self).__init__(serial_protocol, timeout, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.receive_attempts = 0
        self.max_receive_attempts = 3

    # TODO change the name of this method to be more significant
    def start_communication(self):
        """
        Method responsible to try receive message from transductor
        (via socket) based on maximum receive attempts.

        Everytime a message is not received from the socket the
        total of received attemps is increased.

        Returns: The messages received if successful, None otherwise.

        Raises:
            NumberOfAttempsReachedException: Raised if the transductor
            can't send messages via UDP socket.
        """
        self.reset_receive_attempts()

        messages_to_send = self.serial_protocol.create_messages()
        received_messages = []

        while(
            not received_messages and (
                self.receive_attempts < self.max_receive_attempts
            )
        ):
            try:
                received_messages = self.handle_messages_via_socket(
                    messages_to_send
                )
            except socket.timeout:
                pass

            self.receive_attempts += 1

        if received_messages:
            try:
                self.serial_protocol \
                    .check_all_messages_crc(received_messages)
            except CRCInvalidException:
                raise
        else:
            raise NumberOfAttempsReachedException("Maximum attempts reached!")

        return received_messages

    def data_sender(self):
        self.reset_receive_attempts()

        messages_to_send = self.serial_protocol.create_date_send_message()
        received_messages = []

        while(
            not received_messages
            and self.receive_attempts < self.max_receive_attempts
        ):
            try:
                received_messages = self.handle_messages_via_socket(
                    messages_to_send
                )
            except socket.timeout:
                pass
        if received_messages:
            try:
                self.serial_protocol \
                    .check_all_messages_crc(received_messages)
            except CRCInvalidException:
                raise
        else:
            raise NumberOfAttempsReachedException("Maximum attempts reached!")




    def reset_receive_attempts(self):
        """
        Method responsible to reset the number of receive attempts.
        """
        self.receive_attempts = 0

    def handle_messages_via_socket(self, messages_to_send):
        """
        Method responsible to handle send/receive messages via socket UDP.

        Args:
            messages_to_send (list): The requests to be sent to the
            transductor via socket.

        Returns:
            The messages received if successful, None otherwise.
        """
        messages = []

        for i, message in enumerate(messages_to_send):
            self.socket.sendto(
                message,
                (self.transductor.ip_address, self.port)
            )

            try:
                message_received = self.socket.recvfrom(256)
            except socket.timeout:
                raise

            messages.append(message_received[0])

        return messages
