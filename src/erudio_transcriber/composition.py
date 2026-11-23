import threading
from typing import cast

from erudio_transcriber.application.thermal_gate import ThermalGate
from erudio_transcriber.application.toolkit import Toolkit
from erudio_transcriber.domain.thermal import ThermalLimits
from erudio_transcriber.ports.audio_extractor import AudioExtractor
from erudio_transcriber.ports.progress_sink import ProgressSink
from erudio_transcriber.ports.slides import FrameExtractor, SlideDetector
from erudio_transcriber.ports.thermal_sensor import ThermalSensor
from erudio_transcriber.ports.transcriber import Transcriber
from erudio_transcriber.registry import DriverGroup, Options, load

DEFAULT_DRIVERS = {
    DriverGroup.TRANSCRIBER: "faster-whisper",
    DriverGroup.AUDIO_EXTRACTOR: "ffmpeg",
    DriverGroup.SLIDE_DETECTOR: "ffmpeg",
    DriverGroup.FRAME_EXTRACTOR: "ffmpeg",
    DriverGroup.THERMAL_SENSOR: "nvidia-smi",
}


def build_toolkit(options: Options, names: dict[DriverGroup, str] | None = None) -> Toolkit:
    chosen = {**DEFAULT_DRIVERS, **(names or {})}

    def driver(group: DriverGroup) -> object:
        return load(group, chosen[group])(options)

    return Toolkit(
        transcriber=cast(Transcriber, driver(DriverGroup.TRANSCRIBER)),
        audio=cast(AudioExtractor, driver(DriverGroup.AUDIO_EXTRACTOR)),
        slides=cast(SlideDetector, driver(DriverGroup.SLIDE_DETECTOR)),
        frames=cast(FrameExtractor, driver(DriverGroup.FRAME_EXTRACTOR)),
        sensor=cast(ThermalSensor, driver(DriverGroup.THERMAL_SENSOR)),
    )


def build_gate(
    toolkit: Toolkit, limits: ThermalLimits, sink: ProgressSink, stop: threading.Event
) -> ThermalGate:
    return ThermalGate(toolkit.sensor, limits, sink, stop)
