import sys
import socket
import struct
import importlib

from abc import ABCMeta
from abc import abstractmethod
from threading import Thread

from .exceptions import NumberOfAttempsReachedException
from .exceptions import RegisterAddressException
from .exceptions import CRCInvalidException
from .exceptions import InvalidDateException

from .transport import UdpProtocol
from .communication import ModbusRTU

from transductor_model.models import EnergyTransductorModel
from transductor.models import EnergyTransductor
from measurement.models import *
import time


def get_transductors():
    return EnergyTransductor.objects.all()


def get_transductor_model(transductor):
    return globals()[
        transductor.model
    ]()


def single_data_collection(transductor, collection_type, date=None):
    """
    Thread method responsible to handle all the communication used
    by a transductor and save the measurements collected.

    Args:
        transductor (Transductor): The transductor used.
        collection_type (String): The type of collection to be made

    Returns:
        None
    """
    transductor_model = get_transductor_model(transductor)
    serial_protocol_instance, \
        transport_protocol_instance = get_protocols(transductor,
                                                    transductor_model)

    messages_to_send = serial_protocol_instance.create_messages(
        collection_type, date)
    try:
        received_messages = transport_protocol_instance.send_messages(
            messages_to_send)
        received_messages_content = \
            serial_protocol_instance.get_content_from_messages(
                collection_type, received_messages, date)

        return transductor_model.handle_response(collection_type,
                                                 received_messages_content,
                                                 transductor)
    except Exception as e:
        transductor.set_broken(True)
        print(collection_type, datetime.now(), "exception:", e)
        return


def perform_data_rescue(transductor, begin_date, end_date):
    max_acceptable_difference = 30
    while((end_date - begin_date).total_seconds() > max_acceptable_difference):
        single_data_collection(transductor, "DataRescuePost", begin_date)
        time.sleep(1)
        date = single_data_collection(transductor, "DataRescueGet")
        if(date is None):
            return
        begin_date = date + timezone.timedelta(minutes=1)


def get_protocols(transductor, transductor_model):
    # Creating instances of the serial and transport protocol used
    # by the transductor

    serial_protocol_instance = globals()[
        transductor_model.serial_protocol
    ](transductor, transductor_model)
    transport_protocol_instance = globals()[
        transductor_model.transport_protocol
    ](serial_protocol_instance)

    return (serial_protocol_instance, transport_protocol_instance)


def perform_all_data_collection(collection_type):
    """
    Method responsible to start all transductors data collection
    simultaneously.

    Returns:
        None
    """
    threads = []

    transductors = get_transductors()
    for transductor in transductors:
        if(transductor.active):
            collection_thread = Thread(
                target=single_data_collection,
                args=(transductor, collection_type)
            )

            collection_thread.start()

            threads.append(collection_thread)

    for thread in threads:
        thread.join()
