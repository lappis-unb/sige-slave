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

from .transport import *
from .communication import *

from transductor_model.models import EnergyTransductorModel
from transductor_model.models import MD30
from transductor_model.models import TR4020
from transductor.models import EnergyTransductor
from measurement.models import *
import time


def communication_log(status, datetime, type, transductor, errors=[]):
    print('DateTime:\t', datetime)
    print(
        'Transductor:\t', 
        transductor.serial_number + '@' + transductor.physical_location, 
        '(' + transductor.ip_address + ')'
    )
    print('Type:\t\t', type)
    print('Status:\t\t', status)
    if errors:
        print('Errors:')
        for error in errors:
            print('\t\t', error)
    print('\n')


def get_active_transductors():
    return EnergyTransductor.objects.filter(active=True)


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

    communication_step = ''
    try:
        communication_step = 'capturing transductor model'
        transductor_model = get_transductor_model(transductor)
        serial_protocol_instance, \
            transport_protocol_instance = get_protocols(transductor,
                                                        transductor_model)
        communication_step = 'assembling messages'
        messages_to_send = serial_protocol_instance.create_messages(
            collection_type, date)
        communication_step = 'sending messages'
        received_messages = transport_protocol_instance.send_messages(
            messages_to_send)
        communication_step = 'parsing response'
        received_messages_content = \
            serial_protocol_instance.get_content_from_messages(
                collection_type, received_messages, date)
        communication_step = 'handling response'
        handled_response = transductor_model.handle_response(
            collection_type,
            received_messages_content,
            transductor, date)
        communication_log(
            status='Success', 
            datetime=timezone.datetime.now(), 
            type=collection_type, 
            transductor=transductor
        )
        return handled_response
    except Exception as e:
        if(collection_type == "Minutely"):
            transductor.set_broken(True)
        communication_log(
            status='Failure at ' + communication_step, 
            datetime=timezone.datetime.now(), 
            type=collection_type, 
            transductor=transductor, 
            errors=[e]
        )
        return None


def perform_data_rescue(transductor):
    interval = transductor.timeintervals.first()
    if (interval is None or interval.end is None):
        return
    while(True):
        if(single_data_collection(transductor, "DataRescuePost", 
                                  interval.begin) is None):
            return
        time.sleep(0.1)

        measurement = single_data_collection(transductor, "DataRescueGet")
        if(measurement is None):
            return

        inside_interval = interval.change_interval(
            measurement.collection_date)

        if(inside_interval):
            measurement.save()
        else:
            return
        time.sleep(0.1)


def perform_all_data_rescue():
    transductors = get_active_transductors()
    for transductor in transductors:
        perform_data_rescue(transductor)


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

    transductors = get_active_transductors()
    for transductor in transductors:
        collection_thread = Thread(
            target=single_data_collection,
            args=(transductor, collection_type)
        )

        collection_thread.start()

        threads.append(collection_thread)

    for thread in threads:
        thread.join()
