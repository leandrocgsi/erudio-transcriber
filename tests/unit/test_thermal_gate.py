import threading
from collections.abc import Iterator

import pytest

from erudio_transcriber.application.thermal_gate import ThermalGate
from erudio_transcriber.domain.errors import JobCancelledError
from erudio_transcriber.domain.progress import ProgressEvent, Stage
from erudio_transcriber.domain.thermal import ThermalLimits, ThermalReading


class ScriptedSensor:
    def __init__(self, temperatures: list[int]) -> None:
        self.temperatures: Iterator[int] = iter(temperatures)

    def read(self) -> ThermalReading:
        return ThermalReading(gpu_celsius=next(self.temperatures), cpu_celsius=None)


class RecordingSink:
    def __init__(self) -> None:
        self.events: list[ProgressEvent] = []

    def report(self, event: ProgressEvent) -> None:
        self.events.append(event)


def make_gate(
    temperatures: list[int], stop: threading.Event | None = None
) -> tuple[ThermalGate, RecordingSink, list[float]]:
    sink = RecordingSink()
    sleeps: list[float] = []
    gate = ThermalGate(
        ScriptedSensor(temperatures),
        ThermalLimits(78, 72),
        sink,
        stop or threading.Event(),
        sleep=sleeps.append,
    )
    return gate, sink, sleeps


def test_gate_lets_work_through_when_cool() -> None:
    gate, sink, sleeps = make_gate([60])
    gate()
    assert sink.events == []
    assert sleeps == []


def test_gate_waits_until_the_machine_cools_below_the_resume_point() -> None:
    gate, sink, sleeps = make_gate([80, 79, 75, 71])
    gate()
    assert [event.stage for event in sink.events] == [Stage.PAUSED, Stage.PAUSED]
    assert len(sleeps) == 2


def test_gate_raises_when_cancelled() -> None:
    stop = threading.Event()
    stop.set()
    gate, _, _ = make_gate([60], stop)
    with pytest.raises(JobCancelledError):
        gate()
