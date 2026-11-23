import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field

from erudio_transcriber.core.thermal_policy import decide
from erudio_transcriber.domain.errors import JobCancelledError
from erudio_transcriber.domain.progress import ProgressEvent, Stage
from erudio_transcriber.domain.thermal import ThermalAction, ThermalLimits
from erudio_transcriber.ports.progress_sink import ProgressSink
from erudio_transcriber.ports.thermal_sensor import ThermalSensor


@dataclass(slots=True)
class ThermalGate:
    """Called between units of work: blocks while the machine is too hot, raises when cancelled."""

    sensor: ThermalSensor
    limits: ThermalLimits
    sink: ProgressSink
    stop: threading.Event
    check_every: float = 10.0
    poll_every: float = 15.0
    sleep: Callable[[float], None] = time.sleep
    clock: Callable[[], float] = time.monotonic
    last_check: float = field(default=-1e9)

    def __call__(self) -> None:
        self._raise_if_stopped()
        if self.clock() - self.last_check < self.check_every:
            return
        self.last_check = self.clock()
        if decide(self.sensor.read(), self.limits, paused=False) is ThermalAction.RUN:
            return
        self._wait_until_cool()

    def _wait_until_cool(self) -> None:
        while True:
            reading = self.sensor.read()
            if decide(reading, self.limits, paused=True) is ThermalAction.RUN:
                break
            detail = f"gpu={reading.gpu_celsius}C cpu={reading.cpu_celsius}C"
            self.sink.report(ProgressEvent(Stage.PAUSED, "", detail=detail))
            self.sleep(self.poll_every)
            self._raise_if_stopped()
        self.last_check = self.clock()

    def _raise_if_stopped(self) -> None:
        if self.stop.is_set():
            raise JobCancelledError
