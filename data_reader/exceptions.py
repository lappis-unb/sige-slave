class NumberOfAttempsReachedException(Exception):
    """
    Exception to signal that a transductor is broken when
    trying to send messages via Transport Protocol.

    Attributes:
        message (str): The exception message.
    """

    def __init__(self, message):
        super(NumberOfAttempsReachedException, self).__init__(message)
        self.message = message


class RegisterAddressException(Exception):
    """
    Exception to signal that a register address from transductor model
    is in a wrong format.

    Attributes:
        message (str): The exception message.
    """

    def __init__(self, message):
        super(RegisterAddressException, self).__init__(message)
        self.message = message


class CRCInvalidException(Exception):
    def __init__(self, message):
        super(CRCInvalidException, self).__init__(message)
        self.message = message


class InvalidDateException(Exception):
    """
    Exception to signal that date does not make sence in this contest.

    Attributes:
        message (str): The exception message.
    """

    def __init__(self, message):
        super(InvalidDateException, self).__init__(message)
        self.message = message
