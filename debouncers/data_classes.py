from enum import Enum
from dataclasses import dataclass


class VoltageState(Enum):
    CRITICAL_UPPER = 'CriticalHigh'
    PRECARIOUS_UPPER = 'PrecariousHigh'
    NORMAL = 'Normal'
    PRECARIOUS_LOWER = 'PrecariousLow'
    CRITICAL_LOWER = 'CriticalLow'
    PHASE_DOWN = 'PhaseDown'

    def get_target_event_class(voltage_state: str):
        """
        Returns the model class associated with the state of the phase.

        For example:
        > VoltageState.CRITICAL_UPPER => events.models.CriticalVoltageEvent
        > VoltageState.CRITICAL_LOWER => events.models.CriticalVoltageEvent

        > VoltageState.PRECARIOUS_UPPER => events.models.PrecariousVoltageEvent
        > VoltageState.PRECARIOUS_LOWER => events.models.PrecariousVoltageEvent

        > VoltageState.PHASE_DOWN => events.models.PhaseDropEvent

        Args:
            voltage_state (str): Current state of a given phase

        Returns:
            VoltageRelatedEvent:
        """
        from events.models import (
            CriticalVoltageEvent,
            PrecariousVoltageEvent,
            PhaseDropEvent
        )

        m = {
            VoltageState.CRITICAL_UPPER.value: CriticalVoltageEvent,
            VoltageState.CRITICAL_LOWER.value: CriticalVoltageEvent,

            VoltageState.PRECARIOUS_UPPER.value: PrecariousVoltageEvent,
            VoltageState.PRECARIOUS_LOWER.value: PrecariousVoltageEvent,

            VoltageState.PHASE_DOWN.value: PhaseDropEvent,
        }

        return m[voltage_state]


@dataclass
class VoltageBounds:
    upper_bound: float
    lower_bound: float
