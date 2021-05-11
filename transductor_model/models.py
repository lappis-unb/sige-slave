from typing import Callable, Dict, List, Optional, Tuple, Union
from datetime import datetime
from transductor.models import EnergyTransductor

from django.utils import timezone

from measurement.models import (MinutelyMeasurement, MonthlyMeasurement,
                                QuarterlyMeasurement)
from utils import is_datetime_similar


class EnergyTransductorModel():
    transport_protocol = "UdpProtocol"
    serial_protocol = "ModbusRTU"

    MINUTELY_REGISTERS = [
        [10, 1], [11, 1], [14, 1], [15, 1], [16, 1], [17, 1], [66, 2],
        [68, 2], [70, 2], [72, 2], [74, 2], [76, 2], [78, 2], [80, 2],
        [82, 2], [84, 2], [86, 2], [88, 2], [90, 2], [92, 2], [94, 2],
        [96, 2], [98, 2], [100, 2], [102, 2], [104, 2], [106, 2], [108, 2],
        [110, 2], [112, 2], [114, 2], [116, 2], [118, 2], [120, 2],
        [122, 2], [132, 2], [134, 2], [136, 2], [138, 2]
    ]

    QUARTERLY_REGISTERS = [
        [264, 2], [266, 2], [270, 2], [272, 2], [276, 2], [278, 2],
        [282, 2], [284, 2]
    ]

    MONTHLY_REGISTERS = [
        [156, 2],
        [158, 2], [162, 2], [164, 2], [168, 2], [170, 2], [174, 2],
        [176, 2], [180, 2], [182, 2], [186, 2], [188, 2], [420, 2],
        [516, 1], [520, 1], [422, 2], [517, 1], [521, 1], [424, 2],
        [518, 1], [522, 1], [426, 2], [519, 1], [523, 1], [428, 2],
        [524, 1], [528, 1], [430, 2], [525, 1], [529, 1], [432, 2],
        [526, 1], [530, 1], [434, 2], [527, 1], [531, 1], [444, 2],
        [540, 1], [544, 1], [446, 2], [541, 1], [545, 1], [448, 2],
        [542, 1], [546, 1], [450, 2], [543, 1], [547, 1], [452, 2],
        [548, 1], [552, 1], [454, 2], [549, 1], [553, 1], [456, 2],
        [550, 1], [554, 1], [458, 2], [551, 1], [555, 1]
    ]

    CORRECT_DATE_REGISTERS = [
        [10, 1], [11, 1], [14, 1], [15, 1], [16, 1], [17, 1]
    ]

    DATA_RESCUE_POST_REGISTERS = [[160, 4]]

    DATA_RESCUE_GET_REGISTERS = [[200, 22]]

    # TODO: As can be seen, this function returns a strange data structure.
    # Abstract this data structure into a class
    @property
    def registers(self) -> Dict[str, List[List[int]]]:
        """Alias dictionary with register mapping"""
        return {
            "Minutely": self.MINUTELY_REGISTERS,
            "Quarterly": self.QUARTERLY_REGISTERS,
            "Monthly": self.MONTHLY_REGISTERS,
            "CorrectDate": self.CORRECT_DATE_REGISTERS,
            "DataRescuePost": self.DATA_RESCUE_POST_REGISTERS,
            "DataRescueGet": self.DATA_RESCUE_GET_REGISTERS
        }

    # TODO: As can be seen, this function returns a REALLY strange data structure.
    # Abstract this data structure into a class
    # This strange return is the result of a chain of strange returns
    def collection_functions(
        self
    ) -> Dict[str,                                           # method identifier
              Callable[                                      # method
                  [Optional[datetime]],                      # method parameters
                  Union[                                     # method return
                      Tuple[str, List[List[int]]],           # the return can be this
                      Tuple[str, List[List[int]], List[int]] # or this
                   ]
                ]
            ]:
        """
        Alias dictionary for collection functions.

        These are factory functions that create the data structure that will be
        sent to the transductors.
        """
        return {
            "Minutely": self.minutely_collection,
            "Quarterly": self.quarterly_collection,
            "Monthly": self.monthly_collection,
            "CorrectDate": self.correct_date,
        }

    # TODO: As can be seen, this function returns a REALLY strange data structure.
    # Abstract this data structure into a class
    def handle_response_functions(
        self
    ) -> Dict[str, Callable[[list, EnergyTransductor, Optional[datetime]], datetime]]:
        """
        Alias dictionary for handle functions

        These are functions responsible for interpreting and saving the
        information sent by the transductors.
        """
        return {
            "Minutely": self.save_minutely_measurement,
            "Quarterly": self.save_quarterly_measurement,
            "Monthly": self.save_monthly_measurement,
            "CorrectDate": self.verify_rescue_collection_date,
        }

    # TODO: As can be seen, this function returns a really strange data structure.
    # Abstract this data structure into a class
    def data_collection(
        self,
        type: str,
        date: Optional[datetime] = None
    ) -> Union[Tuple[str, List[List[int]]], Tuple[str, List[List[int]], List[int]]]:
        """
        Factory function that will return the data-structure necessary to
        collect certain information from a transducer
        """
        collection_dict = self.collection_functions()
        if date is None:
            return collection_dict[type]()
        else:
            return collection_dict[type](date)

    # TODO: As can be seen, this function returns a strange data structure.
    # Abstract this data structure into a class
    def minutely_collection(self) -> Tuple[str, List[List[int]]]:
        return ("ReadHoldingRegisters", self.registers['Minutely'])

    # TODO: As can be seen, this function returns a strange data structure.
    # Abstract this data structure into a class
    def quarterly_collection(self) -> Tuple[str, List[List[int]]]:
        return ("ReadHoldingRegisters", self.registers['Quarterly'])

    # TODO: As can be seen, this function returns a strange data structure.
    # Abstract this data structure into a class
    def monthly_collection(self) -> Tuple[str, List[List[int]]]:
        return ("ReadHoldingRegisters", self.registers['Monthly'])

    # TODO: As can be seen, this function returns a strange data structure.
    # Abstract this data structure into a class
    def correct_date(
        self,
        date: Optional[datetime] = None
    ) -> Tuple[str, List[List[int]], List[int]]:
        if not date:
            date = timezone.datetime.now()

        payload = [
            date.year,
            date.month,
            date.day,
            date.hour,
            date.minute,
            date.second
        ]

        return ("PresetMultipleRegisters", self.registers['CorrectDate'], payload)

    def handle_response(
        self,
        collection_type: str,
        response: list,
        transductor: EnergyTransductor,
        date: Optional[datetime] = None
    ) -> datetime:
        """
        Helper function to handle transductor response according to the type
        of collection.

        Args:
            collection_type (str): Desired measurement type. Every transductor,
            regardless of hardware, must support at least the following 4 types of
            measurement: (Minutely, Quarterly, Monthly, CorrectDate,  DataRescueGet).
            Some transductor have other types of data collection, such as the case of
            the `MD30` which expands the types of collection with the following
            types: (DataRescuePost, DataRescueGet)

            response (list): [description]

            transductor (EnergyTransductor): Transductor that has the desired
            measurements

            date (Optional[datetime]): Specifying a collection date. The
            transductors store past measurements in their internal memory. In this way
            it is possible to make requests for past dates. When this attribute is not
            specified, the most recent measurement is retrieved. Defaults to None.

        Returns:
            datetime: Every measurement has a date associated with it.
            This function returns this date.
        """

        response_dict = self.handle_response_functions()
        return response_dict[collection_type](response, transductor, date)

    def save_minutely_measurement(
        self,
        response: List[Union[int, float, None]],
        transductor: EnergyTransductor,
        date: Optional[datetime] = None
    ) -> datetime:
        # TODO: Esse comportamento é esperado?
        # After every measurement, a check is made if the transductor time is more than
        # 30s apart, and if the transductor time is wrong, the current measurement is
        # "paused" to make a new request to the meter requesting that the time be
        # updated
        self.verify_collection_date(response, transductor)

        minutely_measurement = MinutelyMeasurement()
        minutely_measurement.transductor = transductor

        # saving the datetime from transductor
        date = timezone.datetime(
            year=response[0],
            month=response[1],
            day=response[2],
            hour=response[3],
            minute=response[4],
            second=response[5]
        )

        minutely_measurement.transctor_collection_date = date
        minutely_measurement.slave_collection_date = timezone.now()

        minutely_measurement.frequency_a = response[6]
        minutely_measurement.voltage_a = response[7]
        minutely_measurement.voltage_b = response[8]
        minutely_measurement.voltage_c = response[9]
        minutely_measurement.current_a = response[10]
        minutely_measurement.current_b = response[11]
        minutely_measurement.current_c = response[12]
        minutely_measurement.active_power_a = response[13]
        minutely_measurement.active_power_b = response[14]
        minutely_measurement.active_power_c = response[15]
        minutely_measurement.total_active_power = response[16]
        minutely_measurement.reactive_power_a = response[17]
        minutely_measurement.reactive_power_b = response[18]
        minutely_measurement.reactive_power_c = response[19]
        minutely_measurement.total_reactive_power = response[20]
        minutely_measurement.apparent_power_a = response[21]
        minutely_measurement.apparent_power_b = response[22]
        minutely_measurement.apparent_power_c = response[23]
        minutely_measurement.total_apparent_power = response[24]
        minutely_measurement.power_factor_a = response[25]
        minutely_measurement.power_factor_b = response[26]
        minutely_measurement.power_factor_c = response[27]
        minutely_measurement.total_power_factor = response[28]
        minutely_measurement.dht_voltage_a = response[29]
        minutely_measurement.dht_voltage_b = response[30]
        minutely_measurement.dht_voltage_c = response[31]
        minutely_measurement.dht_current_a = response[32]
        minutely_measurement.dht_current_b = response[33]
        minutely_measurement.dht_current_c = response[34]
        minutely_measurement.consumption_a = response[35]
        minutely_measurement.consumption_b = response[36]
        minutely_measurement.consumption_c = response[37]
        minutely_measurement.total_consumption = response[38]

        minutely_measurement.check_measurements()
        minutely_measurement.save()
        transductor.set_broken(False)
        return minutely_measurement.transductor_collection_date

    def save_quarterly_measurement(self, response, transductor, date=None):
        quarterly_measurement = QuarterlyMeasurement()
        quarterly_measurement.transductor = transductor

        quarterly_measurement.slave_collection_date = timezone.now()

        current_time = quarterly_measurement.slave_collection_date
        quarterly_measurement.transductor_collection_date = \
            current_time - timezone.timedelta(
                minutes=15 + (current_time.minute % 15),
                seconds=current_time.second,
                microseconds=current_time.microsecond)

        quarterly_measurement.generated_energy_peak_time = response[0]
        quarterly_measurement.generated_energy_off_peak_time = response[1]

        quarterly_measurement.consumption_peak_time = response[2]
        quarterly_measurement.consumption_off_peak_time = response[3]

        quarterly_measurement.inductive_power_peak_time = response[4]
        quarterly_measurement.inductive_power_off_peak_time = response[5]

        quarterly_measurement.capacitive_power_peak_time = response[6]
        quarterly_measurement.capacitive_power_off_peak_time = response[7]

        quarterly_measurement.check_measurements()
        quarterly_measurement.save()

        return quarterly_measurement.transductor_collection_date

    def data_rescue_post(self, date):
        timestamp = int(timezone.datetime.timestamp(date))
        payload = [timestamp]
        return ("PresetMultipleRegisters", self.registers['DataRescuePost'],
                payload)

    def data_rescue_get(self):
        return ("ReadHoldingRegisters", self.registers['DataRescueGet'])

    def save_monthly_measurement(
        self,
        response: list,
        transductor: EnergyTransductor,
        date: Optional[datetime] = None
    ) -> datetime:
        measurement = MonthlyMeasurement()
        measurement.transductor = transductor

        measurement.slave_collection_date = timezone.now()
        current_time = measurement.slave_collection_date
        if current_time.month == 1:
            transductor_collection_year = current_time.year - 1
            transductor_collection_month = 12
        else:
            transductor_collection_year = current_time.year
            transductor_collection_month = current_time.month - 1

        measurement.transductor_collection_date = timezone.datetime(
            year=transductor_collection_year,
            month=transductor_collection_month,
            day=1
        )
        measurement.generated_energy_peak_time = response[0]
        measurement.generated_energy_off_peak_time = response[1]

        measurement.consumption_peak_time = response[2]
        measurement.consumption_off_peak_time = response[3]

        # FIXME - This 2 measurements comming as NaN from the transductor
        measurement.inductive_power_peak_time = response[4]
        measurement.inductive_power_off_peak_time = response[5]

        measurement.capacitive_power_peak_time = response[6]
        measurement.capacitive_power_off_peak_time = response[7]

        measurement.active_max_power_peak_time = response[8]
        measurement.active_max_power_off_peak_time = response[9]

        measurement.reactive_max_power_peak_time = response[10]
        measurement.reactive_max_power_off_peak_time = response[11]

        # Arguments refer to initial positions of response information
        # Further information on transductor's Memory Map

        year = measurement.transductor_collection_date.year

        measurement.active_max_power_list_peak_time = []
        measurement.active_max_power_list_peak = []

        try:
            for i in range(12, 22, 3):
                measurement.active_max_power_list_peak_time.append(
                    timezone.datetime(
                        year, response[i + 1] // 256,
                        response[i + 1] % 256, response[i + 2] // 256,
                        response[i + 2] % 256))
                measurement.active_max_power_list_peak.append(response[i])

        except ValueError:
            pass

        measurement.active_max_power_list_off_peak_time = []
        measurement.active_max_power_list_off_peak = []

        try:
            for i in range(24, 34, 3):
                measurement.active_max_power_list_off_peak_time.append(
                    timezone.datetime(
                        year, response[i + 1] // 256,
                        response[i + 1] % 256, response[i + 2] // 256,
                        response[i + 2] % 256))
                measurement.active_max_power_list_off_peak.append(response[i])

        except ValueError:
            pass

        measurement.reactive_max_power_list_peak_time = []
        measurement.reactive_max_power_list_peak = []
        try:

            for i in range(36, 46, 3):
                measurement.reactive_max_power_list_peak_time.append(
                    timezone.datetime(
                        year, response[i + 1] // 256,
                        response[i + 1] % 256, response[i + 2] // 256,
                        response[i + 2] % 256))
                measurement.reactive_max_power_list_peak.append(response[i])

        except ValueError:
            pass

        measurement.reactive_max_power_list_off_peak_time = []
        measurement.reactive_max_power_list_off_peak = []

        try:

            for i in range(48, 58, 3):
                measurement.reactive_max_power_list_off_peak_time.append(
                    timezone.datetime(
                        year, response[i + 1] // 256,
                        response[i + 1] % 256, response[i + 2] // 256,
                        response[i + 2] % 256))
                measurement.reactive_max_power_list_off_peak.append(response[i])

        except ValueError:
            pass

        measurement.save()
        return measurement.transductor_collection_date

    def verify_rescue_collection_date(
        self,
        response: list,
        transductor: EnergyTransductor,
        date: Optional[datetime] = None
    ):
        # functions that process responses must return datetime to maintain the
        # interface
        return datetime.now()

    def save_rescued_data(
        self,
        response: list,
        transductor: EnergyTransductor,
        date: Optional[datetime] = None
    ):
        measurement = MinutelyMeasurement()

        measurement.transductor_collection_date = response[0][0]
        measurement.slave_collection_date = timezone.now()
        measurement.voltage_a = response[0][1]
        measurement.voltage_b = response[0][2]
        measurement.voltage_c = response[0][3]

        measurement.current_a = response[0][4]
        measurement.current_b = response[0][5]
        measurement.current_c = response[0][6]

        measurement.total_active_power = response[0][7]
        measurement.total_reactive_power = response[0][8]

        measurement.transductor = transductor
        return measurement

    @staticmethod
    def verify_collection_date(
        measurements: List[Union[int, float, None]],
        transductor: EnergyTransductor
    ) -> None:
        from data_reader.utils import single_data_collection
        collected_date = timezone.datetime(
            year=measurements[0],
            month=measurements[1],
            day=measurements[2],
            hour=measurements[3],
            minute=measurements[4],
            second=measurements[5]
        )
        current_date = timezone.datetime.now()

        # If the date the transductor returns is more than acceptable (30s), a new
        # request is sent to reset the meter time
        if not is_datetime_similar(collected_date, current_date):
            single_data_collection(transductor, "CorrectDate")
            measurements[0] = current_date.year
            measurements[1] = current_date.month
            measurements[2] = current_date.day
            measurements[3] = current_date.hour
            measurements[4] = current_date.minute
            measurements[5] = current_date.second


class MD30(EnergyTransductorModel):
    transport_protocol = "TcpProtocol"
    serial_protocol = "ModbusTCP"

    def collection_functions(self) -> Dict[str, Callable[[Optional[datetime]], int]]:

        base_collection_functions = super(
            EnergyTransductorModel, self
        ).collection_functions()

        return dict(base_collection_functions, **{
            "DataRescuePost": self.data_rescue_post,
            "DataRescueGet": self.data_rescue_get,
        })

    def handle_response_functions(self):

        base_handle_response_functions = super(
            EnergyTransductorModel, self
        ).handle_response_functions()

        return dict(base_handle_response_functions, **{
            "DataRescuePost": self.verify_rescue_collection_date,
            "DataRescueGet": self.save_rescued_data,
        })


class TR4020(EnergyTransductorModel):
    pass
