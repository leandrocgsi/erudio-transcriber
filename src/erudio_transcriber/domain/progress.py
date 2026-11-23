from dataclasses import dataclass
from enum import StrEnum


class Stage(StrEnum):
    VOCABULARY = "vocabulary"
    AUDIO = "audio"
    TRANSCRIPTION = "transcription"
    FRAMES = "frames"
    PAUSED = "paused"
    DONE = "done"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class ProgressEvent:
    stage: Stage
    item: str
    fraction: float | None = None
    detail: str = ""
