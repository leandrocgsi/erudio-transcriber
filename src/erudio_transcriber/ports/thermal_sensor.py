from typing import Protocol

from erudio_transcriber.domain.thermal import ThermalReading


class ThermalSensor(Protocol):
    def read(self) -> ThermalReading: ...
