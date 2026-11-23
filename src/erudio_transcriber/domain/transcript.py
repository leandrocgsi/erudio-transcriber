from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Segment:
    start: float
    end: float
    text: str


@dataclass(frozen=True, slots=True)
class Transcript:
    segments: tuple[Segment, ...]
    duration: float
    language: str
