from dataclasses import dataclass

from erudio_transcriber.ports.audio_extractor import AudioExtractor
from erudio_transcriber.ports.slides import FrameExtractor, SlideDetector
from erudio_transcriber.ports.thermal_sensor import ThermalSensor
from erudio_transcriber.ports.transcriber import Transcriber


@dataclass(frozen=True, slots=True)
class Toolkit:
    transcriber: Transcriber
    audio: AudioExtractor
    slides: SlideDetector
    frames: FrameExtractor
    sensor: ThermalSensor


@dataclass(frozen=True, slots=True)
class JobSettings:
    language: str = "pt"
    with_frames: bool = True
