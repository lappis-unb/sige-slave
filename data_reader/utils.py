from typing import Tuple
from threading import Thread
from django.conf import settings
from importlib import import_module

from django.utils import timezone

from .communication import SerialProtocol
from .transport import TransportProtocol

from transductor_model.models import EnergyTransductorModel
from transductor.models import EnergyTransductor
from transductor.models import TimeInterval


def communication_log(status, datetime, type, transductor, file, errors=[]):
    print('DateTime:\t', datetime, file=file)
    print(
        'Transductor:\t',
        transductor.serial_number + '@' + transductor.physical_location,
        '(' + transductor.ip_address + ')',
        file=file
    )
    print('Type:\t\t', type, file=file)
    print('Status:\t\t', status, file=file)
    if errors:
        print('Errors:', file=file)
        for error in errors:
            print('\t\t', error, file=file)
    print('\n', file=file)


def get_active_transductors():
    return EnergyTransductor.objects.filter(active=True)


def single_data_collection(transductor: EnergyTransductor,
                           collection_type: str, date=None):
    """
    Thread method responsible to handle all the communication used
    by a transductor and save the measurements collected.

    Parameters
    ----------
    transductor : EnergyTransductor
        The transductor used.

    collection_type : str
        The type of collection to be made

    Returns:
        None
    """

    # Variable to log the step where the failure occurred.
    communication_step = ''

    try:
        communication_step = 'capturing transductor model'
        transductor_model = get_transductor_model_instance(transductor)

        communication_step = "capturing serial protocol"
        serial_protocol_instance: SerialProtocol = \
            get_serial_protocol(transductor, transductor_model)

        communication_step = "capturing transport protocol"
        transport_protocol_instance: TransportProtocol = \
            get_transport_protocol(serial_protocol_instance, transductor_model)

        communication_step = 'assembling messages'
        messages_to_send = serial_protocol_instance.create_messages(
            collection_type, date)

        communication_step = 'sending messages'
        received_messages = transport_protocol_instance.send_message(
            messages_to_send)

        communication_step = 'parsing response'
        received_messages_content = \
            serial_protocol_instance.get_content_from_messages(
                collection_type, received_messages, date)

        communication_step = 'handling response'
        handled_response = transductor_model.handle_response(
            collection_type,
            received_messages_content,
            transductor,
            date
        )

        filename = os.path.join(
            settings.LOG_PATH,
            'successful_communication_logs.log'
        )

        with open(filename, 'a') as file:
            communication_log(
                status='Success',
                datetime=timezone.datetime.now(),
                type=collection_type,
                transductor=transductor,
                file=file
            )

        if not handled_response:
            handled_response = True

        return handled_response

    except Exception as e:
        filename = os.path.join(
            settings.LOG_PATH,
            'failed_communication_logs.log'
        )

        with open(filename, 'a') as file:
            if (collection_type == "Minutely"):
                transductor.set_broken(True)
            else:
                attribute = get_rescue_attribute(collection_type)
                transductor.__dict__[attribute] = False
                transductor.save(update_fields=[attribute])
            communication_log(
                status='Failure at ' + communication_step,
                datetime=timezone.datetime.now(),
                type=collection_type,
                transductor=transductor,
                errors=[e],
                file=file
            )

        if (collection_type == "Minutely"):
            transductor.set_broken(True)

        elif collection_type in ['Quarterly', 'Monthly']:
            attribute = get_rescue_attribute(collection_type)
            transductor.__dict__[attribute] = False
            transductor.save(update_fields=[attribute])

        else:
            raise e

        return None


def perform_minutely_data_rescue(transductor: EnergyTransductor):
    interval: TimeInterval = transductor.timeintervals.first()
    if (interval is None or interval.end is None):
        return
    while(True):
        response = single_data_collection(
            transductor,
            "DataRescuePost",
            interval.begin
        )
        if(response is None):
            return

        measurement = single_data_collection(transductor, "DataRescueGet")
        if(measurement is None):
            return

        inside_interval = interval.change_interval(
            measurement.transductor_collection_date)

        if inside_interval:
            measurement.check_measurements()
            measurement.save()
        else:
            return


def perform_periodic_data_rescue(transductor, rescue_type):
    attribute = get_rescue_attribute(rescue_type)
    if transductor.__dict__[attribute] is True:
        return
    if single_data_collection(transductor, rescue_type) is None:
        transductor.__dict__[attribute] = False
    else:
        transductor.__dict__[attribute] = True
    transductor.save(update_fields=[attribute])


def get_rescue_function(rescue_type):
    if rescue_type == 'Minutely':
        return perform_minutely_data_rescue
    else:
        return perform_periodic_data_rescue


def get_rescue_attribute(rescue_type):
    if rescue_type == 'Quarterly':
        return 'quarterly_data_rescued'
    if rescue_type == 'Monthly':
        return 'monthly_data_rescued'
    return None


def perform_all_data_rescue(rescue_type):
    transductors = get_active_transductors()
    rescue_function = get_rescue_function(rescue_type)
    for transductor in transductors:
        if rescue_type == "Minutely":
            rescue_function(transductor)
        else:
            rescue_function(transductor, rescue_type)


def get_transductor_model_instance(
        transductor: EnergyTransductor) -> EnergyTransductorModel:
    """
    Dynamic import the transductor model class,
    according to the transductor passed as parameter

    Returns
    -------
    class instance : EnergyTransductorModel
        Imported class instance. This instance can be of
        any class that inherits from EnergyTransductorModel
    """
    transductor_model_class = getattr(
        import_module('transductor_model.models'),
        transductor.model
    )
    return transductor_model_class()


def get_serial_protocol(
        transductor: EnergyTransductor,
        transductor_model: EnergyTransductorModel) -> SerialProtocol:
    """
    Dynamic import the serial protocol model class,
    according to the transductor model passed as parameter

    Returns
    -------
    class instance : SerialProtocol
        Imported class instance. This instance can be of
        any class that inherits from SerialProtocol
    """
    serial_protocol_class = getattr(
        import_module('data_reader.communication'),
        transductor_model.serial_protocol
    )
    return serial_protocol_class(transductor, transductor_model)


def get_transport_protocol(
        serial_protocol_instance: SerialProtocol,
        transductor_model: EnergyTransductorModel) -> TransportProtocol:
    """
    Dynamic import the transport protocol model class,
    according to the transductor model passed as parameter

    Returns
    -------
    class instance : TransportProtocol
        Imported class instance. This instance can be of
        any class that inherits from TransportProtocol
    """
    transport_protocol_class = getattr(
        import_module('data_reader.transport'),
        transductor_model.transport_protocol
    )
    return transport_protocol_class(serial_protocol_instance)


def get_protocols(
    transductor: EnergyTransductor,
    transductor_model
) -> Tuple[SerialProtocol, TransportProtocol]:
    # Creating instances of the serial and transport protocol used
    # by the transductor

    serial_protocol_instance = globals()[
        transductor_model.serial_protocol
    ](transductor, transductor_model)

    transport_protocol_instance = globals()[
        transductor_model.transport_protocol
    ](serial_protocol_instance)

    return (serial_protocol_instance, transport_protocol_instance)


def perform_all_data_collection(collection_type: str) -> None:
    """
    Method responsible to start all transductors data collection
    simultaneously.

    Parameters
    ----------
    collection_type : str
        Time interval in which data collection should
        be performed (Minutely, Quarterly, Monthly)

    Returns:
        None
    """
    threads: list = []

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
