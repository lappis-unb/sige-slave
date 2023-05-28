import datetime

from django.db import models
from django.utils import timezone

from data_collector.modbus.data_reader import ModbusDataReader
from data_collector.models import MemoryMap
from debouncers.data_classes import VoltageState
from debouncers.debouncers import VoltageEventDebouncer


class Transductor(models.Model):
    """
    Transductor are the electricity measuring equipment connected to the
    power grid.
    """


    id = models.IntegerField(primary_key=True)
    serial_number = models.CharField(max_length=8, unique=True)
    ip_address = models.GenericIPAddressField(unique=True, protocol="IPv4")
    port = models.PositiveIntegerField()
    model = models.CharField(max_length=50, blank=False, null=False)
    active = models.BooleanField(default=True)
    broken = models.BooleanField(default=False)
    firmware_version = models.CharField(max_length=20)
    installation_date = models.DateTimeField(blank=True, default=timezone.now)
    physical_location = models.CharField(max_length=30, default="")
    quarterly_data_rescued = models.BooleanField(default=False)
    monthly_data_rescued = models.BooleanField(default=False)
    geolocation_longitude = models.DecimalField(max_digits=15, decimal_places=10)
    geolocation_latitude = models.DecimalField(max_digits=15, decimal_places=10)
    last_clock_battery_change = models.DateTimeField(blank=True, default=timezone.now)
    memory_map = models.ForeignKey(MemoryMap, on_delete=models.DO_NOTHING, related_name="+")

    def __str__(self) -> str:
        return f"{self.ip_address} - {self.model}"

    def collect_data(self, data_group, slave_id):
        register_map = getattr(self.memory_map, data_group)

        collector = ModbusDataReader(
            ip_address=self.ip_address,
            port=self.port,
            slave_id=slave_id,
        )

        modbus_data = {"collected": {}, "erros": "", "broken": self.broken}
        try:
            collected_data = collector.read_datagroup_blocks(register_map)
            collected_data["transductor"] = self.id
            modbus_data["collected"] = collected_data

        except Exception as e:
            modbus_data["broken"] = self.set_broken(True)
            modbus_data["errors"] = str(e)

        return modbus_data

    def set_broken(self, new_status: bool) -> bool:
        """
        Set the broken atribute's new status to match the param.
        If toggled to True, creates a failed connection event
        If toggled to False, closes the created failed connection event

        Args:
            new_status (bool): New broken attribute states

        Raises:
            Exception: When the Transductor tries to close a
            FailedConnectionTransductorEvent that has not been opened is raised an
            exception. This situation is a bug, and should not occur in normal
            situations, as every time a `transductor` takes self.broken = True a
            FailedConnectionTransductorEvent must be created.

        Returns:
            bool: returns the new state of the Transductor
        """
        from events.models import FailedConnectionTransductorEvent

        if new_status == self.broken:
            return self.broken

        self.broken = new_status
        self.active = not new_status
        self.save(update_fields=["broken", "active"])

        if new_status:
            FailedConnectionTransductorEvent.objects.create(transductor=self)
            TimeInterval.objects.create(
                transductor=self,
                begin=timezone.datetime.now(),
            )

        # The transductor was "broken" and now is working
        else:
            last_open_interval = self.timeintervals.last()

            if not last_open_interval:
                raise Exception("There are no open time intervals on this transductor!")

            # closing the last open interval
            last_open_interval.end = timezone.datetime.now()
            last_open_interval.save(update_fields=["end"])

            related_event_qs = FailedConnectionTransductorEvent.objects.filter(
                transductor=self,
                ended_at__isnull=True,
            )

            # save end time of last connection failure event
            if related_event_qs.last():
                last_open_related_event = related_event_qs.last()
                last_open_related_event.ended_at = timezone.now()
                last_open_related_event.save(update_fields=["ended_at"])

            else:
                print("There is no element in queryset filtered.")
                # TODO: send to sentry!!!
                # This is an error, but for now we are ignoring

        return self.broken

    def get_voltage_debouncer(self, measurement_phase: str) -> VoltageEventDebouncer:
        """
        Method to instantiate a debouncer with the historical data saved in the database

        Args:
            measurement_phase (str): Phase that the debouncer will analyze.

        Returns:
            VoltageEventDebouncer
        """

        now = datetime.datetime.now()
        fifteen_minutes_ago = now - datetime.timedelta(minutes=15)

        queryset = self.measurement_minutelymeasurement.filter(
            collection_date__lte=now,
            collection_date__gte=fifteen_minutes_ago,
        )

        # most recent first
        queryset = queryset.order_by("-collection_date")
        latest_measurements = queryset[:15]

        # List with most recent measurements for a given phase
        latest_measurements: list[float] = latest_measurements.values_list(measurement_phase, flat=True)

        debouncer = VoltageEventDebouncer(measurement_phase)
        debouncer.data_history = list(latest_measurements)
        voltage_state = self.voltage_phase_states.get_or_create(phase=measurement_phase)
        debouncer.current_voltage_state = voltage_state.current_voltage_state

        return debouncer

    def update_measurement_phase_state(
        self,
        measurement_phase: str,
        current_state: float,
    ):
        # saves the new state of that phase
        transductor_voltage_state = TransductorVoltageState.objects.get(
            transductor=self,
            phase=measurement_phase,
        )
        # voltage_phase_state = self.voltage_phase_states.get(measurement_phase)
        transductor_voltage_state.current_voltage_state = current_state
        transductor_voltage_state.save()
        return transductor_voltage_state

    def check_voltage_events(
        self,
        voltage_state_transition: tuple[VoltageState, VoltageState],
        measurement_phase: str,
        measurements_value: float,
    ) -> None:
        previous_state, current_state = voltage_state_transition
        self.update_measurement_phase_state(measurement_phase, current_state)

        # If the previous state was not VoltageState.NORMAL, it means that there is
        # an open event that needs to be closed
        if previous_state not in [VoltageState.NORMAL.value, current_state]:
            event_class = VoltageState.get_target_event_class(previous_state)

            related_unfinished_events = event_class.objects.filter(transductor=self, ended_at=None)

            last_event = related_unfinished_events.last()

            if last_event:
                if not last_event.data:
                    data = {
                        "voltage_a": None,
                        "voltage_b": None,
                        "voltage_c": None,
                    }
                    last_event.data = data

                last_event.data[measurement_phase] = None

                if last_event.all_phases_are_none():
                    last_event.ended_at = timezone.datetime.now()

                last_event.save()

        # If the current state is not VoltageState.NORMAL, it means that you need
        # to open a new event for the current state.
        if current_state != VoltageState.NORMAL.value:
            event_class = VoltageState.get_target_event_class(current_state)

            event, created = event_class.objects.get_or_create(transductor=self, ended_at=None)

            if not event.data:
                data = {
                    "voltage_a": None,
                    "voltage_b": None,
                    "voltage_c": None,
                }
                event.data = data

            event.data[measurement_phase] = measurements_value
            event.save()


class TransductorVoltageState(models.Model):
    """
    Model class to store the current states of each phase of the transductors.
    """

    VOLTAGE_STATES = (
        ("CriticalHigh", "CriticalHigh"),
        ("PrecariousHigh", "PrecariousHigh"),
        ("Normal", "Normal"),
        ("PrecariousLow", "PrecariousLow"),
        ("CriticalLow", "CriticalLow"),
        ("PhaseDown", "PhaseDown"),
    )
    id = models.AutoField(primary_key=True)
    current_voltage_state = models.CharField(
        max_length=14,
        choices=VOLTAGE_STATES,
        default=VOLTAGE_STATES[2][0],  # Normal
    )

    transductor = models.ForeignKey(
        Transductor,
        related_name="voltage_phase_states",
        on_delete=models.CASCADE,
    )

    VALID_VOLTAGE_PHASES = (
        ("voltage_a", "voltage_a"),
        ("voltage_b", "voltage_b"),
        ("voltage_c", "voltage_c"),
    )
    phase = models.CharField(max_length=9, choices=VALID_VOLTAGE_PHASES)

    class Meta:
        unique_together = ("transductor", "phase")

    def __str__(self) -> str:
        return "Transductor Nº {} - Voltage Phase {} is {}".format(
            self.transductor,
            self.phase[-1],
            self.current_voltage_state,
        )


class TimeInterval(models.Model):
    id = models.AutoField(primary_key=True)
    begin = models.DateTimeField(null=False)
    end = models.DateTimeField(null=True)

    transductor = models.ForeignKey(
        Transductor,
        models.CASCADE,
        related_name="timeintervals",
    )

    def change_interval(self, time):
        self.begin = time + timezone.timedelta(minutes=1)

        # Verifies if collected date is inside the recovery interval
        if self.end < time:
            self.delete()
            return False
        else:
            self.save(update_fields=["begin"])
            return True
