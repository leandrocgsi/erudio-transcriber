from collections.abc import Callable, Mapping
from enum import StrEnum
from importlib.metadata import entry_points
from typing import TypeAlias

Options: TypeAlias = Mapping[str, str]
DriverFactory: TypeAlias = Callable[[Options], object]


class DriverGroup(StrEnum):
    TRANSCRIBER = "erudio_transcriber.transcribers"
    AUDIO_EXTRACTOR = "erudio_transcriber.audio_extractors"
    SLIDE_DETECTOR = "erudio_transcriber.slide_detectors"
    FRAME_EXTRACTOR = "erudio_transcriber.frame_extractors"
    THERMAL_SENSOR = "erudio_transcriber.thermal_sensors"


class DriverNotFoundError(LookupError):
    pass


def available(group: DriverGroup) -> tuple[str, ...]:
    return tuple(sorted(entry.name for entry in entry_points(group=group.value)))


def load(group: DriverGroup, name: str) -> DriverFactory:
    """A driver is registered as an entry point that points to a factory taking string options."""
    for entry in entry_points(group=group.value):
        if entry.name == name:
            factory: DriverFactory = entry.load()
            return factory
    msg = f"No {group.value} driver named '{name}'. Installed: {', '.join(available(group))}"
    raise DriverNotFoundError(msg)
